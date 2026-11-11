import contextlib
import io
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from socle import config, hooks, installer as installeur
from tests.test_bascule import Projet

MOTEUR = Path(__file__).resolve().parent.parent / "engine"

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

    def test_le_compte_depuis_le_commit_precedent(self):
        """B-0058 : des hooks qui cessent de tirer en cours de session
        gardaient le compte de leurs tirs d'avant, et la trace avait l'air
        saine ; depuis le commit précédent, elle compte zéro."""
        import tempfile
        from pathlib import Path

        racine = Path(tempfile.mkdtemp())
        trace = racine / ".socle/trace/hooks.log"
        trace.parent.mkdir(parents=True)
        trace.write_text("t\tSessionStart\ts\t\nt\tPreToolUse\ts\tBash\nt\tPreToolUse\ts\tBash\n")
        # Sans commit précédent : toute la trace de la session.
        self.assertEqual(hooks.compter_depuis_le_commit(racine, "s"), "PreToolUse=2")
        with trace.open("a") as f:
            f.write("t\tgit-prepare-commit-msg\t\t\nt\tStop\ts\t\nt\tPreToolUse\tautre\tBash\n")
        self.assertEqual(hooks.compter_depuis_le_commit(racine, "s"), "PreToolUse=0")
        self.assertEqual(hooks.compter_session(racine, "s"), "SessionStart=1 PreToolUse=2 Stop=1")
        # Sans session connue : la plus récente depuis le commit précédent.
        self.assertEqual(hooks.compter_depuis_le_commit(racine), "PreToolUse=1")
        with trace.open("a") as f:
            f.write("t\tPreToolUse\ts\tBash\n")
        self.assertEqual(hooks.compter_depuis_le_commit(racine, "s"), "PreToolUse=1")



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

    def test_le_compte_depuis_le_commit_se_lit_avant_de_tracer_celui_ci(self):
        """B-0058 : le commit compte les tirs depuis le précédent, et non
        depuis sa propre ligne de trace, qui le rendrait toujours nul."""
        import os
        import tempfile
        from pathlib import Path
        from unittest import mock

        from socle import config

        racine = Path(tempfile.mkdtemp())
        projet = config.Projet(racine=racine)
        hooks.tracer(racine, "PreToolUse", "s", "Bash")
        premier, second = racine / "MSG1", racine / "MSG2"
        premier.write_text("Premier\n")
        second.write_text("Second\n")
        with mock.patch.dict(os.environ, {"CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "s"}):
            hooks.git_prepare_commit_msg(projet, str(premier))
            hooks.git_prepare_commit_msg(projet, str(second))
        self.assertIn("Socle-Hooks: SessionStart=0 PreToolUse=1 Stop=0\nSocle-Hooks-Since-Commit: PreToolUse=1",
                      premier.read_text())
        self.assertIn("Socle-Hooks: SessionStart=0 PreToolUse=1 Stop=0\nSocle-Hooks-Since-Commit: PreToolUse=0",
                      second.read_text())


class TestHooksNonCharges(unittest.TestCase):
    """B-0060 : une session de Claude Code démarrée hors de la racine du
    projet n'a pas ses hooks ; l'état le dit, le hook avant commit refuse."""

    def setUp(self):
        import shutil
        import tempfile
        from pathlib import Path

        from socle import config

        self.racine = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        self.projet = config.Projet(racine=self.racine)

    def sous(self, **env):
        import os
        from unittest import mock

        base = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
        return mock.patch.dict(os.environ, {**base, **env}, clear=True)

    def test_hooks_non_charges_sans_session_start_pour_la_session(self):
        hooks.tracer(self.racine, "SessionStart", "autre", "startup")
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="s"):
            self.assertTrue(hooks.hooks_non_charges(self.projet))
        hooks.tracer(self.racine, "SessionStart", "s", "startup")
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="s"):
            self.assertFalse(hooks.hooks_non_charges(self.projet))

    def test_l_etat_sans_hooks_dit_de_montrer_le_travail_en_cours(self):
        """B-0108 : sans ses hooks, le pilote ne pouvait plus commiter son
        brouillon, resté dans un stash du conteneur."""
        from socle import state as etat

        hooks.tracer(self.racine, "SessionStart", "autre", "startup")
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="s"):
            sortie = etat.calculer(self.projet)
        self.assertIn("NE SONT PAS CHARGÉS", sortie)
        self.assertIn("git stash show -p --include-untracked", sortie)
        self.assertIn("le montre dans la conversation", sortie)

    def test_une_session_reprise_hors_de_la_racine_est_dite_sans_hooks(self):
        """B-0079 : reprise hors de la racine, la session garde son
        identifiant et le SessionStart d'avant la reprise, mais plus rien ne
        tire ; l'état ne le voyait pas."""
        from datetime import datetime, timedelta, timezone

        trace = config.chemin_trace(self.racine)
        trace.parent.mkdir(parents=True, exist_ok=True)
        avant = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(timespec="seconds")
        trace.write_text(f"{avant}\tSessionStart\ts\tstartup\n{avant}\tPreToolUse\ts\tBash\n")
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="s"):
            self.assertTrue(hooks.hooks_non_charges(self.projet))
            # La commande qui lance l'état vient de passer le filtre : chargés.
            hooks.tracer(self.racine, "PreToolUse", "s", "Bash")
            self.assertFalse(hooks.hooks_non_charges(self.projet))
            plus_tard = datetime.now(timezone.utc) + timedelta(seconds=hooks.FRAICHEUR_HOOKS + 1)
            self.assertTrue(hooks.hooks_non_charges(self.projet, maintenant=plus_tard))

    def test_une_session_qui_installe_le_socle_a_ses_hooks(self):
        """Installé pendant la session, le socle n'a pas vu son SessionStart,
        mais ses hooks tirent dès l'appel d'outil suivant (F-0003) : l'état
        les disait à tort non chargés, et l'agent ne devait plus rien pousser."""
        trace = config.chemin_trace(self.racine)
        trace.parent.mkdir(parents=True, exist_ok=True)
        hooks.tracer(self.racine, "Install", "", "0.1.0")
        hooks.tracer(self.racine, "PreToolUse", "s", "Bash")
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="s"):
            self.assertTrue(hooks.installe_pendant([l.split("\t") for l in config.lire_trace(self.racine)], "s"))
            self.assertFalse(hooks.hooks_non_charges(self.projet))
        # Une autre session, après coup, n'hérite pas de l'installation.
        hooks.tracer(self.racine, "PreToolUse", "autre", "Bash")
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="autre"):
            self.assertTrue(hooks.hooks_non_charges(self.projet))

    def test_hors_d_un_agent_ou_sans_session_rien_n_est_dit(self):
        with self.sous():
            self.assertFalse(hooks.hooks_non_charges(self.projet))
        with self.sous(CLAUDECODE="1"):
            self.assertFalse(hooks.hooks_non_charges(self.projet))

    def test_filtre_absent_depuis_le_commit_precedent(self):
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="s"):
            self.assertEqual(hooks.filtre_absent(self.projet), "PreToolUse=0")
            hooks.tracer(self.racine, "PreToolUse", "s", "Bash")
            self.assertIsNone(hooks.filtre_absent(self.projet))
            hooks.tracer(self.racine, "git-prepare-commit-msg")
            self.assertEqual(hooks.filtre_absent(self.projet), "PreToolUse=0")
        with self.sous():
            self.assertIsNone(hooks.filtre_absent(self.projet))

    def test_un_second_commit_dans_la_meme_commande_le_dit(self):
        """B-0078 : le filtre de l'agent a tiré pour la commande, qui commite
        deux fois ; le second commit était refusé comme si les hooks
        n'étaient pas chargés."""
        import contextlib
        import io

        hooks.tracer(self.racine, "SessionStart", "s", "startup")
        hooks.tracer(self.racine, "PreToolUse", "s", "Bash")
        hooks.tracer(self.racine, "git-prepare-commit-msg")
        sortie = io.StringIO()
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="s"), contextlib.redirect_stderr(sortie):
            self.assertEqual(hooks.git_pre_commit(self.projet), 1)
        self.assertIn("un second commit dans la même commande", sortie.getvalue())
        self.assertNotIn("ne sont pas chargés", sortie.getvalue())

    def test_un_commit_dans_un_autre_worktree_n_est_pas_un_second_commit(self):
        """B-0136 : la trace est commune aux worktrees ; un commit dans l'un,
        puis un autre dans un second, dans la même commande, passent. Deux
        dans le même worktree restent refusés. Le premier commit passe par le
        vrai hook, qui nomme son worktree dans la trace."""
        import subprocess

        from socle import config

        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty",
                        "-m", "base"], cwd=self.racine, check=True)
        autre = self.racine / "autre"
        subprocess.run(["git", "worktree", "add", "-q", "-b", "autre", str(autre)], cwd=self.racine, check=True)
        projet_autre = config.Projet(racine=autre)
        hooks.tracer(self.racine, "SessionStart", "s", "startup")
        hooks.tracer(self.racine, "PreToolUse", "s", "Bash")
        message = self.racine / "MSG"
        message.write_text("Premier\n")
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="s"):
            self.assertIsNone(hooks.filtre_absent(self.projet))
            hooks.git_prepare_commit_msg(self.projet, str(message))
            self.assertIsNone(hooks.filtre_absent(projet_autre))
            self.assertEqual(hooks.filtre_absent(self.projet), "PreToolUse=0")
            message.write_text("Second\n")
            hooks.git_prepare_commit_msg(projet_autre, str(message))
            self.assertEqual(hooks.filtre_absent(projet_autre), "PreToolUse=0")
        self.assertEqual(config.lire_trace(self.racine)[-1].split("\t")[3], str(autre.resolve()))

    def test_un_worktree_neuf_ne_masque_pas_des_hooks_qui_ont_cesse_de_tirer(self):
        """B-0058, dans un worktree neuf : son compte partirait du début de la
        trace. Des hooks qui ne tirent plus depuis un commit ailleurs, et dont
        le dernier passage n'est plus frais, font refuser le commit."""
        import subprocess

        from socle import config

        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty",
                        "-m", "base"], cwd=self.racine, check=True)
        neuf = self.racine / "neuf"
        subprocess.run(["git", "worktree", "add", "-q", "-b", "neuf", str(neuf)], cwd=self.racine, check=True)
        trace = config.chemin_trace(self.racine)
        trace.parent.mkdir(parents=True, exist_ok=True)
        trace.write_text("2026-11-09T08:00:00+00:00\tSessionStart\ts\tstartup\n"
                         "2026-11-09T08:00:01+00:00\tPreToolUse\ts\tBash\n"
                         f"2026-11-09T08:00:02+00:00\tgit-prepare-commit-msg\t\t{self.racine.resolve()}\n")
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="s"):
            self.assertEqual(hooks.filtre_absent(config.Projet(racine=neuf)), "PreToolUse=0")

    def test_le_hook_avant_commit_refuse_sans_passage_du_filtre(self):
        import contextlib
        import io

        sortie = io.StringIO()
        with self.sous(CLAUDECODE="1", CLAUDE_CODE_SESSION_ID="s"), contextlib.redirect_stderr(sortie):
            self.assertEqual(hooks.git_pre_commit(self.projet), 1)
        self.assertIn("commit d'agent sans aucun passage du filtre", sortie.getvalue())
        self.assertIn("relancer la session depuis la racine du projet", sortie.getvalue())


