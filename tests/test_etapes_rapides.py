"""L6 : une vérification réussie se mémorise. La vérification que l'agent
lance, la fin de tour et le hook avant push ne refont pas les étapes
rapides sur un arbre où elles ont déjà toutes passé ; mesuré sur la copie
d'un projet réel, une fin de tour et un push recompilaient le même arbre."""

import contextlib
import io
import shutil
import subprocess
import tempfile
import tomllib
import unittest
import unittest.mock
from pathlib import Path

from socle import config, installer as installeur, utils as outils, verification
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"


class TestEtapesRapides(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-etapes-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        (self.racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", "--no-verify"],
                       cwd=self.racine, check=True)
        self.compte = Path(tempfile.mkdtemp(prefix="socle-compte-")) / "n"
        self.addCleanup(shutil.rmtree, self.compte.parent, ignore_errors=True)
        self.code = 0

    def lancer(self, refaire=False) -> bool:
        projet = config.Projet.charger(self.racine)
        projet.adaptateur["capabilities"] = {
            "tests": {"command": f"echo . >> {self.compte}; exit {self.code}", "fast": True}}
        return verification.etapes_rapides(projet, Rapport(), refaire=refaire)

    def fois(self) -> int:
        return len(self.compte.read_text().split()) if self.compte.is_file() else 0

    def test_un_arbre_deja_verifie_ne_se_reverifie_pas(self):
        self.assertTrue(self.lancer())
        self.assertFalse(self.lancer())
        self.assertEqual(self.fois(), 1)
        self.assertTrue(self.lancer(refaire=True))
        self.assertEqual(self.fois(), 2)

    def test_un_arbre_change_se_reverifie(self):
        self.lancer()
        avant = outils.empreinte_arbre(self.racine)
        (self.racine / "calc.py").write_text("x = 2\n")
        self.assertNotEqual(outils.empreinte_arbre(self.racine), avant)
        self.assertTrue(self.lancer())
        (self.racine / "neuf.py").write_text("y = 1\n")
        self.assertTrue(self.lancer())
        self.assertEqual(self.fois(), 3)

    def test_un_commit_ou_la_memoire_seule_ne_relancent_pas_les_etapes(self):
        """B-0086, relevé sur chess : la fin de tour avait compilé et testé,
        puis le push recompilait le même contenu, commité, ou dont seule la
        mémoire avait changé."""
        (self.racine / "calc.py").write_text("x = 2\n")
        self.assertTrue(self.lancer())
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x = 2", "--no-verify"],
                       cwd=self.racine, check=True)
        self.assertFalse(self.lancer())
        actif = self.racine / "memory/active.md"
        actif.write_text(actif.read_text() + "\nUne ligne de plus.\n")
        self.assertFalse(self.lancer())
        (self.racine / "calc.py").write_text("x = 3\n")
        self.assertTrue(self.lancer())
        self.assertEqual(self.fois(), 2)

    def test_l_empreinte_du_contenu(self):
        avant = outils.empreinte_contenu(self.racine, ("memory/",))
        (self.racine / "memory/active.md").write_text("autre\n")
        self.assertEqual(outils.empreinte_contenu(self.racine, ("memory/",)), avant)
        self.assertNotEqual(outils.empreinte_contenu(self.racine), avant)
        (self.racine / "neuf.py").write_text("y = 1\n")
        self.assertNotEqual(outils.empreinte_contenu(self.racine, ("memory/",)), avant)

    def test_les_etapes_rapides_le_disent_a_leurs_commandes(self):
        # D-0019 : un test trop long pour une fin de tour se met de côté
        # quand la variable est posée ; toutes les étapes, en CI, la retirent.
        projet = config.Projet.charger(self.racine)
        projet.adaptateur["capabilities"] = {"tests": {
            "command": f"echo \"${{{verification.RAPIDE}:-absente}}\" >> {self.compte}", "fast": True}}
        verification.executer_etapes(projet, True, Rapport())
        with unittest.mock.patch.dict("os.environ", {verification.RAPIDE: "1"}):
            verification.executer_etapes(projet, False, Rapport())
        self.assertEqual(self.compte.read_text().split(), ["1", "absente"])

    def test_un_echec_ne_se_memorise_pas(self):
        self.code = 1
        self.lancer()
        self.assertTrue(self.lancer())
        self.assertEqual(self.fois(), 2)


