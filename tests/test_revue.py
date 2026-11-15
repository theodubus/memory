"""Le dossier de la revue adversariale d'un lot (ADR-0042) : ce que reçoit
le relecteur, qui n'a pas la conversation de l'agent mais peut lire le dépôt."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, review as revue, utils as outils


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


ADR = ("<!-- socle: couche=decisions zone=publique -->\n# ADR-0001 — Doubler les entrées\n\n"
       "> statut : acceptée · date : 2026-11-02\n\n## Décision\n\n`double(x)` rend `2 * x`, entiers compris.\n")
SUJET = ("<!-- socle: couche=backlog zone=publique -->\n# B-0001 — Doubler\n\n"
         "> statut : {statut} · origine : ADR-0001\n\nSelon ADR-0001.\n\n## Fait quand\n\n- [x] double est écrit\n")


def commande(racine, **options):
    """`socle review` lancé sur `racine` : son code, sa sortie, ses erreurs."""
    import argparse
    import contextlib
    import io

    from socle import cli

    args = argparse.Namespace(root=str(racine), base=None, max_bytes=60_000, since=None)
    for cle, valeur in options.items():
        setattr(args, cle, valeur)
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
        code = cli.cmd_review(args)
    return code, out.getvalue(), err.getvalue()


class _Lot(unittest.TestCase):
    """Un dépôt cloné, sa branche de travail, et un lot à y faire."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-revue-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        source = self.dossier / "source"
        source.mkdir()
        git(source, "init", "-q", "-b", "main")
        (source / "calc.py").write_text("def double(x):\n    return x + x\n")
        (source / "memory/decisions").mkdir(parents=True)
        (source / "memory/backlog").mkdir(parents=True)
        (source / "memory/decisions/ADR-0001-doubler-les-entrees.md").write_text(ADR)
        (source / "memory/backlog/B-0001-doubler.md").write_text(SUJET.format(statut="ouvert"))
        git(source, "add", "-A")
        git(source, "commit", "-qm", "un")
        self.racine = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(source), str(self.racine))
        git(self.racine, "switch", "-q", "-c", "travail")
        self.projet = config.Projet(racine=self.racine)

    def lot(self):
        """Un lot : du code changé, et le sujet qu'il ferme."""
        (self.racine / "calc.py").write_text("def double(x):\n    return x * 2\n")
        (self.racine / "memory/backlog/B-0001-doubler.md").write_text(SUJET.format(statut="fait"))
        git(self.racine, "commit", "-qam", "le lot")


class TestDossier(_Lot):
    def test_la_base_est_la_branche_distante_sinon_la_branche_par_defaut(self):
        self.assertEqual(revue.base_du_lot(self.racine), "origin/main")
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        self.assertEqual(revue.base_du_lot(self.racine), "origin/travail")

    def test_le_dossier_donne_la_consigne_le_diff_le_sujet_et_sa_decision(self):
        self.lot()
        texte = revue.dossier(self.projet)
        self.assertIn("Ton rôle est de le prendre en défaut", texte)
        # Il peut lire le dépôt pour vérifier un constat (D-0076, ADR-0044).
        self.assertIn("tu peux lire le dépôt pour vérifier un constat", texte)
        self.assertIn("## Le diff du lot (1 fichier(s), depuis origin/main)", texte)
        self.assertIn("+    return x * 2", texte)
        # La mémoire ne passe pas par le diff, mais par ses sujets.
        self.assertNotIn("diff --git a/memory/", texte)
        servis, ouverts = revue.sujets_du_lot(self.projet, "origin/main")
        self.assertEqual(([e.id for e in servis], ouverts), (["B-0001"], []))
        self.assertIn("- [x] double est écrit", texte)
        self.assertEqual([e.id for e in revue.decisions_citees(self.projet, servis)], ["ADR-0001"])
        self.assertIn("`double(x)` rend `2 * x`, entiers compris.", texte)

    def test_un_sujet_encore_ouvert_n_est_pas_dans_le_dossier(self):
        (self.racine / "calc.py").write_text("def double(x):\n    return x * 2\n")
        git(self.racine, "commit", "-qam", "le code seul")
        self.assertEqual(revue.sujets_du_lot(self.projet, "origin/main"), ([], []))
        self.assertNotIn("## Les sujets que le lot ferme", revue.dossier(self.projet))

    def test_un_gros_diff_se_tronque_et_le_dit(self):
        self.lot()
        texte = revue.dossier(self.projet, plafond=40)
        self.assertIn("(diff tronqué :", texte)
        self.assertIn("`git diff origin/main` les donne", texte)

    def test_la_commande_imprime_le_dossier(self):
        import argparse
        import contextlib
        import io

        from socle import cli

        self.lot()
        with contextlib.redirect_stdout(io.StringIO()) as flux:
            code = cli.cmd_review(argparse.Namespace(root=str(self.racine), base="origin/main", max_bytes=60_000))
        self.assertEqual(code, 0)
        self.assertEqual(flux.getvalue(), revue.dossier(config.Projet.charger(self.racine), "origin/main"))

    def test_sans_changement_rien_a_relire(self):
        self.assertIn("(aucun changement hors de la mémoire : rien à relire)", revue.dossier(self.projet))


