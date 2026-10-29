import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from socle import utils as outils


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

    def test_un_clone_de_sa_seule_branche_de_travail_devine_la_branche_par_defaut(self):
        """B-0080 : le dépôt distant a `main`, mais le clone n'a récupéré que
        sa branche de travail ; il la prenait pour la branche par défaut, et
        le hook refusait son push sans dire pourquoi."""
        from socle import commands as commandes, hooks

        amont = self.dossier / "amont"
        amont.mkdir()
        git(amont, "init", "-q", "-b", "main")
        (amont / "a").write_text("a")
        git(amont, "add", "a")
        git(amont, "commit", "-qm", "a")
        git(amont, "branch", "travail")
        local = self.dossier / "local"
        git(self.dossier, "clone", "-q", "--single-branch", "-b", "travail", str(amont), str(local))
        git(local, "remote", "set-head", "origin", "-d")
        self.assertEqual(outils.branche_par_defaut(local), "origin/travail")
        self.assertTrue(outils.branche_par_defaut_devinee(local))
        refus = hooks.irreversible(local, commandes.analyser("git push origin travail")[0])
        self.assertIn("faute de mieux", refus)
        self.assertIn("git fetch origin <elle>", refus)
        git(local, "fetch", "-q", "origin", "main:refs/remotes/origin/main")
        self.assertEqual(outils.branche_par_defaut(local), "origin/main")
        self.assertFalse(outils.branche_par_defaut_devinee(local))
        self.assertIsNone(hooks.irreversible(local, commandes.analyser("git push origin travail")[0]))

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


class TestEcrire(unittest.TestCase):
    """Les écritures de fichiers, en une copie (L7) : l'installeur et la
    mémoire privée avaient chacun la leur, et quatre ajouts au `.gitignore`
    se faisaient à la main."""

    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="socle-ecrire-"))
        self.addCleanup(shutil.rmtree, self.d, ignore_errors=True)

    def test_ecrire_cree_les_dossiers_et_rend_executable(self):
        p = self.d / "a/b/hook"
        outils.ecrire(p, "#!/bin/sh\n", executable=True)
        self.assertEqual(p.read_text(), "#!/bin/sh\n")
        self.assertTrue(os.access(p, os.X_OK))
        outils.ecrire(self.d / "simple.txt", "x")
        self.assertFalse(os.access(self.d / "simple.txt", os.X_OK))

    def test_ajouter_lignes_seulement_les_manquantes(self):
        p = self.d / ".gitignore"
        self.assertEqual(outils.ajouter_lignes(p, ["a/", "b/"], "# pourquoi"), ["a/", "b/"])
        self.assertEqual(p.read_text(), "# pourquoi\na/\nb/\n")
        p.write_text(p.read_text() + "c/\n")
        self.assertEqual(outils.ajouter_lignes(p, ["b/", "d/"], "# encore"), ["d/"])
        self.assertEqual(p.read_text(), "# pourquoi\na/\nb/\nc/\n\n# encore\nd/\n")
        self.assertEqual(outils.ajouter_lignes(p, ["a/", "d/"], "# rien"), [])
        self.assertNotIn("# rien", p.read_text())


class TestLirePlusieurs(unittest.TestCase):
    def test_le_meme_contenu_que_fichier_par_fichier(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-lire-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        git(racine, "init", "-q", "-b", "main")
        (racine / "a.md").write_text("é\nune ligne\n")
        (racine / "vide.md").write_text("")
        (racine / "d").mkdir()
        (racine / "d/b.md").write_text("b" * 70000)
        git(racine, "add", "-A")
        git(racine, "commit", "-qm", "base")
        chemins = ["a.md", "absent.md", "d", "vide.md", "d/b.md"]
        lus = outils.lire_plusieurs(racine, "HEAD", chemins)
        self.assertEqual(lus, {c: outils.lire_a(racine, "HEAD", c) if c != "d" else None for c in chemins})
        self.assertEqual(lus["vide.md"], "")


class TestEmpreinteContenu(unittest.TestCase):
    """B-0091 : un fichier modifié dans la seconde de son dernier `git add`,
    à taille égale, passait pour inchangé. La copie de l'index prenait la
    date du moment, et git ne le relisait plus : les étapes rapides
    n'étaient pas relancées sur un arbre qui avait changé."""

    def test_un_fichier_change_dans_la_seconde_de_l_index_se_voit(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-empreinte-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        git(racine, "init", "-q")
        # L'ajout et la modification dans la même seconde, l'empreinte dans la suivante.
        time.sleep(1 - time.time() % 1 + 0.02)
        (racine / "a.py").write_text("x = 1\n")
        git(racine, "add", "-A")
        avant = outils.empreinte_contenu(racine)
        (racine / "a.py").write_text("x = 2\n")
        time.sleep(1.05)
        self.assertNotEqual(outils.empreinte_contenu(racine), avant)

