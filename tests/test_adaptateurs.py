"""Les adaptateurs maintenus : chacun se lit, déclare chaque capacité, et
reconnaît les tests de son langage."""

import re
import subprocess
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
                         ["csharp", "go", "java", "javascript", "kotlin", "php", "python", "python-pytest", "ruby",
                          "rust"])

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
        # xUnit, NUnit et MSTest dans un même fichier (B-0040).
        "csharp": ("csharp.CalcTests.cs.txt",
                   [("DoublerMultiplieParDeux", True, True, False, False), ("SuivantAjouteUn", True, True, False, False),
                    ("PlusTardAvecRaison", True, True, True, True), ("PlusTardSansRaison", True, True, True, False),
                    ("NeMesureRien", True, False, False, False), ("NUnitIgnoreAvecRaison", True, True, True, True),
                    ("MSTestInconclusif", True, False, True, False), ("SurUneLigne", True, True, False, False),
                    ("Aide", False, False, False, False)],
                   "csharp.Calc.cs.txt", {"Doubler": False, "Tripler": False, "Aide": True, "Interne": True,
                                          "SansModificateur": True, "Ancienne": False}),
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
                    "php": "        $this->assertSame($x, $x);", "csharp": "        Assert.Equal(x, x);"}
        for langage, ligne in exemples.items():
            with self.subTest(langage=langage):
                motifs = [re.compile(m) for m in adaptateurs()[langage]["tests"]["tautology"]]
                self.assertTrue(any(m.search(ligne) for m in motifs))


