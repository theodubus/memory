"""Les fichiers d'un outil tiers (ADR-0031, B-0068) : déclarés une fois dans
les garde-fous, aucun contrôle ne les juge ; un motif qui couvrirait le
socle, la mémoire ou la politique est écarté et signalé."""

import contextlib
import io
import os
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

from socle import config, context as contexte, installer as installeur
from socle.templates import gabarit

MOTEUR = Path(__file__).resolve().parent.parent / "engine"

def depot(fichiers: dict[str, str]) -> Path:
    racine = Path(tempfile.mkdtemp(prefix="socle-tiers-"))
    env = {**os.environ, "HOME": str(racine), "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True, env=env)
    for chemin, texte in fichiers.items():
        p = racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=racine, check=True, env=env)
    return racine


def installer(racine: Path) -> str:
    sortie = io.StringIO()
    with contextlib.redirect_stdout(sortie):
        installeur.installer(racine, "python", "@essai", source=MOTEUR)
    return sortie.getvalue()


def projet(motifs, protege=(".github/workflows/socle.yml",)) -> config.Projet:
    return config.Projet(racine=Path("/nulle-part"), garde_fous={"thirdparty": {"paths": list(motifs)}},
                         politique={"protected": {"paths": list(protege)}})


class TestChemins(unittest.TestCase):
    def test_chemins_tiers_garde_les_motifs_d_un_outil(self):
        self.assertEqual(projet(["_bmad/**", "**/skills/bmad-*/**"]).chemins_tiers(),
                         ["_bmad/**", "**/skills/bmad-*/**"])

    def test_chemins_tiers_ecarte_ce_qui_couvrirait_le_socle(self):
        p = projet(["_bmad/**", "memory/**", ".socle/**", "**", "AGENTS.md", ".github/**"])
        self.assertEqual(p.chemins_tiers(), ["_bmad/**"])
        self.assertEqual(p.erreurs_tiers(), ["memory/**", ".socle/**", "**", "AGENTS.md", ".github/**"])

    def test_hors_tiers_retire_les_fichiers_de_l_outil(self):
        p = projet(["_bmad/**", "**/skills/bmad-*/**"])
        self.assertEqual(p.hors_tiers(["calc.py", "_bmad/scripts/outil.py", ".claude/skills/bmad-build/SKILL.md",
                                       ".claude/skills/socle-x/SKILL.md", "_bmad-output/spec.md"]),
                         ["calc.py", ".claude/skills/socle-x/SKILL.md", "_bmad-output/spec.md"])

    def test_sans_chemins_tiers_rien_ne_change(self):
        self.assertEqual(projet([]).hors_tiers(["a", "b"]), ["a", "b"])

    def test_un_motif_mal_place_met_la_configuration_en_erreur(self):
        p = projet(["memory/**"])
        p.chemins = config.FORMAT_ACTUEL
        rapport = contexte.executer(contexte.Contexte(p, etage="ci", base=None), ids=["memoire.format"])
        self.assertIn("config", rapport.controles_en_echec())
        self.assertIn("memory/**", "\n".join(c.message for c in rapport.constats))


class TestDetection(unittest.TestCase):
    def test_declarer_tiers_remplit_la_liste_du_gabarit(self):
        texte = installeur.declarer_tiers(gabarit("guardrails.toml", "fr"), ["_bmad/**"])
        gf = tomllib.loads(texte)
        self.assertEqual(gf["thirdparty"]["paths"], ["_bmad/**"])
        self.assertEqual(gf["nocopy"]["min_chars"], 200)
        self.assertEqual(installeur.declarer_tiers(texte, ["_bmad/**"]), texte)

    def test_declarer_tiers_ajoute_la_table_qui_manque(self):
        texte = installeur.declarer_tiers('[nocopy]\nmin_chars = 200\n', ["_bmad/**", "x/**"])
        self.assertEqual(tomllib.loads(texte)["thirdparty"]["paths"], ["_bmad/**", "x/**"])
        texte = installeur.declarer_tiers(texte, ["x/**", "y/**"])
        self.assertEqual(tomllib.loads(texte)["thirdparty"]["paths"], ["_bmad/**", "x/**", "y/**"])


class TestContexte(unittest.TestCase):
    def test_les_changes_et_les_fichiers_du_contexte_ignorent_l_outil(self):
        racine = depot({"calc.py": "X = 1\n"})
        installer(racine)
        env = {**os.environ, "HOME": str(racine), "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "a",
               "GIT_AUTHOR_EMAIL": "a@b", "GIT_COMMITTER_NAME": "a", "GIT_COMMITTER_EMAIL": "a@b"}
        subprocess.run(["git", "add", "-A"], cwd=racine, check=True, env=env)
        subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "base"], cwd=racine, check=True, env=env)
        gf = racine / ".socle/guardrails.toml"
        gf.write_text(installeur.declarer_tiers(gf.read_text(encoding="utf-8"), ["_bmad/**"]), encoding="utf-8")
        (racine / "_bmad").mkdir()
        (racine / "_bmad/outil.py").write_text("def aide(x):\n    return x\n", encoding="utf-8")
        (racine / "calc.py").write_text("X = 2\n", encoding="utf-8")
        ctx = contexte.Contexte(config.Projet.charger(racine), etage="ci", base="HEAD")
        self.assertNotIn("_bmad/outil.py", ctx.changes)
        self.assertIn("calc.py", ctx.changes)
        self.assertNotIn("_bmad/outil.py", ctx.fichiers)


