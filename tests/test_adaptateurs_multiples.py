"""Un projet en plusieurs langages : chaque fichier jugé par l'adaptateur
dont les motifs le désignent (ADR-0051). Un projet fabriqué, en Python et en
Kotlin, comme JustCook : ses outils en Python, son app en Kotlin."""

import os
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

from socle import (config, context as contexte, checks_tests as controles_tests, hooks, installer as installeur,
                   mutation, requests as demandes, state as etat, verification)
from socle.report import Rapport

ADAPTATEURS = Path(__file__).resolve().parent.parent / "engine/socle/adapters"

CALC = "FACTEUR = 2\n\n\ndef double(x):\n    return FACTEUR * x\n"
TEST_CALC = ("import unittest\n\nfrom calc import double\n\n\nclass TestCalc(unittest.TestCase):\n"
             "    def test_double(self):\n        self.assertEqual(double(2), 4)\n")
CALC_KT = "package essai\n\nfun doubler(x: Int): Int = 2 * x\n"
TEST_KT = ("package essai\n\nimport kotlin.test.Test\nimport kotlin.test.assertEquals\n\nclass CalcTest {\n"
           "    @Test\n    fun doublerMultiplieParDeux() {\n        assertEquals(4, doubler(2))\n    }\n}\n")


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class DeuxLangages(unittest.TestCase):
    """La base : Python en principal, Kotlin dans `.socle/adapters/`, chacun
    avec son code et son test."""

    principal = "python"

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-deux-langages-"))
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / ".socle/adapters").mkdir(parents=True)
        shutil.copy(ADAPTATEURS / f"{self.principal}.toml", self.racine / ".socle/adapter.toml")
        shutil.copy(ADAPTATEURS / "kotlin.toml", self.racine / ".socle/adapters/kotlin.toml")
        self.ecrire("calc.py", CALC)
        self.ecrire("tests/test_calc.py", TEST_CALC)
        self.ecrire("src/main/kotlin/essai/Calc.kt", CALC_KT)
        self.ecrire("src/test/kotlin/essai/CalcTest.kt", TEST_KT)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def ecrire(self, chemin: str, texte: str):
        p = self.racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte)

    def projet(self) -> config.Projet:
        return config.Projet.charger(self.racine)

    def controle(self, ident: str, base: str | None = None) -> list[str]:
        ctx = contexte.Contexte(self.projet(), etage="ci", base=base)
        r = contexte.executer(ctx, [ident])
        return [c.message for c in r.erreurs(ident)]


class LeProjet(DeuxLangages):
    def test_le_projet_lit_ses_adaptateurs_le_principal_d_abord(self):
        p = self.projet()
        self.assertEqual([(a.nom, a.chemin) for a in p.adaptateurs],
                         [("python", ".socle/adapter.toml"), ("kotlin", ".socle/adapters/kotlin.toml")])
        self.assertTrue(p.plusieurs_adaptateurs)
        self.assertEqual(config.fichiers_adaptateurs(self.racine, ".socle/adapters"),
                         [".socle/adapters/kotlin.toml"])
        self.assertEqual(config.fichiers_adaptateurs(self.racine, ".socle/adapters", "HEAD"),
                         [".socle/adapters/kotlin.toml"])

    def test_la_vue_d_un_adaptateur_juge_avec_ses_seuls_motifs(self):
        p = self.projet()
        kotlin = p.adaptateurs[1]
        vue = p.pour(kotlin)
        self.assertEqual(vue.adaptateur["language"], "kotlin")
        self.assertEqual(vue.chemins.adaptateur, ".socle/adapters/kotlin.toml")
        self.assertEqual(vue.adaptateur_courant.nom, "kotlin")
        self.assertEqual(p.adaptateur_courant.nom, "python")
        # La vue garde tous les adaptateurs du projet.
        self.assertEqual([a.nom for a in vue.adaptateurs], ["python", "kotlin"])
        tous = sorted(outils_fichiers(self.racine))
        self.assertEqual(p.designes(kotlin, tous), ["src/main/kotlin/essai/Calc.kt", "src/test/kotlin/essai/CalcTest.kt"])
        self.assertEqual(p.designes(p.adaptateurs[0], tous), ["calc.py", "tests/test_calc.py"])
        # Le code du projet : les sources de tous.
        self.assertIn("**/src/**/kotlin/**/*.kt", p.chemins_code())
        self.assertIn("**/*.py", p.chemins_code())

    def test_les_adaptateurs_des_autres_langages_sont_proteges(self):
        self.assertIn(".socle/adapters/**", self.projet().chemins_proteges())

    def test_un_projet_a_un_seul_langage_n_a_que_son_adaptateur(self):
        shutil.rmtree(self.racine / ".socle/adapters")
        p = self.projet()
        self.assertEqual([a.nom for a in p.adaptateurs], ["python"])
        self.assertFalse(p.plusieurs_adaptateurs)

    def test_un_adaptateur_illisible_est_une_erreur_de_configuration(self):
        self.ecrire(".socle/adapters/casse.toml", "language = \n")
        p = self.projet()
        self.assertEqual([c for c, _ in p.erreurs_config], [".socle/adapters/casse.toml"])
        self.assertEqual([a.nom for a in p.adaptateurs], ["python", "kotlin"])


def outils_fichiers(racine: Path) -> list[str]:
    from socle import utils as outils

    return outils.fichiers_courants(racine)


class Recouvrement(DeuxLangages):
    def test_des_motifs_disjoints_ne_recouvrent_rien(self):
        self.assertEqual(self.controle("adaptateur.recouvrement"), [])

    def test_un_fichier_designe_par_deux_adaptateurs_est_refuse(self):
        shutil.copy(ADAPTATEURS / "python.toml", self.racine / ".socle/adapters/doublon.toml")
        ctx = contexte.Contexte(self.projet(), etage="ci")
        r = Rapport()
        controles_tests.recouvrement(ctx, r)
        lieux = {c.chemin for c in r.erreurs("adaptateur.recouvrement")}
        self.assertEqual(lieux, {"calc.py", "tests/test_calc.py"})
        self.assertIn("(python, doublon)", r.erreurs("adaptateur.recouvrement")[0].message)


