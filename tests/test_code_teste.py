import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, contexte, controles_tests, outils
from socle.rapport import Rapport

ADAPTATEUR = Path(__file__).resolve().parent.parent / "moteur/socle/adaptateurs/python.toml"

CALC = """FACTEUR = 2


def double(x):
    return FACTEUR * x
"""

TEST_CALC = """import unittest

from calc import double


class TestCalc(unittest.TestCase):
    def test_double(self):
        self.assertEqual(double(2), 4)
"""


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestCodeTeste(unittest.TestCase):
    """Un projet Python fabriqué : une base où `double` est testée, puis du
    code ajouté par-dessus."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-code-teste-"))
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / ".socle").mkdir()
        shutil.copy(ADAPTATEUR, self.racine / ".socle/adapter.toml")
        (self.racine / "calc.py").write_text(CALC)
        (self.racine / "tests").mkdir()
        (self.racine / "tests/test_calc.py").write_text(TEST_CALC)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def verifier(self, tete=None) -> list[str]:
        projet = config.Projet.charger(self.racine)
        ctx = contexte.Contexte(projet, etage="ci", base=self.base, tete=tete)
        r = Rapport()
        controles_tests.code_teste(ctx, r)
        return [c.message for c in r.erreurs("tests.code-teste")]

    def ajouter_triple(self):
        with open(self.racine / "calc.py", "a") as f:
            f.write("\n\ndef triple(x):\n    return 3 * x\n\n\ndef _aide(x):\n    return x\n")

    def test_une_fonction_publique_ajoutee_sans_test_est_refusee(self):
        self.ajouter_triple()
        erreurs = self.verifier()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("fonction `triple` ajoutée, qu'aucun test ne nomme", erreurs[0])

    def test_nommee_par_un_test_elle_passe(self):
        self.ajouter_triple()
        with open(self.racine / "tests/test_calc.py", "a") as f:
            f.write("\n    def test_triple(self):\n        from calc import triple\n        self.assertEqual(triple(2), 6)\n")
        self.assertEqual(self.verifier(), [])

    def test_une_fonction_modifiee_est_jugee_aussi(self):
        (self.racine / "calc.py").write_text(CALC + "\n\ndef moitie(x):\n    return x / 2\n")
        git(self.racine, "commit", "-qam", "moitie, dispensée\n\nDispense-test: moitie — couverte par l'essai d'intégration")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        (self.racine / "calc.py").write_text(CALC + "\n\ndef moitie(x):\n    return x // 2\n")
        erreurs = self.verifier()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("fonction `moitie` modifiée", erreurs[0])

    def test_une_fonction_que_le_diff_ne_touche_pas_passe(self):
        (self.racine / "calc.py").write_text(CALC + "\n\ndef moitie(x):\n    return x / 2\n")
        git(self.racine, "commit", "-qam", "moitie\n\nDispense-test: moitie — couverte par l'essai d'intégration")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        (self.racine / "calc.py").write_text("# Le module de calcul.\n" + CALC + "\n\ndef moitie(x):\n    return x / 2\n")
        self.assertEqual(self.verifier(), [])

    def test_une_dispense_motivee_la_laisse_passer(self):
        self.ajouter_triple()
        git(self.racine, "commit", "-qam", "triple\n\nDispense-test: triple — appelée seulement par l'interface")
        self.assertEqual(self.verifier(tete="HEAD"), [])

    def test_une_dispense_sans_raison_est_refusee(self):
        self.ajouter_triple()
        git(self.racine, "commit", "-qam", "triple\n\nDispense-test: triple")
        projet = config.Projet.charger(self.racine)
        ctx = contexte.Contexte(projet, etage="ci", base=self.base, tete="HEAD")
        r = Rapport()
        self.assertEqual(controles_tests.dispenses_tests(ctx, r), set())
        self.assertIn("dispense illisible", r.erreurs()[0].message)

    def test_une_fonction_locale_compte_pour_celle_qui_la_contient(self):
        with open(self.racine / "calc.py", "a") as f:
            f.write("\n\ndef double_tout(xs):\n    def un(x):\n        return double(x)\n    return [un(x) for x in xs]\n")
        erreurs = self.verifier()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("`double_tout`", erreurs[0])

    def test_le_moteur_installe_n_est_pas_du_code_du_projet(self):
        moteur = self.racine / ".socle/engine/socle"
        moteur.mkdir(parents=True)
        (moteur / "outils.py").write_text("def git(*args):\n    return args\n")
        self.assertEqual(self.verifier(), [])

    def test_section_code_de_l_adaptateur_maintenu_a_defaut(self):
        adaptateur = self.racine / ".socle/adapter.toml"
        texte = adaptateur.read_text()
        debut, fin = texte.index("[code]"), texte.index("[tests]")
        adaptateur.write_text(texte[:debut] + texte[fin:])
        chemins, exclus, prive = controles_tests.config_code(config.Projet.charger(self.racine))
        self.assertEqual(chemins, ["**/*.py"])
        self.assertIn("tests/**", exclus)
        self.assertTrue(prive)
        adaptateur.write_text(adaptateur.read_text().replace('language = "python"', 'language = "inconnu"'))
        chemins, exclus, prive = controles_tests.config_code(config.Projet.charger(self.racine))
        self.assertEqual(chemins, ["**/*.py"])
        self.assertIn(".socle/**", exclus)
        self.assertIsNone(prive)

    def test_lignes_changees(self):
        (self.racine / "calc.py").write_text(CALC.replace("FACTEUR * x", "x * FACTEUR"))
        self.assertEqual(outils.lignes_changees(self.racine, self.base, None, "calc.py"), {5})
        (self.racine / "calc.py").write_text(CALC.replace("FACTEUR = 2\n", ""))
        self.assertEqual(outils.lignes_changees(self.racine, self.base, None, "calc.py"), {1})
        (self.racine / "neuf.py").write_text("x = 1\n")
        self.assertIsNone(outils.lignes_changees(self.racine, self.base, None, "neuf.py"))

    def test_rev_commit_et_commits_d_un_arbre(self):
        git(self.racine, "commit", "-q", "--allow-empty", "-m", "vide")
        projet = config.Projet.charger(self.racine)
        arbre = git(self.racine, "write-tree").strip()
        ctx = contexte.Contexte(projet, etage="git", base=self.base, tete=arbre)
        self.assertEqual(ctx.rev_commit, "HEAD")
        self.assertEqual([c["message"].strip() for c in ctx.commits], ["vide"])
        tete = git(self.racine, "rev-parse", "HEAD").strip()
        self.assertEqual(contexte.Contexte(projet, base=self.base, tete=tete).rev_commit, tete)


if __name__ == "__main__":
    unittest.main()
