"""Le point 2 de la politique, option B (J-2026-10-11-J) : une valeur
attendue ne change que sous une demande validée par l'humain, ou sous une
spécification que l'humain a écrite. Une ADR que l'agent écrit dans le même
travail ne suffit plus : c'est ce qu'un agent sur trois a fait au banc (s9)."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from socle import config, context as contexte, checks_tests as controles_tests, installer as installeur
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
TEST = "import unittest\n\nfrom calc import double\n\n\nclass T(unittest.TestCase):\n" \
       "    def test_double(self):\n        self.assertEqual(double(2), {attendu})\n"
ADR = ("<!-- socle: couche=decisions zone=publique -->\n# ADR-0001 — Le facteur passe à 3\n\n"
       "> statut : acceptée · date : 2026-10-11\n\n## Décision\n\n`test_double` attend désormais 6.\n")
AGENT = "\n\nCo-Authored-By: Claude <noreply@anthropic.com>\nSocle-Agent: claude-code"


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestValeurAttendue(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-attendus-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        (self.racine / "tests").mkdir()
        (self.racine / "tests/test_calc.py").write_text(TEST.format(attendu=4))
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def ecrire(self, rel, texte):
        p = self.racine / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte)

    def commit(self, message):
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", message, "--no-verify")

    def erreurs(self, etage="ci") -> tuple[list[str], list[str]]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage=etage, base=self.base,
                                tete=None if etage == "agent" else "HEAD")
        r = Rapport()
        controles_tests.attendus(ctx, r)
        return [c.message for c in r.erreurs("tests.attendus")], [c.message for c in r.constats if c.gravite == "avertissement"]

    def test_une_adr_de_l_agent_ne_justifie_pas_le_changement(self):
        self.ecrire("memory/decisions/ADR-0001-facteur.md", ADR)
        self.ecrire("tests/test_calc.py", TEST.format(attendu=6))
        self.commit("Le facteur passe à 3" + AGENT)
        erreurs, _ = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("écrite par l'agent", erreurs[0])

    def test_une_adr_en_cours_d_ecriture_ne_justifie_pas_non_plus(self):
        self.ecrire("memory/decisions/ADR-0001-facteur.md", ADR)
        self.ecrire("tests/test_calc.py", TEST.format(attendu=6))
        erreurs, _ = self.erreurs("agent")
        self.assertEqual(len(erreurs), 1, erreurs)

    def test_une_specification_commitee_par_l_humain_justifie_le_changement(self):
        self.ecrire("memory/decisions/ADR-0001-facteur.md", ADR)
        self.commit("Le facteur passe à 3, décidé par Théo")
        self.ecrire("tests/test_calc.py", TEST.format(attendu=6))
        self.commit("Le test suit le facteur" + AGENT)
        erreurs, avertissements = self.erreurs()
        self.assertEqual(erreurs, [])
        self.assertTrue(any("spécification changée par l'humain" in a for a in avertissements), avertissements)

    # Le relevé de la passe de recul, section E (vécu en CI le 2026-10-12) :
    # deux tests homonymes dans deux classes, ou une assertion reformatée à
    # valeur égale, se lisaient comme une valeur attendue changée.
    HOMONYMES = ("import unittest\n\nfrom calc import double\n\n\nclass A(unittest.TestCase):\n"
                 "    def test_double(self):\n        self.assertEqual(double(2), 4)\n\n\n"
                 "class B(unittest.TestCase):\n    def test_double(self):\n        self.assertEqual(double(3), 6)\n")

    def test_deux_homonymes_s_apparient_dans_l_ordre(self):
        self.ecrire("tests/test_calc.py", self.HOMONYMES)
        self.commit("Deux classes")
        base, self.base = self.base, git(self.racine, "rev-parse", "HEAD").strip()
        self.ecrire("tests/test_calc.py", self.HOMONYMES + "\n    def test_zero(self):\n"
                    "        self.assertEqual(double(0), 0)\n")
        self.commit("Un test de plus" + AGENT)
        self.assertEqual(self.erreurs()[0], [])
        self.ecrire("tests/test_calc.py", self.HOMONYMES.replace("double(3), 6", "double(3), 7"))
        self.commit("Une valeur changée" + AGENT)
        erreurs, _ = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("self.assertEqual(double(3), 6)", erreurs[0])
        self.base = base

    def test_une_assertion_reformatee_garde_sa_valeur(self):
        self.ecrire("tests/test_calc.py", TEST.format(attendu=4).replace(
            "self.assertEqual(double(2), 4)", "self.assertEqual(\n            double(2),\n            4,\n        )"))
        self.commit("Reformaté" + AGENT)
        self.assertEqual(self.erreurs()[0], [])

    def test_une_valeur_sur_une_ligne_de_continuation_compte(self):
        multi = TEST.format(attendu=4).replace("self.assertEqual(double(2), 4)",
                                               "self.assertEqual(\n            double(2),\n            {v},\n        )")
        self.ecrire("tests/test_calc.py", multi.format(v=4))
        self.commit("Sur trois lignes")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        self.ecrire("tests/test_calc.py", multi.format(v=5))
        self.commit("La valeur change" + AGENT)
        erreurs, _ = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)



class TestValeursHorsDesAssertions(unittest.TestCase):
    """ADR-0024 : une valeur attendue placée hors de la ligne d'assertion
    (une variable, une constante, une aide) changeait sans bruit. Rien ne la
    distingue d'une donnée de test : elle est dite, pas refusée."""

    TEST = ("import unittest\n\nfrom calc import double\n\nATTENDU = {constante}\n\n\n"
            "def verifier(x):\n    assert x == {aide}\n\n\nclass T(unittest.TestCase):\n"
            "    def test_double(self):\n        attendu = {variable}\n        self.assertEqual(double(2), attendu)\n\n"
            "    def test_constante(self):\n        self.assertEqual(double(2), ATTENDU)\n\n"
            "    def test_aide(self):\n        verifier(double(2))\n")
    VALEURS = {"constante": 4, "aide": 4, "variable": 4}

    def setUp(self):
        TestValeurAttendue.setUp(self)
        self.ecrire("tests/test_calc.py", self.TEST.format(**self.VALEURS))
        TestValeurAttendue.commit(self, "Les trois formes")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    ecrire = TestValeurAttendue.ecrire
    erreurs = TestValeurAttendue.erreurs

    def changer(self, **valeurs) -> tuple[list[str], list[str]]:
        self.ecrire("tests/test_calc.py", self.TEST.format(**{**self.VALEURS, **valeurs}))
        TestValeurAttendue.commit(self, "Une valeur change" + AGENT)
        return self.erreurs()

    def test_une_variable(self):
        erreurs, avertissements = self.changer(variable=5)
        self.assertEqual(erreurs, [])
        self.assertTrue(any("hors des assertions" in a and "`test_double`" in a for a in avertissements), avertissements)

    def test_une_constante_et_une_aide(self):
        erreurs, avertissements = self.changer(constante=5, aide=5)
        self.assertEqual(erreurs, [])
        texte = " ".join(avertissements)
        self.assertIn("`test_aide`", texte)
        self.assertIn("`test_constante`", texte)
        self.assertNotIn("`test_double`", texte)

    def test_rien_ne_change(self):
        self.ecrire("tests/test_calc.py", self.TEST.format(**self.VALEURS) + "\n    def test_zero(self):\n"
                    "        self.assertEqual(double(0), 0)\n")
        TestValeurAttendue.commit(self, "Un test de plus" + AGENT)
        self.assertEqual(self.erreurs(), ([], []))

    def test_les_litteraux(self):
        import tomllib

        from socle import tests_reader as tests_lecture

        cfg = tomllib.loads((installeur.ADAPTATEURS / "python.toml").read_text())["tests"]
        self.assertEqual(tests_lecture.litteraux('x = 4  # 5\ny = "a b"\nf(x1, 2.5, True)\n"""9"""\n', cfg),
                         Counter({"4": 1, '"a b"': 1, "2.5": 1, "True": 1}))


