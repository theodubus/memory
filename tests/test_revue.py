"""Le dossier de la revue adversariale d'un lot (ADR-0042) : ce que reçoit
le relecteur, qui n'a pas la conversation de l'agent mais peut lire le dépôt."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, review as revue


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


ADR = ("<!-- socle: couche=decisions zone=publique -->\n# ADR-0001 — Doubler les entrées\n\n"
       "> statut : acceptée · date : 2026-11-02\n\n## Décision\n\n`double(x)` rend `2 * x`, entiers compris.\n")
SUJET = ("<!-- socle: couche=backlog zone=publique -->\n# B-0001 — Doubler\n\n"
         "> statut : {statut} · origine : ADR-0001\n\nSelon ADR-0001.\n\n## Fait quand\n\n- [x] double est écrit\n")


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
        self.assertEqual([e.id for e in revue.sujets_fermes(self.projet, "origin/main")], ["B-0001"])
        self.assertIn("- [x] double est écrit", texte)
        self.assertEqual([e.id for e in revue.decisions_citees(self.projet, revue.sujets_fermes(self.projet,
                                                                                               "origin/main"))],
                         ["ADR-0001"])
        self.assertIn("`double(x)` rend `2 * x`, entiers compris.", texte)

    def test_un_sujet_encore_ouvert_n_est_pas_dans_le_dossier(self):
        (self.racine / "calc.py").write_text("def double(x):\n    return x * 2\n")
        git(self.racine, "commit", "-qam", "le code seul")
        self.assertEqual(revue.sujets_fermes(self.projet, "origin/main"), [])
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
    menace de ses sujets, et classe chaque constat, bloquant ou pour le
    backlog."""

    GARDE = ("<!-- socle: couche=backlog zone=publique -->\n# B-0003 — Refuser l'écriture du verrou\n\n"
             "> statut : ouvert · origine : ADR-0001\n\n## Modèle de menace\n\nUn agent distrait, pas hostile : "
             "une redirection vers le verrou est arrêtée, un interpréteur qui l'écrit passe.\n\n"
             "## Fait quand\n\n- [x] la redirection est refusée\n- [ ] l'interpréteur est refusé\n")

    def test_la_consigne_donne_la_barre_et_les_deux_classes(self):
        self.lot()
        texte = revue.dossier(self.projet)
        self.assertIn("Ta barre est celle des sujets du lot, plus bas : leur critère « Fait quand »", texte)
        self.assertIn("**Bloquant** : il contredit un critère coché ou une décision citée", texte)
        self.assertIn("contourne un garde-fou dans son modèle de menace", texte)
        self.assertIn("un garde-fou que le lot pose ou change sans modèle de menace écrit est lui-même un constat "
                      "bloquant", texte)
        self.assertIn("**Pour le backlog** : tout le reste, dont un contournement hors du modèle de menace", texte)
        self.assertIn("Seuls les bloquants se corrigent dans le lot.", texte)
        self.assertIn("Rends deux listes numérotées, « Bloquants » puis « Pour le backlog »", texte)
        # Les trois parties de la consigne précèdent le diff.
        self.assertLess(texte.index("Rends deux listes"), texte.index("## Le diff du lot"))

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
