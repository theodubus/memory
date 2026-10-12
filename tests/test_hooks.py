import unittest

from socle import hooks

LANCEUR = ".socle/" + "socle"  # en morceaux : ce fichier ne lance rien


class TestCiblesEcrites(unittest.TestCase):
    def test_redirections(self):
        self.assertEqual(hooks.cibles_ecrites("echo x > a.txt; cat b >> c.txt 2>&1"), ["a.txt", "c.txt"])

    def test_executer_n_est_pas_ecrire(self):
        self.assertEqual(hooks.cibles_ecrites(f"python3 {LANCEUR} check > /tmp/rapport.txt"), ["/tmp/rapport.txt"])
        self.assertEqual(hooks.cibles_ecrites(f"cat {LANCEUR} | grep x"), [])

    def test_commandes_qui_ecrivent(self):
        self.assertEqual(hooks.cibles_ecrites("rm -f a b && touch c"), ["a", "b", "c"])
        self.assertEqual(hooks.cibles_ecrites("cp source.toml dest.toml"), ["dest.toml"])
        self.assertEqual(hooks.cibles_ecrites("sed -i 's/a/b/' x.toml"), ["x.toml"])
        self.assertEqual(hooks.cibles_ecrites("echo y | tee -a journal.md"), ["journal.md"])

    def test_sed_sans_i_ne_compte_pas(self):
        self.assertEqual(hooks.cibles_ecrites("sed -n '1,5p' x.toml"), [])


class TestCommandesHumaines(unittest.TestCase):
    def test_invocation_refusee(self):
        self.assertTrue(hooks.COMMANDES_HUMAINES.search(f"python3 {LANCEUR} answer D-0001 valider"))
        self.assertTrue(hooks.COMMANDES_HUMAINES.search("PYTHONPATH=moteur python3 -m socle approve --text x"))

    def test_relais_avec_citation_permis(self):
        cmd = f"python3 {LANCEUR} answer D-0001 valider --relayed --by Théo --quote-file /tmp/c.txt"
        m = hooks.COMMANDES_HUMAINES.search(cmd)
        self.assertEqual(m.group(1), "answer")  # reconnu ; le hook le laisse passer grâce à --relayed et --quote

    def test_citation_acceptee(self):
        self.assertIsNone(hooks.COMMANDES_HUMAINES.search("grep -n 'socle answer' AGENTS.md"))


class TestTrailer(unittest.TestCase):
    def test_compte_de_la_session_la_plus_recente(self):
        import tempfile
        from pathlib import Path

        racine = Path(tempfile.mkdtemp())
        trace = racine / ".socle/trace/hooks.log"
        trace.parent.mkdir(parents=True)
        trace.write_text(
            "t\tSessionStart\tvieille\t\nt\tPreToolUse\tvieille\tBash\n"
            "t\tInstall\t\t0.1.0\nt\tPreToolUse\tneuve\tBash\nt\tPreToolUse\tneuve\tEdit\n"
        )
        self.assertEqual(hooks.compter_session(racine), "SessionStart=installation PreToolUse=2 Stop=0")
        trace.write_text("t\tSessionStart\ts\t\nt\tPreToolUse\ts\tBash\nt\tStop\ts\t\n")
        self.assertEqual(hooks.compter_session(racine), "SessionStart=1 PreToolUse=1 Stop=1")

    def test_la_session_qui_commite_et_non_la_plus_recente(self):
        """B-0044, L2 : une session dont les hooks sont coupés empruntait la
        trace d'une session plus ancienne, et sa trace avait l'air saine."""
        import tempfile
        from pathlib import Path

        racine = Path(tempfile.mkdtemp())
        trace = racine / ".socle/trace/hooks.log"
        trace.parent.mkdir(parents=True)
        trace.write_text("t\tSessionStart\tvieille\t\nt\tPreToolUse\tvieille\tBash\n")
        self.assertEqual(hooks.compter_session(racine, "sans-hooks"), "SessionStart=0 PreToolUse=0 Stop=0")
        self.assertEqual(hooks.compter_session(racine, "vieille"), "SessionStart=1 PreToolUse=1 Stop=0")



