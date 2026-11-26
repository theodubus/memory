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

# Un `Corrige:` dans un paragraphe à part, avant les lignes d'attribution :
# git ne le lit pas comme un trailer (B-0348).
MESSAGE_CORRIGE_EGARE = ("Double accepte une chaîne\n\nLe calcul convertit son entrée.\n\nCorrige: T-0001\n\n"
                         "Co-Authored-By: t <t@t>\nClaude-Session: https://example.org/s")


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

    def corriger(self, texte, message="fix: double accepte une chaîne"):
        (self.racine / "calc.py").write_text(texte)
        git(self.racine, "commit", "-qam", message, "--no-verify")

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

    def test_une_demande_validee_qui_nomme_le_commit_l_admet(self):
        """D-0047 : un correctif dont le test passe sur le parent dans la CI,
        parce que sa preuve dépend de l'environnement, bloquait la PR à jamais ;
        l'humain l'admet par une demande validée qui nomme son commit."""
        from socle import requests as demandes

        self.corriger(CORRIGE.replace("double(self.entree()) == 6", "double(3) == 6"))
        sha = git(self.racine, "rev-parse", "HEAD").strip()
        chemin = self.racine / "memory/requests/D-0001-admettre.md"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(f"<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Admettre le correctif {sha[:8]}\n\n"
                          "> date : 2026-10-29\n\nSon test ne prouve rien dans la CI.\n\n## Réponses possibles\n\n"
                          "- `valider` — l'admettre.\n- `contexte-insuffisant` — réécrire la demande.\n")
        d = next(x for x in demandes.toutes(self.racine) if x.id == "D-0001")
        demandes.ecrire_reponse(self.racine, d, "valider", "", "Théo", "2026-10-29", canal="conversation",
                                citation="valider")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "D-0001 validée", "--no-verify")
        ctx = self.contexte()
        r = Rapport()
        controles_tests.regression(ctx, r)
        self.assertEqual(r.erreurs("tests.regression"), [])
        self.assertTrue(any("admis par D-0001" in c.message for c in r.constats))
        # Six caractères du commit ne le nomment pas.
        from types import SimpleNamespace

        courte = SimpleNamespace(validations=[SimpleNamespace(id="D-0002", texte=f"le correctif {sha[:6]}")])
        self.assertIsNone(controles_tests._admis_par(courte, sha))

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

    def test_un_corrige_hors_du_dernier_paragraphe_fait_un_correctif(self):
        """B-0348 : une ligne `Corrige:` écrite dans un paragraphe à part,
        avant les lignes d'attribution, que git ne lit pas comme un trailer,
        faisait sauter en silence la vérification du test de régression ; le
        commit est un correctif, refusé sans test qui échoue sur son parent
        (ADR-0109)."""
        self.corriger(CALC.replace("2 * x", "2 * int(x)"), MESSAGE_CORRIGE_EGARE)
        erreurs = self.erreurs(self.contexte())
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("correctif sans test de régression", erreurs[0])
        self.assertIn("Double accepte une chaîne", erreurs[0])

    def test_un_corrige_hors_du_dernier_paragraphe_avec_son_test_passe(self):
        self.corriger(CORRIGE, MESSAGE_CORRIGE_EGARE)
        self.assertEqual(self.erreurs(self.contexte()), [])
        # Le test est bien rejoué : un test qui passe déjà sur le parent ne
        # prouve rien, et le commit reste refusé.
        git(self.racine, "reset", "-q", "--hard", self.base)
        self.corriger(CORRIGE.replace("double(self.entree()) == 6", "double(3) == 6"), MESSAGE_CORRIGE_EGARE)
        erreurs = self.erreurs(self.contexte())
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("passe déjà sur le parent", erreurs[0])

    def test_est_correctif_lit_corrige_et_fixes_ou_qu_ils_soient(self):
        projet = config.Projet.charger(self.racine)
        attribution = "\n\nCo-Authored-By: t <t@t>"
        for message in ("fix: double accepte une chaîne", "Double\n\nCorrige: T-0001",
                        "Double\n\nFixes: T-0001", MESSAGE_CORRIGE_EGARE,
                        "Double\n\nUn corps.\n\nFixes: T-0001" + attribution,
                        "Double\nCorrige: T-0001"):
            self.assertTrue(controles_tests.est_correctif(projet, message), message)
        for message in ("Double accepte une chaîne", "Double\n\nRefs: T-0001\n\nCorrige T-0001 sans deux-points.",
                        "Double\n\nUn corps qui dit corrige: sans commencer la ligne." + attribution,
                        "Double\n\nRefs: T-0001" + attribution):
            self.assertFalse(controles_tests.est_correctif(projet, message), message)