class TestCommitMsg(unittest.TestCase):
    def test_le_diff_de_commit_v_n_est_pas_lu_comme_le_message(self):
        """Une dispense écrite dans le message reste lue quand `git commit -v`
        met le diff en bas (relevé de la passe de recul, F)."""
        import contextlib
        import io
        import tempfile
        from pathlib import Path
        from unittest import mock

        from socle import config

        racine = Path(tempfile.mkdtemp())
        message = racine / "MSG"
        message.write_text("Sujet\n\nDispense-test: f — une raison assez longue\n"
                           "# ------------------------ >8 ------------------------\n"
                           "diff --git a/x b/x\n+une ligne\n")
        vus = []
        with mock.patch.object(hooks, "code_sans_test", lambda projet, m: vus.append(m)), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(hooks.git_commit_msg(config.Projet(racine=racine), str(message)), 0)
        self.assertEqual(len(vus), 1)
        self.assertNotIn("diff --git", vus[0])
        self.assertIn("Dispense-test", vus[0])


class TestHooksAbsents(unittest.TestCase):
    """B-0050 : un commit d'agent dont aucun hook de l'agent n'a tiré n'était
    vu qu'en CI ; le hook commit-msg le dit dès le commit, sans refuser."""

    def message(self, trace: str, agent: bool = True) -> str:
        return ("Sujet\n\n" + ("Co-Authored-By: Claude <noreply@anthropic.com>\n" if agent else "")
                + f"Socle-Hooks: {trace}\n")

    def test_un_commit_d_agent_sans_hook_de_l_agent(self):
        import contextlib
        import io
        import tempfile
        from pathlib import Path
        from unittest import mock

        from socle import config

        projet = config.Projet(racine=Path(tempfile.mkdtemp()))
        avert = hooks.hooks_absents(projet, self.message("SessionStart=0 PreToolUse=0 Stop=0"))
        self.assertIn("la CI le refusera (`hooks.trace`)", avert)
        self.assertIsNone(hooks.hooks_absents(projet, self.message("SessionStart=1 PreToolUse=4 Stop=1")))
        self.assertIsNone(hooks.hooks_absents(projet, self.message("SessionStart=0 PreToolUse=0 Stop=0", agent=False)))
        # Par le hook lui-même : un avertissement, jamais un refus.
        fichier = projet.racine / "MSG"
        fichier.write_text(self.message("SessionStart=0 PreToolUse=0 Stop=0"))
        with mock.patch.object(hooks, "code_sans_test", lambda projet, m: None), \
                contextlib.redirect_stderr(io.StringIO()) as erreurs:
            self.assertEqual(hooks.git_commit_msg(projet, str(fichier)), 0)
        self.assertIn("sans aucun hook de l'agent", erreurs.getvalue())

    def test_des_hooks_arretes_depuis_le_commit_precedent(self):
        """B-0058 : des tirs en début de session, plus aucun depuis."""
        import tempfile
        from pathlib import Path

        from socle import config

        projet = config.Projet(racine=Path(tempfile.mkdtemp()))
        session = "SessionStart=1 PreToolUse=4 Stop=1"
        avert = hooks.hooks_absents(projet, self.message(session) + "Socle-Hooks-Since-Commit: PreToolUse=0\n")
        self.assertIn("depuis le commit précédent", avert)
        self.assertIn("la CI le refusera (`hooks.trace`)", avert)
        self.assertIsNone(hooks.hooks_absents(projet, self.message(session) + "Socle-Hooks-Since-Commit: PreToolUse=1\n"))
        # Un commit d'avant ce compte ne le porte pas : rien à en dire.
        self.assertIsNone(hooks.hooks_absents(projet, self.message(session)))


