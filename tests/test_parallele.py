"""Le lanceur de la suite sur plusieurs cœurs, `tests/parallele.py` (B-0257,
T-0044) : sur un petit dossier de tests factice, il rend 1 quand un module
échoue ou ne s'importe pas, imprime leur sortie puis un bilan, transmet
l'environnement et lance les modules en même temps."""

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from tests import parallele

LANCEUR = Path(__file__).resolve().parent / "parallele.py"
RACINE = LANCEUR.parent.parent

PASSE = """
import unittest

class T(unittest.TestCase):
    def test_passe(self):
        self.assertEqual(1 + 1, 2)
"""

SAUTE = """
import unittest

class T(unittest.TestCase):
    @unittest.skip("sauté exprès")
    def test_saute(self):
        self.fail("jamais lancé")
"""

ECHOUE = """
import unittest

class T(unittest.TestCase):
    def test_echoue(self):
        self.assertEqual("valeur-obtenue", "valeur-factice-attendue")
"""

CASSE = """
import module_factice_qui_n_existe_pas
"""

ENVIRONNEMENT = """
import os
import unittest
from pathlib import Path

class T(unittest.TestCase):
    def test_environnement_et_dossier(self):
        self.assertEqual(os.environ.get("SOCLE_RAPIDE"), "1")
        self.assertEqual(Path.cwd().resolve(), Path(__file__).resolve().parent.parent)
"""

# Chacun pose sa marque, puis attend celle de l'autre : les deux ne passent
# que s'ils tournent en même temps.
RENDEZ_VOUS = """
import time
import unittest
from pathlib import Path

ICI = Path(__file__).resolve().parent

class T(unittest.TestCase):
    def test_rendez_vous(self):
        (ICI / "{moi}.marque").touch()
        limite = time.monotonic() + 60
        while not (ICI / "{autre}.marque").exists():
            self.assertLess(time.monotonic(), limite, "l'autre module ne tourne pas en même temps")
            time.sleep(0.05)
"""


class TestLanceurParallele(unittest.TestCase):

    def setUp(self):
        self.racine = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.racine / "tests").mkdir()
        (self.racine / "tests/__init__.py").write_text("", encoding="utf-8")

    def ecrire(self, nom: str, texte: str):
        chemin = self.racine / "tests" / nom
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(textwrap.dedent(texte), encoding="utf-8")

    def lancer(self, *options: str, **env: str) -> subprocess.CompletedProcess:
        environnement = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        environnement.pop("SOCLE_RAPIDE", None)
        environnement.update(env)
        return subprocess.run([sys.executable, str(LANCEUR), "--root", str(self.racine), *options],
                              capture_output=True, text=True, encoding="utf-8", env=environnement,
                              timeout=300)

    def test_un_module_en_echec_et_un_qui_ne_s_importe_pas_rendent_1_et_impriment_leur_sortie(self):
        self.ecrire("test_passe.py", PASSE)
        self.ecrire("test_echoue.py", ECHOUE)
        self.ecrire("test_casse.py", CASSE)
        p = self.lancer("-j", "2")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("=== tests.test_echoue : échec (code 1,", p.stdout)
        self.assertIn("valeur-factice-attendue", p.stdout)
        self.assertIn("=== tests.test_casse : échec (code 1,", p.stdout)
        self.assertIn("module_factice_qui_n_existe_pas", p.stdout)
        self.assertNotIn("tests.test_passe", p.stdout)
        derniere = p.stdout.rstrip().splitlines()[-1]
        self.assertTrue(derniere.startswith("modules : 3 · en échec : 2 (test_casse, test_echoue) · tests : 3 "),
                        derniere)
        self.assertIn("sur 2 fils", derniere)
        self.assertIn("les plus longs : ", derniere)

    def test_une_suite_qui_passe_rend_0_et_n_imprime_que_le_bilan(self):
        self.ecrire("test_passe.py", PASSE)
        self.ecrire("test_saute.py", SAUTE)
        p = self.lancer("-j", "1")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        lignes = p.stdout.strip().splitlines()
        self.assertEqual(len(lignes), 1, p.stdout)
        self.assertTrue(lignes[0].startswith("modules : 2 · en échec : 0 · tests : 2 (sautés : 1) · mur : "),
                        lignes[0])
        self.assertIn("sur 1 fils", lignes[0])

    def test_un_sous_dossier_de_tests_se_lance_aussi(self):
        self.ecrire("sous/__init__.py", "")
        self.ecrire("sous/test_echoue.py", ECHOUE)
        p = self.lancer()
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("=== tests.sous.test_echoue : échec", p.stdout)

    def test_chaque_module_recoit_l_environnement_et_tourne_depuis_la_racine(self):
        self.ecrire("test_environnement.py", ENVIRONNEMENT)
        self.assertEqual(self.lancer(SOCLE_RAPIDE="1").returncode, 0)
        sans = self.lancer()
        self.assertEqual(sans.returncode, 1, sans.stdout)
        self.assertIn("=== tests.test_environnement : échec", sans.stdout)

    def test_les_modules_tournent_en_meme_temps(self):
        self.ecrire("test_un.py", RENDEZ_VOUS.format(moi="un", autre="deux"))
        self.ecrire("test_deux.py", RENDEZ_VOUS.format(moi="deux", autre="un"))
        p = self.lancer("-j", "2")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_aucun_fichier_de_tests_rend_1(self):
        p = self.lancer()
        self.assertEqual(p.returncode, 1)
        self.assertIn("rien à lancer", p.stderr)

    def test_un_nombre_de_fils_nul_est_refuse(self):
        self.ecrire("test_passe.py", PASSE)
        p = self.lancer("-j", "0")
        self.assertEqual(p.returncode, 2)
        self.assertIn("-j attend un entier positif", p.stderr)


