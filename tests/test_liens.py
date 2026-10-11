import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, liens

DEPOT = "https://github.com/essai/calc"


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestAdresses(unittest.TestCase):
    def test_adresse_du_depot_selon_la_forme_du_distant(self):
        self.assertEqual(liens.depuis_distant("https://github.com/theodubus/memory"), "https://github.com/theodubus/memory")
        self.assertEqual(liens.depuis_distant("https://jeton@github.com/o/r.git"), "https://github.com/o/r")
        self.assertEqual(liens.depuis_distant("git@github.com:o/r.git"), "https://github.com/o/r")
        self.assertEqual(liens.depuis_distant("ssh://git@github.com:22/o/r.git"), "https://github.com/o/r")

    def test_un_relais_local_ne_dit_pas_ou_l_humain_lit(self):
        self.assertIsNone(liens.depuis_distant("http://proxy@127.0.0.1:4242/git/o/r"))
        self.assertIsNone(liens.depuis_distant("/tmp/origine"))
        self.assertIsNone(liens.depuis_distant(""))

    def test_ancre_d_un_titre_comme_github(self):
        self.assertEqual(liens.ancre("B-0014 — Exiger un test, et pour du code qu'on découvre"),
                         "b-0014--exiger-un-test-et-pour-du-code-quon-découvre")
        self.assertEqual(liens.ancre("J-2026-10-10-P — Backlog clos : B-0007, B-0015"),
                         "j-2026-10-10-p--backlog-clos--b-0007-b-0015")
        self.assertEqual(liens.ancre("`socle` « x » — a.b"), "socle--x---ab")

    def test_ce_qui_ressemble_a_un_chemin(self):
        self.assertEqual(liens.ressemble_a_un_chemin("moteur/socle/liens.py"), "moteur/socle/liens.py")
        self.assertEqual(liens.ressemble_a_un_chemin("tests/test_humain.py:65"), "tests/test_humain.py")
        self.assertEqual(liens.ressemble_a_un_chemin("memoire/"), "memoire/")
        self.assertEqual(liens.ressemble_a_un_chemin("AGENTS.md"), "AGENTS.md")
        for pas_un_chemin in ("origin/main", "outils.git", "socle url D-0005", "chess:CLAUDE.md",
                              "**/*.md", "ADR-0007@ac16270e", "/home/user/x.md", "python3.11"):
            self.assertIsNone(liens.ressemble_a_un_chemin(pas_un_chemin), pas_un_chemin)