class ParAdaptateur(DeuxLangages):
    def test_chaque_test_se_juge_avec_son_adaptateur(self):
        self.ecrire("src/test/kotlin/essai/VideTest.kt",
                    "package essai\n\nimport kotlin.test.Test\n\nclass VideTest {\n"
                    "    @Test\n    fun neMesureRien() {\n        doubler(2)\n    }\n}\n")
        erreurs = self.controle("tests.creux")
        self.assertEqual(erreurs, ["kotlin : test `neMesureRien` sans assertion : il passe sans rien mesurer"])

    def test_une_fonction_kotlin_se_teste_en_kotlin(self):
        # Un test Python qui la nommerait ne la teste pas : chaque fichier se
        # juge avec les motifs de son adaptateur (ADR-0051, point 3).
        self.ecrire("src/main/kotlin/essai/Calc.kt", CALC_KT + "\nfun tripler(x: Int): Int = 3 * x\n")
        self.ecrire("tests/test_calc.py", TEST_CALC + "\n    def test_tripler(self):\n"
                    "        self.assertEqual(tripler(2), 6)  # tripler\n")
        erreurs = self.controle("tests.code-teste", self.base)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertTrue(erreurs[0].startswith("kotlin : fonction `tripler` ajoutée"), erreurs[0])

    def test_un_constat_commun_aux_adaptateurs_ne_se_dit_qu_une_fois(self):
        def verifier(ctx, r):
            r.erreur("essai.commun", "d'un fichier de cas", "docs/cas.json")
            r.erreur("essai.commun", "dans chaque langage")
            r.erreur("essai.commun", f"propre à {ctx.projet.adaptateur['language']}")

        c = contexte.Controle("essai.commun", verifier, ("ci",), False, False, "", True)
        r = Rapport()
        contexte._par_adaptateur(c, contexte.Contexte(self.projet(), etage="ci"), r)
        # Un fichier qu'aucun ne désigne : sans nom ; le même refus dans les
        # deux langages : les deux noms (revue du lot, constat 11).
        self.assertEqual([k.message for k in r.constats],
                         ["d'un fichier de cas", "python, kotlin : dans chaque langage",
                          "python : propre à python", "kotlin : propre à kotlin"])

    def test_un_correctif_se_prouve_dans_le_langage_du_code_corrige(self):
        p = self.projet()
        python, kotlin = (p.pour(a) for a in p.adaptateurs)
        self.assertTrue(controles_tests.concerne(python, ["calc.py"]))
        self.assertFalse(controles_tests.concerne(kotlin, ["calc.py"]))
        self.assertTrue(controles_tests.concerne(kotlin, ["src/main/kotlin/essai/Calc.kt"]))
        self.assertFalse(controles_tests.concerne(python, ["src/main/kotlin/essai/Calc.kt"]))
        # Des deux langages : un test dans chacun.
        deux = ["calc.py", "src/main/kotlin/essai/Calc.kt"]
        self.assertTrue(controles_tests.concerne(python, deux) and controles_tests.concerne(kotlin, deux))
        # Le code d'aucun : le principal en répond, comme dans un projet à un
        # seul langage.
        self.assertTrue(controles_tests.concerne(python, ["README.md"]))
        self.assertFalse(controles_tests.concerne(kotlin, ["README.md"]))
        # Un test Python ajouté à un correctif du code Kotlin ne fait pas de
        # Python le langage du code corrigé (revue du lot, constat 4).
        mixte = ["src/main/kotlin/essai/Calc.kt", "src/test/kotlin/essai/CalcTest.kt", "tests/test_calc.py"]
        self.assertTrue(controles_tests.concerne(kotlin, mixte))
        self.assertFalse(controles_tests.concerne(python, mixte))
        # Des tests seuls, sans code : ceux de leur langage.
        self.assertTrue(controles_tests.concerne(kotlin, ["src/test/kotlin/essai/CalcTest.kt"]))
        self.assertFalse(controles_tests.concerne(python, ["src/test/kotlin/essai/CalcTest.kt"]))

    def test_corrige_son_code_lit_les_fichiers_du_correctif(self):
        self.ecrire("src/main/kotlin/essai/Calc.kt", CALC_KT.replace("2 * x", "x * 2"))
        git(self.racine, "commit", "-qam", "fix: doubler")
        sha = git(self.racine, "rev-parse", "HEAD").strip()
        p = self.projet()
        ctx = contexte.Contexte(p, etage="ci", base=self.base)
        self.assertFalse(controles_tests.corrige_son_code(ctx.pour(p.adaptateurs[0]), self.base, sha))
        self.assertTrue(controles_tests.corrige_son_code(ctx.pour(p.adaptateurs[1]), self.base, sha))

    def test_le_hook_avertit_d_un_correctif_sans_test_dans_le_langage_corrige(self):
        self.ecrire("src/main/kotlin/essai/Calc.kt", CALC_KT.replace("2 * x", "x * 2"))
        git(self.racine, "add", "-A")
        alerte = hooks.correctif_sans_test(self.projet(), "fix: doubler", amendement=False)
        self.assertIsNotNone(alerte)
        self.assertIn("src/test/kotlin/**/*Test.kt", alerte)
        self.assertNotIn("tests/test_*.py", alerte)
        self.ecrire("src/test/kotlin/essai/CalcTest.kt", TEST_KT.replace("assertEquals(4, doubler(2))",
                                                                          "assertEquals(6, doubler(3))"))
        git(self.racine, "add", "-A")
        self.assertIsNone(hooks.correctif_sans_test(self.projet(), "fix: doubler", amendement=False))

    def test_une_demande_nomme_les_tests_de_chaque_langage(self):
        d = demandes.Demande.__new__(demandes.Demande)
        d.texte = "Valider `doublerMultiplieParDeux` et `test_double`."
        nommes = demandes.gestes_nommes(d, self.projet())
        self.assertIn("doublerMultiplieParDeux", nommes)
        self.assertIn("test_double", nommes)

    def test_l_etat_ne_signale_pas_un_langage_qu_un_adaptateur_couvre(self):
        self.ecrire("build.gradle.kts", "plugins { kotlin(\"jvm\") }\n")
        self.ecrire("pyproject.toml", "[project]\nname = \"essai\"\n")
        self.assertEqual(etat.audit_adaptateur(self.projet()), [])
        shutil.rmtree(self.racine / ".socle/adapters")
        self.assertIn("kotlin", "\n".join(etat.audit_adaptateur(self.projet())))


class Verification(DeuxLangages):
    def test_verify_lance_les_etapes_de_chaque_adaptateur_et_nomme_celle_qui_echoue(self):
        for chemin, code in ((".socle/adapter.toml", 0), (".socle/adapters/kotlin.toml", 3)):
            p = self.racine / chemin
            texte = p.read_text()
            debut = texte.index("[capabilities.tests]")
            fin = texte.index("\n[", debut + 1)
            p.write_text(texte[:debut] + f'[capabilities.tests]\ncommand = "exit {code}"\nfast = true\n' + texte[fin:])
        r = Rapport()
        verification.executer_etapes(self.projet(), True, r)
        self.assertIn("verify.python.tests", r.executes)
        self.assertIn("verify.kotlin.tests", r.executes)
        # Jusqu'au bout : Kotlin échoue, Python passe.
        self.assertIn("verify.kotlin.tests", r.controles_en_echec())
        self.assertNotIn("verify.python.tests", r.controles_en_echec())

    def test_la_ci_installe_les_outils_de_tous(self):
        commandes = verification.commandes_ci(self.projet())
        self.assertTrue(any("pip install" in c for c in commandes) or commandes == [], commandes)
        etapes = installeur.etapes_de_ci([(ADAPTATEURS / "python-pytest.toml").read_text(),
                                          (ADAPTATEURS / "kotlin.toml").read_text(),
                                          (ADAPTATEURS / "kotlin.toml").read_text()])
        self.assertIn("pytest et mutmut", etapes)
        self.assertEqual(etapes.count("actions/setup-java"), 1)


