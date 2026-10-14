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


class TestCouverture(unittest.TestCase):
    """`mutation.couverture` : un module qui porte du code est au cliquet ; un
    module « à mesurer » n'y est qu'un avertissement (B-0034, P1)."""

    def verifier(self, caps, sources):
        from types import SimpleNamespace

        from socle.checks_tests import couverture_mutation
        from socle.report import Rapport

        p = projet(caps)
        p.adaptateur["capabilities"]["mutation"].update(modules=["src/**/*.rs"], has_code=r"\bfn\b")
        ctx = SimpleNamespace(projet=p, fichiers=list(sources), lire=sources.get)
        r = Rapport()
        couverture_mutation(ctx, r)
        return r

    def test_hors_du_cliquet_casse(self):
        r = self.verifier({}, {"src/eval.rs": "fn f() {}\n"})
        self.assertIn("module hors du cliquet", r.erreurs()[0].message)

    def test_a_mesurer_avertit(self):
        r = self.verifier({"src/eval.rs": {"pending": True}}, {"src/eval.rs": "fn f() {}\n"})
        self.assertTrue(r.reussi)
        self.assertIn("module à mesurer", r.constats[0].message)

    def test_sans_code_rien(self):
        self.assertEqual(self.verifier({}, {"src/vide.rs": "// rien\n"}).constats, [])


class TestAMesurer(unittest.TestCase):
    """B-0034, P1 : un module « à mesurer » n'a pas de plafond ; le verdict
    dit son compte, et `poser` l'écrit dans les garde-fous."""

    GARDE_FOUS = '[mutation.caps]\n"src/eval.rs" = { pending = true }\n"src/tt.rs" = { pending = true }\n'

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp())
        out = self.dossier / "eval/mutants.out"
        out.mkdir(parents=True)
        (out / "missed.txt").write_text("src/eval.rs:10:5: replace + with -\n")
        (out / "caught.txt").write_text("src/tt.rs:3:1: replace y\n")
        (self.dossier / ".socle").mkdir()
        (self.dossier / ".socle/guardrails.toml").write_text(self.GARDE_FOUS)

    def tearDown(self):
        shutil.rmtree(self.dossier)

    def projet(self):
        import tomllib

        p = projet(tomllib.loads((self.dossier / ".socle/guardrails.toml").read_text())["mutation"]["caps"])
        p.racine = self.dossier
        return p

    def test_un_module_a_mesurer_ne_casse_pas(self):
        r = mutation.verdict(self.projet(), self.dossier)
        self.assertTrue(r.reussi)
        self.assertTrue(any("src/eval.rs : à mesurer — 1 survivant(s)" in c.message for c in r.constats))

    def test_poser_ecrit_le_plafond_mesure(self):
        mutation.verdict(self.projet(), self.dossier, poser=True)
        texte = (self.dossier / ".socle/guardrails.toml").read_text()
        self.assertIn('"src/tt.rs" = { max = 0 }', texte)
        self.assertRegex(texte, r'"src/eval.rs" = \{ max = 1, reason = "mesuré le [\d-]+ : 1 survivant\(s\)" \}')
        self.assertTrue(mutation.verdict(self.projet(), self.dossier).reussi)

    def test_cmd_mutation_verdict_avec_poser(self):
        import argparse
        import io
        from contextlib import redirect_stdout
        from unittest import mock

        from socle import cli

        with mock.patch.object(cli, "_projet", return_value=self.projet()), redirect_stdout(io.StringIO()) as flux:
            code = cli.cmd_mutation_verdict(argparse.Namespace(results=str(self.dossier), poser=True))
        self.assertEqual(code, 0, flux.getvalue())
        self.assertIn("plafond posé", flux.getvalue())
        self.assertIn('"src/tt.rs" = { max = 0 }', (self.dossier / ".socle/guardrails.toml").read_text())

    def test_poser_plafonds_ne_touche_que_les_modules_a_mesurer(self):
        gf = self.dossier / ".socle/guardrails.toml"
        gf.write_text(self.GARDE_FOUS + '"src/x.rs" = { max = 4, reason = "équivalents" }\n')
        mutation.poser_plafonds(self.projet(), {"src/eval.rs": 0, "src/x.rs": 0})
        self.assertIn('"src/x.rs" = { max = 4, reason = "équivalents" }', gf.read_text())
        self.assertIn('"src/eval.rs" = { max = 0 }', gf.read_text())

    def test_poser_les_autres_formes_de_cle(self):
        """Relevé de la passe de recul, F : une clé entre guillemets simples,
        ou une table, était annoncée posée sans être écrite."""
        import tomllib

        gf = self.dossier / ".socle/guardrails.toml"
        gf.write_text("[mutation.caps]\n'src/eval.rs' = { pending = true }\n\n"
                      '[mutation.caps."src/tt.rs"]\npending = true\nreason = "pas encore balayé"\n')
        self.assertEqual(mutation.poser_plafonds(self.projet(), {"src/eval.rs": 1, "src/tt.rs": 0}), [])
        caps = tomllib.loads(gf.read_text())["mutation"]["caps"]
        self.assertEqual(caps["src/eval.rs"]["max"], 1)
        self.assertEqual(caps["src/tt.rs"], {"max": 0})

    def test_un_plafond_non_ecrit_est_dit(self):
        gf = self.dossier / ".socle/guardrails.toml"
        gf.write_text('[mutation]\ncaps = { "src/eval.rs" = { pending = true }, "src/tt.rs" = { pending = true } }\n')
        self.assertEqual(sorted(mutation.poser_plafonds(self.projet(), {"src/eval.rs": 1, "src/tt.rs": 0})),
                         ["src/eval.rs", "src/tt.rs"])
        r = mutation.verdict(self.projet(), self.dossier, poser=True)
        self.assertTrue(any("plafond annoncé mais non écrit" in c.message for c in r.erreurs()))


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

    def test_un_module_qui_commence_par_x(self):
        """Relevé de la passe de recul, F : `pkg.x_util.x_f` comptait pour
        `pkg`, coupé au premier `.x_`."""
        (self.dossier / "mutmut-results.txt").write_text("    pkg.x_util.x_f__mutmut_1: survived\n")
        res = mutation.lire_mutmut(self.dossier)
        self.assertEqual(res["pkg/x_util.py"]["survivants"], 1)
        self.assertNotIn("pkg.py", res)


if __name__ == "__main__":
    unittest.main()
