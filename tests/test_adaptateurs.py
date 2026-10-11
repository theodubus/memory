"""Les adaptateurs maintenus : chacun se lit, déclare chaque capacité, et
reconnaît les tests de son langage."""

import re
import tomllib
import unittest
from pathlib import Path

from socle import installeur, mutation, tests_lecture
from socle.controles_tests import CAPACITES

EXEMPLE = Path(__file__).parent / "donnees/exemple-pytest.py.txt"


def adaptateurs() -> dict[str, dict]:
    return {p.stem: tomllib.loads(p.read_text(encoding="utf-8")) for p in installeur.ADAPTATEURS.glob("*.toml")}


class TestAdaptateursMaintenus(unittest.TestCase):
    def test_les_trois_adaptateurs(self):
        self.assertEqual(sorted(adaptateurs()), ["python", "python-pytest", "rust"])

    def test_chaque_capacite_est_declaree(self):
        for nom, a in adaptateurs().items():
            for cap in CAPACITES:
                c = a["capabilities"].get(cap, {})
                self.assertTrue("command" in c or ("absent" in c and "replacement" in c), f"{nom} : {cap}")

    def test_une_mutation_declaree_a_son_lecteur(self):
        for nom, a in adaptateurs().items():
            c = a["capabilities"]["mutation"]
            if "command" in c:
                self.assertIn(c["parser"], mutation.LECTEURS, nom)
                self.assertTrue(c["modules"], nom)

    def test_section_code(self):
        for nom, a in adaptateurs().items():
            self.assertTrue(a["code"]["paths"], nom)
            re.compile(a["code"]["private"])

    def test_pytest_reconnait_ses_tests_et_ses_assertions(self):
        cfg = adaptateurs()["python-pytest"]["tests"]
        fonctions = tests_lecture.extraire(EXEMPLE.read_text(), "tests/test_x.py", cfg)
        self.assertEqual([(f.nom, f.est_test) for f in fonctions],
                         [("test_double", True), ("test_refuse", True), ("aide", False)])
        assertion = re.compile(cfg["assertion"])
        self.assertTrue(all(tests_lecture.affirme(f, assertion, set()) for f in fonctions if f.est_test))
        self.assertRegex("@pytest.mark.xfail", cfg["ignore"])


if __name__ == "__main__":
    unittest.main()