class Mutation(DeuxLangages):
    principal = "python-pytest"

    def setUp(self):
        super().setUp()
        self.ecrire("src/outil.py", CALC)
        self.ecrire(".socle/guardrails.toml", '[mutation.caps]\n"src/outil.py" = { max = 0 }\n'
                    '"src/main/kotlin/essai/Calc.kt" = { max = 1, reason = "un survivant connu" }\n')

    def test_chaque_adaptateur_tient_les_plafonds_de_ses_modules(self):
        p = self.projet()
        python, kotlin = (p.pour(a) for a in p.adaptateurs)
        self.assertEqual(list(mutation.plafonds_de(python)), ["src/outil.py"])
        self.assertEqual(list(mutation.plafonds_de(kotlin)), ["src/main/kotlin/essai/Calc.kt"])
        # Un projet à un seul langage les juge tous, comme avant.
        shutil.rmtree(self.racine / ".socle/adapters")
        self.assertEqual(len(mutation.plafonds_de(self.projet())), 2)

    def test_un_plafond_qu_aucun_adaptateur_ne_designe_revient_au_principal(self):
        # Revue du lot, constat 5 : sans lui, `calc.py`, hors de `src/`, ne
        # serait plus jugé par personne.
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(gf.read_text() + '"calc.py" = { max = 0 }\n')
        p = self.projet()
        python, kotlin = (p.pour(a) for a in p.adaptateurs)
        self.assertEqual(sorted(mutation.plafonds_de(python)), ["calc.py", "src/outil.py"])
        self.assertEqual(list(mutation.plafonds_de(kotlin)), ["src/main/kotlin/essai/Calc.kt"])

    def test_chaque_balayage_ecrit_dans_son_dossier(self):
        p = self.projet()
        commandes, dossier, faute = mutation.commandes_de_balayage(p.pour(p.adaptateurs[1]))
        self.assertEqual((commandes, dossier, faute), (["./gradlew -q pitest"], self.racine, None))
        # Un outil lancé module par module écrit sous le dossier de son
        # adaptateur : deux langages ne s'écrasent pas.
        k = self.racine / ".socle/adapters/kotlin.toml"
        k.write_text(k.read_text().replace('command = "./gradlew -q pitest"',
                                           'command = "./gradlew -q pitest -Pmodule={module} -Pout={output}"', 1))
        p = self.projet()
        commandes, dossier, faute = mutation.commandes_de_balayage(p.pour(p.adaptateurs[1]))
        self.assertIsNone(faute)
        self.assertEqual(dossier, self.racine / mutation.SORTIES / "kotlin")
        self.assertEqual(commandes, [f"./gradlew -q pitest -Pmodule=src/main/kotlin/essai/Calc.kt "
                                     f"-Pout={dossier / '000'}"])

    def test_le_balayage_nomme_l_adaptateur_de_chaque_constat(self):
        with open(os.devnull, "w") as nul:
            r = mutation.balayer(self.projet(), flux=nul)
        messages = [c.message for c in r.constats]
        self.assertTrue(messages)
        self.assertTrue(all(m.startswith(("python : ", "kotlin : ")) for m in messages), messages)

    def test_le_balayage_planifie_compte_pour_tous(self):
        niveau, message, flux, _ = mutation.etat_du_balayage(self.projet(), outils_fichiers(self.racine),
                                                              lambda f: None)
        self.assertEqual(niveau, "erreur")
        self.assertIn("socle-mutation.yml", message)