class TestPrepareCommitMsg(unittest.TestCase):
    """Les trailers d'un commit d'agent : au bon endroit, avec la trace de la
    session qui commite, et sans remonter le diff de `git commit -v`."""

    def test_trailers_sans_le_diff_de_commit_v(self):
        import os
        import tempfile
        from pathlib import Path
        from unittest import mock

        from socle import config

        racine = Path(tempfile.mkdtemp())
        message = racine / "MSG"
        message.write_text("Sujet du commit\n\n# Un commentaire de git\n"
                           "# ------------------------ >8 ------------------------\n"
                           "diff --git a/x b/x\n+une ligne\n")
        with mock.patch.dict(os.environ, {"CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "sans-hooks"}):
            self.assertEqual(hooks.git_prepare_commit_msg(config.Projet(racine=racine), str(message)), 0)
        texte = message.read_text()
        haut, bas = texte.split("# ------------------------ >8", 1)
        self.assertIn("Socle-Hooks: SessionStart=0 PreToolUse=0 Stop=0", haut)
        self.assertNotIn("diff --git", haut)
        self.assertIn("diff --git", bas)


class TestSousUnAgent(unittest.TestCase):
    def test_sous_un_agent(self):
        import contextlib
        import io
        import os
        from unittest import mock

        with mock.patch.dict(os.environ, {"CLAUDECODE": "1"}), contextlib.redirect_stderr(io.StringIO()):
            self.assertTrue(hooks.sous_un_agent("`socle approve`"))
        with mock.patch.dict(os.environ):
            os.environ.pop("CLAUDECODE", None)
            self.assertFalse(hooks.sous_un_agent("`socle approve`"))


class TestTraceDesRefus(unittest.TestCase):
    """Chaque refus d'un hook laisse dans la trace son étage et ce qui a
    refusé : le banc d'évaluation y compte les défauts attrapés par étage."""

    def test_un_refus_du_hook_de_l_agent_est_trace(self):
        import contextlib
        import io
        import subprocess
        import tempfile
        from pathlib import Path

        from socle import config

        racine = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=racine, check=True)
        projet = config.Projet.charger(racine)
        entree = {"session_id": "s", "tool_name": "Bash", "tool_input": {"command": "git push --force origin main"}}
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            hooks.pre_tool_use(projet, entree)
        self.assertIn('"deny"', sortie.getvalue())
        refus = [l.split("\t") for l in config.lire_trace(racine) if "\tRefus\t" in l]
        self.assertEqual(len(refus), 1)
        self.assertEqual(refus[0][2], "s")
        self.assertTrue(refus[0][3].startswith("PreToolUse:Bash — "))
        hooks.tracer_refus(racine, "git-pre-commit", "tests.creux,memoire.references")
        self.assertTrue(config.lire_trace(racine)[-1].endswith("\tRefus\t\tgit-pre-commit:tests.creux,memoire.references"))
        self.assertEqual(hooks.compter_session(racine), "SessionStart=0 PreToolUse=1 Stop=0")


class TestTraceDesRefusDeFinDeTourEtDeGit(unittest.TestCase):
    """`stop`, `exiger_recap` et `git_pre_commit` notent leur refus, avec
    ce qui a échoué, dans un projet où le socle est installé."""

    FAUX = "\n## F-0001 — Un fait sans preuve\n\n> statut : mesuré\n"

    @classmethod
    def setUpClass(cls):
        import contextlib
        import io
        import subprocess
        import tempfile
        from pathlib import Path

        from socle import installeur

        cls.racine = Path(tempfile.mkdtemp(prefix="socle-trace-"))
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=cls.racine, check=True)
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(cls.racine, "python", "@essai", source=Path(__file__).resolve().parent.parent / "moteur")
        cls.canonique = cls.racine / "memory/canonical.md"
        cls.sain = cls.canonique.read_text()

    def setUp(self):
        from socle import config

        self.addCleanup(self.canonique.write_text, self.sain)
        self.projet = config.Projet.charger(self.racine)

    def dernier_refus(self) -> list[str]:
        from socle import config

        return [l.split("\t") for l in config.lire_trace(self.racine) if "\tRefus\t" in l][-1]

    def appeler(self, f, *args) -> str:
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()) as sortie, contextlib.redirect_stderr(io.StringIO()):
            f(*args)
        return sortie.getvalue()

    def test_stop_trace_les_controles_en_echec(self):
        self.canonique.write_text(self.sain + self.FAUX)
        self.assertIn('"block"', self.appeler(hooks.stop, self.projet, {"session_id": "t"}))
        refus = self.dernier_refus()
        self.assertEqual(refus[2], "t")
        self.assertTrue(refus[3].startswith("Stop:"))
        self.assertIn("memoire.preuves", refus[3].split(":", 1)[1].split(","))

    def test_exiger_recap_trace_le_recap_manquant(self):
        import json
        import tempfile
        from pathlib import Path

        transcript = Path(tempfile.mkdtemp()) / "t.jsonl"
        transcript.write_text(json.dumps({"type": "assistant", "message": {"content": "Fait."}}))
        sortie = self.appeler(hooks.exiger_recap, self.projet, {"session_id": "r", "transcript_path": str(transcript)})
        self.assertIn('"block"', sortie)
        self.assertEqual(self.dernier_refus()[2:], ["r", "Stop:recap"])

    def test_git_pre_commit_trace_les_controles_en_echec(self):
        import subprocess

        self.canonique.write_text(self.sain + self.FAUX)
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        self.addCleanup(subprocess.run, ["git", "reset", "-q"], cwd=self.racine)
        self.assertEqual(self.code(hooks.git_pre_commit), 1)
        refus = self.dernier_refus()
        self.assertEqual(refus[1], "Refus")
        self.assertTrue(refus[3].startswith("git-pre-commit:"))
        self.assertIn("memoire.preuves", refus[3])

    def code(self, f) -> int:
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return f(self.projet)


if __name__ == "__main__":
    unittest.main()
