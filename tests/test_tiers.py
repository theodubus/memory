"""Les fichiers d'un outil tiers (ADR-0031, B-0068) : déclarés une fois dans
les garde-fous, aucun contrôle ne les juge ; l'installeur déclare ceux des
outils qu'il reconnaît ; un motif qui couvrirait le socle, la mémoire ou la
politique est écarté et signalé."""

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

# Ce que BMAD Method pose dans un projet, en réduction : un script sans test,
# un test sans assertion, un skill qui écrit `file:line` dans sa prose, et
# deux skills qui partagent un paragraphe.
PARAGRAPHE = ("Chaque étape se lit en entier avant d'agir, et l'on ne charge jamais deux fichiers d'étape à la "
              "fois : la suite se découvre au fil du travail, comme le veut l'architecture des workflows.\n")
FICHIERS_BMAD = {
    "_bmad/scripts/outil.py": "def aide(x):\n    return x\n",
    ".claude/skills/bmad-build/SKILL.md": "# Build\n\nCiter chaque constat par `file:line`.\n\n" + PARAGRAPHE,
    ".claude/skills/bmad-review/SKILL.md": "# Review\n\n" + PARAGRAPHE,
    ".claude/skills/bmad-review/scripts/tests/test_revue.py": "def test_rien():\n    pass\n",
}


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
    def test_outils_tiers_reconnait_bmad_par_son_dossier(self):
        racine = depot({"_bmad/config.toml": ""})
        self.assertEqual([n for n, _ in installeur.outils_tiers(racine)], ["BMAD Method"])

    def test_outils_tiers_reconnait_bmad_par_ses_skills(self):
        racine = depot({".agents/skills/bmad-prd/SKILL.md": ""})
        self.assertEqual([n for n, _ in installeur.outils_tiers(racine)], ["BMAD Method"])

    def test_outils_tiers_ne_voit_rien_sans_outil(self):
        racine = depot({"calc.py": "", ".claude/skills/socle-demande/SKILL.md": ""})
        self.assertEqual(installeur.outils_tiers(racine), [])

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


class TestInstallation(unittest.TestCase):
    def test_une_installation_avec_bmad_declare_ses_fichiers_et_passe(self):
        racine = depot({"calc.py": "def double(x):\n    return 2 * x\n",
                        "tests/__init__.py": "",
                        "tests/test_calc.py": "import unittest\n\nfrom calc import double\n\n\n"
                                              "class T(unittest.TestCase):\n    def test_double(self):\n"
                                              "        self.assertEqual(double(2), 4)\n",
                        **FICHIERS_BMAD})
        sortie = installer(racine)
        self.assertIn("BMAD Method", sortie)
        p = config.Projet.charger(racine)
        self.assertEqual(p.chemins_tiers(), ["_bmad/**", "**/skills/bmad-*/**"])
        rapport = contexte.executer(contexte.Contexte(p, etage="ci", base=None))
        for c in ("docs.copie", "memoire.references", "tests.creux", "tests.code-teste"):
            self.assertNotIn(c, rapport.controles_en_echec(), c)

    def test_garde_fous_initiaux_laissent_l_outil_hors_du_cliquet_de_mutation(self):
        racine = depot({"calc.py": "def double(x):\n    return 2 * x\n", **FICHIERS_BMAD})
        adaptateur = '[capabilities.mutation]\ncommand = "muter"\nmodules = ["**/*.py"]\n'
        caps = tomllib.loads(installeur.garde_fous_initiaux(racine, adaptateur))["mutation"]["caps"]
        self.assertIn("calc.py", caps)
        self.assertNotIn("_bmad/scripts/outil.py", caps)

    def test_une_mise_a_jour_declare_un_outil_venu_depuis_et_le_dit_a_approuver(self):
        racine = depot({"calc.py": "X = 1\n"})
        installer(racine)
        for chemin, texte in FICHIERS_BMAD.items():
            (racine / chemin).parent.mkdir(parents=True, exist_ok=True)
            (racine / chemin).write_text(texte, encoding="utf-8")
        sortie = installer(racine)
        self.assertIn("approve --keys thirdparty.paths", sortie)
        self.assertEqual(config.Projet.charger(racine).chemins_tiers(), ["_bmad/**", "**/skills/bmad-*/**"])


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


if __name__ == "__main__":
    unittest.main()