class Installation(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-install-deux-"))
        git(self.racine, "init", "-q", "-b", "main")
        for chemin, texte in (("pyproject.toml", "[project]\nname = \"outils\"\n[tool.pytest.ini_options]\n"),
                              ("src/outils/verif.py", "def verifier():\n    return True\n"),
                              ("settings.gradle.kts", "include(\":app\")\n"),
                              ("app/build.gradle.kts", "plugins { kotlin(\"jvm\") }\n"),
                              ("app/src/main/kotlin/app/App.kt", "package app\n\nfun main() {}\n")):
            p = self.racine / chemin
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(texte)

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def test_l_installeur_reconnait_un_adaptateur_par_langage(self):
        self.assertEqual(installeur.detecter_adaptateurs(self.racine), ["python-pytest", "kotlin"])

    def test_un_depot_a_un_seul_langage_n_en_a_qu_un(self):
        shutil.rmtree(self.racine / "app")
        self.assertEqual(installeur.detecter_adaptateurs(self.racine), ["python-pytest"])

    def test_le_premier_nomme_prend_l_adaptateur_principal(self):
        with open(os.devnull, "w") as nul:
            import contextlib
            with contextlib.redirect_stdout(nul), contextlib.redirect_stderr(nul):
                installeur.installer(self.racine, ["python-pytest", "kotlin"], "@essai")
        p = config.Projet.charger(self.racine)
        self.assertEqual([(a.nom, a.chemin) for a in p.adaptateurs],
                         [("python", ".socle/adapter.toml"), ("kotlin", ".socle/adapters/kotlin.toml")])
        ci = (self.racine / ".github/workflows/socle.yml").read_text()
        self.assertIn("actions/setup-java", ci)
        self.assertIn("mutmut", ci)
        self.assertTrue((self.racine / mutation.WORKFLOW).is_file())
        caps = (self.racine / ".socle/guardrails.toml").read_text()
        self.assertIn('"app/src/main/kotlin/app/App.kt"', caps)
        self.assertIn('"src/outils/verif.py"', caps)


def installer(racine: Path, adaptateurs, proprietaire="@essai") -> int:
    import contextlib

    with open(os.devnull, "w") as nul, contextlib.redirect_stdout(nul), contextlib.redirect_stderr(nul):
        return installeur.installer(racine, adaptateurs, proprietaire)


class MiseAJour(unittest.TestCase):
    """Un projet Python déjà équipé, auquel du Kotlin s'ajoute : le chemin de
    JustCook (revue du lot de B-0095)."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-maj-deux-"))
        git(self.racine, "init", "-q", "-b", "main")
        for chemin, texte in (("pyproject.toml", "[project]\nname = \"outils\"\n[tool.pytest.ini_options]\n"),
                              ("src/outils/verif.py", "def verifier():\n    return True\n")):
            self.ecrire(chemin, texte)
        installer(self.racine, ["python-pytest"])
        self.ecrire("settings.gradle.kts", "include(\":app\")\n")
        self.ecrire("app/build.gradle.kts", "plugins { kotlin(\"jvm\") }\n")
        self.ecrire("app/src/main/kotlin/app/App.kt", "package app\n\nfun main() {}\n")

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def ecrire(self, chemin: str, texte: str):
        p = self.racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte)

    def test_les_modules_du_langage_ajoute_entrent_a_mesurer(self):
        installer(self.racine, "auto")
        caps = (self.racine / ".socle/guardrails.toml").read_text()
        self.assertIn('"app/src/main/kotlin/app/App.kt" = { pending = true }', caps)
        self.assertIn('"src/outils/verif.py"', caps)

    def test_la_ci_garde_les_outils_du_principal_quand_seul_l_autre_est_nomme(self):
        installer(self.racine, ["kotlin"])
        self.assertTrue((self.racine / ".socle/adapters/kotlin.toml").is_file())
        self.assertIn('language = "python"', (self.racine / ".socle/adapter.toml").read_text())
        ci = (self.racine / ".github/workflows/socle.yml").read_text()
        self.assertIn("mutmut", ci)
        self.assertIn("actions/setup-java", ci)

    def test_un_principal_sans_langage_ne_recoit_pas_de_doublon(self):
        p = self.racine / ".socle/adapter.toml"
        p.write_text(p.read_text().replace('language = "python"\n', "", 1))
        installer(self.racine, "auto")
        self.assertFalse((self.racine / ".socle/adapters/python-pytest.toml").exists())
        self.assertFalse((self.racine / ".socle/adapters/kotlin.toml").exists())
        # Nommé, il s'ajoute.
        installer(self.racine, ["kotlin"])
        self.assertTrue((self.racine / ".socle/adapters/kotlin.toml").is_file())

    def test_ajouter_a_mesurer_cree_la_table_qui_manque(self):
        self.assertEqual(installeur.ajouter_a_mesurer("[memory]\n", ["a.kt"]),
                         '[memory]\n\n[mutation.caps]\n"a.kt" = { pending = true }\n')
        self.assertEqual(installeur.ajouter_a_mesurer('[mutation.caps]\n"b.py" = { max = 0 }\n', ["a.kt"]),
                         '[mutation.caps]\n"a.kt" = { pending = true }\n"b.py" = { max = 0 }\n')
        self.assertEqual(installeur.modules_a_mesurer(self.racine, [(ADAPTATEURS / "kotlin.toml").read_text()]),
                         ["app/src/main/kotlin/app/App.kt"])


class PythonSecond(unittest.TestCase):
    """Un projet Kotlin dont Python est le second langage, sa copie
    `python.toml` posée : un `conftest.py` neuf fait détecter `python-pytest`
    (B-0144)."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-python-second-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        for chemin, texte in (("build.gradle.kts", "plugins { kotlin(\"jvm\") }\n"),
                              ("src/main/kotlin/A.kt", "fun a() = 1\n"),
                              ("outils/pyproject.toml", "[project]\nname = \"outils\"\n"),
                              ("outils/calc.py", "def f():\n    return 1\n"),
                              ("tests/test_calc.py", "import unittest\n")):
            p = self.racine / chemin
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(texte)
        installer(self.racine, "auto")
        self.assertEqual(sorted(p.name for p in (self.racine / ".socle/adapters").glob("*.toml")), ["python.toml"])
        git(self.racine, "add", "-A")
        git(self.racine, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "installation")
        (self.racine / "conftest.py").write_text("")

    def test_une_mise_a_jour_automatique_garde_la_seule_copie_python(self):
        self.assertEqual(installeur.detecter_adaptateurs(self.racine), ["kotlin", "python-pytest"])
        sortie = installer_et_lire(self.racine, "auto")
        self.assertEqual(sorted(p.name for p in (self.racine / ".socle/adapters").glob("*.toml")), ["python.toml"])
        self.assertIn("adaptateur : kotlin, python (détecté)", sortie)
        self.assertNotIn("adaptateur.recouvrement            ECHEC", sortie)

    def test_nomme_l_adaptateur_d_un_langage_que_couvre_une_copie_est_la_copie(self):
        sortie = installer_et_lire(self.racine, ["kotlin", "python-pytest"])
        self.assertFalse((self.racine / ".socle/adapters/python-pytest.toml").exists())
        self.assertIn("adaptateur : kotlin, python\n", sortie)
        # Seul nommé, il ne prend pas la place du principal : la CI en part.
        installer(self.racine, ["python-pytest"])
        self.assertFalse((self.racine / ".socle/adapters/python-pytest.toml").exists())
        self.assertIn('language = "kotlin"', (self.racine / ".socle/adapter.toml").read_text())
        self.assertIn("actions/setup-java", (self.racine / ".github/workflows/socle.yml").read_text())

    ECARTE = ("!! {nom} non posé : .socle/adapters/python.toml existe déjà pour python, et se garde. Pour le "
              "remplacer : ")

    def test_nomme_un_adaptateur_maintenu_que_remplace_la_copie_l_installeur_le_dit(self):
        """B-0327 : `--adapter python-pytest` sur une copie `python` n'est pas
        posé ; l'installeur le dit, comme pour la copie principale."""
        sortie = installer_et_lire(self.racine, ["kotlin", "python-pytest"])
        self.assertFalse((self.racine / ".socle/adapters/python-pytest.toml").exists())
        self.assertIn(self.ECARTE.format(nom="python-pytest"), sortie)
        ligne = next(l for l in sortie.splitlines() if "python-pytest non posé" in l)
        self.assertIn("par une demande, de retirer .socle/adapters/python.toml", ligne)
        self.assertIn("le même `--adapter`", ligne)

    def test_nomme_un_fichier_que_remplace_la_copie_l_installeur_le_dit(self):
        dossier = Path(tempfile.mkdtemp(prefix="socle-adaptateur-"))
        self.addCleanup(shutil.rmtree, dossier, ignore_errors=True)
        fichier = dossier / "mon-python.toml"
        fichier.write_text((ADAPTATEURS / "python-pytest.toml").read_text())
        sortie = installer_et_lire(self.racine, ["kotlin", str(fichier)])
        self.assertFalse((self.racine / ".socle/adapters/mon-python.toml").exists())
        self.assertIn(self.ECARTE.format(nom="mon-python"), sortie)

    def test_detecte_en_automatique_la_copie_ne_fait_rien_dire_de_plus(self):
        """Détecté, `python-pytest` est la copie `python` sans que l'installeur
        en dise plus : personne ne l'a demandé."""
        self.assertIn("python-pytest", installeur.detecter_adaptateurs(self.racine))
        sortie = installer_et_lire(self.racine, "auto")
        self.assertNotIn("non posé", sortie)
        self.assertFalse((self.racine / ".socle/adapters/python-pytest.toml").exists())

    def test_nomme_la_copie_elle_meme_ne_fait_rien_dire_de_plus(self):
        sortie = installer_et_lire(self.racine, ["kotlin", "python"])
        self.assertNotIn("non posé", sortie)

    def test_langages_en_place_lit_chaque_copie(self):
        self.assertEqual(installeur.langages_en_place(self.racine, config.FORMAT_ACTUEL), {"kotlin", "python"})


def installer_et_lire(racine: Path, adaptateurs) -> str:
    """L'installeur, et ce qu'il imprime."""
    import contextlib
    import io

    sortie = io.StringIO()
    with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(io.StringIO()):
        installeur.installer(racine, adaptateurs, "@essai")
    return sortie.getvalue()


class Rafraichissement(unittest.TestCase):
    """La mise à jour ne rafraîchit une copie d'adaptateur, la principale
    comprise, que si le projet ne l'a pas adaptée (ADR-0052)."""

    KT = ".socle/adapters/kotlin.toml"
    MOTEUR_KT = ".socle/engine/socle/adapters/kotlin.toml"

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-rafraichir-"))
        git(self.racine, "init", "-q", "-b", "main")
        for chemin, texte in (("pyproject.toml", "[project]\nname = \"outils\"\n[tool.pytest.ini_options]\n"),
                              ("src/outils/verif.py", "def verifier():\n    return True\n"),
                              ("settings.gradle.kts", "include(\":app\")\n"),
                              ("app/build.gradle.kts", "plugins { kotlin(\"jvm\") }\n"),
                              ("app/src/main/kotlin/app/App.kt", "package app\n\nfun main() {}\n")):
            self.ecrire(chemin, texte)
        installer(self.racine, "auto")
        self.commit("installation")
        self.maintenu = {n: (ADAPTATEURS / f"{n}.toml").read_text() for n in ("kotlin", "python-pytest", "python")}

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def ecrire(self, chemin: str, texte: str):
        p = self.racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte)

    def lire(self, chemin: str) -> str:
        return (self.racine / chemin).read_text()

    def commit(self, message: str):
        # Un dépôt jetable : ses versions d'essai du moteur ne passent pas par
        # les hooks git que l'installeur y a branchés.
        git(self.racine, "add", "-A")
        git(self.racine, "-c", "core.hooksPath=/dev/null", "commit", "-qm", message)

    def test_une_copie_non_adaptee_se_rafraichit(self):
        # Le moteur installé portait une version d'avant, que la copie a gardée.
        ancien = self.maintenu["kotlin"] + "\n# version d'avant\n"
        self.ecrire(self.MOTEUR_KT, ancien)
        self.ecrire(self.KT, ancien)
        self.commit("version d'avant")
        sortie = installer_et_lire(self.racine, "auto")
        self.assertEqual(self.lire(self.KT), self.maintenu["kotlin"])
        self.assertIn(f"{self.KT} rafraîchi depuis l'adaptateur maintenu kotlin, que le projet n'avait pas adapté",
                      sortie)

    def test_la_copie_principale_d_une_version_de_l_historique_se_rafraichit(self):
        # Posée par une version ancienne, que le moteur installé n'a plus : la
        # copie principale d'un projet à un seul langage, qu'aucune mise à jour
        # ne rafraîchissait.
        v1 = self.maintenu["python-pytest"] + "\n# version 1\n"
        self.ecrire(".socle/engine/socle/adapters/python-pytest.toml", v1)
        self.ecrire(".socle/adapter.toml", v1)
        self.commit("version 1")
        self.ecrire(".socle/engine/socle/adapters/python-pytest.toml", self.maintenu["python-pytest"] + "\n# v2\n")
        self.commit("version 2")
        sortie = installer_et_lire(self.racine, ["python-pytest"])
        self.assertEqual(self.lire(".socle/adapter.toml"), self.maintenu["python-pytest"])
        self.assertIn(".socle/adapter.toml rafraîchi depuis l'adaptateur maintenu python-pytest", sortie)

    def test_une_copie_adaptee_se_garde_et_l_installeur_dit_quand_son_maintenu_a_change(self):
        adaptee = self.maintenu["kotlin"].replace("cache: gradle", "cache: gradle\n          # Android")
        self.ecrire(self.KT, adaptee)
        sortie = installer_et_lire(self.racine, "auto")
        self.assertEqual(self.lire(self.KT), adaptee)
        self.assertIn(f"{self.KT} adapté par le projet : conservé ; l'adaptateur maintenu kotlin n'a pas changé",
                      sortie)
        # Le moteur installé portait une version d'avant : le maintenu a changé.
        self.ecrire(self.MOTEUR_KT, self.maintenu["kotlin"] + "\n# version d'avant\n")
        self.commit("version d'avant")
        avant = git(self.racine, "rev-parse", "HEAD").strip()[:12]
        voir = ["git", "diff", avant, "--", self.MOTEUR_KT]
        for _ in range(2):
            # Relancé avant le commit, l'installeur trouve le moteur nouveau
            # dans l'arbre : il juge encore contre le dernier commit.
            sortie = installer_et_lire(self.racine, "auto")
            self.assertEqual(self.lire(self.KT), adaptee)
            self.assertIn(f"!! {self.KT} adapté par le projet : conservé ; l'adaptateur maintenu kotlin a changé",
                          sortie)
            self.assertIn(f"`{' '.join(voir)}`", sortie)
        # La commande montre ce qui a changé, avant le commit de la mise à
        # jour comme après.
        self.assertIn("# version d'avant", git(self.racine, *voir[1:]))
        self.commit("mise à jour")
        self.assertIn("# version d'avant", git(self.racine, *voir[1:]))

    def test_un_maintenu_absent_du_moteur_installe_se_compare_a_la_copie(self):
        adaptee = self.maintenu["kotlin"] + "\n# adaptée\n"
        self.ecrire(self.KT, adaptee)
        (self.racine / self.MOTEUR_KT).unlink()
        self.commit("moteur sans kotlin")
        sortie = installer_et_lire(self.racine, "auto")
        self.assertEqual(self.lire(self.KT), adaptee)
        self.assertIn(f"!! {self.KT} : conservé ; l'adaptateur maintenu kotlin n'était pas dans le moteur installé : "
                      f"le comparer à la copie (`diff {self.KT} {self.MOTEUR_KT}`)", sortie)

    def test_un_clone_superficiel_se_signale(self):
        clone = Path(tempfile.mkdtemp(prefix="socle-rafraichir-clone-"))
        self.addCleanup(shutil.rmtree, clone, ignore_errors=True)
        git(clone, "clone", "-q", "--depth", "1", f"file://{self.racine}", "copie")
        sortie = installer_et_lire(clone / "copie", "auto")
        self.assertIn("!! clone superficiel : l'historique du moteur y est incomplet", sortie)
        self.assertNotIn("clone superficiel", installer_et_lire(self.racine, "auto"))

    def test_la_ci_garde_la_copie_principale_quand_la_detection_change_d_adaptateur(self):
        # Une copie adaptée de `python` ; le dépôt dit pytest : la détection
        # propose `python-pytest`, qu'aucun nom n'impose (constat 2 de la revue).
        adaptee = self.maintenu["python"].replace(
            'ci_setup = ""', 'ci_setup = """\n      - name: Outil maison\n        run: echo outil-maison\n"""', 1)
        self.assertTrue(adaptee != self.maintenu["python"])
        self.ecrire(".socle/adapter.toml", adaptee)
        installer(self.racine, "auto")
        self.assertTrue(self.lire(".socle/adapter.toml") == adaptee)
        self.assertIn("echo outil-maison", self.lire(".github/workflows/socle.yml"))

    def test_une_copie_resserree_par_une_demande_se_garde(self):
        # Le point 2 d'ADR-0051 : un recouvrement se règle en resserrant les
        # motifs d'une copie ; la mise à jour ne le défait pas.
        resserree = self.maintenu["kotlin"].replace('sources = ["**/src/**/kotlin/**/*.kt"',
                                                     'sources = ["app/src/**/kotlin/**/*.kt"', 1)
        self.assertTrue(resserree != self.maintenu["kotlin"])
        self.ecrire(self.KT, resserree)
        installer(self.racine, "auto")
        self.assertTrue(self.lire(self.KT) == resserree)

    def test_la_ci_part_de_la_copie_gardee(self):
        adaptee = self.maintenu["kotlin"].replace(
            '"""\n\n[capabilities.format]',
            '      - name: SDK Android\n        run: echo sdk-android\n"""\n\n[capabilities.format]', 1)
        self.assertTrue(adaptee != self.maintenu["kotlin"])
        self.ecrire(self.KT, adaptee)
        installer(self.racine, "auto")
        ci = self.lire(".github/workflows/socle.yml")
        self.assertIn("echo sdk-android", ci)
        self.assertIn("mutmut", ci)

    def test_la_ci_part_de_la_copie_principale_gardee(self):
        adaptee = self.maintenu["python-pytest"].replace(
            "run: python3 -m pip install pytest mutmut\n",
            "run: python3 -m pip install pytest mutmut hypothesis\n", 1)
        self.assertTrue(adaptee != self.maintenu["python-pytest"])
        self.ecrire(".socle/adapter.toml", adaptee)
        installer(self.racine, "auto")
        self.assertTrue(self.lire(".socle/adapter.toml") == adaptee)
        self.assertIn("pip install pytest mutmut hypothesis", self.lire(".github/workflows/socle.yml"))
        # Nommer un autre adaptateur maintenu pour son langage en fait la CI.
        installer(self.racine, ["python", "kotlin"])
        ci = self.lire(".github/workflows/socle.yml")
        self.assertNotIn("hypothesis", ci)
        self.assertTrue(self.lire(".socle/adapter.toml") == adaptee)

    def test_versions_maintenues_lit_le_moteur_installe_et_l_historique(self):
        v1 = self.maintenu["kotlin"] + "\n# version 1\n"
        self.ecrire(self.MOTEUR_KT, v1)
        self.commit("version 1")
        self.ecrire(self.MOTEUR_KT, self.maintenu["kotlin"] + "\n# arbre\n")
        connus = installeur.versions_maintenues(self.racine, ".socle/engine")
        # Le moteur installé est celui du dernier commit ; l'arbre compte parmi les versions.
        self.assertEqual(connus.installes["kotlin"], v1)
        self.assertEqual(connus.versions["kotlin"],
                         {self.maintenu["kotlin"], v1, self.maintenu["kotlin"] + "\n# arbre\n"})
        self.assertEqual(connus.moteur, ".socle/engine")
        self.assertEqual(connus.commit, git(self.racine, "rev-parse", "HEAD").strip()[:12])
        self.assertFalse(connus.superficiel)
        # Une version que seul un renommage porte, sous l'ancien dossier du moteur.
        v2 = v1 + "# renommée\n"
        self.ecrire("ancien/socle/adapters/kotlin.toml", v1)
        self.commit("ancien moteur")
        git(self.racine, "mv", "ancien", "nouveau")
        self.ecrire("nouveau/socle/adapters/kotlin.toml", v2)
        self.commit("moteur renommé")
        self.assertIn(v2, installeur.versions_maintenues(self.racine, ".socle/engine").versions["kotlin"])
        # Les copies du projet, sous `.socle/adapters/`, ne sont pas des versions maintenues.
        self.ecrire(self.KT, "# propre au projet\n")
        self.commit("copie")
        self.assertNotIn("# propre au projet\n", installeur.versions_maintenues(self.racine, ".socle/engine")
                         .versions["kotlin"])

    def test_adaptateur_de_base_de_la_copie_principale(self):
        versions = {n: {t} for n, t in self.maintenu.items()}
        self.assertEqual(installeur.adaptateur_de_base(self.maintenu["python"], versions), "python")
        # Adaptée : l'adaptateur maintenu de son langage le plus proche.
        self.assertEqual(installeur.adaptateur_de_base(self.maintenu["python-pytest"] + "\n# adapté\n", versions),
                         "python-pytest")
        self.assertEqual(installeur.adaptateur_de_base(self.maintenu["python"] + "\n# adapté\n", versions), "python")
        # Sans langage qu'un adaptateur maintenu porte : propre au projet.
        self.assertIsNone(installeur.adaptateur_de_base('language = "cobol"\n', versions))
        self.assertIsNone(installeur.adaptateur_de_base("[capabilities]\n", versions))
        self.assertIsNone(installeur.adaptateur_de_base("language = \n", versions))

    def test_rafraichir_copie_garde_un_adaptateur_propre_au_projet(self):
        connus = installeur.versions_maintenues(self.racine, ".socle/engine")
        self.ecrire(".socle/adapters/maison.toml", 'language = "maison"\n')
        self.assertEqual(installeur.rafraichir_copie(self.racine, ".socle/adapters/maison.toml", None, connus),
                         [".socle/adapters/maison.toml existe : conservé (comparer au gabarit à la main si besoin)"])
        self.assertEqual(installeur.rafraichir_copie(self.racine, self.KT, "kotlin", connus), [])
        self.assertEqual(self.lire(".socle/adapters/maison.toml"), 'language = "maison"\n')