class TestCorrectifSansTest(Projet):
    """B-0024 : un correctif sans test de régression n'était vu qu'en CI ; le
    hook commit-msg le dit dès le commit, quand l'amender suffit encore."""

    def test_un_correctif_qui_n_apporte_aucun_test(self):
        from socle import config
        from tests.test_bascule import git

        racine = self.racine
        (racine / "calc.py").write_text("def double(x):\n    return 2 * int(x)\n")
        git(racine, "add", "calc.py")
        projet = config.Projet.charger(racine)
        avert = hooks.correctif_sans_test(projet, "fix: double accepte une chaîne")
        self.assertIn("la CI le refusera (`tests.regression`)", avert)
        self.assertIsNone(hooks.correctif_sans_test(projet, "Une amélioration de double"))
        (racine / "tests").mkdir(exist_ok=True)
        (racine / "tests/test_double.py").write_text("def test_chaine():\n    assert True\n")
        git(racine, "add", "tests/test_double.py")
        self.assertIsNone(hooks.correctif_sans_test(projet, "fix: double accepte une chaîne"))

    def test_un_correctif_amende_se_juge_contre_le_parent_du_commit_amende(self):
        """B-0084 : amendé pour y ajouter une doc, un correctif qui portait
        déjà son test se voyait dire qu'il n'en avait pas."""
        from tests.test_bascule import git

        racine = self.racine
        (racine / "calc.py").write_text("def double(x):\n    return 2 * int(x)\n")
        (racine / "tests").mkdir(exist_ok=True)
        (racine / "tests/test_double.py").write_text("def test_chaine():\n    assert True\n")
        git(racine, "add", "-A")
        git(racine, "commit", "-qm", "fix: double accepte une chaîne", "--no-verify")
        (racine / "docs/notes.md").write_text("Une ligne de doc de plus.\n")
        git(racine, "add", "-A")
        projet = config.Projet.charger(racine)
        message = "fix: double accepte une chaîne"
        self.assertIsNone(hooks.correctif_sans_test(projet, message, amendement=True))
        # Le même index, en commit nouveau : il n'apporte bien aucun test.
        self.assertIn("la CI le refusera", hooks.correctif_sans_test(projet, message, amendement=False))

    def test_l_amendement_se_lit_dans_la_commande_de_git(self):
        import os
        import subprocess
        import sys
        from pathlib import Path

        moteur = Path(hooks.__file__).resolve().parent.parent
        code = "from socle import hooks; print(hooks.amendement_en_cours())"
        # Le hook est l'enfant de la commande git : ici, d'un parent qui en
        # porte les arguments.
        parent = "import subprocess, sys; subprocess.run([sys.executable, '-c', sys.argv[1]])"

        def lancer(*args):
            return subprocess.run([sys.executable, "-c", parent, code, *args], capture_output=True, text=True,
                                  env={**os.environ, "PYTHONPATH": str(moteur)}).stdout.strip()

        self.assertEqual(lancer("commit", "--amend", "--no-edit"), "True")
        self.assertEqual(lancer("commit", "-m", "x"), "False")


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

        from socle import installer as installeur

        cls.racine = Path(tempfile.mkdtemp(prefix="socle-trace-"))
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=cls.racine, check=True)
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(cls.racine, "python", "@essai", source=Path(__file__).resolve().parent.parent / "engine")
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

    def test_le_compteur_d_echecs_appartient_a_sa_session(self):
        """Relevé de la passe de recul, F : une session nouvelle escaladait
        dès son premier échec, sur le compte d'une autre."""
        from socle import config

        compteur = self.racine / config.COMPTEUR_STOP
        self.addCleanup(compteur.unlink, missing_ok=True)
        self.canonique.write_text(self.sain + self.FAUX)
        self.appeler(hooks.stop, self.projet, {"session_id": "a"})
        self.assertIn("tentative 2/", self.appeler(hooks.stop, self.projet, {"session_id": "a"}))
        self.assertIn("tentative 1/", self.appeler(hooks.stop, self.projet, {"session_id": "b"}))
        self.assertIn("tentative 2/", self.appeler(hooks.stop, self.projet, {"session_id": "b"}))

    def test_une_relance_sur_un_echec_inchange_ne_bloque_plus(self):
        """B-0143 : le hook relançait trois fois un tour qui ne pouvait rien
        corriger, et l'agent redisait son récap à chaque relance."""
        import json

        from socle import config

        compteur = self.racine / config.COMPTEUR_STOP
        self.addCleanup(compteur.unlink, missing_ok=True)
        compteur.unlink(missing_ok=True)
        self.canonique.write_text(self.sain + self.FAUX)
        premier = json.loads(self.appeler(hooks.stop, self.projet, {"session_id": "i", "stop_hook_active": False}))
        self.assertEqual(premier["decision"], "block")
        self.assertIn("réponds en une ligne", premier["reason"])
        relance = json.loads(self.appeler(hooks.stop, self.projet, {"session_id": "i", "stop_hook_active": True}))
        self.assertNotIn("decision", relance)
        self.assertIn("sans changement depuis la tentative précédente", relance["systemMessage"])
        self.assertIn("memoire.preuves", relance["systemMessage"])
        # Le premier arrêt du tour suivant bloque de nouveau, sans compter la
        # relance comme une tentative.
        self.assertIn("tentative 2/", self.appeler(hooks.stop, self.projet, {"session_id": "i"}))

    def test_une_relance_apres_un_changement_bloque_encore(self):
        from socle import config

        compteur = self.racine / config.COMPTEUR_STOP
        self.addCleanup(compteur.unlink, missing_ok=True)
        compteur.unlink(missing_ok=True)
        self.canonique.write_text(self.sain + self.FAUX)
        self.appeler(hooks.stop, self.projet, {"session_id": "j", "stop_hook_active": False})
        self.canonique.write_text(self.sain + self.FAUX + "\nUne ligne de plus.\n")
        self.assertIn("tentative 2/", self.appeler(hooks.stop, self.projet, {"session_id": "j", "stop_hook_active": True}))
        # La signature change avec l'arbre.
        avant = hooks.signature_d_echec(self.racine, ["memoire.preuves x"])
        self.assertNotEqual(hooks.signature_d_echec(self.racine, ["memoire.preuves y"]), avant)
        self.canonique.write_text(self.sain + self.FAUX)
        self.assertNotEqual(hooks.signature_d_echec(self.racine, ["memoire.preuves x"]), avant)

    def test_l_empreinte_voit_le_contenu_d_un_fichier_non_suivi(self):
        """Relevé de la passe de recul, F : seuls les noms des fichiers non
        suivis comptaient ; une vérification réussie restait valable après
        qu'on les avait changés."""
        import subprocess

        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", "--no-verify"],
                       cwd=self.racine, check=True)
        nouveau = self.racine / "nouveau.py"
        self.addCleanup(nouveau.unlink, missing_ok=True)
        nouveau.write_text("x = 1\n")
        avant = hooks._empreinte_arbre(self.racine)
        nouveau.write_text("x = 2\n")
        self.assertNotEqual(hooks._empreinte_arbre(self.racine), avant)

    def test_exiger_recap_trace_le_recap_manquant(self):
        import json
        import tempfile
        from pathlib import Path

        transcript = Path(tempfile.mkdtemp()) / "t.jsonl"
        transcript.write_text(json.dumps({"type": "assistant", "message": {"content": "Fait."}}))
        sortie = self.appeler(hooks.exiger_recap, self.projet, {"session_id": "r", "transcript_path": str(transcript)})
        self.assertIn('"block"', sortie)
        self.assertEqual(self.dernier_refus()[2:], ["r", "Stop:recap"])

    def test_pre_tool_use_refuse_le_widget_de_questions_de_l_agent(self):
        """B-0105 : une décision posée dans le widget de questions de l'agent
        s'y lit en texte brut, sans liens à suivre."""
        import json

        sortie = self.appeler(hooks.pre_tool_use, self.projet, {
            "session_id": "w", "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [{"question": "Approuves-tu la spécification ?", "header": "Spec",
                                          "multiSelect": False, "options": []}]}})
        decision = json.loads(sortie)["hookSpecificOutput"]
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn("widget de questions de l'agent", decision["permissionDecisionReason"])
        self.assertIn("socle new request", decision["permissionDecisionReason"])
        # Le hook ne le voit que si le réglage de Claude Code le lui montre.
        reglage = json.loads((self.racine / ".claude/settings.json").read_text())
        self.assertIn("AskUserQuestion", reglage["hooks"]["PreToolUse"][0]["matcher"].split("|"))

    def test_exiger_recap_rappelle_l_ordre_du_backlog(self):
        import json
        import tempfile
        from pathlib import Path

        backlog = self.racine / "memory/backlog"
        backlog.mkdir(parents=True, exist_ok=True)
        for ident, meta in (("B-0001", ""), ("B-0002", " · forme : jalon · après : B-0001")):
            f = backlog / f"{ident}-essai.md"
            f.write_text(f"<!-- socle: couche=backlog zone=publique -->\n# {ident} — Le sujet {ident}\n\n"
                         f"> statut : ouvert · origine : fichier:calc.py{meta}\n\nPour l'essai.\n")
            self.addCleanup(f.unlink)
        transcript = Path(tempfile.mkdtemp()) / "t.jsonl"
        transcript.write_text(json.dumps({"type": "assistant", "message": {"content": "Fait."}}))
        sortie = self.appeler(hooks.exiger_recap, self.projet, {"session_id": "o", "transcript_path": str(transcript)})
        self.assertIn("prochain jalon : B-0002 — Le sujet B-0002 ; reste : B-0001", sortie)
        self.assertIn("prêt : B-0001 — Le sujet B-0001", sortie)

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


