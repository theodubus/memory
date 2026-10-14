"""`tests.regression` sur un test écrit dans le module qu'il teste, comme
Rust les écrit (B-0051) : refusé à tort à R6, tâche 4, parce que seul un
test d'un fichier de tests se posait sur le commit parent. Le langage est
simulé en Python, pour ne pas dépendre de cargo : le code et ses tests dans
le même fichier, les tests dans une classe qui tient lieu de module."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, context as contexte, checks_tests as controles_tests, installer as installeur
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
CALC = """def double(x):
    return 2 * x


class Tests:
    def test_double(self):
        assert double(2) == 4
"""
# Le correctif : le code, une aide du module de tests et le test qui s'en sert.
CORRIGE = """def double(x):
    return 2 * int(x)


class Tests:
    def entree(self):
        return "3"

    def test_double(self):
        assert double(2) == 4

    def test_double_une_chaine(self):
        assert double(self.entree()) == 6
"""
MODULE = {
    "paths": ["*.py"], "function": r"^\s*def\s+(\w+)\s*\(", "marker_name": "^test", "block": "indent",
    "test_module": r"^class Tests\b",
}
COMMANDE = "python3 -c \"import calc; t = calc.Tests(); [getattr(t, n)() for n in '{names}'.split()]\""


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestTestDuModule(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-regression-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text(CALC)
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def corriger(self, texte):
        (self.racine / "calc.py").write_text(texte)
        git(self.racine, "commit", "-qam", "fix: double accepte une chaîne", "--no-verify")

    def contexte(self, module_command=True):
        projet = config.Projet.charger(self.racine)
        projet.adaptateur["tests"] = MODULE
        if module_command:
            projet.adaptateur["capabilities"]["regression"]["module_command"] = COMMANDE
        return contexte.Contexte(projet, etage="ci", base=self.base, tete="HEAD")

    def erreurs(self, ctx) -> list[str]:
        r = Rapport()
        controles_tests.regression(ctx, r)
        return [c.message for c in r.erreurs("tests.regression")]

    def test_un_test_du_module_prouve_le_correctif(self):
        self.corriger(CORRIGE)
        self.assertEqual(self.erreurs(self.contexte()), [])

    def test_sur_le_parent_seules_les_lignes_de_test_s_appliquent(self):
        self.corriger(CORRIGE)
        fichiers, noms = controles_tests.tests_du_module(self.contexte(), "HEAD~1", "HEAD", ["calc.py"])
        self.assertEqual(noms, ["test_double_une_chaine"])
        self.assertIn("return 2 * x\n", fichiers["calc.py"], "le code du parent reste")
        self.assertIn('return "3"', fichiers["calc.py"], "l'aide du module de tests suit le test")

    def test_un_test_du_module_qui_passe_deja_sur_le_parent_est_refuse(self):
        self.corriger(CORRIGE.replace("double(self.entree()) == 6", "double(3) == 6"))
        erreurs = self.erreurs(self.contexte())
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("passe déjà sur le parent", erreurs[0])

    def test_sans_commande_de_module_le_correctif_reste_sans_test(self):
        self.corriger(CORRIGE)
        erreurs = self.erreurs(self.contexte(module_command=False))
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("sans test de régression", erreurs[0])

    def test_un_correctif_sans_aucun_test_reste_refuse(self):
        self.corriger(CALC.replace("2 * x", "2 * int(x)"))
        erreurs = self.erreurs(self.contexte())
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("ni test changé dans un module de code", erreurs[0])


class TestChargement(unittest.TestCase):
    """Relevé de la passe de recul, D : un test de régression qui échoue sur
    le parent parce qu'il ne s'y charge pas (un import manquant) ne prouve
    rien du défaut ; il faisait foi."""

    def setUp(self):
        TestTestDuModule.setUp(self)
        (self.racine / "tests").mkdir()

    def erreurs(self) -> list[str]:
        import tomllib

        projet = config.Projet.charger(self.racine)
        maintenu = tomllib.loads((installeur.ADAPTATEURS / "python.toml").read_text(encoding="utf-8"))
        projet.adaptateur["capabilities"]["regression"] = maintenu["capabilities"]["regression"]
        r = Rapport()
        controles_tests.regression(contexte.Contexte(projet, etage="ci", base=self.base, tete="HEAD"), r)
        return [c.message for c in r.erreurs("tests.regression")]

    def corriger(self, test):
        (self.racine / "calc.py").write_text(CALC.replace("2 * x", "2 * int(x)") + "\n\ndef triple(x):\n    return 3 * x\n")
        (self.racine / "tests/test_calc.py").write_text(test)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "fix: double accepte une chaîne", "--no-verify")

    def test_un_test_qui_ne_se_charge_pas_sur_le_parent_ne_prouve_rien(self):
        self.corriger("import unittest\n\nfrom calc import double, triple\n\n\nclass T(unittest.TestCase):\n"
                      "    def test_chaine(self):\n        self.assertEqual(double(\"3\"), 6)\n")
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("ne se charge pas sur le parent", erreurs[0])

    def test_un_test_qui_echoue_sur_le_defaut_fait_foi(self):
        self.corriger("import unittest\n\nfrom calc import double\n\n\nclass T(unittest.TestCase):\n"
                      "    def test_chaine(self):\n        self.assertEqual(double(\"3\"), 6)\n")
        self.assertEqual(self.erreurs(), [])


if __name__ == "__main__":
    unittest.main()