class TestLiensDuDepot(unittest.TestCase):
    """Un dépôt et son origine, fabriqués : ce qui est poussé a un lien,
    ce qui ne l'est pas n'en a pas."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-liens-"))
        source = self.dossier / "source"
        (source / "docs").mkdir(parents=True)
        git(source, "init", "-q", "-b", "main")
        (source / "docs/a.md").write_text("# A\n")
        (source / ".socle").mkdir()
        (source / ".socle/politique.toml").write_text(f'[human]\nrepo_url = "{DEPOT}"\n')
        git(source, "add", "-A")
        git(source, "commit", "-qm", "un")
        self.clone = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(source), str(self.clone))
        git(self.clone, "switch", "-q", "-c", "claude/essai")
        (self.clone / "docs/b.md").write_text("# B\n")
        git(self.clone, "add", "-A")
        git(self.clone, "commit", "-qm", "deux")
        self.projet = config.Projet.charger(self.clone)
        self.main = git(self.clone, "rev-parse", "origin/main").strip()

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)

    def test_permalien_au_commit_pousse(self):
        url, avertissement = liens.lien(self.projet, "docs/a.md")
        self.assertEqual(url, f"{DEPOT}/blob/{self.main}/docs/a.md")
        self.assertEqual(avertissement, "")

    def test_pas_de_lien_vers_ce_qui_n_est_pas_pousse(self):
        url, avertissement = liens.lien(self.projet, "docs/b.md")
        self.assertIsNone(url)
        self.assertIn("pousser d'abord", avertissement)

    def test_une_version_locale_non_poussee_est_signalee(self):
        (self.clone / "docs/a.md").write_text("# A modifié\n")
        url, avertissement = liens.lien(self.projet, "docs/a.md")
        self.assertEqual(url, f"{DEPOT}/blob/{self.main}/docs/a.md")
        self.assertIn("pas poussée", avertissement)

    def test_liens_morts_d_un_message(self):
        message = (
            "Voir [la doc](docs/a.md), `docs/absent.md` et "
            f"{DEPOT}/blob/{self.main}/docs/b.md.\n"
            "```\ncat docs/exemple-dans-un-bloc.md `docs/rien.md`\n```\n"
        )
        morts, sans_lien = liens.problemes(self.projet, message)
        self.assertEqual(len(morts), 3, morts)
        self.assertIn("lien relatif « docs/a.md »", morts[0])
        self.assertIn("`docs/absent.md`", morts[1])
        self.assertIn("docs/b.md n'existe pas", morts[2])
        self.assertEqual(sans_lien, [])

    def test_liens_vivants_d_un_message(self):
        git(self.clone, "push", "-q", "origin", "claude/essai")
        message = (
            f"Voir {DEPOT}/blob/{self.main}/docs/a.md, {DEPOT}/blob/claude/essai/docs/b.md, "
            f"{DEPOT}/tree/main/docs, {DEPOT}/pull/3, `docs/a.md` et `origin/main`."
        )
        self.assertEqual(liens.problemes(self.projet, message), ([], []))


class TestDemandeLue(unittest.TestCase):
    """B-0022 : une réponse ne se relaie qu'à une demande que l'humain a pu
    lire, poussée telle qu'elle est."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-relais-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        origine = self.dossier / "origine.git"
        git(self.dossier, "init", "-q", "--bare", str(origine))
        self.racine = self.dossier / "projet"
        (self.racine / ".socle").mkdir(parents=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / ".socle/politique.toml").write_text(f'[human]\nrepo_url = "{DEPOT}"\n')
        self.demande = self.racine / "memoire/demandes/D-0001-essai.md"
        self.demande.parent.mkdir(parents=True)
        self.demande.write_text("<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Essai ?\n")
        git(self.racine, "remote", "add", "origin", str(origine))
        self.projet = config.Projet.charger(self.racine)

    def illisible(self):
        from socle import cli, demandes

        d = next(x for x in demandes.toutes(self.racine) if x.id == "D-0001")
        return cli.demande_illisible(self.projet, d)

    def pousser(self):
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "demande")
        git(self.racine, "push", "-q", "-u", "origin", "main")

    def test_une_demande_jamais_poussee_n_a_pas_pu_etre_lue(self):
        self.assertIn("pousser", self.illisible())

    def test_une_demande_poussee_telle_quelle_a_pu_etre_lue(self):
        self.pousser()
        self.assertIsNone(self.illisible())

    def test_cmd_answer_refuse_de_relayer_une_reponse_a_une_demande_non_lue(self):
        import argparse
        import contextlib
        import io

        from socle import cli

        (self.racine / "citation.txt").write_text("oui")
        args = argparse.Namespace(root=str(self.racine), request="D-0001", answer="valider", text="", by="Théo",
                                  relayed=True, quote=None, quote_file=str(self.racine / "citation.txt"))
        erreurs = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(erreurs):
            self.assertEqual(cli.cmd_answer(args), 2)
        self.assertIn("n'a pas pu être lue par l'humain", erreurs.getvalue())
        self.assertEqual(list(self.demande.parent.glob("*.reponse.toml")), [])

    def test_une_demande_changee_depuis_le_push_n_est_pas_celle_qu_il_a_lue(self):
        self.pousser()
        self.demande.write_text(self.demande.read_text() + "\nUn ajout après coup.\n")
        self.assertIn("diffère", self.illisible())

if __name__ == "__main__":
    unittest.main()
