import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, contexte, controles_memoire, memoire
from socle.rapport import Rapport


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


def adr(num: int, lu: str) -> str:
    return (f"<!-- socle: couche=decisions zone=publique -->\n# ADR-{num:04d} — Décision {num}\n\n"
            f"> statut : acceptée · date : 2026-10-10{lu}\n\n## Décision\n\nLa décision {num}.\n")


class TestLecturesSuccessives(unittest.TestCase):
    """Une branche ajoute trois décisions, chacune après avoir lu l'index tel
    qu'il était : l'ajout des suivantes ne périme pas la lecture des
    premières."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-lectures-"))
        git(self.racine, "init", "-q", "-b", "main")
        self.decisions = self.racine / "memoire/decisions"
        self.decisions.mkdir(parents=True)
        (self.decisions / "ADR-0001-une.md").write_text(adr(1, ""))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        for num in (2, 3, 4):
            lu = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "decisions")
            (self.decisions / f"ADR-{num:04d}-suivante.md").write_text(adr(num, f" · lu : decisions@{lu}"))

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def erreurs(self) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete=None)
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        return [c.message for c in r.erreurs("memoire.lectures")]

    def test_chaque_lecture_reste_valide(self):
        self.assertEqual(self.erreurs(), [])

    def test_une_empreinte_inventee_reste_refusee(self):
        p = self.decisions / "ADR-0003-suivante.md"
        p.write_text(adr(3, " · lu : decisions@0badc0de"))
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("decisions@0badc0de", erreurs[0])


if __name__ == "__main__":
    unittest.main()