class TestAutotestUneFois(unittest.TestCase):
    """L6 : `socle ci` lançait l'auto-test deux fois, dans la suite de tests
    de ce dépôt puis lui-même."""

    def test_la_suite_sait_que_l_autotest_suit(self):
        import argparse
        import os
        from unittest import mock

        from socle import selftest as autotest, cli, context as contexte

        vus = []
        with mock.patch.object(cli, "_projet", return_value=mock.Mock()), \
                mock.patch.object(cli, "_base", return_value=None), \
                mock.patch.object(verification, "executer_etapes",
                                  lambda *a, **k: vus.append(os.environ.get(autotest.ENSUITE))), \
                mock.patch.object(contexte, "executer", return_value=Rapport()), \
                mock.patch.object(contexte, "Contexte"), \
                mock.patch.object(autotest, "executer", return_value=Rapport()), \
                contextlib.redirect_stdout(io.StringIO()):
            cli.cmd_ci(argparse.Namespace(base=None, no_selftest=False))
            cli.cmd_ci(argparse.Namespace(base=None, no_selftest=True))
        self.assertEqual(vus, ["1", None])
        self.assertIsNone(os.environ.get(autotest.ENSUITE))

    def test_verify_rapide_passe_par_la_memoire_et_refaire_la_contourne(self):
        import argparse
        from unittest import mock

        from socle import cli, context as contexte

        appels = []
        with mock.patch.object(cli, "_projet", return_value=mock.Mock()), \
                mock.patch.object(cli, "_base", return_value=None), \
                mock.patch.object(verification, "etapes_rapides",
                                  lambda projet, rapport, flux=None, refaire=False: appels.append(("rapides", refaire))), \
                mock.patch.object(verification, "executer_etapes", lambda *a, **k: appels.append(("toutes", None))), \
                mock.patch.object(contexte, "executer", return_value=Rapport()), \
                mock.patch.object(contexte, "Contexte"), \
                contextlib.redirect_stdout(io.StringIO()):
            cli.cmd_verify(argparse.Namespace(base=None, fast=True, refaire=False))
            cli.cmd_verify(argparse.Namespace(base=None, fast=True, refaire=True))
            cli.cmd_verify(argparse.Namespace(base=None, fast=False, refaire=False))
        self.assertEqual(appels, [("rapides", False), ("rapides", True), ("toutes", None)])


