"""Le banc de la revue adversariale (B-0124) : ses lots passent leurs
tests, son dossier porte la décision, et son juge reconnaît un défaut
trouvé. Le relecteur, un agent réel et payant, ne tourne pas ici."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "bench"))

import review as banc  # noqa: E402

from socle import config, review as revue  # noqa: E402


class TestLots(unittest.TestCase):
    def test_chaque_lot_passe_ses_tests_et_son_dossier_porte_la_decision(self):
        with tempfile.TemporaryDirectory() as d:
            for fautif in (True, False):
                projet = banc.preparer(Path(d), fautif)
                r = subprocess.run([sys.executable, "-m", "unittest", "-q"], cwd=projet, capture_output=True,
                                   text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
                dossier = revue.dossier(config.Projet(racine=projet), "main")
                self.assertIn("À partir de 10 unités, le total reçoit 5 % de remise.", dossier)
                self.assertIn("- [x] la remise s'applique à partir de 10 unités", dossier)
                self.assertIn("if quantite > 10:" if fautif else "if quantite >= 10:", dossier)


class TestDefauts(unittest.TestCase):
    def test_chaque_defaut_est_dans_le_lot_fautif_et_pas_dans_le_lot_sain(self):
        """Les tests du lot fautif passent : ses défauts, que la revue doit
        trouver, ne se voient qu'à la lecture d'ADR-0001."""
        import runpy

        with tempfile.TemporaryDirectory() as d:
            fautif = runpy.run_path(str(banc.preparer(Path(d), True) / "prix.py"))
            sain = runpy.run_path(str(banc.preparer(Path(d), False) / "prix.py"))
        total, formater = fautif["total"], fautif["formater"]
        self.assertEqual(total(100, 10), 1000)  # seuil : pas de remise à 10 unités
        self.assertEqual(total(13, 11), 136)  # arrondi : round(135,85), pas le centime inférieur
        self.assertEqual(total(100, 0), 0)  # nulle : acceptée
        self.assertEqual(formater(105), "1,5 €")  # centimes : le zéro perdu
        self.assertEqual(sain["total"](100, 10), 950)
        self.assertEqual(sain["total"](13, 11), 135)
        with self.assertRaises(ValueError):
            sain["total"](100, 0)
        self.assertEqual(sain["formater"](105), "1,05 €")


class TestJuge(unittest.TestCase):
    def test_un_constat_trouve_un_defaut_par_son_indice_ou_sa_ligne(self):
        sortie = ("1. `prix.py:6` : la remise exige `quantite > 10`, ADR-0001 dit à partir de 10.\n"
                  "2. prix.py, ligne 13 : le format perd le zéro.\n"
                  "3. Le nom `brut` est vague.\n")
        self.assertEqual(len(banc.constats(sortie)), 3)
        jugement = banc.juger(sortie)
        self.assertEqual(jugement["trouves"], ["centimes", "seuil"])
        self.assertEqual(jugement["constats"], 3)
        self.assertEqual(jugement["autres"], ["3. Le nom `brut` est vague."])

    def test_aucun_constat(self):
        self.assertEqual(banc.juger("Aucun constat."), {"trouves": [], "constats": 0, "autres": []})


if __name__ == "__main__":
    unittest.main()
