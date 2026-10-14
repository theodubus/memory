"""B-0057 : depuis un worktree secondaire, git passe `GIT_DIR` et
`GIT_INDEX_FILE` à ses hooks. Hérités par les tests du projet, ils faisaient
viser le dépôt du projet à leurs dépôts jetables : la régression rejouée y
ajoutait un worktree par correctif, qui relançait la suite, sans fin, et un
`git init --bare` détourné y posait `core.bare = true`."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from socle import utils as outils
from tests.test_bascule import git


class TestHookDansUnWorktree(unittest.TestCase):
    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-worktree-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        self.addCleanup(setattr, outils, "_index_du_hook", None)
        self.depot = self.dossier / "depot"
        self.depot.mkdir()
        git(self.depot, "init", "-q", "-b", "main")
        (self.depot / "a.txt").write_text("a\n")
        git(self.depot, "add", "-A")
        git(self.depot, "commit", "-qm", "a", "--no-verify")
        self.worktree = self.dossier / "w"
        git(self.depot, "worktree", "add", "-q", "--detach", str(self.worktree))
        self.gitdir = self.depot / ".git/worktrees/w"
        # Ce que git passe au hook d'un worktree secondaire.
        self.env = {"GIT_DIR": str(self.gitdir), "GIT_INDEX_FILE": str(self.gitdir / "index")}

    def test_un_depot_jetable_reste_le_sien(self):
        jetable = self.dossier / "jetable.git"
        jetable.mkdir()
        with mock.patch.dict(os.environ, self.env):
            outils.isoler_du_hook(self.worktree)
            self.assertNotIn("GIT_DIR", os.environ)
            outils.git(jetable, "init", "-q", "--bare")
        self.assertTrue((jetable / "HEAD").is_file())
        self.assertEqual(git(self.depot, "config", "core.bare").strip(), "false")

    def test_par_le_point_d_entree_du_hook(self):
        # Ce qu'a fait le hook de ce dépôt : un dépôt jetable créé pendant
        # un hook git lancé du worktree visait le dépôt du projet.
        import contextlib
        import io

        from socle import cli

        jetable = self.dossier / "jetable.git"
        jetable.mkdir()
        with mock.patch.dict(os.environ, self.env), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["--root", str(self.worktree), "hook", "git-commit-msg"]), 0)
            outils.git(jetable, "init", "-q", "--bare")
        self.assertEqual(git(self.depot, "config", "core.bare").strip(), "false")
        self.assertTrue((jetable / "HEAD").is_file())

    def test_l_index_juge_est_celui_que_git_passe(self):
        # Un `git commit -a` juge un index temporaire, pas celui du dépôt.
        temporaire = self.dossier / "index-temporaire"
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update(GIT_INDEX_FILE=str(temporaire), GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t")
        import subprocess

        subprocess.run(["git", "read-tree", "HEAD"], cwd=self.worktree, env=env, check=True)
        (self.worktree / "b.txt").write_text("b\n")
        subprocess.run(["git", "update-index", "--add", "b.txt"], cwd=self.worktree, env=env, check=True)
        attendu = subprocess.run(["git", "write-tree"], cwd=self.worktree, env=env, check=True,
                                 capture_output=True, text=True).stdout.strip()
        with mock.patch.dict(os.environ, {**self.env, "GIT_INDEX_FILE": str(temporaire)}):
            outils.isoler_du_hook(self.worktree)
            self.assertEqual(outils.arbre_de_l_index(self.worktree), attendu)
        self.assertNotEqual(git(self.worktree, "write-tree").strip(), attendu)


if __name__ == "__main__":
    unittest.main()
