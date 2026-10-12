import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import outils


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestBaseDeTravail(unittest.TestCase):
    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-outils-"))

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)

    def test_depot_sans_branche_par_defaut_retombe_sur_la_branche_suivie(self):
        # Le cas de ce dépôt à sa naissance : une seule branche, pas de `main`.
        amont = self.dossier / "amont"
        amont.mkdir()
        git(amont, "init", "-q", "-b", "travail")
        (amont / "a").write_text("a")
        git(amont, "add", "a")
        git(amont, "commit", "-qm", "a")
        local = self.dossier / "local"
        local.mkdir()
        git(local, "init", "-q", "-b", "autre")
        git(local, "remote", "add", "origin", str(amont))
        git(local, "fetch", "-q", "origin")
        git(local, "checkout", "-q", "-b", "travail", "--track", "origin/travail")
        self.assertEqual(outils.branche_par_defaut(local), "origin/travail")
        self.assertEqual(outils.base_de_travail(local), git(local, "rev-parse", "HEAD").strip())

    def test_sans_rien_pas_de_base(self):
        git(self.dossier, "init", "-q", "-b", "seule")
        (self.dossier / "a").write_text("a")
        git(self.dossier, "add", "a")
        git(self.dossier, "commit", "-qm", "a")
        self.assertIsNone(outils.base_de_travail(self.dossier))


if __name__ == "__main__":
    unittest.main()


class TestRenommages(unittest.TestCase):
    """B-0044, L2 : un renommage ne gardait que le nouveau nom ; un fichier
    protégé ou un test renommés passaient tous les étages."""

    def test_un_renommage_donne_ses_deux_chemins(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-renommage-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        git(racine, "init", "-q", "-b", "main")
        (racine / "politique.toml").write_text("max = 3\n" * 20)
        git(racine, "add", "-A")
        git(racine, "commit", "-qm", "base")
        base = git(racine, "rev-parse", "HEAD").strip()
        git(racine, "mv", "politique.toml", "ancienne.toml")
        self.assertEqual(outils.fichiers_changes(racine, base), ["ancienne.toml", "politique.toml"])
        git(racine, "commit", "-qm", "renommage")
        self.assertEqual(outils.fichiers_changes(racine, base, "HEAD"), ["ancienne.toml", "politique.toml"])
