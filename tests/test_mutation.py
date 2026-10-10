import shutil
import tempfile
import unittest
from pathlib import Path

from socle import config, mutation


def projet(caps, parser="cargo-mutants"):
    p = config.Projet(racine=Path("."))
    p.adaptateur = {"capabilities": {"mutation": {"command": "x", "parser": parser}}}
    p.garde_fous = {"mutation": {"caps": caps}}
    return p


class TestVerdict(unittest.TestCase):
    """Les cas fabriqués de `chess:.github/mutation-verdict-test.sh`, rejoués
    sur le verdict générique."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp())
        out = self.dossier / "eval/mutants.out"
        out.mkdir(parents=True)
        (out / "missed.txt").write_text("src/eval.rs:10:5: replace + with -\nsrc/eval.rs:12:5: replace > with >=\n")
        (out / "caught.txt").write_text("src/eval.rs:20:5: replace x\nsrc/tt.rs:3:1: replace y\n")

    def tearDown(self):
        shutil.rmtree(self.dossier)

    def test_hausse_casse(self):
        r = mutation.verdict(projet({"src/eval.rs": {"max": 1}, "src/tt.rs": {"max": 0}}), self.dossier)
        self.assertFalse(r.reussi)
        self.assertIn("2 survivant(s) pour un plafond de 1", r.erreurs()[0].message)

    def test_egalite_passe_et_baisse_signalee(self):
        r = mutation.verdict(projet({"src/eval.rs": {"max": 2}, "src/tt.rs": {"max": 1}}), self.dossier)
        self.assertTrue(r.reussi)
        self.assertTrue(any("resserrer" in c.message for c in r.constats))

    def test_module_jamais_balaye_casse(self):
        r = mutation.verdict(projet({"src/eval.rs": {"max": 2}, "src/see.rs": {"max": 0}}), self.dossier)
        self.assertEqual([c.message.split(" :")[0] for c in r.erreurs()], ["src/see.rs"])

    def test_plafond_vide_casse(self):
        self.assertFalse(mutation.verdict(projet({}), self.dossier).reussi)

    def test_lecteur_inconnu_casse(self):
        self.assertFalse(mutation.verdict(projet({"src/eval.rs": {"max": 9}}, parser="?"), self.dossier).reussi)


if __name__ == "__main__":
    unittest.main()


class TestMutmut(unittest.TestCase):
    """La sortie réelle de `mutmut results --all true` sur le projet jetable
    du jalon 6 (`tests/donnees/mutmut-results.txt`), puis les cas qu'il
    n'avait pas : statuts rares, méthodes, paquets, disposition `src/`."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp())
        shutil.copy(Path(__file__).parent / "donnees/mutmut-results.txt", self.dossier / "mutmut-results.txt")

    def tearDown(self):
        shutil.rmtree(self.dossier)

    def test_sortie_reelle(self):
        c = mutation.lire_mutmut(self.dossier)["romains/conversion.py"]
        self.assertEqual((c["attrapes"], c["survivants"], c["expires"]), (25, 3, 6))
        self.assertTrue(mutation.verdict(projet({"romains/conversion.py": {"max": 3}}, "mutmut"), self.dossier).reussi)
        r = mutation.verdict(projet({"romains/conversion.py": {"max": 2}}, "mutmut"), self.dossier)
        self.assertIn("3 survivant(s) pour un plafond de 2", r.erreurs()[0].message)

    def test_un_mutant_non_prouve_attrape_compte_comme_survivant(self):
        (self.dossier / "autre").mkdir()
        (self.dossier / "autre/mutmut-results.txt").write_text(
            "    calc.x_f__mutmut_1: not checked\n"
            "    calc.x_f__mutmut_2: check was interrupted by user\n"
            "    calc.x_f__mutmut_3: un statut que mutmut n'avait pas\n"
            "    calc.x_f__mutmut_4: caught by type check\n"
            "    calc.x_f__mutmut_5: segfault\n")
        c = mutation.lire_mutmut(self.dossier)["calc.py"]
        self.assertEqual((c["survivants"], c["attrapes"], c["expires"]), (3, 1, 1))

    def test_methodes_paquets_et_disposition_src(self):
        (self.dossier / "mutmut-results.txt").write_text(
            "    romains.xǁConvertisseurǁconvertir__mutmut_1: survived\n"
            "    romains.x_aide__mutmut_1: killed\n")
        res = mutation.lire_mutmut(self.dossier)
        self.assertEqual(res["romains.py"]["survivants"], 1)
        self.assertEqual(res["romains/__init__.py"]["attrapes"], 1)
        self.assertEqual(res["src/romains/__init__.py"]["survivants"], 1)
