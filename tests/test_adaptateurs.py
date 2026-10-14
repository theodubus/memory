"""Les adaptateurs maintenus : chacun se lit, déclare chaque capacité, et
reconnaît les tests de son langage."""

import re
import tempfile
import tomllib
import unittest
from pathlib import Path

from socle import installer as installeur, mutation, tests_reader as tests_lecture
from socle.checks_tests import CAPACITES, commande_regression

EXEMPLE = Path(__file__).parent / "donnees/exemple-pytest.py.txt"
DONNEES = Path(__file__).parent / "donnees/adaptateurs"


def adaptateurs() -> dict[str, dict]:
    return {p.stem: tomllib.loads(p.read_text(encoding="utf-8")) for p in installeur.ADAPTATEURS.glob("*.toml")}


class TestAdaptateursMaintenus(unittest.TestCase):
    def test_les_adaptateurs_maintenus(self):
        self.assertEqual(sorted(adaptateurs()),
                         ["go", "java", "javascript", "php", "python", "python-pytest", "ruby", "rust"])

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



def _desactive(f: tests_lecture.Fonction, cfg: dict) -> tuple[bool, bool]:
    """(désactivé, avec sa raison), comme `tests.creux` le lit."""
    marques = [*f.attributs, f.entete, *f.lignes_corps]
    ignore = re.compile(cfg["ignore"])
    raison = re.compile(cfg["ignore_reason"])
    return any(ignore.search(m) for m in marques), any(raison.search(m) for m in marques)


class TestLangages(unittest.TestCase):
    """B-0030 : chaque adaptateur nouveau reconnaît, dans un fichier
    d'exemple de son langage, les tests, leurs assertions, un test désactivé
    avec ou sans raison, et les fonctions publiques de son code."""

    CAS = {
        # langage : fichier de tests, [(nom, est_test, affirme, désactivé, raison)], fichier de code, {nom: privée}
        "javascript": ("javascript.test.js.txt",
                       [("double multiplie par deux", True, True, False, False),
                        ("triple, plus tard — raison : la spécification attend", True, True, True, True),
                        ("ne mesure rien", True, False, False, False),
                        ("sans dire pourquoi", True, True, True, False)],
                       "javascript.calc.js.txt", {"double": False, "triple": False, "aide": True}),
        "go": ("go_test.go.txt",
               [("TestDouble", True, True, False, False), ("TestRien", True, False, False, False),
                ("TestPlusTard", True, True, True, False), ("aide", False, False, False, False)],
               "go.calc.go.txt", {"Double": False, "aide": True, "Ajouter": False}),
        "java": ("java.CalcTest.java.txt",
                 [("doubleMultiplieParDeux", True, True, False, False), ("plusTard", True, True, True, False),
                  ("neMesureRien", True, False, False, False), ("aide", False, False, False, False)],
                 "java.Calc.java.txt", {"double_": False, "aide": True, "paquet": True}),
        "ruby": ("ruby_spec.rb.txt",
                 [("multiplie par deux", True, True, False, False), ("ne mesure rien", True, False, False, False),
                  ("plus tard", True, True, True, False), ("attend, avec sa raison", True, True, True, True)],
                 "ruby.calc.rb.txt", {"double": False, "aide": True}),
        "php": ("php.CalcTest.php.txt",
                [("testDouble", True, True, False, False), ("testRien", True, False, False, False),
                 ("testPlusTard", True, True, True, False), ("aide", False, False, False, False)],
                "php.Calc.php.txt", {"double": False, "aide": True}),
    }

    def test_chaque_langage_lit_ses_tests_et_son_code(self):
        tous = adaptateurs()
        for langage, (tests, attendus, code, prives) in self.CAS.items():
            cfg, prive = tous[langage]["tests"], re.compile(tous[langage]["code"]["private"])
            assertion = re.compile(cfg["assertion"])
            fonctions = tests_lecture.extraire((DONNEES / tests).read_text(), tests, cfg)
            with self.subTest(langage=langage):
                lus = [(f.nom, f.est_test, tests_lecture.affirme(f, assertion, set()), *_desactive(f, cfg))
                       for f in fonctions]
                self.assertEqual(lus, attendus)
                texte = (DONNEES / code).read_text()
                lignes = texte.splitlines()
                vus = {f.nom: bool(prive.match(lignes[f.ligne - 1]))
                       for f in tests_lecture.extraire(texte, code, cfg)}
                self.assertEqual(vus, prives)

    def test_la_tautologie_de_chaque_langage(self):
        exemples = {"javascript": "    expect(x).toBe(x);", "go": "\tif got != got {",
                    "java": "        assertEquals(x, x);", "ruby": "    expect(x).to eq(x)",
                    "php": "        $this->assertSame($x, $x);"}
        for langage, ligne in exemples.items():
            with self.subTest(langage=langage):
                motifs = [re.compile(m) for m in adaptateurs()[langage]["tests"]["tautology"]]
                self.assertTrue(any(m.search(ligne) for m in motifs))


