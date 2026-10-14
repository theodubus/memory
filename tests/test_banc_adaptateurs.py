"""Le banc des adaptateurs (`bench/adapters.py`) : ses projets jetables
sont cohérents avec leurs adaptateurs, sans lancer les outils, que le banc
lui-même exige."""

import fnmatch
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "bench"))

import adapters as banc  # noqa: E402
from socle import installer as installeur, utils as outils  # noqa: E402


def adaptateur(nom: str) -> dict:
    return tomllib.loads((installeur.ADAPTATEURS / f"{nom}.toml").read_text(encoding="utf-8"))


class TestProjetsJetables(unittest.TestCase):
    def test_un_projet_par_adaptateur_nouveau(self):
        self.assertEqual(sorted(banc.LANGAGES), ["go", "java", "javascript", "php", "ruby"])

    def test_chaque_defaut_s_applique_a_son_projet(self):
        for nom, l in banc.LANGAGES.items():
            for fichier, avant, _ in (l.creux, l.desactive, l.attendu, l.fonction, l.bogue):
                with self.subTest(langage=nom, fichier=fichier):
                    self.assertIn(avant, l.fichiers[fichier])

    def test_l_adaptateur_se_deduit_du_projet(self):
        for nom, l in banc.LANGAGES.items():
            with self.subTest(langage=nom), tempfile.TemporaryDirectory() as d:
                for rel in l.fichiers:
                    (Path(d) / rel).parent.mkdir(parents=True, exist_ok=True)
                    (Path(d) / rel).write_text(l.fichiers[rel])
                self.assertEqual(installeur.detecter_langage(Path(d)), l.adaptateur)

    def test_le_code_est_dans_les_modules_et_le_test_de_regression_se_rejoue(self):
        for nom, l in banc.LANGAGES.items():
            caps = adaptateur(l.adaptateur)["capabilities"]
            with self.subTest(langage=nom):
                self.assertEqual(outils.filtrer([l.code], caps["mutation"]["modules"],
                                                caps["mutation"].get("modules_exclude", [])), [l.code])
                self.assertEqual(outils.filtrer([l.regression[0]], caps["regression"]["test_paths"]),
                                 [l.regression[0]])


class TestVerdictDuBanc(unittest.TestCase):
    def test_refuse_par_lit_la_ligne_de_synthese(self):
        sortie = "  tests.creux    ECHEC\n\nECHEC — 2 contrôle(s) : tests.creux, tests.attendus\n"
        self.assertTrue(banc.refuse_par(sortie, "tests.attendus"))
        self.assertFalse(banc.refuse_par(sortie, "tests.regression"))
        self.assertFalse(banc.refuse_par("TOUT PASSE\n", "tests.creux"))


if __name__ == "__main__":
    unittest.main()
