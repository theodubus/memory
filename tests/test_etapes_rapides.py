"""L6 : une vérification réussie se mémorise. La vérification que l'agent
lance, la fin de tour et le hook avant push ne refont pas les étapes
rapides sur un arbre où elles ont déjà toutes passé ; mesuré à la copie du
projet d'échecs, une fin de tour et un push recompilaient le même arbre."""

import contextlib
import io
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from socle import config, installer as installeur, utils as outils, verification
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"


class TestEtapesRapides(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-etapes-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        (self.racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", "--no-verify"],
                       cwd=self.racine, check=True)
        self.compte = Path(tempfile.mkdtemp(prefix="socle-compte-")) / "n"
        self.addCleanup(shutil.rmtree, self.compte.parent, ignore_errors=True)
        self.code = 0

    def lancer(self, refaire=False) -> bool:
        projet = config.Projet.charger(self.racine)
        projet.adaptateur["capabilities"] = {
            "tests": {"command": f"echo . >> {self.compte}; exit {self.code}", "fast": True}}
        return verification.etapes_rapides(projet, Rapport(), refaire=refaire)

    def fois(self) -> int:
        return len(self.compte.read_text().split()) if self.compte.is_file() else 0

    def test_un_arbre_deja_verifie_ne_se_reverifie_pas(self):
        self.assertTrue(self.lancer())
        self.assertFalse(self.lancer())
        self.assertEqual(self.fois(), 1)
        self.assertTrue(self.lancer(refaire=True))
        self.assertEqual(self.fois(), 2)

    def test_un_arbre_change_se_reverifie(self):
        self.lancer()
        avant = outils.empreinte_arbre(self.racine)
        (self.racine / "calc.py").write_text("x = 2\n")
        self.assertNotEqual(outils.empreinte_arbre(self.racine), avant)
        self.assertTrue(self.lancer())
        (self.racine / "neuf.py").write_text("y = 1\n")
        self.assertTrue(self.lancer())
        self.assertEqual(self.fois(), 3)

    def test_les_etapes_rapides_le_disent_a_leurs_commandes(self):
        # D-0019 : un test trop long pour une fin de tour se met de côté
        # quand la variable est posée ; toutes les étapes, en CI, la retirent.
        projet = config.Projet.charger(self.racine)
        projet.adaptateur["capabilities"] = {"tests": {
            "command": f"echo \"${{{verification.RAPIDE}:-absente}}\" >> {self.compte}", "fast": True}}
        verification.executer_etapes(projet, True, Rapport())
        with unittest.mock.patch.dict("os.environ", {verification.RAPIDE: "1"}):
            verification.executer_etapes(projet, False, Rapport())
        self.assertEqual(self.compte.read_text().split(), ["1", "absente"])

    def test_un_echec_ne_se_memorise_pas(self):
        self.code = 1
        self.lancer()
        self.assertTrue(self.lancer())
        self.assertEqual(self.fois(), 2)


class TestAutotestUneFois(unittest.TestCase):
    """L6 : `socle ci` lançait l'auto-test deux fois, dans la suite de tests
    de ce dépôt puis lui-même."""

    def test_la_suite_sait_que_l_autotest_suit(self):
        import argparse
        import os
        from unittest import mock

        from socle import selftest as autotest, cli, context as contexte

        vus = []
        with mock.patch.object(cli, "_projet", return_value=mock.Mock()), \
                mock.patch.object(cli, "_base", return_value=None), \
                mock.patch.object(verification, "executer_etapes",
                                  lambda *a, **k: vus.append(os.environ.get(autotest.ENSUITE))), \
                mock.patch.object(contexte, "executer", return_value=Rapport()), \
                mock.patch.object(contexte, "Contexte"), \
                mock.patch.object(autotest, "executer", return_value=Rapport()), \
                contextlib.redirect_stdout(io.StringIO()):
            cli.cmd_ci(argparse.Namespace(base=None, no_selftest=False))
            cli.cmd_ci(argparse.Namespace(base=None, no_selftest=True))
        self.assertEqual(vus, ["1", None])
        self.assertIsNone(os.environ.get(autotest.ENSUITE))

    def test_verify_rapide_passe_par_la_memoire_et_refaire_la_contourne(self):
        import argparse
        from unittest import mock

        from socle import cli, context as contexte

        appels = []
        with mock.patch.object(cli, "_projet", return_value=mock.Mock()), \
                mock.patch.object(cli, "_base", return_value=None), \
                mock.patch.object(verification, "etapes_rapides",
                                  lambda projet, rapport, flux=None, refaire=False: appels.append(("rapides", refaire))), \
                mock.patch.object(verification, "executer_etapes", lambda *a, **k: appels.append(("toutes", None))), \
                mock.patch.object(contexte, "executer", return_value=Rapport()), \
                mock.patch.object(contexte, "Contexte"), \
                contextlib.redirect_stdout(io.StringIO()):
            cli.cmd_verify(argparse.Namespace(base=None, fast=True, refaire=False))
            cli.cmd_verify(argparse.Namespace(base=None, fast=True, refaire=True))
            cli.cmd_verify(argparse.Namespace(base=None, fast=False, refaire=False))
        self.assertEqual(appels, [("rapides", False), ("rapides", True), ("toutes", None)])


class TestSansAucunTest(unittest.TestCase):
    """B-0026 : un projet qui commence n'a pas encore de test, et unittest
    le dit par un échec ; l'adaptateur le reconnaît, et `verify` avertit au
    lieu d'échouer."""

    def test_un_projet_sans_test_avertit(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-sans-test-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True)
        (racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(racine, "python", "@essai", source=MOTEUR)
        projet = config.Projet.charger(racine)
        for dossier in (None, "tests"):  # sans dossier, puis un dossier vide
            if dossier:
                (racine / dossier).mkdir()
                (racine / dossier / "__init__.py").write_text("")
            rapport = Rapport()
            verification.executer_etapes(projet, True, rapport)
            self.assertEqual(rapport.erreurs("verify.tests"), [], dossier)
            self.assertIn("aucun test trouvé", rapport.texte())
        # Un vrai échec reste un échec.
        (racine / "tests/test_x.py").write_text("import unittest\n\nclass T(unittest.TestCase):\n"
                                                "    def test_x(self):\n        self.fail('non')\n")
        rapport = Rapport()
        verification.executer_etapes(projet, True, rapport)
        self.assertTrue(rapport.erreurs("verify.tests"))