class TestOrdreEtBilan(unittest.TestCase):

    def test_modules_donne_les_plus_gros_fichiers_d_abord_puis_par_nom(self):
        with tempfile.TemporaryDirectory() as d:
            racine = Path(d)
            (racine / "tests/sous").mkdir(parents=True)
            (racine / "tests/test_petit.py").write_text("#", encoding="utf-8")
            (racine / "tests/test_b.py").write_text("#" * 50, encoding="utf-8")
            (racine / "tests/test_a.py").write_text("#" * 50, encoding="utf-8")
            (racine / "tests/sous/test_gros.py").write_text("#" * 500, encoding="utf-8")
            (racine / "tests/aide.py").write_text("#" * 900, encoding="utf-8")
            self.assertEqual(parallele.modules(racine),
                             ["tests.sous.test_gros", "tests.test_a", "tests.test_b", "tests.test_petit"])

    def test_bilan_compte_le_resume_de_unittest_et_non_ce_qu_un_test_imprime(self):
        imprime = "Ran 99 tests in 0.000s\nOK (skipped=7)\n"
        resume = "\n----------------------------------------------------------------------\n" \
                 "Ran 3 tests in 0.010s\n\nOK (skipped=1)\n"
        resultats = [parallele.Resultat("tests.test_a", 0, 12.4, imprime + resume),
                     parallele.Resultat("tests.test_b", 1, 30.6, "Ran 2 tests in 0.1s\n\nFAILED (failures=1)\n")]
        texte = parallele.bilan(resultats, 31.2, 4)
        self.assertEqual(texte, "modules : 2 · en échec : 1 (test_b) · tests : 5 (sautés : 1) · mur : 31 s "
                                "sur 4 fils · les plus longs : test_b 31 s, test_a 12 s")


# Les modules les plus longs de la suite, que chacun met de côté lui-même
# pendant les étapes rapides (T-0218, D-0237) : la CI, qui lance la suite
# sans `SOCLE_RAPIDE`, les joue toujours.
LENTS = ["tests.test_hooks", "tests.test_installeur", "tests.test_adaptateurs_multiples",
         "tests.test_adoption", "tests.test_attendus"]

# Charge chaque module nommé et imprime, par module : ses tests, ceux que leur
# classe met de côté et, quand `SOCLE_RAPIDE` est posée, ceux que unittest
# lance puis ceux qu'il saute. Un module dont une classe n'est pas mise de
# côté ne se lance pas (-1 -1) : il tournerait pour de bon, des minutes.
SONDE = """
import io, os, sys, unittest
def cas(suite):
    for t in suite:
        yield from cas(t) if isinstance(t, unittest.TestSuite) else [t]
for nom in sys.argv[1:]:
    suite = unittest.defaultTestLoader.loadTestsFromName(nom)
    tous = list(cas(suite))
    ligne = [nom, len(tous), sum(bool(getattr(type(t), "__unittest_skip__", False)) for t in tous)]
    if os.environ.get("SOCLE_RAPIDE"):
        r = unittest.TextTestRunner(stream=io.StringIO()).run(suite) if ligne[2] == len(tous) else None
        ligne += [r.testsRun, len(r.skipped)] if r else [-1, -1]
    print(*ligne)
"""


class TestModulesLents(unittest.TestCase):
    """Les modules les plus longs se mettent de côté quand `SOCLE_RAPIDE` est
    posée, chacune de leurs classes avec sa raison écrite, et tournent sans
    elle : la vérification rapide tient sous son seuil, la CI les joue."""

    def sonder(self, **env: str) -> dict[str, list[int]]:
        environnement = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        environnement.pop("SOCLE_RAPIDE", None)
        environnement.update(env)
        sortie = subprocess.run([sys.executable, "-c", SONDE, *LENTS], cwd=RACINE, capture_output=True,
                                text=True, encoding="utf-8", env=environnement, timeout=300, check=True).stdout
        return {nom: [int(n) for n in nombres] for nom, *nombres in (l.split() for l in sortie.splitlines())}

    def test_un_module_lent_est_mis_de_cote_pendant_les_etapes_rapides_et_lance_sans_elles(self):
        rapides, completes = self.sonder(SOCLE_RAPIDE="1"), self.sonder()
        self.assertEqual(sorted(rapides), sorted(LENTS))
        for nom in LENTS:
            with self.subTest(nom):
                tests, marques, lances, sautes = rapides[nom]
                self.assertGreater(tests, 0)
                self.assertEqual([marques, lances, sautes], [tests, tests, tests])
                self.assertEqual(completes[nom], [tests, 0])


if __name__ == "__main__":
    unittest.main()
