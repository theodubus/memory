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


if __name__ == "__main__":
    unittest.main()
