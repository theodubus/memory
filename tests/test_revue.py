"""Le dossier de la revue adversariale d'un lot (ADR-0042) : ce que reçoit
le relecteur, qui n'a pas la conversation de l'agent mais peut lire le dépôt."""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, messages, review as revue, utils as outils


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
        self.assertNotIn("## Les entrées du backlog que sert le lot", revue.dossier(self.projet))

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
        self.assertIn("Ta barre est celle des entrées du backlog que sert le lot, plus bas : leurs critères (« Fait quand » d'une "
                      "tâche, « Satisfait quand » d'un besoin)", texte)
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

    def test_une_case_qui_livre_une_demande_un_releve_ou_une_entree_se_juge_par_ce_qu_elle_produit(self):
        """ADR-0088, T-0087 : la consigne, du dossier complet comme du
        dossier court, dit comment juger une telle case, dans les deux
        langues ; le format de la mémoire dit l'exception."""
        self.lot()
        attendus = {
            "fr": "Une case d'une tâche se vérifie par un test, sauf celle dont le livrable est une demande posée, "
                  "un relevé écrit (le compte rendu d'une mesure ou d'un essai) ou une entrée de la mémoire "
                  "récrite : elle se vérifie par ce qu'elle produit, que la case nomme (la demande, et la réponse "
                  "de l'humain consignée au journal une fois donnée ; le fichier du relevé ; ce qu'en montre "
                  "`socle show` ou `socle roadmap`). Juge alors que ce produit existe et dit ce que la case "
                  "promet ; l'absence d'un test n'y est pas un constat.",
            "en": "A box of a task is checked by a test, except one whose deliverable is a request posed, a report "
                  "written (the account of a measurement or a trial) or a memory entry rewritten: it is checked by "
                  "what it produces, which the box names (the request, and the human's answer recorded in the "
                  "journal once given; the report's file; what `socle show` or `socle roadmap` shows of it). Then "
                  "judge that this product exists and says what the box promises; the lack of a test is not a "
                  "finding there.",
        }
        for lg, phrase in attendus.items():
            for court in (False, True):
                with messages.dans(lg):
                    texte = revue.dossier(self.projet, court=court)
                self.assertIn(phrase, texte, (lg, court))
                # Dans la consigne, avant le diff.
                self.assertLess(texte.index(phrase), texte.index("+    return x * 2"), (lg, court))
        from socle.templates import DOSSIER
        format_ = " ".join((DOSSIER / "../FORMAT.md").read_text(encoding="utf-8").split())
        self.assertIn("une case dont le livrable est une demande posée, un relevé écrit (le compte rendu d'une "
                      "mesure ou d'un essai) ou une entrée de la mémoire récrite se vérifie aussi par ce qu'elle "
                      "produit, que la case nomme : la demande, et la réponse de l'humain consignée au journal ; le "
                      "fichier du relevé ; ce qu'en montre `socle show` ou `socle roadmap` ; tout autre livrable "
                      "garde son test", format_)

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
        self.assertIn("## Les entrées du backlog que sert le lot : leurs critères sont ta barre", texte)
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
        self.assertIn("## Les entrées que le lot ouvre : ce qu'il renvoie au backlog\n\n"
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
            self.assertIn("## Les entrées du backlog que sert le lot : leurs critères sont ta barre\n\n# B-0001 — Doubler",
                          texte, etape)
            self.assertIn("- [x] double est écrit", texte, etape)
            self.assertIn("## Les décisions et les demandes qu'elles citent\n\n# ADR-0001", texte, etape)

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
        self.assertIn("## Les décisions et les demandes qu'elles citent\n\n# ADR-0001", texte)
        self.assertEqual(revue.decisions_ecrites(self.projet, "HEAD"), [])

    def test_le_dossier_donne_la_demande_que_cite_une_decision_que_le_lot_ecrit(self):
        # B-0273 : la spécification validée que citait ADR-0084, écrite par le lot, manquait au relecteur.
        (self.racine / "memory/requests").mkdir()
        (self.racine / "memory/requests/D-0002-valider-la-specification.md").write_text(
            "<!-- socle: couche=demandes zone=publique -->\n# D-0002 — Valider la spécification du doublement\n\n"
            "> date : 2026-11-12\n\n## Question posée\n\nUne chaîne se double-t-elle ?\n\n"
            "## Proposition\n\nNon : une chaîne n'est jamais doublée, un nombre l'est.\n", encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "la spécification posée")
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        self.lot()
        (self.racine / "memory/decisions/ADR-0002-le-modele-de-menace.md").write_text(
            "<!-- socle: couche=decisions zone=publique -->\n# ADR-0002 — Appliquer D-0002\n\n"
            "> statut : acceptée · date : 2026-11-13\n\n## Décision\n\nCe que D-0002 valide, selon ADR-0001.\n",
            encoding="utf-8")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "la décision du lot")
        texte = revue.dossier(self.projet)
        cite = texte[texte.index("## Les décisions et les demandes qu'elles citent"):]
        # La demande en entier, une fois ; ADR-0001, que citent le sujet et la décision, une fois aussi.
        self.assertIn("# D-0002 — Valider la spécification du doublement", cite)
        self.assertIn("Non : une chaîne n'est jamais doublée, un nombre l'est.", cite)
        self.assertEqual(texte.count("# D-0002 — Valider la spécification du doublement"), 1)
        self.assertEqual(texte.count("# ADR-0001 — Doubler les entrées"), 1)
        # La décision que le lot écrit n'est pas redonnée parmi celles qu'elles citent.
        self.assertNotIn("# ADR-0002", cite)

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