class TestCorrectifHorsDeToutAdaptateur(unittest.TestCase):
    """D-0088 : un correctif qui ne touche aucun fichier qu'un adaptateur
    juge (du Dart, sous un adaptateur Python) ne se prouve par aucun test ;
    il reste refusé, en le disant, et une demande validée qui nomme son
    commit l'admet."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-hors-adaptateur-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text(CALC)
        (self.racine / "app").mkdir()
        (self.racine / "app/main.dart").write_text("int doubler(int x) => 2 * x;\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        (self.racine / "app/main.dart").write_text("int doubler(int x) => x * 2;\n")
        git(self.racine, "commit", "-qam", "fix: doubler en Dart", "--no-verify")
        self.sha = git(self.racine, "rev-parse", "HEAD").strip()

    def juger(self) -> Rapport:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete="HEAD")
        r = Rapport()
        controles_tests.regression(ctx, r)
        return r

    def test_il_est_refuse_en_nommant_ses_fichiers_et_les_issues(self):
        erreurs = [c.message for c in self.juger().erreurs("tests.regression")]
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("correctif qui ne touche aucun fichier qu'un adaptateur juge (app/main.dart)", erreurs[0])
        self.assertIn("ou une demande que l'humain valide, qui nomme ce commit et l'admet sans test", erreurs[0])
        self.assertNotIn("sans test de régression", erreurs[0])

    def test_une_demande_validee_qui_nomme_le_commit_l_admet_sans_test(self):
        from socle import requests as demandes

        chemin = self.racine / "memory/requests/D-0001-admettre.md"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(f"<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Admettre le correctif "
                          f"{self.sha[:8]}\n\n> date : 2026-11-09\n\nAucun adaptateur ne juge le Dart.\n\n"
                          "## Réponses possibles\n\n- `valider` — l'admettre.\n- `contexte-insuffisant` — réécrire "
                          "la demande.\n")
        d = next(x for x in demandes.toutes(self.racine) if x.id == "D-0001")
        demandes.ecrire_reponse(self.racine, d, "valider", "", "Théo", "2026-11-09", canal="conversation",
                                citation="valider")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "D-0001 validée", "--no-verify")
        r = self.juger()
        self.assertEqual(r.erreurs("tests.regression"), [])
        self.assertTrue(any("correctif hors de tout adaptateur, admis sans test par D-0001" in c.message
                            for c in r.constats))

    def test_hors_de_tout_adaptateur(self):
        projet = config.Projet.charger(self.racine)
        self.assertEqual(controles_tests.hors_de_tout_adaptateur(projet, ["app/main.dart", "README.md"]),
                         ["app/main.dart", "README.md"])
        self.assertEqual(controles_tests.hors_de_tout_adaptateur(projet, ["app/main.dart", "calc.py"]), [])
        # Le dossier du socle n'est à aucun adaptateur : un correctif qui n'y
        # touche que lui s'admet aussi par une demande.
        self.assertEqual(controles_tests.hors_de_tout_adaptateur(projet, [".socle/policy.toml"]),
                         [".socle/policy.toml"])
        self.assertEqual(controles_tests.hors_de_tout_adaptateur(projet, []), [])
        # Ce qu'il corrige d'abord, la mémoire et la documentation qui
        # l'accompagnent ensuite.
        self.assertEqual(controles_tests.hors_de_tout_adaptateur(
            projet, ["README.md", "memory/active.md", "src/main.dart"]),
            ["src/main.dart", "README.md", "memory/active.md"])

    def test_des_fichiers_declares_tiers_ne_sont_pas_juges(self):
        """La deuxième issue du refus : ses fichiers déclarés tiers, le
        correctif n'est plus jugé, au lieu d'exiger un test Python."""
        gf = self.racine / ".socle/guardrails.toml"
        texte = gf.read_text()
        i = texte.index("[thirdparty]\n")
        gf.write_text(texte[:i] + texte[i:].replace("paths = []", 'paths = ["app/**"]', 1))
        self.assertEqual(config.Projet.charger(self.racine).chemins_tiers(), ["app/**"])
        r = self.juger()
        self.assertEqual(r.erreurs("tests.regression"), [])
        self.assertTrue(any("correctif qui ne touche que des fichiers tiers : non jugé" in c.message
                            for c in r.constats))

    def test_un_correctif_qui_ne_touche_que_la_memoire_n_est_pas_juge(self):
        """B-0359 : dans chess, « Correction : … » d'une entrée de la mémoire
        était refusé comme un correctif hors de tout adaptateur."""
        entree = self.racine / "memory/journal/2026-11-26.md"
        entree.parent.mkdir(parents=True, exist_ok=True)
        entree.write_text("## J-2026-11-26-A — Une entrée\n\nUn mot faux.\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "Une entrée du journal", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        entree.write_text("## J-2026-11-26-A — Une entrée\n\nLe mot juste.\n")
        git(self.racine, "commit", "-qam", "Correction : le mot de J-2026-11-26-A", "--no-verify")
        r = self.juger()
        self.assertEqual(r.erreurs("tests.regression"), [])
        self.assertTrue(any("correctif qui ne touche que la mémoire : non jugé" in c.message
                            for c in r.constats), [c.message for c in r.constats])

    def test_un_permalien_vers_le_commit_ne_l_admet_pas(self):
        """Un permalien porte le SHA complet du dernier commit poussé : une
        demande sans rapport qui en donne un ne nomme pas ce correctif."""
        from socle import requests as demandes

        chemin = self.racine / "memory/requests/D-0001-autre.md"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text("<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Une autre question\n\n"
                          f"> date : 2026-11-09\n\nVoir [le test](https://github.com/o/r/blob/{self.sha}/t.py#L2)."
                          "\n\n## Réponses possibles\n\n- `valider` — oui.\n- `contexte-insuffisant` — réécrire.\n")
        d = next(x for x in demandes.toutes(self.racine) if x.id == "D-0001")
        demandes.ecrire_reponse(self.racine, d, "valider", "", "Théo", "2026-11-09", canal="conversation",
                                citation="valider")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "D-0001 validée", "--no-verify")
        erreurs = [c.message for c in self.juger().erreurs("tests.regression")]
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("aucun fichier qu'un adaptateur juge", erreurs[0])

    def test_le_hook_se_tait_quand_le_principal_ne_rejoue_rien(self):
        from socle import hooks

        (self.racine / "app/main.dart").write_text("int doubler(int x) => x + x;\n")
        git(self.racine, "add", "app/main.dart")
        projet = config.Projet.charger(self.racine)
        projet.adaptateur["capabilities"]["regression"].pop("command", None)
        self.assertIsNone(hooks.correctif_sans_test(projet, "fix: doubler encore", amendement=False))

    def test_le_hook_le_dit_des_le_commit(self):
        from socle import hooks

        (self.racine / "app/main.dart").write_text("int doubler(int x) => x + x;\n")
        git(self.racine, "add", "app/main.dart")
        message = hooks.correctif_sans_test(config.Projet.charger(self.racine), "fix: doubler encore",
                                            amendement=False)
        self.assertIn("ce correctif ne touche aucun fichier qu'un adaptateur juge (app/main.dart)", message)


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
