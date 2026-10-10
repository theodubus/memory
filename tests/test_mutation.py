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
