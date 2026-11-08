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


class TestDossier(unittest.TestCase):
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
