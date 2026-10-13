import re
import tomllib
import unittest
from pathlib import Path

from socle import tests_lecture

ADAPTATEURS = Path(__file__).resolve().parent.parent / "moteur/socle/adaptateurs"


def cfg(langage):
    return tomllib.loads((ADAPTATEURS / f"{langage}.toml").read_text(encoding="utf-8"))["tests"]


DONNEES = Path(__file__).resolve().parent / "donnees"
# Hors des fichiers de test : sinon le contrôle des tests creux y verrait de
# vrais tests sans assertion.
RUST = (DONNEES / "exemple.rs.txt").read_text(encoding="utf-8")

PYTHON = (DONNEES / "exemple.py.txt").read_text(encoding="utf-8")


def analyser(langage, texte):
    c = cfg(langage)
    fonctions = tests_lecture.extraire(texte, "x", c)
    assertion = re.compile(c["assertion"])
    aides = tests_lecture.aides_qui_affirment(fonctions, assertion)
    return c, fonctions, assertion, aides


class TestRust(unittest.TestCase):
    def setUp(self):
        self.c, self.f, self.assertion, self.aides = analyser("rust", RUST)
        self.par_nom = {f.nom: f for f in self.f}

    def test_tests_reconnus(self):
        self.assertEqual(sorted(f.nom for f in self.f if f.est_test),
                         ["lent", "lent_mais_motive", "perft_un", "rien", "tautologie"])

    def test_assertion_par_aide(self):
        self.assertIn("verifie", self.aides)
        self.assertTrue(tests_lecture.affirme(self.par_nom["perft_un"], self.assertion, self.aides))

    def test_sans_assertion_malgre_l_accolade_dans_la_chaine(self):
        self.assertFalse(tests_lecture.affirme(self.par_nom["rien"], self.assertion, self.aides))

    def test_ignore_sans_et_avec_raison(self):
        ignore, raison = re.compile(self.c["ignore"]), re.compile(self.c["ignore_reason"])
        lent, motive = self.par_nom["lent"], self.par_nom["lent_mais_motive"]
        self.assertTrue(any(ignore.search(a) for a in lent.attributs))
        self.assertFalse(any(raison.search(a) for a in lent.attributs))
        self.assertTrue(any(raison.search(a) for a in motive.attributs))

    def test_tautologie(self):
        motifs = [re.compile(t) for t in self.c["tautology"]]
        corps = self.par_nom["tautologie"].corps
        self.assertTrue(any(m.search(corps) for m in motifs))
        self.assertFalse(any(m.search(self.par_nom["lent"].corps) for m in motifs))

    def test_zones_de_test_du_module(self):
        # Le module de tests entier, ses aides comprises ; un test hors du
        # module, depuis son commentaire et son attribut.
        texte = ("pub fn double(x: i32) -> i32 {\n    2 * x\n}\n\n// hors module\n#[test]\nfn seul() {\n"
                 "    assert_eq!(double(1), 2);\n}\n\n#[cfg(test)]\nmod tests {\n    use super::*;\n\n"
                 "    fn aide() -> i32 { 3 }\n\n    #[test]\n    fn trois() {\n        assert_eq!(double(aide()), 6);\n"
                 "    }\n}\n")
        lignes = texte.splitlines()
        zones = sorted(tests_lecture.zones_de_test(texte, "x", cfg("rust")))
        self.assertEqual([lignes[d:f] for d, f in zones][:2],
                         [lignes[4:9], lignes[10:21]])
        self.assertEqual(lignes[10], "#[cfg(test)]")
        self.assertEqual(lignes[20], "}")


class TestPython(unittest.TestCase):
    def setUp(self):
        self.c, self.f, self.assertion, self.aides = analyser("python", PYTHON)
        self.par_nom = {f.nom: f for f in self.f}

    def test_corps_par_indentation(self):
        self.assertEqual(self.par_nom["test_vide"].corps.strip(), "double(3)  # aucune assertion")

    def test_assertions(self):
        self.assertTrue(tests_lecture.affirme(self.par_nom["test_via_aide"], self.assertion, self.aides))
        self.assertFalse(tests_lecture.affirme(self.par_nom["test_vide"], self.assertion, self.aides))

    def test_enonces_entiers_et_normalises(self):
        lignes = ["x = 1", "self.assertEqual(", "    double(2),", "    4,", ")", "assert y // 2 == 'a b'"]
        enonces = tests_lecture.enonces(lignes, self.assertion, self.c)
        self.assertEqual(enonces, {"self.assertEqual(double(2),4)": ["self.assertEqual("],
                                   "asserty//2=='a b'": ["assert y // 2 == 'a b'"]})

    def test_skip(self):
        ignore, raison = re.compile(self.c["ignore"]), re.compile(self.c["ignore_reason"])
        nu, motive = self.par_nom["test_saute"], self.par_nom["test_saute_motive"]
        self.assertTrue(any(ignore.search(a) for a in nu.attributs))
        self.assertFalse(any(raison.search(a) for a in nu.attributs))
        self.assertTrue(any(raison.search(a) for a in motive.attributs))

    def test_tautologie(self):
        motifs = [re.compile(t) for t in self.c["tautology"]]
        lignes = self.par_nom["test_tauto"].lignes_corps
        self.assertTrue(any(m.search(l) for m in motifs for l in lignes))


if __name__ == "__main__":
    unittest.main()