class Detection(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-detection-"))
        git(self.racine, "init", "-q", "-b", "main")

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def ecrire(self, chemin: str, texte: str):
        p = self.racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte)

    def test_un_langage_tiers_n_appelle_pas_d_adaptateur(self):
        self.ecrire("pyproject.toml", "[project]\nname = \"x\"\n")
        self.ecrire("x.py", "X = 1\n")
        # À la racine : le manifeste d'un sous-dossier n'appelle pas
        # d'adaptateur, tiers ou non (B-0168).
        self.ecrire("package.json", "{}\n")
        self.assertEqual(installeur.detecter_adaptateurs(self.racine), ["python", "javascript"])
        self.ecrire(".socle/guardrails.toml", '[thirdparty]\npaths = ["package.json"]\n')
        self.assertEqual(installeur.detecter_adaptateurs(self.racine), ["python"])

    def test_un_python_second_sous_pytest_prend_python_pytest(self):
        self.ecrire("build.gradle.kts", "plugins { kotlin(\"jvm\") }\n")
        self.ecrire("src/main/kotlin/A.kt", "fun a() = 1\n")
        self.ecrire("tools/pyproject.toml", "[project]\nname = \"t\"\n[tool.pytest.ini_options]\n")
        self.ecrire("tools/t.py", "T = 1\n")
        self.assertEqual(installeur.detecter_adaptateurs(self.racine), ["kotlin", "python-pytest"])


