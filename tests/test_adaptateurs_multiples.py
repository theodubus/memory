"""Un projet en plusieurs langages : chaque fichier jugé par l'adaptateur
dont les motifs le désignent (ADR-0051). Un projet fabriqué, en Python et en
Kotlin, comme JustCook : ses outils en Python, son app en Kotlin."""

import os
import shutil
import subprocess
import tempfile
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
            r.erreur("essai.commun", "commun")
            r.erreur("essai.commun", f"propre à {ctx.projet.adaptateur['language']}")

        c = contexte.Controle("essai.commun", verifier, ("ci",), False, False, "", True)
        r = Rapport()
        contexte._par_adaptateur(c, contexte.Contexte(self.projet(), etage="ci"), r)
        self.assertEqual([k.message for k in r.constats],
                         ["commun", "python : propre à python", "kotlin : propre à kotlin"])

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


if __name__ == "__main__":
    unittest.main()