class TestBarre(_Lot):
    """ADR-0073 : le relecteur juge le lot contre le critère et le modèle de
    menace de ses sujets, et classe chaque constat, bloquant, pour le
    backlog ou écarté (D-0112, D-0116)."""

    GARDE = ("<!-- socle: couche=backlog zone=publique -->\n# B-0003 — Refuser l'écriture du verrou\n\n"
             "> statut : ouvert · origine : ADR-0001\n\n## Modèle de menace\n\nUn agent distrait, pas hostile : "
             "une redirection vers le verrou est arrêtée, un interpréteur qui l'écrit passe.\n\n"
             "## Fait quand\n\n- [x] la redirection est refusée\n- [ ] l'interpréteur est refusé\n")

    def test_la_consigne_donne_la_barre_et_les_trois_classes(self):
        self.lot()
        texte = revue.dossier(self.projet)
        self.assertIn("Ta barre est celle des sujets du lot, plus bas : leur critère « Fait quand »", texte)
        self.assertIn("**Bloquant** : il contredit un critère coché ou une décision citée", texte)
        self.assertIn("contourne un garde-fou dans son modèle de menace", texte)
        self.assertIn("un garde-fou que le lot pose ou change sans modèle de menace écrit est lui-même un constat "
                      "bloquant", texte)
        self.assertIn("**Pour le backlog** : un constat qui ne bloque pas, s'il peut se produire dans l'usage normal "
                      "du projet, ou si rien ne rattrape ensuite son effet", texte)
        self.assertIn("**Écarté** : un constat exotique", texte)
        self.assertIn("Seuls les bloquants se corrigent dans le lot.", texte)
        self.assertIn("Rends trois listes numérotées, « Bloquants », « Pour le backlog » puis « Écartés »", texte)
        # Les trois parties de la consigne précèdent le diff.
        self.assertLess(texte.index("Rends trois listes"), texte.index("## Le diff du lot"))

    def test_un_sujet_encore_ouvert_que_le_lot_touche_donne_son_critere_et_son_modele_de_menace(self):
        base = self.racine / "memory/backlog/B-0003-refuser.md"
        base.write_text(self.GARDE.replace("- [x] la redirection", "- [ ] la redirection"), encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "le sujet du garde-fou")
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        (self.racine / "garde.py").write_text("def refuse(cmd):\n    return '>' in cmd\n")
        base.write_text(self.GARDE, encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "la redirection refusée")
        servis, ouverts = revue.sujets_du_lot(self.projet, "origin/travail")
        self.assertEqual(([e.id for e in servis], ouverts), (["B-0003"], []))
        texte = revue.dossier(self.projet)
        self.assertIn("## Les sujets du lot : leur critère « Fait quand » est ta barre", texte)
        self.assertIn("## Modèle de menace\n\nUn agent distrait, pas hostile", texte)
        self.assertIn("- [x] la redirection est refusée\n- [ ] l'interpréteur est refusé", texte)
        # Un sujet ouvert que le lot ne touche pas n'y est pas.
        self.assertNotIn("# B-0001 — Doubler", texte)

    def test_un_sujet_que_le_lot_ouvre_ne_donne_que_son_titre(self):
        self.lot()
        (self.racine / "memory/backlog/B-0002-tripler.md").write_text(
            "<!-- socle: couche=backlog zone=publique -->\n# B-0002 — Tripler, renvoyé au backlog\n\n"
            "> statut : ouvert · origine : ADR-0001\n\nUn constat de la revue, hors du critère.\n",
            encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "un sujet ouvert par le lot")
        servis, ouverts = revue.sujets_du_lot(self.projet, "origin/main")
        self.assertEqual(([e.id for e in servis], [e.id for e in ouverts]), (["B-0001"], ["B-0002"]))
        texte = revue.dossier(self.projet)
        self.assertIn("## Les sujets que le lot ouvre : ce qu'il renvoie au backlog\n\n"
                      "- B-0002 — Tripler, renvoyé au backlog", texte)
        self.assertNotIn("Un constat de la revue, hors du critère.", texte)
        # Ouvert et clos dans le même lot, il est servi.
        chemin = self.racine / "memory/backlog/B-0002-tripler.md"
        chemin.write_text(chemin.read_text(encoding="utf-8").replace("statut : ouvert", "statut : fait · ref : x"),
                          encoding="utf-8")
        git(self.racine, "commit", "-qam", "clos")
        servis, ouverts = revue.sujets_du_lot(self.projet, "origin/main")
        self.assertEqual(([e.id for e in servis], ouverts), (["B-0001", "B-0002"], []))

    VOISIN = ("<!-- socle: couche=backlog zone=publique -->\n# B-0002 — Un voisin\n\n"
              "> statut : ouvert · origine : ADR-0001\n\nLe voisin.\n\n## Fait quand\n\n- [ ] le voisin est fait\n")
    ANCIEN = ("<!-- socle: couche=backlog zone=publique -->\n# B-0004 — Un ancien\n\n"
              "> statut : fait · origine : ADR-0001 · ref : x\n\nL'ancien.\n\n## Fait quand\n\n- [x] l'ancien\n")

    def test_un_sujet_touche_en_passant_n_est_pas_la_barre(self):
        """B-0213, ADR-0081 : un `après` changé, un constat ajouté, un sujet
        clos rangé par `socle archive` ne font pas la barre du relecteur."""
        backlog = self.racine / "memory/backlog"
        (backlog / "B-0002-voisin.md").write_text(self.VOISIN, encoding="utf-8")
        (backlog / "B-0004-ancien.md").write_text(self.ANCIEN, encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "deux sujets")
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        self.lot()
        (backlog / "B-0002-voisin.md").write_text(
            self.VOISIN.replace("origine : ADR-0001", "origine : ADR-0001 · après : B-0001")
            .replace("Le voisin.", "Le voisin.\n\nUn constat ajouté par une revue."), encoding="utf-8")
        (backlog / "closed").mkdir()
        git(self.racine, "mv", "memory/backlog/B-0004-ancien.md", "memory/backlog/closed/B-0004-ancien.md")
        git(self.racine, "commit", "-qam", "en passant")
        texte = revue.dossier(self.projet)
        self.assertNotIn("# B-0002 — Un voisin", texte)
        self.assertNotIn("# B-0004 — Un ancien", texte)
        self.assertIn("- [x] double est écrit", texte)
        servis, ouverts = revue.sujets_du_lot(self.projet, "origin/travail")
        self.assertEqual(([e.id for e in servis], ouverts), (["B-0001"], []))
        # Une case cochée, ou un statut changé, le remettent dans la barre.
        (backlog / "B-0002-voisin.md").write_text(self.VOISIN.replace("- [ ] le voisin", "- [x] le voisin"),
                                                  encoding="utf-8")
        self.assertEqual([e.id for e in revue.sujets_du_lot(self.projet, "origin/travail")[0]],
                         ["B-0001", "B-0002"])

    def test_un_sujet_que_le_lot_clot_et_range_reste_la_barre(self):
        """B-0214 : le lot clôt son sujet, puis `socle archive` le range
        dans `closed/` ; rangé, indexé ou commité, il reste la barre, avec
        la décision qu'il cite."""
        from socle import archive as archivage

        self.lot()
        self.assertEqual(archivage.ranger_backlog(self.racine),
                         [("memory/backlog/B-0001-doubler.md", "memory/backlog/closed/B-0001-doubler.md")])
        for etape in ("indexé", "commité"):
            if etape == "commité":
                git(self.racine, "commit", "-qm", "rangé")
            servis, ouverts = revue.sujets_du_lot(self.projet, "origin/main")
            self.assertEqual(([e.fichier for e in servis], ouverts),
                             (["memory/backlog/closed/B-0001-doubler.md"], []), etape)
            texte = revue.dossier(self.projet)
            self.assertIn("## Les sujets du lot : leur critère « Fait quand » est ta barre\n\n# B-0001 — Doubler",
                          texte, etape)
            self.assertIn("- [x] double est écrit", texte, etape)
            self.assertIn("## Les décisions et les demandes qu'ils citent\n\n# ADR-0001", texte, etape)

    # Le préfixe des identifiants privés, à part : écrit en toutes lettres
    # dans un fichier public, le contrôle de la mémoire privée le refuse.
    P = "P"
    PRIVE = ("<!-- socle: couche=backlog zone=privee -->\n# {ident} — {titre} le client Orion\n\n"
             "> statut : {statut} · origine : ADR-0001\n\nLe client Orion.\n\n## Fait quand\n\n"
             "- [{case}] Orion démarché\n")

    def test_un_sujet_prive_n_est_pas_dans_le_dossier(self):
        """B-0214 : la mémoire privée ne sort pas vers le relecteur. Un sujet
        privé que le lot clôt, un autre qu'il ouvre, et la décision privée
        qu'il écrit ne sont ni la barre, ni ce qu'il renvoie au backlog, ni
        ses décisions ; le sujet public du lot l'est toujours."""
        clos, ouvert, decision = f"{self.P}B-0002", f"{self.P}B-0003", f"{self.P}ADR-0002"
        prive = self.racine / "memory/private"
        (prive / "backlog").mkdir(parents=True)
        (prive / "decisions").mkdir()
        sujet = prive / f"backlog/{clos}-demarcher.md"
        sujet.write_text(self.PRIVE.format(ident=clos, titre="Démarcher", statut="ouvert", case=" "),
                         encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "un sujet privé")
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        self.lot()
        sujet.write_text(self.PRIVE.format(ident=clos, titre="Démarcher", statut="fait · ref : x", case="x"),
                         encoding="utf-8")
        (prive / f"backlog/{ouvert}-relancer.md").write_text(
            self.PRIVE.format(ident=ouvert, titre="Relancer", statut="ouvert", case=" "), encoding="utf-8")
        (prive / f"decisions/{decision}-viser-orion.md").write_text(
            f"<!-- socle: couche=decisions zone=privee -->\n# {decision} — Viser Orion\n\n"
            "> statut : acceptée · date : 2026-11-15\n\n## Décision\n\nOrion d'abord.\n", encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "le lot privé")
        from socle import memory as memoire

        mem = memoire.Memoire.charger(self.racine)
        self.assertEqual({e.id for e in mem.entrees() if memoire.est_prive(e.fichier)}, {clos, ouvert, decision})
        servis, ouverts = revue.sujets_du_lot(self.projet, "origin/travail")
        self.assertEqual(([e.id for e in servis], ouverts), (["B-0001"], []))
        self.assertEqual(revue.decisions_ecrites(self.projet, "origin/travail"), [])
        texte = revue.dossier(self.projet)
        self.assertIn("- [x] double est écrit", texte)
        for prive_ in ("Orion", clos, ouvert, decision, "memory/private"):
            self.assertNotIn(prive_, texte)

    def test_la_seconde_revue_ne_montre_que_la_correction_et_garde_les_sujets_du_lot(self):
        self.lot()
        relu = git(self.racine, "rev-parse", "HEAD").strip()
        (self.racine / "calc.py").write_text("def double(x):\n    return int(x) * 2\n")
        git(self.racine, "commit", "-qam", "Le bloquant 1 corrigé : une chaîne se double en entier\n\n"
                                         "Le détail.\n\nCo-Authored-By: t <t@t>\nSocle-Hooks: Stop=1")
        self.assertEqual(revue.messages_depuis(self.racine, relu),
                         ["Le bloquant 1 corrigé : une chaîne se double en entier\n\nLe détail."])
        texte = revue.dossier(self.projet, depuis=relu)
        self.assertIn("## Seconde revue\n\nSeconde revue : ce diff corrige des constats bloquants", texte)
        self.assertIn("```text\nLe bloquant 1 corrigé : une chaîne se double en entier\n\nLe détail.\n```", texte)
        self.assertNotIn("Co-Authored-By", texte)
        self.assertIn(f"## Le diff de la correction (1 fichier(s), depuis {relu})", texte)
        self.assertIn("-    return x * 2\n+    return int(x) * 2", texte)
        self.assertNotIn("-    return x + x", texte)
        self.assertIn("- [x] double est écrit", texte)
        self.assertIn("`double(x)` rend `2 * x`, entiers compris.", texte)

    def test_la_seconde_revue_garde_le_titre_d_un_correctif(self):
        """La revue de B-0209, constat bloquant 1 : un titre `fix: …` ou un
        trailer seul ressemblent à une ligne de fin, mais restent."""
        self.lot()
        relu = git(self.racine, "rev-parse", "HEAD").strip()
        (self.racine / "calc.py").write_text("def double(x):\n    return int(x) * 2\n")
        git(self.racine, "commit", "-qam", "fix: une chaîne se double en entier\n\nCo-Authored-By: t <t@t>")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * int(x)\n")
        git(self.racine, "commit", "-qam", "Corrige: B-0001")
        (self.racine / "calc.py").write_text("def double(x):\n    return int(x) + int(x)\n")
        git(self.racine, "commit", "-qam", "Le cas vide\n\nLe détail.\nNote: le cas vide reste ouvert\n\n"
                                         "Co-Authored-By: t <t@t>")
        self.assertEqual(revue.messages_depuis(self.racine, relu),
                         ["fix: une chaîne se double en entier", "Corrige: B-0001",
                          "Le cas vide\n\nLe détail.\nNote: le cas vide reste ouvert"])

    def test_la_specification_que_le_lot_ecrit_est_dans_le_dossier_sans_etre_citee(self):
        self.lot()
        (self.racine / "memory/decisions/ADR-0002-le-modele-de-menace.md").write_text(
            "<!-- socle: couche=decisions zone=publique -->\n# ADR-0002 — Le modèle de menace du doublement\n\n"
            "> statut : acceptée · date : 2026-11-13\n\n## Décision\n\nUne chaîne n'est pas doublée.\n",
            encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "la spécification")
        self.assertEqual([e.id for e in revue.decisions_ecrites(self.projet, "origin/main")], ["ADR-0002"])
        texte = revue.dossier(self.projet)
        self.assertIn("## Les décisions et les demandes que le lot écrit\n\n# ADR-0002 — Le modèle de menace du "
                      "doublement", texte)
        self.assertIn("Une chaîne n'est pas doublée.", texte)
        # Celle que le sujet cite, déjà là à la base, suit à part.
        self.assertIn("## Les décisions et les demandes qu'ils citent\n\n# ADR-0001", texte)
        self.assertEqual(revue.decisions_ecrites(self.projet, "HEAD"), [])

    def test_la_commande_donne_la_seconde_revue(self):
        import argparse
        import contextlib
        import io

        from socle import cli

        self.lot()
        relu = git(self.racine, "rev-parse", "HEAD").strip()
        with contextlib.redirect_stdout(io.StringIO()) as flux:
            code = cli.cmd_review(argparse.Namespace(root=str(self.racine), base=None, max_bytes=60_000,
                                                     since=relu))
        self.assertEqual(code, 0)
        self.assertEqual(flux.getvalue(), revue.dossier(config.Projet.charger(self.racine), None, depuis=relu))
        self.assertIn("(aucun changement hors de la mémoire : rien à relire)", flux.getvalue())


