"""Relevé de la passe de recul, D : une seule `Dispense-doc` couvrait toute
la plage et toute la table de correspondance. Elle ne vaut plus que pour le
code du commit qui la porte."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, contexte, controles_docs, installeur
from socle.rapport import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "moteur"
DISPENSE = "\n\nDispense-doc: un renommage interne, rien de visible à documenter"


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestDispenseDoc(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-dispense-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        for rel in ("src/a.py", "src/b.py", "docs/a.md", "docs/b.md"):
            (self.racine / rel).parent.mkdir(exist_ok=True)
            (self.racine / rel).write_text("x = 1\n" if rel.endswith(".py") else "# Doc\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(gf.read_text() + '\n[[docmap]]\ncode = ["src/a.py"]\ndocs = ["docs/a.md"]\n\n'
                      '[[docmap]]\ncode = ["src/b.py"]\ndocs = ["docs/b.md"]\n')
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def commit(self, rel, message):
        (self.racine / rel).write_text("x = 2\n")
        git(self.racine, "commit", "-qam", message, "--no-verify")

    def erreurs(self) -> list[str]:
        r = Rapport()
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete="HEAD")
        controles_docs.correspondance(ctx, r)
        return [c.message for c in r.erreurs("docs.correspondance")]

    def test_la_dispense_couvre_son_commit(self):
        self.commit("src/a.py", "Renommage" + DISPENSE)
        self.assertEqual(self.erreurs(), [])

    def test_la_dispense_ne_couvre_pas_un_autre_commit(self):
        self.commit("src/a.py", "Renommage" + DISPENSE)
        self.commit("src/b.py", "Un vrai changement")
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("src/b.py", erreurs[0])
        self.assertNotIn("src/a.py", erreurs[0])
        self.assertEqual(list(controles_docs.fichiers_dispenses(
            contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete="HEAD"))), ["src/a.py"])


if __name__ == "__main__":
    unittest.main()
