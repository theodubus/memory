import io
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from socle import installeur

MOTEUR = Path(__file__).resolve().parent.parent / "moteur"
CLAUDE = "# Projet\n\nLes instructions du projet, écrites avant le socle.\n"


def depot(fichiers: dict[str, str]) -> Path:
    racine = Path(tempfile.mkdtemp(prefix="socle-installeur-"))
    env = {**os.environ, "HOME": str(racine), "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True, env=env)
    for chemin, texte in fichiers.items():
        p = racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")
    return racine


def installer(racine: Path, adoption=True):
    with redirect_stdout(io.StringIO()):
        installeur.installer(racine, "python", "@essai", adoption=adoption, source=MOTEUR)


class TestAdoption(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def test_claude_md_renomme_quand_rien_ne_le_lit(self):
        self.racine = depot({"CLAUDE.md": CLAUDE, "app.py": "print('ok')\n"})
        installer(self.racine)
        self.assertEqual((self.racine / "CLAUDE.md").read_text().strip(), "@AGENTS.md")
        agents = (self.racine / "AGENTS.md").read_text()
        self.assertIn("écrites avant le socle", agents)
        self.assertIn(installeur.DEBUT_SOCLE, agents)

    def test_claude_md_garde_quand_le_projet_le_lit(self):
        # Le cas de chess : un test du projet lit CLAUDE.md par son nom.
        self.racine = depot({"CLAUDE.md": CLAUDE, "tests/test_doc.py": "open('CLAUDE.md').read()\n"})
        installer(self.racine)
        self.assertFalse((self.racine / "AGENTS.md").exists())
        claude = (self.racine / "CLAUDE.md").read_text()
        self.assertTrue(claude.startswith(CLAUDE.rstrip("\n")))
        self.assertIn(installeur.DEBUT_SOCLE, claude)
        self.assertIn('"CLAUDE.md" = { max_bytes =', (self.racine / ".socle/guardrails.toml").read_text())

    def test_relance_regenere_la_section_sans_la_dupliquer(self):
        self.racine = depot({"app.py": "print('ok')\n"})
        installer(self.racine, adoption=False)
        installer(self.racine, adoption=False)
        agents = (self.racine / "AGENTS.md").read_text()
        self.assertEqual(agents.count(installeur.DEBUT_SOCLE), 1)
        self.assertEqual((self.racine / "CLAUDE.md").read_text().strip(), "@AGENTS.md")


if __name__ == "__main__":
    unittest.main()


class TestRelance(unittest.TestCase):
    """B-0044, L1 : relancer l'installeur ne perd rien."""

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def test_relancee_depuis_le_projet_elle_garde_son_moteur(self):
        """La source était aussi la destination : supprimée avant la copie."""
        self.racine = depot({"app.py": "print('ok')\n"})
        installer(self.racine, adoption=False)
        with redirect_stdout(io.StringIO()) as flux:
            installeur.installer(self.racine, "python", "@essai", source=self.racine / ".socle/engine")
        self.assertTrue((self.racine / ".socle/engine/socle/cli.py").is_file())
        self.assertIn("moteur déjà en place", flux.getvalue())

    def test_un_claude_md_propre_au_projet_passe_dans_agents_md(self):
        """Il était remplacé par la seule ligne d'import dès qu'AGENTS.md existait."""
        self.racine = depot({"AGENTS.md": "# Projet\n", "CLAUDE.md": "Règle propre à Claude : répondre bref.\n"})
        installer(self.racine, adoption=False)
        self.assertEqual((self.racine / "CLAUDE.md").read_text().strip(), "@AGENTS.md")
        self.assertIn("Règle propre à Claude : répondre bref.", (self.racine / "AGENTS.md").read_text())

    def test_une_seconde_adoption_complete_la_liste(self):
        """Elle écrivait une seconde table `[adoption]` : les garde-fous ne se
        lisaient plus."""
        import tomllib

        self.racine = depot({"app.py": "print('ok')\n", "LISEZMOI.md": "Voir [la suite](absent.md).\n"})
        installer(self.racine)
        paragraphe = "Un long paragraphe recopié tel quel dans deux fichiers du projet, " * 4 + "\n"
        (self.racine / "a.md").write_text(paragraphe)
        (self.racine / "b.md").write_text(paragraphe)
        installer(self.racine)
        gf = tomllib.loads((self.racine / ".socle/guardrails.toml").read_text())
        self.assertEqual(sorted(gf["adoption"]["warn_only"]), ["docs.copie", "memoire.references"])