class TestLecteursDeMutation(unittest.TestCase):
    """Chaque lecteur compte, pour le fichier du plafond, ce que son outil
    rapporte ; un statut inconnu compte survivant."""

    def test_chaque_outil(self):
        cas = {
            "stryker": ("src/calc.js", {"attrapes": 1, "survivants": 2, "expires": 1, "inviables": 1}),
            "gremlins": ("calc.go", {"attrapes": 1, "survivants": 2, "expires": 1}),
            "pit": ("src/main/java/essai/Calc.java", {"attrapes": 1, "survivants": 2, "expires": 1}),
            "mutant": ("lib/calc.rb", {"attrapes": 2, "expires": 1, "survivants": 1}),
            "infection": ("src/Calc.php", {"attrapes": 1, "survivants": 2, "expires": 1}),
        }
        for outil, (module, attendu) in cas.items():
            with self.subTest(outil=outil):
                res = mutation.LECTEURS[outil](DONNEES / "mutation" / outil)
                self.assertEqual(dict(res[module]), attendu)

    def test_chaque_outil_a_son_lecteur(self):
        self.assertEqual({o: mutation.LECTEURS[o] for o in ("stryker", "gremlins", "pit", "mutant", "infection")},
                         {"stryker": mutation.lire_stryker, "gremlins": mutation.lire_gremlins,
                          "pit": mutation.lire_pit, "mutant": mutation.lire_mutant,
                          "infection": mutation.lire_infection})

    def test_mutant_ne_lit_que_la_session_la_plus_recente(self):
        res = mutation.lire_mutant(DONNEES / "mutation/mutant")
        self.assertEqual(sum(res["calc.rb"].values()), 4)

    def test_un_chemin_compte_pour_chacun_de_ses_suffixes(self):
        res = mutation.lire_infection(DONNEES / "mutation/infection")
        self.assertEqual(res["Calc.php"], res["projet/src/Calc.php"])

    def test_un_dossier_sans_rapport_ne_compte_rien(self):
        with tempfile.TemporaryDirectory() as d:
            for outil in ("stryker", "gremlins", "pit", "mutant", "infection"):
                self.assertEqual(mutation.LECTEURS[outil](Path(d)), {})


class TestDetectionEtRegression(unittest.TestCase):
    def test_le_langage_se_deduit_de_son_fichier(self):
        for fichier, langage in (("go.mod", "go"), ("pom.xml", "java"), ("Gemfile", "ruby"),
                                 ("composer.json", "php"), ("package.json", "javascript")):
            with self.subTest(fichier=fichier), tempfile.TemporaryDirectory() as d:
                (Path(d) / fichier).write_text("")
                self.assertEqual(installeur.detecter_langage(Path(d)), langage)

    def test_go_rejoue_un_test_par_son_paquet(self):
        cap = adaptateurs()["go"]["capabilities"]["regression"]
        self.assertEqual(commande_regression(cap, ["calc/calc_test.go", "calc/autre_test.go", "x_test.go"]),
                         "go test ./calc ./")



if __name__ == "__main__":
    unittest.main()
