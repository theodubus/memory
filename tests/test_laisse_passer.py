"""Des contrôles des tests qui laissaient passer, relevé de la passe de
recul, section D : un « assert » en commentaire, en docstring ou dans le
code de production faisait affirmer un test ; un groupe entier de tests se
désactivait sans raison ; un nom se cherchait comme sous-chaîne, et un
commentaire suffisait à « tester » une fonction."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import (config, context as contexte, checks_tests as controles_tests, installer as installeur,
                   tests_reader as tests_lecture)
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
CALC = "def double(x):\n    return 2 * x\n"
TEST = "import unittest\n\nfrom calc import double\n\n\nclass T(unittest.TestCase):\n{corps}"
AGENT = "\n\nCo-Authored-By: Claude <noreply@anthropic.com>\nSocle-Agent: claude-code"


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class Projet(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-laisse-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text(CALC)
        (self.racine / "tests").mkdir()
        (self.racine / "tests/test_calc.py").write_text(
            TEST.format(corps="    def test_double(self):\n        self.assertEqual(double(2), 4)\n"))
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def ecrire(self, rel, texte):
        (self.racine / rel).write_text(texte)

    def erreurs(self, controle, nom) -> list[str]:
        """À la fin du tour, avec les tests de l'adaptateur maintenu : celui
        que l'installeur a posé dans le projet est figé à sa version."""
        projet = config.Projet.charger(self.racine)
        maintenu = (installeur.ADAPTATEURS / "python.toml").read_text(encoding="utf-8")
        projet.adaptateur["tests"] = __import__("tomllib").loads(maintenu)["tests"]
        r = Rapport()
        controle(contexte.Contexte(projet, etage="agent", base=self.base), r)
        return [c.message for c in r.erreurs(nom)]


class TestCreux(Projet):
    def creux(self, corps) -> list[str]:
        self.ecrire("tests/test_calc.py", TEST.format(corps=corps))
        return self.erreurs(controles_tests.creux, "tests.creux")

    def test_un_assert_en_commentaire_ou_en_docstring_n_affirme_rien(self):
        for corps in ('    def test_double(self):\n        # self.assertEqual(double(2), 4)\n        double(2)\n',
                      '    def test_double(self):\n        """On assert que double(2) vaut 4."""\n        double(2)\n',
                      '    def test_double(self):\n        double(2)  # assert 4\n'):
            with self.subTest(corps=corps):
                self.assertTrue(any("sans assertion" in e for e in self.creux(corps)))
        self.assertEqual(self.creux('    def test_double(self):\n        self.assertEqual(double(2), 4)  # # !\n'), [])

    def test_un_assert_du_code_de_production_n_affirme_rien_pour_le_test(self):
        self.ecrire("calc.py", "def double(x):\n    assert x is not None\n    return 2 * x\n")
        self.assertTrue(any("sans assertion" in e for e in self.creux("    def test_double(self):\n        double(2)\n")))
        # Une aide écrite dans les tests, elle, affirme pour celui qui l'appelle.
        self.ecrire("tests/aides.py", "def verifier(x):\n    assert x == 4\n")
        self.assertEqual(self.creux("    def test_double(self):\n        verifier(double(2))\n"), [])

    def test_un_skip_cite_dans_une_chaine_ne_desactive_pas(self):
        # L6 : un test qui parle d'un `skip` dans une chaîne passait pour désactivé.
        corps = "    def test_double(self):\n        self.assertNotIn(\"@unittest.skip\", texte(double(2)))\n"
        self.assertEqual(self.creux(corps), [])

    def test_un_groupe_desactive_sans_raison(self):
        corps = "    def test_double(self):\n        self.assertEqual(double(2), 4)\n"
        self.ecrire("tests/test_calc.py", TEST.format(corps=corps).replace("class T", "@unittest.skip\nclass T"))
        erreurs = self.erreurs(controles_tests.creux, "tests.creux")
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("groupe de tests désactivé", erreurs[0])
        self.ecrire("tests/test_calc.py", TEST.format(corps=corps).replace(
            "class T", '@unittest.skip("le service de calcul est en panne")\nclass T'))
        self.assertEqual(self.erreurs(controles_tests.creux, "tests.creux"), [])


class TestNoms(Projet):
    def test_un_commentaire_ne_teste_pas_une_fonction(self):
        self.ecrire("calc.py", CALC + "\n\ndef triple(x):\n    return 3 * x\n")
        self.ecrire("tests/test_calc.py", TEST.format(
            corps="    def test_double(self):\n        # triple viendra plus tard\n        self.assertEqual(double(2), 4)\n"))
        erreurs = self.erreurs(controles_tests.code_teste, "tests.code-teste")
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("`triple`", erreurs[0])

    def test_une_validation_ne_couvre_que_le_test_qu_elle_nomme(self):
        self.assertTrue(controles_tests._nomme("valider `test_double`.", "test_double"))
        self.assertFalse(controles_tests._nomme("valider `test_double_negatif`.", "test_double"))


class TestSansCommentaires(unittest.TestCase):
    def test_python_et_rust(self):
        import tomllib

        cfg = {n: tomllib.loads((installeur.ADAPTATEURS / f"{n}.toml").read_text())["tests"] for n in ("python", "rust")}
        texte = 'x = "# pas un commentaire"  # assert\n"""\nassert dans la docstring\n"""\n# assert\ny = 1'
        self.assertEqual(tests_lecture.sans_commentaires(texte, cfg["python"]), 'x = "# pas un commentaire"  \n\ny = 1')
        texte = 'let a = "/* garde */"; /* assert!(x)\n */ b(); // assert!(y)\n// assert!(z)\nc();'
        self.assertEqual(tests_lecture.sans_commentaires(texte, cfg["rust"]), 'let a = "/* garde */";  b(); \nc();')


if __name__ == "__main__":
    unittest.main()