class TestCommitsTiers(unittest.TestCase):
    """B-0169 : le commit d'une autre session d'agent, sans les hooks du
    socle, qui ne touche que des chemins déclarés tiers, n'est pas jugé ; un
    commit qui touche aussi un fichier du projet l'est en entier."""

    AGENT = "Co-Authored-By: Claude <noreply@anthropic.com>"

    def setUp(self):
        self.racine = depot({"calc.py": "X = 1\n"})
        installer(self.racine)
        self.env = {**os.environ, "HOME": str(self.racine), "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "a",
                    "GIT_AUTHOR_EMAIL": "a@b", "GIT_COMMITTER_NAME": "a", "GIT_COMMITTER_EMAIL": "a@b"}
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(installeur.declarer_tiers(gf.read_text(encoding="utf-8"), ["ui/**"]), encoding="utf-8")
        self.base = self.commit("Le projet, son interface déclarée tierce")

    def commit(self, message: str) -> str:
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True, env=self.env)
        subprocess.run(["git", "commit", "-q", "--no-verify", "--allow-empty", "-m", message], cwd=self.racine,
                       check=True, env=self.env)
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.racine, check=True, env=self.env,
                              capture_output=True, text=True).stdout.strip()

    def ecrire(self, chemin: str, texte: str):
        p = self.racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")

    def test_commits_du_projet_ecarte_ceux_qui_ne_touchent_que_des_tiers(self):
        self.ecrire("ui/app.py", "def rendu(x):\n    return x\n")
        seul = self.commit(f"fix: l'interface\n\n{self.AGENT}")
        self.ecrire("ui/app.py", "def rendu(x):\n    return 2 * x\n")
        self.ecrire("calc.py", "X = 2\n")
        mixte = self.commit(f"L'interface et le calcul\n\n{self.AGENT}")
        vide = self.commit(f"Rien\n\n{self.AGENT}")
        projet = config.Projet.charger(self.racine)
        ctx = contexte.Contexte(projet, etage="ci", base=self.base)
        self.assertEqual([c["sha"] for c in ctx.commits], [seul, mixte, vide])
        self.assertEqual([c["sha"] for c in ctx.commits_du_projet], [mixte, vide])
        self.assertTrue(contexte.ne_touche_que_des_tiers(projet, self.racine, ctx.commits[0]))
        self.assertFalse(contexte.ne_touche_que_des_tiers(projet, self.racine, ctx.commits[1]))
        self.assertFalse(contexte.ne_touche_que_des_tiers(projet, self.racine, ctx.commits[2]))

    def test_la_trace_des_hooks_ne_juge_pas_le_commit_qui_ne_touche_que_des_tiers(self):
        self.ecrire("ui/app.py", "def rendu(x):\n    return x\n")
        seul = self.commit(f"L'interface\n\n{self.AGENT}")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base)
        self.assertEqual(contexte.executer(ctx, ids=["hooks.trace"]).erreurs("hooks.trace"), [])
        self.ecrire("ui/app.py", "def rendu(x):\n    return 2 * x\n")
        self.ecrire("calc.py", "X = 2\n")
        mixte = self.commit(f"L'interface et le calcul\n\n{self.AGENT}")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base)
        rapport = contexte.executer(ctx, ids=["hooks.trace"])
        erreurs = "\n".join(c.message for c in rapport.erreurs("hooks.trace"))
        self.assertIn(mixte[:10], erreurs)
        self.assertNotIn(seul[:10], erreurs)


    def test_une_dispense_portee_par_un_commit_tiers_n_est_ni_jugee_ni_lue(self):
        """Illisible, elle ne fait pas échouer la CI ; valable, elle ne
        dispense pas une fonction du projet de même nom."""
        from socle import checks_tests as controles_tests
        from socle.report import Rapport

        self.ecrire("ui/app.py", "def rendu(x):\n    return x\n")
        self.commit(f"L'interface\n\nDispense-test: rendu\n{self.AGENT}")
        self.ecrire("ui/app.py", "def calcul(x):\n    return x\n")
        self.commit(f"L'interface encore\n\nDispense-test: calcul — une raison assez longue\n{self.AGENT}")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base)
        r = Rapport()
        self.assertEqual(controles_tests.dispenses_tests(ctx, r), set())
        self.assertEqual(r.erreurs("tests.code-teste"), [])

if __name__ == "__main__":
    unittest.main()