class TestLotDejaPousse(_Lot):
    """B-0212, ADR-0075 : un lot poussé avant sa revue, le cas ordinaire en
    session cloud, laissait un dossier vide, sans diff ni sujets, que le
    relecteur jugeait sans constat."""

    def setUp(self):
        super().setUp()
        self.commun = git(self.racine, "rev-parse", "origin/main").strip()

    def correction(self):
        (self.racine / "calc.py").write_text("def double(x):\n    return int(x) * 2\n")
        git(self.racine, "commit", "-qam", "Le bloquant 1 corrigé")

    def test_un_lot_deja_pousse_se_mesure_depuis_l_ancetre_commun_et_le_dit(self):
        self.lot()
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        texte = revue.dossier(self.projet)
        self.assertIn("+    return x * 2", texte)
        self.assertIn("- [x] double est écrit", texte)
        self.assertIn("`double(x)` rend `2 * x`, entiers compris.", texte)
        self.assertIn(f"## Le diff du lot (1 fichier(s), depuis {self.commun})", texte)
        self.assertTrue(revue.contient_le_lot(self.projet, "origin/travail"))
        self.assertFalse(revue.contient_le_lot(self.projet, self.commun))
        base, note = revue.base_par_defaut(self.projet)
        self.assertEqual(base, self.commun)
        self.assertIn("la branche distante origin/travail contient déjà le lot", note)
        self.assertIn("`socle review --base <le commit d'avant le lot>`", note)
        self.assertIn(note, texte)
        # Une base donnée est prise telle quelle.
        self.assertIn("(aucun changement hors de la mémoire : rien à relire)",
                      revue.dossier(self.projet, "origin/travail"))

    def test_apres_une_fusion_par_ecrasement_le_lot_suivant_ne_reprend_pas_le_lot_fusionne(self):
        """La revue du lot 5 : une pull request fusionnée par écrasement, la
        branche distante supprimée sur GitHub mais son image locale restée
        (aucun `fetch --prune`), la branche repartie de la branche par
        défaut ; le lot suivant ne se mesure pas depuis le début du lot
        fusionné, qui reviendrait avec son sujet clos."""
        self.lot()
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        source = self.dossier / "source"
        git(source, "merge", "-q", "--squash", "travail")
        git(source, "commit", "-qm", "le lot (#1)")
        git(source, "branch", "-q", "-D", "travail")
        git(self.racine, "fetch", "-q", "origin")
        git(self.racine, "reset", "-q", "--hard", "origin/main")
        (self.racine / "calc.py").write_text("def double(x):\n    return x * 2\n\n\ndef triple(x):\n    return x * 3\n")
        git(self.racine, "commit", "-qam", "le lot suivant")
        fusion = git(self.racine, "rev-parse", "origin/main").strip()
        base, note = revue.base_par_defaut(self.projet)
        self.assertEqual(base, fusion)
        self.assertIn("la branche distante origin/travail est restée en arrière de", note)
        texte = revue.dossier(self.projet)
        self.assertIn("+def triple(x):", texte)
        self.assertNotIn("+    return x * 2", texte)
        self.assertNotIn("- [x] double est écrit", texte)

    def test_un_lot_pas_encore_pousse_se_mesure_toujours_depuis_la_branche_distante(self):
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        self.lot()
        self.assertEqual(revue.base_par_defaut(self.projet), ("origin/travail", None))
        self.assertIn("## Le diff du lot (1 fichier(s), depuis origin/travail)", revue.dossier(self.projet))
        # Sans branche distante, la branche par défaut, sans note.
        git(self.racine, "branch", "-q", "--unset-upstream")
        self.assertEqual(revue.base_par_defaut(self.projet), ("origin/main", None))

    def test_la_seconde_revue_d_un_lot_deja_pousse_garde_ses_sujets(self):
        self.lot()
        relu = git(self.racine, "rev-parse", "HEAD").strip()
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        self.correction()
        # La correction pas encore poussée : le commit relu l'est déjà.
        self.assertTrue(revue.contient_le_lot(self.projet, "origin/travail", relu))
        self.assertEqual(revue.base_par_defaut(self.projet, relu)[0], self.commun)
        git(self.racine, "push", "-q")
        texte = revue.dossier(self.projet, depuis=relu)
        self.assertIn("la branche distante origin/travail contient déjà le lot", texte)
        self.assertIn(f"## Le diff de la correction (1 fichier(s), depuis {relu})", texte)
        self.assertIn("+    return int(x) * 2", texte)
        self.assertIn("- [x] double est écrit", texte)

    def test_un_lot_deja_dans_la_branche_par_defaut_dit_pourquoi_le_dossier_est_vide(self):
        self.lot()
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        git(self.dossier / "source", "merge", "-q", "--ff-only", "travail")
        git(self.racine, "fetch", "-q", "origin")
        base, note = revue.base_par_defaut(self.projet)
        self.assertEqual(base, "origin/travail")
        self.assertIn("la branche distante origin/travail contient déjà le lot, et la branche par défaut "
                      "origin/main aussi", note)
        self.assertIn("`socle review --base <ce commit>`", note)
        texte = revue.dossier(self.projet)
        self.assertIn(note, texte)
        self.assertIn("(aucun changement hors de la mémoire : rien à relire)", texte)
        # La commande qu'elle donne relit le lot.
        self.assertIn("+    return x * 2", revue.dossier(self.projet, self.commun))


    def test_un_lot_pousse_en_partie_le_dit(self):
        """La revue de B-0212 : un lot poussé à moitié ne montrait que sa
        partie non poussée, sans le dire."""
        (self.racine / "calc.py").write_text("def double(x):\n    return x * 2\n")
        git(self.racine, "commit", "-qam", "la première moitié")
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        git(self.racine, "commit", "-qam", "la seconde moitié")
        texte = revue.dossier(self.projet)
        note = (f"(la branche distante origin/travail porte déjà 1 commit(s) hors de la mémoire depuis {self.commun}, "
                "l'ancêtre commun de HEAD et de origin/main, que ce dossier ne montre pas : si le lot en comprend, "
                "`socle review --base <le commit d'avant le lot>`)")
        self.assertIn(note, texte)
        self.assertEqual(revue.base_par_defaut(self.projet), ("origin/travail", note))
        self.assertIn("## Le diff du lot (1 fichier(s), depuis origin/travail)", texte)

    def test_un_commit_de_memoire_seule_deja_pousse_ne_fait_pas_de_note(self):
        (self.racine / "memory/journal").mkdir(parents=True)
        (self.racine / "memory/journal/2026-11-1.md").write_text("<!-- socle: couche=journal zone=publique -->\n",
                                                               encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "la mémoire seule")
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        self.lot()
        self.assertEqual(revue.base_par_defaut(self.projet), ("origin/travail", None))

    def test_des_lots_deja_pousses_disent_sur_combien_de_commits_porte_la_mesure(self):
        """La revue de B-0212 : des lots poussés qui s'accumulent se relisent
        ensemble ; la note dit sur combien de commits, et comment réduire."""
        self.lot()
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        self.correction()
        (self.racine / "memory/journal").mkdir(parents=True)
        (self.racine / "memory/journal/2026-11-1.md").write_text("<!-- socle: couche=journal zone=publique -->\n",
                                                               encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "la mémoire seule")
        git(self.racine, "push", "-q")
        base, note = revue.base_par_defaut(self.projet)
        self.assertEqual(base, self.commun)
        self.assertIn(f"il se mesure depuis {self.commun}, l'ancêtre commun de HEAD et de origin/main, sur 2 "
                      "commit(s) hors de la mémoire ; s'il commence plus tard, `socle review --base <le commit "
                      "d'avant le lot>`)", note)

    def test_sous_since_la_commande_de_la_note_garde_since(self):
        """La revue de B-0212 : sous `--since`, la note proposait une
        commande sans `--since`, qui donne une première revue."""
        self.lot()
        relu = git(self.racine, "rev-parse", "HEAD").strip()
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        self.correction()
        git(self.racine, "push", "-q")
        texte = revue.dossier(self.projet, depuis=relu)
        self.assertIn(f"`socle review --base <le commit d'avant le lot> --since {relu}`)", texte)
        self.assertNotIn("`socle review --base <le commit d'avant le lot>`)", texte)

    def test_une_branche_par_defaut_devinee_le_dit(self):
        """La revue de B-0212 : quand la branche par défaut n'est que
        devinée, la note disait qu'elle contient aussi le lot."""
        self.lot()
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        git(self.racine, "remote", "set-head", "origin", "-d")
        git(self.racine, "update-ref", "-d", "refs/remotes/origin/main")
        git(self.racine, "branch", "-q", "-D", "main")
        base, note = revue.base_par_defaut(self.projet)
        self.assertIn("(la branche distante origin/travail contient déjà le lot, et ce clone ne connaît pas la "
                      "branche par défaut : ni `origin/HEAD`, ni `main`, ni `master`.", note)
        self.assertNotIn("aussi", note)
        self.assertEqual(base, "origin/travail")
        self.assertTrue(outils.branche_par_defaut_devinee(self.racine))

    def test_un_clone_superficiel_sans_ancetre_commun_le_dit(self):
        """La revue de B-0212 : sans ancêtre commun, un clone superficiel,
        la note disait que la branche par défaut contient aussi le lot ; une
        base sans ancêtre commun avec HEAD est refusée (ADR-0081)."""
        source = self.dossier / "source"
        git(source, "switch", "-q", "-c", "travail")
        (source / "calc.py").write_text("def double(x):\n    return x * 2\n")
        git(source, "commit", "-qam", "le lot")
        git(source, "switch", "-q", "main")
        (source / "autre.py").write_text("AUTRE = 1\n")
        git(source, "add", "-A")
        git(source, "commit", "-qm", "main avance")
        superficiel = self.dossier / "superficiel"
        git(self.dossier, "clone", "-q", "--depth", "1", "--no-single-branch", source.as_uri(), str(superficiel))
        git(superficiel, "switch", "-q", "travail")
        projet = config.Projet(racine=superficiel)
        base, note = revue.base_par_defaut(projet)
        self.assertIn("(la branche distante origin/travail contient déjà le lot, et HEAD n'a pas d'ancêtre commun "
                      "avec la branche par défaut origin/main dans ce clone, superficiel peut-être (`git fetch "
                      "--unshallow`).", note)
        self.assertEqual(base, "origin/travail")
        code, out, err = commande(superficiel, base="origin/main")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("aucun ancêtre commun entre HEAD et origin/main dans ce clone", err)