class TestSansAucunTest(unittest.TestCase):
    """B-0026 : un projet qui commence n'a pas encore de test, et unittest
    le dit par un échec ; l'adaptateur le reconnaît, et `verify` avertit au
    lieu d'échouer."""

    def test_un_projet_sans_test_avertit(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-sans-test-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True)
        (racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(racine, "python", "@essai", source=MOTEUR)
        projet = config.Projet.charger(racine)
        for dossier in (None, "tests"):  # sans dossier, puis un dossier vide
            if dossier:
                (racine / dossier).mkdir()
                (racine / dossier / "__init__.py").write_text("")
            rapport = Rapport()
            verification.executer_etapes(projet, True, rapport)
            self.assertEqual(rapport.erreurs("verify.tests"), [], dossier)
            self.assertIn("aucun test trouvé", rapport.texte())
        # Un vrai échec reste un échec.
        (racine / "tests/test_x.py").write_text("import unittest\n\nclass T(unittest.TestCase):\n"
                                                "    def test_x(self):\n        self.fail('non')\n")
        rapport = Rapport()
        verification.executer_etapes(projet, True, rapport)
        self.assertTrue(rapport.erreurs("verify.tests"))


class TestSansCode(unittest.TestCase):
    """B-0089 : un projet neuf s'installe avant son premier fichier, et la
    commande de test de presque tout adaptateur y échoue (pas de manifeste,
    pas d'outil, aucun test). Sans aucun fichier source à lui, `verify`
    avertit sans lancer ses étapes ; le premier fichier les relance."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-sans-code-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        (self.racine / "README.md").write_text("# neuf\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python-pytest", "@essai", source=MOTEUR)
        self.projet = config.Projet.charger(self.racine)
        self.tests = self.projet.adaptateur["capabilities"]["tests"]

    def verifier(self) -> Rapport:
        rapport = Rapport()
        verification.executer_etapes(self.projet, True, rapport)
        return rapport

    def test_sans_code_les_etapes_avertissent_sans_tourner(self):
        # Une commande qui échoue toujours, comme cargo sans manifeste.
        self.tests["command"] = "python3 -c 'raise SystemExit(3)'"
        tiers = self.racine / ".claude/skills/bmad-essai/scripts/outil.py"
        tiers.parent.mkdir(parents=True)
        tiers.write_text("x = 1\n")
        with unittest.mock.patch.object(self.projet, "chemins_tiers", return_value=["**/skills/bmad-*/**"]):
            # Le moteur du socle et les fichiers tiers ne sont pas du code du projet.
            self.assertTrue(verification.sans_code(self.projet))
            rapport = self.verifier()
            self.assertEqual(rapport.erreurs(), [])
            self.assertIn("pas encore de code (aucun fichier `**/*.py`)", rapport.texte())
            # Le premier fichier relance les étapes.
            (self.racine / "app.py").write_text("x = 1\n")
            self.assertFalse(verification.sans_code(self.projet))
            self.assertTrue(self.verifier().erreurs("verify.tests"))

    def test_pytest_sans_aucun_test_avertit(self):
        (self.racine / "app.py").write_text("x = 1\n")
        self.tests["command"] = "python3 -c \"print('no tests ran in 0.01s'); raise SystemExit(5)\""
        rapport = self.verifier()
        self.assertEqual(rapport.erreurs("verify.tests"), [])
        self.assertIn("aucun test trouvé", rapport.texte())

    def test_un_outil_absent_se_dit_avec_les_commandes_de_la_ci(self):
        """B-0090 : le pilote n'avait que « No module named pytest », sans
        savoir que la CI l'installe, ni comment."""
        (self.racine / "app.py").write_text("x = 1\n")
        for commande in ("python3 -m module_qui_n_existe_pas", "commande-qui-n-existe-pas"):
            self.tests["command"] = commande
            texte = "\n".join(c.message for c in self.verifier().erreurs("verify.tests"))
            self.assertIn("l'outil manque à cet environnement ; la CI l'installe ainsi : "
                          "`python3 -m pip install pytest mutmut`", texte, commande)
        # Un échec ordinaire ne parle pas d'outil.
        self.tests["command"] = "python3 -c 'raise SystemExit(1)'"
        erreurs = self.verifier().erreurs("verify.tests")
        self.assertTrue(erreurs)
        self.assertNotIn("l'outil manque", erreurs[0].message)

    def test_commandes_ci_lit_les_etapes_de_chaque_adaptateur(self):
        # `npm ci` attend `package.json`, comme dans la CI (B-0179).
        (self.racine / "package.json").write_text("{}\n")
        attendu = {
            "python-pytest": ["python3 -m pip install pytest mutmut"],
            "javascript": ["npm ci"],
            "rust": ["rustup show active-toolchain || rustup toolchain install stable --profile minimal "
                     "--component rustfmt,clippy ; rustc --version && cargo --version"],
            "python": [],
        }
        for nom, commandes in attendu.items():
            texte = (MOTEUR / "socle/adapters" / f"{nom}.toml").read_text()
            self.projet.adaptateur["ci_setup"] = tomllib.loads(texte).get("ci_setup", "")
            self.assertEqual(verification.commandes_ci(self.projet), commandes, nom)