class TestKotlin(unittest.TestCase):
    """L'adaptateur Kotlin pour Gradle (B-0095, D-0082) : il lit les tests de
    kotlin.test, de JUnit et de MockK, leurs assertions, un test désactivé
    avec ou sans raison, les fonctions en expression ou annotées sur leur
    ligne, tout public sauf `private` et `internal`, et retrouve les
    résultats de PIT d'un fichier Kotlin."""

    def setUp(self):
        self.ad = adaptateurs()["kotlin"]
        self.cfg = self.ad["tests"]

    def test_il_lit_ses_tests_et_leurs_assertions(self):
        assertion = re.compile(self.cfg["assertion"])
        fonctions = tests_lecture.extraire((DONNEES / "kotlin.CalcTest.kt.txt").read_text(), "CalcTest.kt", self.cfg)
        lus = [(f.nom, f.est_test, tests_lecture.affirme(f, assertion, set()), *_desactive(f, self.cfg))
               for f in fonctions]
        self.assertEqual(lus, [("creuxEnExpression", True, False, False, False),
                               ("doublerMultiplieParDeux", True, True, False, False),
                               ("parExpression", True, True, False, False),
                               ("surUneLigne", True, True, False, False),
                               ("`refuse un nombre negatif`", True, True, False, False),
                               ("verifieLAppel", True, True, False, False),
                               ("neMesureRien", True, False, False, False),
                               ("plusTard", True, True, True, False),
                               ("kotlinTestAvecRaison", True, True, True, True),
                               ("junit4AvecRaison", True, True, True, True),
                               ("attendAvecSaRaison", True, True, True, True),
                               ("aide", False, False, False, False)])

    def test_tout_est_public_sauf_private_et_internal(self):
        prive = re.compile(self.ad["code"]["private"])
        texte = (DONNEES / "kotlin.Calc.kt.txt").read_text()
        lignes = texte.splitlines()
        fonctions = tests_lecture.extraire(texte, "Calc.kt", self.cfg)
        self.assertEqual({f.nom: bool(prive.match(lignes[f.ligne - 1])) for f in fonctions},
                         {"doubler": False, "tripler": False, "racine": False, "plusGrand": False, "total": False,
                          "principal": False, "pourLesSousClasses": False, "aide": True, "interne": True,
                          "toString": False})
        # Une fonction en expression finit sur sa ligne : celle qui la suit
        # n'y est pas prise pour une fonction imbriquée.
        tripler = next(f for f in fonctions if f.nom == "tripler")
        self.assertEqual(tripler.fin, tripler.ligne)

    def test_un_fichier_sans_corps_n_entre_pas_a_la_mutation(self):
        a_du_code = re.compile(self.ad["capabilities"]["mutation"]["has_code"])
        self.assertTrue(a_du_code.search("    fun doubler(x: Int): Int {"))
        self.assertTrue(a_du_code.search("    fun tripler(x: Int) = 3 * x"))
        self.assertFalse(a_du_code.search("    fun doubler(x: Int = g()): Int"))
        self.assertFalse(a_du_code.search("expect fun plateforme(): String"))

    def test_sa_tautologie(self):
        motifs = [re.compile(m) for m in self.cfg["tautology"]]
        self.assertTrue(any(m.search("        assertEquals(x, x)") for m in motifs))
        self.assertFalse(any(m.search("        assertEquals(4, x)") for m in motifs))

    def test_il_rejoue_un_test_par_sa_classe_dans_chaque_module(self):
        cap = self.ad["capabilities"]["regression"]
        self.assertEqual(commande_regression(cap, ["src/test/kotlin/essai/RegressionTest.kt"]),
                         "./gradlew -q test --tests '*RegressionTest'")
        from socle import utils as outils

        for chemin in ("app/src/test/kotlin/essai/RegressionTest.kt", "app/src/test/java/essai/RegressionTest.kt",
                       "shared/src/commonTest/kotlin/essai/RegressionTest.kt"):
            self.assertTrue(outils.filtrer([chemin], cap["test_paths"]), chemin)

    def test_un_build_gradle_en_kotlin_ne_suffit_pas_sans_source_kotlin(self):
        """Un projet Java sous Gradle porte lui aussi `build.gradle.kts`, et
        souvent des greffons de construction en Kotlin sous `buildSrc/` : il
        faut encore du Kotlin dans le projet même."""
        with tempfile.TemporaryDirectory() as d:
            racine = Path(d)
            (racine / "build.gradle.kts").write_text("plugins { java }\n")
            (racine / "src/main/java").mkdir(parents=True)
            (racine / "src/main/java/App.java").write_text("class App {}\n")
            (racine / "buildSrc/src/main/kotlin").mkdir(parents=True)
            (racine / "buildSrc/src/main/kotlin/Convention.kt").write_text("fun f() {}\n")
            self.assertIsNone(installeur.detecter_langage(racine))
            self.assertEqual(installeur.langages_presents(
                ["build.gradle.kts", "src/main/java/App.java", "buildSrc/src/main/kotlin/Convention.kt"]), {})
            (racine / "src/main/kotlin").mkdir(parents=True)
            (racine / "src/main/kotlin/App.kt").write_text("fun main() {}\n")
            self.assertEqual(installeur.detecter_langage(racine), "kotlin")
            self.assertEqual(installeur.langages_presents(["build.gradle.kts", "src/main/kotlin/App.kt"]),
                             {"kotlin": ["build.gradle.kts"]})

    def test_pit_retrouve_le_fichier_kotlin_de_chaque_mutation(self):
        """PIT ne connaît que le paquet et le nom du fichier source : le
        lecteur retrouve le fichier dans le dépôt, rangé sous son paquet, ou
        seul de son nom à déclarer ce paquet ; un homonyme d'un autre paquet
        ne prête pas ses résultats."""
        with tempfile.TemporaryDirectory() as d:
            racine = Path(d)
            for chemin, texte in (("src/main/kotlin/essai/Calc.kt", "package essai\n"),
                                  ("src/main/kotlin/autre/Calc.kt", "package autre\n"),
                                  ("src/main/kotlin/App.kt", "package org.exemple.app\n"),
                                  ("build/generated/essai/Calc.kt", "package essai\n")):
                (racine / chemin).parent.mkdir(parents=True, exist_ok=True)
                (racine / chemin).write_text(texte)
            (racine / "build/reports/pitest").mkdir(parents=True)
            (racine / "build/reports/pitest/mutations.xml").write_text(
                "<mutations>"
                "<mutation status='KILLED'><sourceFile>Calc.kt</sourceFile><mutatedClass>essai.Calc</mutatedClass>"
                "</mutation>"
                "<mutation status='SURVIVED'><sourceFile>Calc.kt</sourceFile><mutatedClass>essai.Calc</mutatedClass>"
                "</mutation>"
                "<mutation status='SURVIVED'><sourceFile>App.kt</sourceFile>"
                "<mutatedClass>org.exemple.app.AppKt</mutatedClass></mutation>"
                "</mutations>")
            resultats = mutation.lire_pit(racine)
        self.assertEqual(resultats["src/main/kotlin/essai/Calc.kt"], {"attrapes": 1, "survivants": 1})
        self.assertEqual(resultats["src/main/kotlin/App.kt"], {"survivants": 1})
        self.assertNotIn("src/main/kotlin/autre/Calc.kt", resultats)


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

    def test_stryker_net_et_ses_chemins_absolus(self):
        # Le rapport de Stryker.NET : même schéma, autre nom, chemins absolus (B-0040).
        res = mutation.lire_stryker(DONNEES / "mutation/stryker-net")
        self.assertEqual(dict(res["src/Calc/Calc.cs"]), {"attrapes": 1, "survivants": 2, "expires": 1, "inviables": 2})
        self.assertEqual(res["Calc.cs"], res["/home/runner/work/calc/calc/src/Calc/Calc.cs".lstrip("/")])

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

    def test_csharp_se_deduit_de_sa_solution_ou_de_son_projet(self):
        for fichier in ("Calc.sln", "Calc.slnx", "Calc.csproj"):
            with self.subTest(fichier=fichier), tempfile.TemporaryDirectory() as d:
                (Path(d) / fichier).write_text("")
                (Path(d) / "package.json").write_text("{}")
                self.assertEqual(installeur.detecter_langage(Path(d)), "csharp")

    def test_un_projet_net_plus_bas_est_vu_par_l_audit(self):
        presents = installeur.langages_presents(["package.json", "src/App/App.csproj", ".socle/x.csproj"])
        self.assertEqual(presents, {"csharp": ["src/App/App.csproj"], "javascript": ["package.json"]})

    def test_csharp_rejoue_ses_tests_par_leur_classe(self):
        # Le filtre de `dotnet test`, tel que le shell le compose : un `|` entre deux classes.
        cap = adaptateurs()["csharp"]["capabilities"]["regression"]
        commande = commande_regression(cap, ["tests/A.Tests/ATests.cs", "tests/A.Tests/BTests.cs"])
        self.assertTrue(commande.startswith("dotnet test --nologo --filter "))
        sortie = subprocess.run("printf '%s\\n' " + commande.removeprefix("dotnet test --nologo --filter "),
                                shell=True, capture_output=True, text=True).stdout
        self.assertEqual(sortie, "FullyQualifiedName~ATests|FullyQualifiedName~BTests\n")

    def test_les_arguments_de_test_se_joignent_par_le_separateur_de_l_adaptateur(self):
        cap = {"command": "outil {test_args}", "test_arg": "{stem}", "test_arg_separator": ","}
        self.assertEqual(commande_regression(cap, ["t/ATest.x", "t/BTest.x"]), "outil ATest,BTest")
        sans = {k: v for k, v in cap.items() if k != "test_arg_separator"}
        self.assertEqual(commande_regression(sans, ["t/ATest.x", "t/BTest.x"]), "outil ATest BTest")

    def test_java_rejoue_deux_classes_en_une_commande(self):
        # B-0075 : `-Dtest=ATest BTest` faisait lire à Maven une phase `BTest`.
        cap = adaptateurs()["java"]["capabilities"]["regression"]
        commande = commande_regression(cap, ["src/test/java/essai/ATest.java", "src/test/java/essai/BTest.java"])
        self.assertEqual(commande, "mvn -q -B test -Dsurefire.failIfNoSpecifiedTests=false -Dtest=ATest,BTest")

    def test_go_rejoue_un_test_par_son_paquet(self):
        cap = adaptateurs()["go"]["capabilities"]["regression"]
        self.assertEqual(commande_regression(cap, ["calc/calc_test.go", "calc/autre_test.go", "x_test.go"]),
                         "go test ./calc ./")



if __name__ == "__main__":
    unittest.main()