class TestMesure(_Lot):
    """B-0213, ADR-0081 : le lot se mesure depuis l'ancêtre commun de sa base
    et de HEAD, et une référence qui ne le mesure pas est refusée."""

    SUJET_DE_MAIN = ("<!-- socle: couche=backlog zone=publique -->\n# B-0005 — Un sujet de main\n\n"
                     "> statut : {statut} · origine : ADR-0001\n\nSur main.\n\n## Fait quand\n\n- [{case}] fait\n")

    def avancer_main(self):
        """La branche par défaut avance sans la branche : du code, et un
        sujet qu'elle seule clôt."""
        source = self.dossier / "source"
        (source / "autre.py").write_text("ECRIT_SUR_MAIN = 1\n")
        (source / "memory/backlog/B-0005-de-main.md").write_text(
            self.SUJET_DE_MAIN.format(statut="fait · ref : x", case="x"), encoding="utf-8")
        git(source, "add", "-A")
        git(source, "commit", "-qm", "main avance")
        git(self.racine, "fetch", "-q", "origin")

    def test_la_branche_par_defaut_qui_avance_n_entre_pas_dans_le_lot(self):
        source = self.dossier / "source"
        (source / "memory/backlog/B-0005-de-main.md").write_text(
            self.SUJET_DE_MAIN.format(statut="ouvert", case=" "), encoding="utf-8")
        git(source, "add", "-A")
        git(source, "commit", "-qm", "un sujet de main")
        git(self.racine, "fetch", "-q", "origin")
        git(self.racine, "reset", "-q", "--hard", "origin/main")
        commun = git(self.racine, "rev-parse", "HEAD").strip()
        self.lot()
        self.avancer_main()
        texte = revue.dossier(self.projet)
        self.assertNotIn("ECRIT_SUR_MAIN", texte)
        self.assertNotIn("# B-0005 — Un sujet de main", texte)
        self.assertIn("+    return x * 2", texte)
        self.assertIn("- [x] double est écrit", texte)
        self.assertIn(f"## Le diff du lot (1 fichier(s), depuis {commun}, l'ancêtre commun de HEAD et de "
                      "origin/main)", texte)
        self.assertEqual([e.id for e in revue.sujets_du_lot(self.projet, "origin/main")[0]], ["B-0001"])
        self.assertEqual(revue.debut_du_lot(self.racine, "origin/main"), commun)

    def test_un_commit_pousse_d_ailleurs_n_entre_pas_dans_le_lot(self):
        """La revue de B-0212 : une branche distante en avance sur HEAD par
        du code donnait pour diff du lot l'inverse du commit poussé
        d'ailleurs."""
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        commun = git(self.racine, "rev-parse", "HEAD").strip()
        source = self.dossier / "source"
        git(source, "switch", "-q", "travail")
        (source / "ailleurs.py").write_text("ECRIT_AILLEURS = 1\n")
        git(source, "add", "-A")
        git(source, "commit", "-qm", "poussé d'ailleurs")
        git(source, "switch", "-q", "main")
        git(self.racine, "fetch", "-q", "origin")
        # Rien du lot n'y manque encore : elle le contient.
        self.assertTrue(revue.contient_le_lot(self.projet, "origin/travail"))
        self.lot()
        texte = revue.dossier(self.projet)
        self.assertNotIn("ECRIT_AILLEURS", texte)
        self.assertIn("+    return x * 2", texte)
        self.assertIn(f"## Le diff du lot (1 fichier(s), depuis {commun}, l'ancêtre commun de HEAD et de "
                      "origin/travail)", texte)
        self.assertFalse(revue.contient_le_lot(self.projet, "origin/travail"))

    def test_une_reference_inconnue_est_refusee(self):
        self.lot()
        for option in ("base", "since"):
            code, out, err = commande(self.racine, **{option: "origin/inconnue"})
            self.assertEqual((code, out), (2, ""), option)
            self.assertIn(f"--{option} origin/inconnue : aucune branche, étiquette ni commit de ce nom dans ce "
                          "dépôt", err)
        with self.assertRaises(revue.ReferenceRefusee):
            revue.dossier(self.projet, "origin/inconnue")
        self.assertIsNone(revue.refus_des_references(self.projet, "origin/main", None))

    def test_un_since_qui_n_est_pas_un_ancetre_de_head_est_refuse(self):
        self.lot()
        self.avancer_main()
        etranger = git(self.racine, "rev-parse", "origin/main").strip()
        code, out, err = commande(self.racine, since=etranger)
        self.assertEqual((code, out), (2, ""))
        self.assertIn(f"--since {etranger} n'est pas un ancêtre de HEAD", err)
        relu = git(self.racine, "rev-parse", "HEAD").strip()
        self.assertIsNone(revue.refus_des_references(self.projet, None, relu))
        self.assertEqual(commande(self.racine, since=relu)[0], 0)

    def test_une_base_qui_n_est_pas_un_ancetre_se_mesure_depuis_l_ancetre_commun(self):
        """Une base qui a avancé reste admise : la branche par défaut après
        d'autres fusions."""
        self.lot()
        self.avancer_main()
        code, out, _ = commande(self.racine, base="origin/main")
        self.assertEqual(code, 0)
        self.assertIn("l'ancêtre commun de HEAD et de origin/main)", out)
        self.assertNotIn("ECRIT_SUR_MAIN", out)

    def test_une_base_sans_ancetre_commun_est_refusee(self):
        self.lot()
        git(self.racine, "switch", "-q", "--orphan", "orpheline")
        (self.racine / "seul.txt").write_text("seul\n")
        git(self.racine, "add", "seul.txt")
        git(self.racine, "commit", "-qm", "une autre histoire")
        git(self.racine, "switch", "-q", "-f", "travail")
        code, out, err = commande(self.racine, base="orpheline")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("aucun ancêtre commun entre HEAD et orpheline dans ce clone : rien ne mesure le lot", err)
        self.assertIsNone(revue.debut_du_lot(self.racine, "orpheline"))