class Balayage(unittest.TestCase):
    def test_un_workflow_qui_ne_lance_qu_un_outil_ne_suffit_pas(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-balayage-deux-"))
        try:
            git(racine, "init", "-q", "-b", "main")
            (racine / ".github/workflows").mkdir(parents=True)
            (racine / ".github/workflows/pit.yml").write_text("jobs:\n  m:\n    steps:\n      - run: ./gradlew pitest\n")
            py, kt = ((ADAPTATEURS / f"{n}.toml").read_text() for n in ("python-pytest", "kotlin"))
            self.assertEqual(installeur._balayage_planifie(racine, kt)[0], False)
            self.assertEqual(installeur._balayage_planifie(racine, py, [kt])[0], True)
            (racine / ".socle/adapters").mkdir(parents=True)
            (racine / ".socle/adapter.toml").write_text(py)
            (racine / ".socle/adapters/kotlin.toml").write_text(kt)
            projet = config.Projet.charger(racine)
            fichiers = outils_fichiers(racine)
            niveau, message, _, _ = mutation.etat_du_balayage(projet, fichiers, lambda f: (racine / f).read_text())
            self.assertEqual(niveau, "erreur")
        finally:
            shutil.rmtree(racine, ignore_errors=True)


# Ce qu'une étape de `ci_setup` exige d'un fichier de build, et les motifs que
# sa condition peut citer : ceux que l'outil lit. Un cache d'un outil absent
# de la table est une faute : la table s'étend avec les adaptateurs.
CACHES = {
    "gradle": {"**/*.gradle*", "**/gradle-wrapper.properties", "buildSrc/**/Versions.kt",
               "buildSrc/**/Dependencies.kt", "gradle/*.versions.toml", "**/versions.properties"},
    "maven": {"**/pom.xml"},
    "npm": {"**/package-lock.json", "**/npm-shrinkwrap.json"}, "yarn": {"**/yarn.lock"},
    "pnpm": {"**/pnpm-lock.yaml"}, "pip": {"**/requirements.txt"}, "pipenv": {"**/Pipfile.lock"},
    "poetry": {"**/poetry.lock"},
}
COMMANDES = (
    (r"\bnpm (?:ci|install)\b|\byarn(?: install)?(?:\s|$)|\bpnpm install\b", {"package.json"}),
    (r"\bcomposer install\b", {"composer.json"}),
    (r"\bdotnet restore\b", {"*.sln", "*.slnx", "*.csproj"}),
    (r"\bmvn\b", {"pom.xml", "**/pom.xml"}),
    (r"\./gradlew\b", {"gradlew"}),
    (r"\bbundle install\b", {"Gemfile", "gems.rb"}),
)
# Une clé ou une option qui nomme le fichier qu'elle lit : la condition le cite.
NOMME_SON_FICHIER = re.compile(r"(?:[\w-]+-file|cache-dependency-path):\s*['\"]?([^\s,}'\"]+)"
                               r"|\bpip3? install\b[^\n]*?\s-r\s*(\S+)")


def etapes_yaml(texte: str) -> list[str]:
    """Les étapes d'un `ci_setup` ou d'un workflow, une par bloc `      - `."""
    return [b for b in re.split(r"(?m)^(?=      - )", texte) if b.strip()]


def exigences(bloc: str) -> list[tuple[str, set[str] | None]]:
    """Ce que l'étape exige d'un fichier de build : ce qui l'exige, et les
    motifs permis à sa condition (None : un cache que la table ignore)."""
    code = re.sub(r"(?m)^\s*(?:- )?(?:name:|#).*$", "", bloc)
    res = [(f"cache: {outil}", CACHES.get(outil))
           for outil in re.findall(r"(?<![\w-])cache:\s*['\"]?([\w-]+)", code) if outil != "false"]
    res += [(m.group(0).strip(), permis) for motif, permis in COMMANDES for m in [re.search(motif, code)] if m]
    res += [(m.group(0).strip(), {m.group(1) or m.group(2)}) for m in NOMME_SON_FICHIER.finditer(code)]
    return res


def fautes_d_etape(bloc: str) -> list[str]:
    """Ce qui manque à la condition d'une étape qui exige un fichier."""
    exige = exigences(bloc)
    if not exige:
        return []
    m = re.search(r"(?m)^\s*(?:- )?if:\s*hashFiles\(([^)]*)\)\s*!=\s*''\s*$", bloc)
    if not m:
        return [f"{quoi} : aucune condition `if: hashFiles(…) != ''`" for quoi, _ in exige]
    motifs = set(re.findall(r"'([^']+)'", m.group(1)))
    fautes = []
    for quoi, permis in exige:
        if permis is None:
            fautes.append(f"{quoi} : outil absent de la table des caches")
        elif not motifs or not motifs <= permis:
            # Chaque motif cité est lu par l'outil : la condition vraie,
            # l'outil trouve son fichier.
            fautes.append(f"{quoi} : la condition cite {sorted(motifs)}, hors de {sorted(permis)}")
    return fautes


class AvantLePremierFichier(unittest.TestCase):
    """B-0179 : un adaptateur posé avant le premier fichier de son langage ne
    fait pas échouer la CI. Le pilote, en `python-pytest` et `kotlin` sans
    Gradle, voyait `actions/setup-java` refuser son `cache: gradle`. Le
    workflow ne tourne que sur GitHub : son texte se juge ici."""

    def test_une_etape_qui_exige_un_fichier_de_build_l_attend(self):
        fautes, conditionnees = [], 0
        for chemin in sorted(ADAPTATEURS.glob("*.toml")):
            for bloc in etapes_yaml(tomllib.loads(chemin.read_text()).get("ci_setup", "")):
                fautes += [f"{chemin.name} : {f}" for f in fautes_d_etape(bloc)]
                conditionnees += bool(exigences(bloc))
        self.assertEqual(fautes, [])
        self.assertGreaterEqual(conditionnees, 5)

    def test_le_juge_des_etapes_reconnait_chaque_forme(self):
        """Chaque forme qu'une étape prend pour exiger un fichier est vue en
        faute, sans condition ou avec une condition qui cite autre chose."""
        fautives = (
            "      - uses: actions/setup-node@v5\n        with:\n          cache: npm\n",
            "      - uses: actions/setup-python@v6\n        with: {python-version: '3.12', cache: pip}\n",
            "      - uses: actions/setup-go@v6\n        with:\n          go-version-file: go.mod\n",
            "      - uses: actions/setup-dotnet@v5\n        with:\n          global-json-file: global.json\n",
            "      - uses: actions/setup-python@v6\n        with:\n          cache-dependency-path: req/dev.txt\n",
            "      - name: D\n        run: python3 -m pip install -r requirements.txt\n",
            "      - name: D\n        run: yarn install --frozen-lockfile\n",
            "      - name: D\n        run: pnpm install\n",
            "      - name: D\n        if: hashFiles('composer.json') != ''\n        run: npm ci\n",
            "      - uses: actions/setup-java@v5\n        if: hashFiles('**/*.gradle*', 'settings.gradle') != ''\n"
            "        with:\n          cache: gradle\n",
            "      - uses: actions/setup-java@v5\n        with:\n          cache: sbt\n",
        )
        for bloc in fautives:
            self.assertTrue(fautes_d_etape(bloc), bloc)
        saines = (
            "      - uses: ruby/setup-ruby@v1\n        with:\n          bundler-cache: true\n",
            "      - name: pytest et mutmut\n        run: python3 -m pip install pytest mutmut\n",
            "      - name: D\n        if: hashFiles('package.json') != ''\n        run: npm ci\n",
            "      - uses: actions/setup-go@v6\n        if: hashFiles('go.mod') != ''\n        with:\n"
            "          go-version-file: go.mod\n",
        )
        for bloc in saines:
            self.assertEqual(fautes_d_etape(bloc), [], bloc)

    def test_un_projet_python_et_kotlin_sans_gradle_passe_la_ci(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-sans-gradle-"))
        try:
            git(racine, "init", "-q", "-b", "main")
            (racine / "pyproject.toml").write_text("[project]\nname = \"pilote\"\n")
            self.assertEqual(installer(racine, ["python-pytest", "kotlin"]), 0)
            self.assertFalse([f for f in racine.rglob("*") if f.suffix == ".kt" or ".gradle" in f.name])
            ci = (racine / ".github/workflows/socle.yml").read_text()
            java = [b for b in etapes_yaml(ci) if "actions/setup-java" in b]
            self.assertEqual(len(java), 1, ci)
            self.assertIn("if: hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') != ''", java[0])
            self.assertIn("cache: gradle", java[0])
            self.assertEqual([f for b in etapes_yaml(ci) for f in fautes_d_etape(b)], [])
            git(racine, "add", "-A")
            git(racine, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "socle")
            # `socle ci` sans l'auto-test : les capacités, puis les contrôles.
            projet = config.Projet.charger(racine)
            r = Rapport()
            verification.executer_etapes(projet, False, r)
            r.fusionner(contexte.executer(contexte.Contexte(projet, etage="ci", base=None)))
            self.assertTrue(r.reussi, r.texte())
            # Le saut des capacités de Kotlin se dit, il n'est pas silencieux.
            sauts = [c.message for c in r.constats if c.controle == "verify.kotlin.tests"]
            self.assertTrue(sauts and "pas encore de code" in sauts[0], sauts)
        finally:
            shutil.rmtree(racine, ignore_errors=True)

    def test_l_agent_ne_lance_pas_une_commande_qui_attend_son_fichier_de_build(self):
        """Revue de B-0179 : la condition vaut aussi côté agent. Un projet
        `javascript` et `csharp` neuf, sans `package.json` ni solution : ni
        l'installeur ni le hook de démarrage ne lancent `npm ci` ou
        `dotnet restore`, ils disent qu'elles attendent."""
        from unittest import mock

        racine = Path(tempfile.mkdtemp(prefix="socle-sans-manifeste-"))
        try:
            git(racine, "init", "-q", "-b", "main")
            sortie = installer_et_lire(racine, ["javascript", "csharp"])
            self.assertNotIn("donner à l'agent les outils que la CI installe", sortie)
            self.assertIn("attendent leur fichier de build", sortie)
            self.assertIn("`npm ci` (attend `package.json`)", sortie)
            projet = config.Projet.charger(racine)
            self.assertEqual(verification.commandes_ci(projet), [])
            attente = verification.commandes_en_attente(projet)
            self.assertEqual([c for c, _ in attente], ["npm ci", "dotnet restore && dotnet tool restore"])
            self.assertIn("`dotnet restore && dotnet tool restore` (attend `*.sln`, `*.slnx`, `*.csproj`)",
                          verification.attente_dite(attente))
            with mock.patch.dict(os.environ, {hooks.SESSION_CLOUD: "true"}):
                lignes = hooks.installer_outils(projet)
            self.assertEqual(len(lignes), 1, lignes)
            self.assertIn("en attente de leur fichier de build", lignes[0])
            self.assertFalse([x for x in lignes if x.startswith("!!")])
            # Le manifeste là, la commande se donne, comme la CI la lancera.
            (racine / "package.json").write_text("{}\n")
            self.assertEqual(verification.commandes_ci(projet), ["npm ci"])
            self.assertEqual([c for c, _ in verification.commandes_en_attente(projet)],
                             ["dotnet restore && dotnet tool restore"])
            # Sans condition, une commande se donne toujours ; un `ci_setup`
            # sans liste d'étapes se lit encore.
            self.assertEqual(verification.etapes_ci("      - name: O\n        run: echo o\n"), [("echo o", [])])
            self.assertEqual(verification.etapes_ci("run: echo o\n"), [("echo o", [])])
        finally:
            shutil.rmtree(racine, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