class TestEnAttenteDeLHumain(TestValeurAttendue):
    """B-0033 : une valeur attendue changée, que nomme une demande en attente
    poussée telle quelle, ne bloque pas la fin du tour ; le commit et la CI
    attendent toujours la réponse de l'humain."""

    DEMANDE = ("<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Le facteur passe à 3 ?\n\n"
               "> date : 2026-10-11\n\n## Décision demandée\n\nValider que `test_double` attende 6.\n")

    def setUp(self):
        super().setUp()
        origine = self.racine.parent / (self.racine.name + "-origine.git")
        git(self.racine.parent, "init", "-q", "--bare", str(origine))
        self.addCleanup(shutil.rmtree, origine, ignore_errors=True)
        git(self.racine, "remote", "add", "origin", str(origine))
        pol = self.racine / ".socle/policy.toml"
        pol.write_text(pol.read_text().replace("[human]\n", '[human]\nrepo_url = "https://github.com/x/y"\n', 1))
        self.commit("Adresse du dépôt")
        self.ecrire("memory/requests/D-0001-facteur.md", self.DEMANDE)
        self.commit("La demande")

    def pousser(self):
        git(self.racine, "push", "-q", "--no-verify", "-u", "origin", "main")

    def test_une_demande_poussee_laisse_finir_le_tour(self):
        from socle import requests as demandes

        self.pousser()
        d = next(x for x in demandes.toutes(self.racine) if x.id == "D-0001")
        self.assertIsNone(demandes.illisible(config.Projet.charger(self.racine), d))
        self.ecrire("tests/test_calc.py", TEST.format(attendu=6))
        erreurs, avertissements = self.erreurs("agent")
        self.assertEqual(erreurs, [])
        self.assertTrue(any("en attente de D-0001" in a for a in avertissements), avertissements)

    def test_une_demande_non_poussee_ne_suffit_pas(self):
        self.ecrire("tests/test_calc.py", TEST.format(attendu=6))
        erreurs, _ = self.erreurs("agent")
        self.assertEqual(len(erreurs), 1, erreurs)

    def test_la_ci_attend_toujours_la_reponse(self):
        self.pousser()
        self.ecrire("tests/test_calc.py", TEST.format(attendu=6))
        self.commit("Le test suit")
        erreurs, _ = self.erreurs("ci")
        self.assertEqual(len(erreurs), 1, erreurs)

if __name__ == "__main__":
    unittest.main()