class TestDossierCourt(_Lot):
    """B-0288 : le relecteur d'un petit lot reçoit un dossier court, le diff
    et les critères de ses tâches, et ne juge que le diff et les fichiers
    touchés ; un lot qui touche un garde-fou garde la revue complète."""

    def test_le_dossier_court_donne_la_consigne_le_diff_et_les_criteres(self):
        self.lot()
        texte = revue.dossier(self.projet, court=True)
        self.assertIn("Juge le diff et les fichiers qu'il touche", texte)
        self.assertIn("n'explore pas au-delà", texte)
        self.assertIn("+    return x * 2", texte)
        self.assertIn("## Les critères des tâches du lot : ta barre", texte)
        self.assertIn("### B-0001 — Doubler", texte)
        self.assertIn("- [x] double est écrit", texte)
        # Les classes des constats restent : le skill lit les trois listes.
        self.assertIn("**Bloquant**", texte)
        # Ni le reste des entrées, ni les décisions qu'elles citent, ni la
        # consigne d'explorer le dépôt.
        for absent in ("Selon ADR-0001.", "`double(x)` rend `2 * x`", "tu peux lire le dépôt",
                       "## Les entrées du backlog que sert le lot"):
            self.assertNotIn(absent, texte)
        self.assertLess(len(texte), len(revue.dossier(self.projet)))

    def test_la_commande_donne_le_dossier_court(self):
        self.lot()
        code, sortie, _ = commande(self.racine, short=True)
        self.assertEqual(code, 0)
        self.assertEqual(sortie, revue.dossier(config.Projet.charger(self.racine), court=True))

    def test_un_lot_qui_touche_un_garde_fou_est_renvoye_au_dossier_complet(self):
        self.lot()
        # Un fichier que les garde-fous déclarent comme l'outillage, par défaut.
        (self.racine / ".github/workflows").mkdir(parents=True)
        (self.racine / ".github/workflows/ci.yml").write_text("on: push\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "la CI")
        self.assertEqual(revue.garde_fous_touches(config.Projet.charger(self.racine), ["calc.py",
                                                                                        ".github/workflows/ci.yml"]),
                         [".github/workflows/ci.yml"])
        with self.assertRaises(revue.CourtRefuse) as refus:
            revue.dossier(config.Projet.charger(self.racine), court=True)
        self.assertIn("le lot touche un garde-fou : .github/workflows/ci.yml", str(refus.exception))
        self.assertIn("`socle review` sans `--short` donne le dossier complet", str(refus.exception))
        code, sortie, erreurs = commande(self.racine, short=True)
        self.assertEqual((code, sortie), (2, ""))
        self.assertIn("le lot touche un garde-fou", erreurs)
        # Le dossier complet, lui, se donne.
        self.assertEqual(commande(self.racine)[0], 0)

    def test_les_chemins_que_la_politique_protege_sont_des_garde_fous(self):
        (self.racine / ".socle").mkdir()
        (self.racine / ".socle/policy.toml").write_text('[protected]\npaths = ["garde/**"]\n')
        projet = config.Projet.charger(self.racine)
        self.assertEqual(revue.garde_fous_touches(projet, ["calc.py", "garde/regle.py", ".socle/policy.toml",
                                                           ".socle/guardrails.toml"]),
                         ["garde/regle.py", ".socle/policy.toml", ".socle/guardrails.toml"])
        (self.racine / "garde").mkdir()
        (self.racine / "garde/regle.py").write_text("x = 1\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "un garde-fou")
        with self.assertRaises(revue.CourtRefuse) as refus:
            revue.dossier(projet, court=True)
        self.assertIn(".socle/policy.toml, garde/regle.py", str(refus.exception))


class TestContenusApprouves(_Lot):
    """B-0286 : une décision prise en séance qui approuve un contenu (un
    format, un exemple) le désigne par son `sujet` ; le relecteur d'un lot
    dont une tâche la cite reçoit ce contenu dans son dossier, et non le
    seul résumé de la tâche."""

    SEANCE = ("<!-- socle: couche=demandes zone=publique -->\n# D-0001 — La vue proposée : la valider ?\n\n"
              "> date : 2026-11-16 · forme : séance · sujet : docs/vue.md\n\n## Question posée\n\n"
              "La vue proposée : la valider ?\n")
    VUE = "# La vue\n\n```text\nL-0001 ▶ 2/3\n```\n\nUne colonne par lot.\n"

    def lot_qui_sert_la_seance(self, vue: str = VUE):
        (self.racine / "docs").mkdir(exist_ok=True)
        (self.racine / "docs/vue.md").write_text(vue)
        (self.racine / "memory/requests").mkdir(exist_ok=True)
        (self.racine / "memory/requests/D-0001-la-vue-proposee-la-valider.md").write_text(self.SEANCE)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "la vue validée en séance")
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        (self.racine / "calc.py").write_text("def double(x):\n    return x * 2\n")
        (self.racine / "memory/backlog/B-0001-doubler.md").write_text(
            SUJET.format(statut="fait").replace("origine : ADR-0001", "origine : D-0001"))
        git(self.racine, "commit", "-qam", "le lot")

    def test_le_dossier_donne_le_texte_que_designe_la_decision_de_seance(self):
        self.lot_qui_sert_la_seance()
        for court in (False, True):
            texte = revue.dossier(self.projet, court=court)
            self.assertIn("## Ce qu'approuvent les décisions de séance qu'elles citent", texte, court)
            self.assertIn("### D-0001 — `docs/vue.md`", texte, court)
            # Le document entier, ses propres blocs compris, dans une clôture
            # plus longue que les siennes.
            self.assertIn("````\n" + self.VUE.rstrip("\n") + "\n````", texte, court)

    def test_le_dossier_donne_la_version_approuvee_que_le_lot_change(self):
        # Relevé par la revue de L-0018 : lu dans l'arbre de travail, le dossier donnait pour barre la version
        # que le lot avait modifiée, non celle que l'humain avait approuvée.
        self.lot_qui_sert_la_seance()
        (self.racine / "docs/vue.md").write_text(self.VUE.replace("Une colonne par lot.", "Changé par le lot."))
        git(self.racine, "commit", "-qam", "le lot change la vue")
        for court in (False, True):
            texte = revue.dossier(self.projet, court=court)
            approuve = texte[texte.index("## Ce qu'approuvent les décisions de séance"):]
            self.assertIn("````\n" + self.VUE.rstrip("\n") + "\n````", approuve, court)
            self.assertIn("(le lot change `docs/vue.md` : voici sa version d'avant le lot", approuve, court)
            self.assertNotIn("Changé par le lot.", approuve, court)

    def test_au_dela_de_la_borne_le_chemin_seul(self):
        self.lot_qui_sert_la_seance("x" * (revue.PLAFOND_SUJET + 1))
        texte = revue.dossier(self.projet)
        self.assertIn(f"(`docs/vue.md` : {revue.PLAFOND_SUJET + 1} octets, au-delà de la borne du dossier "
                      f"({revue.PLAFOND_SUJET}) : le lire dans le dépôt)", texte)
        self.assertNotIn("x" * 100, texte)

    def test_une_decision_sans_sujet_ou_hors_seance_ne_donne_rien(self):
        from socle import memory as memoire

        self.lot_qui_sert_la_seance()
        decision = (self.racine / "memory/requests/D-0001-la-vue-proposee-la-valider.md")
        decision.write_text(self.SEANCE.replace(" · sujet : docs/vue.md", ""))
        mem = memoire.Memoire.charger(self.racine)
        self.assertEqual(revue.contenus_approuves(self.projet, [mem.entree("D-0001")]), [])
        decision.write_text(self.SEANCE.replace(" · sujet : docs/vue.md", " · sujet : ../hors.md"))
        self.assertEqual(revue.contenus_approuves(self.projet, [memoire.Memoire.charger(self.racine).entree("D-0001")]),
                         [])

    def test_un_fichier_prive_ne_se_donne_pas_quelle_que_soit_l_ecriture_de_son_chemin(self):
        # B-0297 : jugé sur le chemin brut du `sujet`, `./memory/private/…` passait pour public.
        from socle import memory as memoire

        self.lot_qui_sert_la_seance()
        (self.racine / "memory/private").mkdir(parents=True, exist_ok=True)
        (self.racine / "memory/private/secret.md").write_text("Le texte privé, approuvé en séance.\n")
        decision = (self.racine / "memory/requests/D-0001-la-vue-proposee-la-valider.md")
        for chemin in ("memory/private/secret.md", "./memory/private/secret.md", "docs/../memory/private/secret.md"):
            decision.write_text(self.SEANCE.replace("sujet : docs/vue.md", f"sujet : {chemin}"))
            mem = memoire.Memoire.charger(self.racine)
            self.assertEqual(revue.contenus_approuves(self.projet, [mem.entree("D-0001")]), [], chemin)
            self.assertNotIn("Le texte privé", revue.dossier(self.projet), chemin)


class TestLeGuideNeRenvoiePasALAtelier(unittest.TestCase):
    """B-0268 : le guide citait `D-0098`, une demande de la mémoire de ce
    dépôt, qu'un projet équipé ne connaît pas (ADR-0033). Comme les notes de
    version, il ne cite ni identifiant de la mémoire, ni l'atelier."""

    def test_le_guide_ne_cite_ni_identifiant_de_la_memoire_ni_l_atelier(self):
        from socle import memory as memoire

        paquet = Path(revue.__file__).resolve().parent
        for nom in ("HELP.md", "HELP.en.md"):
            with self.subTest(guide=nom):
                texte = (paquet / nom).read_text(encoding="utf-8")
                self.assertEqual([m.group(0) for m in memoire.ID_RE.finditer(texte)], [])
                for mot in ("docs/fabrication", "chess", "Théo", "atelier", "workshop"):
                    self.assertNotIn(mot, texte)


class TestLesFormesDuShellHorsDuProduit(unittest.TestCase):
    """T-0060 (B-0276, D-0128, ADR-0099) : un projet équipé ne reçoit plus
    de procédure sur les formes du shell que le hook ne juge pas, ni leur
    liste ; le guide garde le modèle de menace du hook, comme description
    de l'outil."""

    PROCEDURE = {
        "fr": ("forme du shell qu'un agent n'écrit pas", "formes connues", "Un trou ouvre",
               "n'ouvre pas d'entrée au backlog", "signaler au dépôt du socle"),
        "en": ("shell form an agent does not write", "known forms", "A hole opens", "opens no backlog entry",
               "reporting it to the socle's repository"),
    }
    MODELE = {
        "fr": ("**Ce que juge le hook de l'agent.** Le hook de l'agent arrête les erreurs d'un agent coopératif "
               "avant qu'elles agissent. Il juge les formes du shell qu'un agent écrit dans son travail, pour tout "
               "effet ; pour ce que rien ne rattrape ensuite (supprimer le projet ou un dossier qui le contient, "
               "une action externe irréversible, une fuite de la mémoire privée, la part de la mémoire qui ne se "
               "publie pas), il refuse aussi ce qu'il ne sait pas lire. Un agent coopératif ne cherche pas à "
               "contourner ses garde-fous. Le hook ne modélise pas tout bash : une écriture d'un fichier protégé "
               "sous une forme qu'on n'écrit que pour contourner (un `eval`, `IFS`, un chemin construit au vol "
               "dans un autre langage) est hors de son modèle, comme des formes qui lui échappent",
               "la garantie est alors le contrôle des fichiers protégés, à la fin du tour, au commit et dans la "
               "CI. **Faire ce que l'agent ne peut pas faire.**"),
        "en": ("**What the agent's hook judges.** The agent's hook stops the mistakes of a cooperative agent "
               "before they take effect. It judges the shell forms an agent writes in its work, for every effect; "
               "for what nothing catches afterwards (deleting the project or a directory that contains it, an "
               "irreversible external action, a leak of the private memory, the part of the memory that is not "
               "published), it also refuses what it cannot read. A cooperative agent does not try to get around "
               "its guardrails. The hook does not model all of bash: a write to a protected file in a form one "
               "writes only to get around it (an `eval`, `IFS`, a path built on the fly in another language) is "
               "outside its model, as are forms that escape it",
               "the guarantee is then the protected-files check, at the end of the turn, at commit and in CI. "
               "**Doing what the agent cannot do.**"),
    }
    # Le tri des autres constats reste dans la consigne du relecteur.
    CLASSES = {
        "fr": ("**Écarté** : un constat exotique (un geste rare, une forme qu'on n'écrit que pour contourner, un "
               "cas jamais reproduit) dont l'effet est rattrapé",
               "Rends trois listes numérotées, « Bloquants », « Pour le backlog » puis « Écartés »"),
        "en": ("**Dismissed**: an exotic finding (a rare gesture, a form one only writes to get around something, "
               "a case never reproduced) whose effect is caught",
               "Return three numbered lists, “Blocking”, “For the backlog” then “Dismissed”"),
    }

    def poses(self, lg: str) -> dict[str, str]:
        """Le skill, les instructions et le guide posés dans un projet neuf
        de cette langue, et la consigne du relecteur dans cette langue."""
        import contextlib
        import io

        from socle import installer as installeur

        racine = Path(tempfile.mkdtemp(prefix="socle-formes-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        git(racine, "init", "-q", "-b", "main")
        (racine / "app.py").write_text("print('ok')\n", encoding="utf-8")
        moteur = Path(revue.__file__).resolve().parent.parent
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(racine, "python", "@essai", source=moteur, langue_memoire=lg)
        guide = "HELP.md" if lg == "fr" else "HELP.en.md"
        textes = {"skill": racine / installeur.SKILLS / "socle-review" / "SKILL.md",
                  "instructions": racine / "AGENTS.md",
                  "guide": racine / config.Projet.charger(racine).chemins.moteur / "socle" / guide}
        res = {nom: " ".join(p.read_text(encoding="utf-8").split()) for nom, p in textes.items()}
        with messages.dans(lg):
            res["consigne"] = " ".join(messages.trad(revue.CONSIGNE_CLASSES).split())
        return res

    def test_poses_dans_un_projet_ils_ne_disent_ni_la_procedure_ni_la_liste(self):
        for lg in ("fr", "en"):
            textes = self.poses(lg)
            for nom, texte in textes.items():
                for mot in self.PROCEDURE[lg]:
                    self.assertNotIn(mot, texte, (lg, nom))
            # La liste citait, pour chaque forme, la note de version qui l'inscrivait.
            self.assertNotRegex(textes["guide"], r"\(\d{4}-\d{2}-\d{2}-[a-z]\)\.", lg)
            for phrase in self.CLASSES[lg]:
                self.assertIn(phrase, textes["consigne"], lg)

    def test_le_guide_garde_le_modele_de_menace_du_hook(self):
        paquet = Path(revue.__file__).resolve().parent
        for lg, nom in (("fr", "HELP.md"), ("en", "HELP.en.md")):
            texte = " ".join((paquet / nom).read_text(encoding="utf-8").split())
            for phrase in self.MODELE[lg]:
                self.assertIn(phrase, texte, lg)


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

    def test_une_branche_qui_a_fusionne_la_branche_par_defaut_ne_montre_que_son_lot(self):
        """B-0241 : la branche, poussée, fusionne la branche par défaut en
        cours de lot ; le dossier ne montre ni le code ni le sujet clos
        que la fusion a apportés. La branche poussée porte déjà un lot
        d'avant, que la branche par défaut n'a pas reçu."""
        (self.racine / "avant.py").write_text("LOT_D_AVANT = 1\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "le lot d'avant")
        git(self.racine, "push", "-q", "-u", "origin", "travail")
        pousse = git(self.racine, "rev-parse", "HEAD").strip()
        self.avancer_main()
        self.lot()
        git(self.racine, "merge", "-q", "--no-edit", "origin/main")
        (self.racine / "calc.py").write_text("def double(x):\n    return x * 2  # après la fusion\n")
        git(self.racine, "commit", "-qam", "la suite du lot")
        texte = revue.dossier(self.projet)
        self.assertNotIn("ECRIT_SUR_MAIN", texte)
        self.assertNotIn("# B-0005 — Un sujet de main", texte)
        self.assertIn("+    return x * 2  # après la fusion", texte)
        self.assertIn("- [x] double est écrit", texte)
        self.assertIn(f"(la branche a fusionné origin/main depuis {pousse[:7]} : le lot se mesure sans ce que "
                      "cette fusion a apporté", texte)
        self.assertIn("## Le diff du lot (1 fichier(s), depuis origin/travail)", texte)
        origine, note = revue.sans_la_fusion(self.projet, pousse)
        self.assertNotEqual(origine, pousse)
        self.assertEqual([e.id for e in revue.sujets_du_lot(self.projet, origine)[0]], ["B-0001"])
        # Sans fusion depuis le début du lot, rien ne change.
        self.assertEqual(revue.sans_la_fusion(self.projet, git(self.racine, "rev-parse", "HEAD").strip())[1], None)

    def test_une_seconde_revue_apres_une_fusion_de_la_branche_par_defaut_ne_montre_que_la_correction(self):
        """La revue de L-0007 : entre deux passes, la branche fusionne la
        branche par défaut ; le dossier de la seconde ne montre ni son
        code ni les messages de ses commits."""
        self.lot()
        relu = git(self.racine, "rev-parse", "HEAD").strip()
        self.avancer_main()
        git(self.racine, "merge", "-q", "--no-edit", "origin/main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        git(self.racine, "commit", "-qam", "la correction")
        texte = revue.dossier(self.projet, depuis=relu)
        self.assertNotIn("ECRIT_SUR_MAIN", texte)
        self.assertNotIn("main avance", texte)
        self.assertIn("la correction", texte)
        self.assertIn("+    return 2 * x", texte)
        self.assertIn(f"## Le diff de la correction (1 fichier(s), depuis {relu})", texte)
        self.assertEqual(revue.messages_depuis(self.racine, relu)[-1], "la correction")

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