class TestOutilsEnSessionCloud(unittest.TestCase):
    """D-0048 : en session cloud, le conteneur repart de zéro, et le pilote
    n'avait pas pytest ; le hook de démarrage installe les outils de
    l'adaptateur, par les commandes que la CI lance pour eux."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-outils-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python-pytest", "@essai", source=MOTEUR)
        self.projet = config.Projet.charger(self.racine)
        self.compte = self.racine / ".git/compte"
        self.etape(f"echo . >> {self.compte}")

    def etape(self, commande: str):
        self.projet.adaptateur["ci_setup"] = f"      - name: Outils\n        run: {commande}\n"

    def fois(self) -> int:
        return len(self.compte.read_text().split()) if self.compte.is_file() else 0

    def demarrer(self) -> str:
        sortie = io.StringIO()
        with unittest.mock.patch.dict("os.environ", {hooks.SESSION_CLOUD: "true"}), \
                contextlib.redirect_stdout(sortie):
            hooks.session_start(self.projet, {})
        return sortie.getvalue()

    def test_hors_session_cloud_rien_ne_s_installe(self):
        with unittest.mock.patch.dict("os.environ", {hooks.SESSION_CLOUD: ""}):
            self.assertEqual(hooks.installer_outils(self.projet), [])
        self.assertEqual(self.fois(), 0)

    def test_en_session_cloud_les_outils_s_installent_une_fois_par_conteneur(self):
        sortie = self.demarrer()
        self.assertIn(f"outils de l'adaptateur installés (session cloud) : `echo . >> {self.compte}`", sortie)
        self.assertEqual(self.fois(), 1)
        # Une reprise ou un compactage, dans le même conteneur : rien à refaire.
        self.assertNotIn("outils de l'adaptateur", self.demarrer())
        self.assertEqual(self.fois(), 1)

    def test_un_echec_se_dit_sans_bloquer_et_se_retente(self):
        self.etape("echo pip absent >&2; exit 4")
        sortie = self.demarrer()
        self.assertIn("!! outils de l'adaptateur : `echo pip absent >&2; exit 4` a rendu 4", sortie)
        self.assertIn("pip absent", sortie)
        self.assertIn("== ", sortie)  # l'état est là quand même
        self.assertIn("a rendu 4", self.demarrer())

    def test_l_adaptateur_maintenu_installe_pytest_et_mutmut(self):
        projet = config.Projet.charger(self.racine)
        with unittest.mock.patch.object(hooks.subprocess, "run") as lancer, \
                unittest.mock.patch.dict("os.environ", {hooks.SESSION_CLOUD: "true"}):
            lancer.return_value = subprocess.CompletedProcess([], 0, "", "")
            hooks.installer_outils(projet)
        self.assertEqual(lancer.call_args[0][0], "python3 -m pip install pytest mutmut")