class TestRelectureAFroid(unittest.TestCase):
    """ADR-0046 : le lecteur n'a que le texte de la demande, dans le rôle de
    l'humain qui revient sur le projet après des semaines."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-froid-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "memory/requests").mkdir(parents=True)
        self.texte = ("<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Choisir la source des tickets\n\n"
                      "> date : 2026-11-08\n\n## Contexte\n\nLe banc d'essai note un fournisseur.\n")
        (self.racine / "memory/requests/D-0001-choisir.md").write_text(self.texte, encoding="utf-8")
        git(self.racine, "add", "-A")
        self.projet = config.Projet(racine=self.racine)

    def test_le_dossier_donne_la_consigne_puis_la_demande_seule(self):
        texte = revue.dossier_demande(self.projet, "D-0001")
        self.assertTrue(texte.startswith("# Relecture à froid d'une demande\n\nTu es l'humain à qui cette demande "
                                         "s'adresse. Tu n'as pas ouvert ce projet depuis trois semaines"))
        self.assertIn("n'ouvre aucun lien, ne lis aucun fichier", texte)
        self.assertIn("3. Chaque mot, nom, sigle ou renvoi que le texte emploie sans te l'expliquer", texte)
        self.assertTrue(texte.endswith("## La demande\n\n" + self.texte.strip() + "\n"))

    def test_une_demande_inconnue(self):
        import argparse
        import contextlib
        import io

        from socle import cli

        self.assertIsNone(revue.dossier_demande(self.projet, "D-0002"))
        with contextlib.redirect_stderr(io.StringIO()) as err:
            code = cli.cmd_review(argparse.Namespace(root=str(self.racine), base=None, max_bytes=60_000,
                                                     request="D-0002"))
        self.assertEqual(code, 2)
        self.assertIn("aucune demande D-0002", err.getvalue())
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(cli.cmd_review(argparse.Namespace(root=str(self.racine), base=None, max_bytes=60_000,
                                                               request="D-0001")), 0)
        self.assertIn("## La demande", out.getvalue())


if __name__ == "__main__":
    unittest.main()
