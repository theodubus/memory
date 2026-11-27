import contextlib
import io
import os
import shutil
import subprocess
import sys
import time
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from socle import cli, config, hooks, installer as installeur
from tests.test_bascule import Projet, git

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

    def test_l_aide_passe_et_rien_de_plus(self):
        """B-0184 : l'aide de `socle answer`, `decision` et `reviewed` était
        refusée comme une réponse donnée à la place de l'humain."""
        projet = config.Projet.charger(Path(__file__).resolve().parent.parent)
        for nom in ("answer", "decision", "reviewed"):
            for aide in ("--help", "-h"):
                self.assertIsNone(hooks.refus_bash(projet, f"python3 {LANCEUR} {nom} {aide}"), (nom, aide))
        refus = "répond jamais à la place de l'humain"
        for cmd in (f"python3 {LANCEUR} answer D-0001 valider --help",
                    f"python3 {LANCEUR} decision --help \"Q ?\" oui",
                    f"python3 {LANCEUR} reviewed -h --by Théo",
                    f"python3 {LANCEUR} answer D-0001 valider"):
            self.assertIn(refus, hooks.refus_bash(projet, cmd) or "", cmd)
        self.assertIn("réservé à l'humain", hooks.refus_bash(projet, f"python3 {LANCEUR} approve --help") or "")

    def test_une_option_de_python_a_valeur_ne_cache_pas_la_commande(self):
        """B-0187 : `python3 -W ignore … answer` passait le hook ; la valeur
        de l'option était prise pour le script."""
        projet = config.Projet.charger(Path(__file__).resolve().parent.parent)
        refus = "répond jamais à la place de l'humain"
        for options in ("-W ignore", "-X utf8", "-Wignore", "-bW error", "-B -X dev", "--check-hash-based-pycs never",
                        "-W ignore -m socle", "-I -m socle", "-msocle"):
            cmd = f"python3 {options} {'' if 'socle' in options else LANCEUR} answer D-0001 oui"
            self.assertIn(refus, hooks.refus_bash(projet, cmd) or "", cmd)
        self.assertEqual(hooks.options_de_python(["-W", "ignore", LANCEUR, "x"]), [LANCEUR, "x"])
        self.assertEqual(hooks.options_de_python(["-Xutf8", "-m", "socle", "x"]), ["-m socle", "x"])
        # Ce qui n'est pas le lanceur du socle n'est pas pris pour lui.
        self.assertIsNone(hooks.options_de_python(["-c", "print(1)", LANCEUR]))
        self.assertIsNone(hooks.options_de_python(["-m", "unittest", LANCEUR, "answer"]))
        for cmd in (f"python3 -c 'print(1)' {LANCEUR} answer D-0001 oui",
                    f"python3 -W ignore -m unittest {LANCEUR} answer D-0001 oui",
                    "python3 -X utf8 outil.py answer D-0001 oui"):
            self.assertIsNone(hooks.refus_bash(projet, cmd), cmd)


class TestInstalleurHorsMode(unittest.TestCase):
    """B-0141 : un relecteur sans contexte a lancé l'installeur, en mode
    projet, sur ce dépôt en mode amont ; le hook refuse désormais
    l'installeur visé sur un projet équipé dans un autre mode que son verrou
    (ADR-0062), et laisse passer la mise à jour dans le mode du verrou."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.racine = self.tmp / "projet"
        (self.racine / ".socle").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.racine)], check=True)
        (self.racine / ".socle/engine.lock").write_text('mode = "amont"\nengine_dir = "engine"\n')
        self.projet = config.Projet.charger(self.racine)
        self.jetable = self.tmp / "jetable"
        self.jetable.mkdir()

    def juger(self, cmd: str, cwd: Path | None = None) -> str | None:
        return hooks.refus_bash(self.projet, cmd, str(cwd or self.racine))

    def test_l_incident_est_refuse(self):
        # La commande de l'incident : le mode par défaut, `projet`, sur la racine en amont.
        raison = self.juger(f"python3 {LANCEUR} install --target . --adapter kotlin --owner @essai")
        self.assertIn("dans un autre mode que celui de son verrou", raison)
        self.assertIn("`--mode amont`", raison)
        # La cible absolue, par `--target=`, ou atteinte après un `cd`.
        self.assertIsNotNone(self.juger(f"python3 {LANCEUR} install --target={self.racine} --mode projet"))
        self.assertIsNotNone(self.juger(f"cd {self.jetable} && python3 {self.racine}/.socle/socle install "
                                        f"--target {self.racine}"))
        self.assertEqual(hooks.installeur_hors_mode(
            self.projet, hooks.commandes.analyser(f"python3 {LANCEUR} install")[0], str(self.racine)),
            (str(self.racine.resolve()), "projet", "amont"))

    def test_une_copie_equipee_juge_par_son_propre_verrou(self):
        copie = self.tmp / "worktree"
        (copie / ".socle").mkdir(parents=True)
        (copie / ".socle/engine.lock").write_text('mode = "amont"\n')
        self.assertIsNotNone(self.juger(f"python3 {LANCEUR} install --target {copie}"))
        self.assertIsNone(self.juger(f"python3 {LANCEUR} install --target {copie} --mode amont"))

    def test_la_mise_a_jour_et_le_dossier_temporaire_passent(self):
        self.assertIsNone(self.juger(f"python3 {LANCEUR} install --target . --mode amont"))
        self.assertIsNone(self.juger(f"python3 {LANCEUR} install --target {self.jetable} --adapter python"))
        self.assertIsNone(self.juger(f"cd {self.jetable} && python3 {self.racine}/.socle/socle install --target ."))
        self.assertIsNone(self.juger(f"grep -n 'socle install --target .' {self.racine}/AGENTS.md"))
        self.assertIsNone(hooks.installeur_hors_mode(self.projet, hooks.commandes.analyser("git status")[0]))

    def test_une_cible_que_le_hook_ne_resout_pas_fait_refuser_toute_la_commande(self):
        """Revue du lot : `Path.expanduser` levait sur `~zz`, hors du `try` ;
        le hook sortait en erreur et laissait passer toute la commande, le
        push forcé compris."""
        pousse = "git " + "push --force origin main"
        raison = self.juger(f"python3 {LANCEUR} install --target ~zz; {pousse}")
        self.assertIsNotNone(raison)
        self.assertIn("ne sait pas résoudre", raison)
        self.assertIn("en toutes lettres", raison)
        for cible in ("~zz", "~+", "~zz/x"):
            c = hooks.commandes.analyser(f"python3 {LANCEUR} install --target {cible} --mode amont")[0]
            self.assertEqual(hooks.installeur_hors_mode(self.projet, c, str(self.racine))[2], "", cible)
        # Le dossier de l'utilisateur, lui, se résout.
        self.assertIsNone(self.juger(f"python3 {LANCEUR} install --target ~/jetable-inexistant-socle"))

    def test_une_cible_ecrite_par_une_variable_est_refusee(self):
        """Revue du lot : chaque appel repart d'un shell neuf, où `$D` est
        vide ; la cible serait le dossier courant, le projet."""
        for cmd in (f'python3 {LANCEUR} install --target "$D" --mode amont',
                    f"python3 {LANCEUR} install --target=$D",
                    f'cd "$D" && python3 {self.racine}/.socle/socle install --target .',
                    f'python3 {LANCEUR} install --target "$(pwd)"',
                    f"python3 {LANCEUR} install --target $(pwd)",
                    f"python3 {LANCEUR} install --target `pwd`",
                    f"cd `mktemp -d` && python3 {self.racine}/.socle/socle install"):
            raison = self.juger(cmd)
            self.assertIsNotNone(raison, cmd)
            self.assertIn("ne sait pas résoudre", raison, cmd)
        # Le chemin écrit en toutes lettres passe.
        self.assertIsNone(self.juger(f"cd {self.jetable} && python3 {self.racine}/.socle/socle install --target ."))

    def test_les_options_abregees_sont_refusees(self):
        """Revue du lot : `install --mo amont` passait le hook, qui lit
        `--mode` par son nom entier, et `argparse` l'acceptait."""
        from socle import cli

        analyseur = cli.analyseur()[0]
        for args in (["install", "--mo", "amont"], ["install", "--targ", "/tmp/x"], ["--ro", ".", "state"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit, msg=args):
                analyseur.parse_args(args)
        self.assertEqual(analyseur.parse_args(["install", "--mode", "amont"]).mode, "amont")

    def test_les_arguments_du_socle(self):
        c = hooks.commandes.analyser(f"python3 {LANCEUR} --root . install --target x")[0]
        self.assertEqual(hooks.arguments_socle(c), ["install", "--target", "x"])
        self.assertIsNone(hooks.arguments_socle(hooks.commandes.analyser("ls -la")[0]))


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


class TestHooksGitAuDemarrage(unittest.TestCase):
    """B-0252 : après le redémarrage d'un conteneur cloud, `core.hooksPath`
    valait le chemin absolu de `<racine>/.socle/git-hooks`, et le démarrage
    disait débranchés des hooks qui tiraient ; un chemin vers les hooks d'un
    autre worktree reste un choix local, signalé."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-hookspath-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        self.racine, self.autre = self.dossier / "projet", self.dossier / "autre"
        self.racine.mkdir()
        git(self.racine, "init", "-q", "-b", "main")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python-pytest", "@essai", source=MOTEUR)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "socle", "--no-verify")
        # Un worktree partage la configuration de son dépôt.
        git(self.racine, "worktree", "add", "-q", str(self.autre))

    def chemin(self) -> str:
        return git(self.racine, "config", "--get", "core.hooksPath").strip()

    def demarrer(self) -> str:
        with unittest.mock.patch.dict("os.environ", {hooks.SESSION_CLOUD: ""}), \
                contextlib.redirect_stdout(io.StringIO()) as sortie:
            hooks.session_start(config.Projet.charger(self.racine), {})
        return sortie.getvalue()

    def test_le_chemin_absolu_des_hooks_de_la_racine_les_dit_branches(self):
        self.assertEqual(self.chemin(), ".socle/git-hooks")
        absolu = str((self.racine / ".socle/git-hooks").resolve())
        git(self.racine, "config", "core.hooksPath", absolu)
        self.assertTrue(hooks.installer_hooks_git(self.racine))
        self.assertEqual(self.chemin(), absolu)  # rien n'est récrit
        self.assertNotIn("hooks git non branchés", self.demarrer())

    def test_le_chemin_absolu_des_hooks_d_un_autre_worktree_reste_signale(self):
        ailleurs = str((self.autre / ".socle/git-hooks").resolve())
        git(self.racine, "config", "core.hooksPath", ailleurs)
        self.assertFalse(hooks.installer_hooks_git(self.racine))
        self.assertEqual(self.chemin(), ailleurs)  # le choix local reste
        self.assertIn("!! hooks git non branchés : `git config core.hooksPath .socle/git-hooks`", self.demarrer())
        # Depuis l'autre worktree, ce sont les siens.
        self.assertTrue(hooks.installer_hooks_git(self.autre))


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

    def test_un_corrige_hors_du_dernier_paragraphe_est_un_correctif(self):
        """B-0348 : une ligne `Corrige:` écrite dans un paragraphe à part,
        avant les lignes d'attribution, fait du commit un correctif ; le hook
        le dit comme la CI le jugera (ADR-0109)."""
        from socle import config
        from tests.test_bascule import git

        racine = self.racine
        (racine / "calc.py").write_text("def double(x):\n    return 2 * int(x)\n")
        git(racine, "add", "calc.py")
        projet = config.Projet.charger(racine)
        message = "Double accepte une chaîne\n\nCorrige: T-0001\n\nCo-Authored-By: t <t@t>"
        avert = hooks.correctif_sans_test(projet, message, amendement=False)
        self.assertIsNotNone(avert, "le hook se tait sur un correctif sans test")
        self.assertIn("la CI le refusera (`tests.regression`)", avert)

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
        # Et du code : un correctif de la seule documentation n'est plus jugé
        # (B-0373), le commit nouveau doit encore corriger du code sans test.
        (racine / "calc.py").write_text("def double(x):\n    return 2 * int(x, 10)\n")
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

    def test_une_relance_sur_un_test_rouge_ne_bloque_plus(self):
        """Revue du lot : la signature contenait la sortie de l'outil, dont la
        durée (« Ran N tests in X.XXXs ») change à chaque relance ; un test
        rouge, le cas le plus courant, bloquait encore trois fois."""
        import json

        from socle import config

        compteur = self.racine / config.COMPTEUR_STOP
        self.addCleanup(compteur.unlink, missing_ok=True)
        compteur.unlink(missing_ok=True)
        dossier = self.racine / "tests"
        cree = not dossier.exists()
        dossier.mkdir(exist_ok=True)
        if cree:
            self.addCleanup(shutil.rmtree, dossier, True)
        init = dossier / "__init__.py"
        if not init.exists():
            init.touch()
            self.addCleanup(init.unlink, missing_ok=True)
        rouge = dossier / "test_rouge_socle.py"
        self.addCleanup(rouge.unlink, missing_ok=True)
        # La sortie change à chaque lancement, comme une durée.
        rouge.write_text("import time\nimport unittest\n\n\nclass T(unittest.TestCase):\n"
                         "    def test_rouge(self):\n        self.fail(str(time.time_ns()))\n")
        premier = json.loads(self.appeler(hooks.stop, self.projet, {"session_id": "r", "stop_hook_active": False}))
        self.assertEqual(premier.get("decision"), "block", premier)
        self.assertIn("verify.", premier["reason"])
        relance = json.loads(self.appeler(hooks.stop, self.projet, {"session_id": "r", "stop_hook_active": True}))
        self.assertNotIn("decision", relance)
        self.assertIn("sans changement depuis la tentative précédente", relance["systemMessage"])

    def test_le_refus_sur_des_tests_rouges_n_en_donne_que_l_essentiel(self):
        """B-0290 : le refus recopiait le rapport entier, sortie des tests
        comprise ; il ne donne plus que le nom du contrôle, la première ligne
        utile de chaque test en échec et la commande qui montre tout."""
        import json

        from socle import config

        compteur = self.racine / config.COMPTEUR_STOP
        self.addCleanup(compteur.unlink, missing_ok=True)
        compteur.unlink(missing_ok=True)
        dossier = self.racine / "tests"
        cree = not dossier.exists()
        dossier.mkdir(exist_ok=True)
        if cree:
            self.addCleanup(shutil.rmtree, dossier, True)
        init = dossier / "__init__.py"
        if not init.exists():
            init.touch()
            self.addCleanup(init.unlink, missing_ok=True)
        rouge = dossier / "test_deux_rouges_socle.py"
        self.addCleanup(rouge.unlink, missing_ok=True)
        rouge.write_text("import unittest\n\n\nclass T(unittest.TestCase):\n"
                         "    def test_echoue(self):\n        self.assertEqual(1, 2)\n\n"
                         "    def test_leve(self):\n        raise ValueError('invalide')\n")
        raison = json.loads(self.appeler(hooks.stop, self.projet, {"session_id": "e"}))["reason"]
        self.assertIn("verify.tests", raison)
        self.assertIn("FAIL: test_echoue (tests.test_deux_rouges_socle.T.test_echoue)", raison)
        self.assertIn("ERROR: test_leve (tests.test_deux_rouges_socle.T.test_leve)", raison)
        self.assertIn("`python3 .socle/socle verify --fast`", raison)
        for absent in ("Traceback", "=====", "AssertionError", "self.assertEqual", "memoire.format"):
            self.assertNotIn(absent, raison)

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
        for ident, meta in (("B-0001", ""), ("T-0001", " · besoin : B-0001"), ("JA-0002", " · après : B-0001")):
            f = backlog / f"{ident}-essai.md"
            f.write_text(f"<!-- socle: couche=backlog zone=publique -->\n# {ident} — Le sujet {ident}\n\n"
                         f"> statut : ouvert · origine : fichier:calc.py{meta}\n\nPour l'essai.\n")
            self.addCleanup(f.unlink)
        transcript = Path(tempfile.mkdtemp()) / "t.jsonl"
        transcript.write_text(json.dumps({"type": "assistant", "message": {"content": "Fait."}}))
        sortie = self.appeler(hooks.exiger_recap, self.projet, {"session_id": "o", "transcript_path": str(transcript)})
        self.assertIn("prochain jalon : JA-0002 — Le sujet JA-0002 ; besoins ouverts : B-0001", sortie)
        self.assertIn("tâche prête : T-0001 — Le sujet T-0001", sortie)

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


class TestFinDeTourSurLesSeulsTests(unittest.TestCase):
    """B-0182 : la fin de tour ne lançait les étapes rapides que si un
    fichier des `sources` de l'adaptateur avait changé ; un fichier de tests
    que l'adaptateur déclare, hors de ses sources, compte aussi."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-fin-tests-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        (self.racine / "app").mkdir()
        (self.racine / "app/calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", "--no-verify"],
                       cwd=self.racine, check=True)

    def lancees(self) -> bool:
        from socle import context as contexte, verification
        from socle.report import Rapport

        projet = config.Projet.charger(self.racine)
        projet.adaptateur["sources"] = ["app/**/*.py"]  # les tests hors des sources
        projet.adaptateur.setdefault("tests", {})["exclude"] = ["tests/donnees/**"]
        appels = []
        with unittest.mock.patch.object(verification, "etapes_rapides", lambda *a, **k: appels.append(1)), \
                unittest.mock.patch.object(contexte, "executer", return_value=Rapport()), \
                unittest.mock.patch.object(hooks, "exiger_recap", return_value=0), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            hooks.stop(projet, {"session_id": "t"})
        return bool(appels)

    def test_un_fichier_de_tests_change_lance_les_etapes_rapides(self):
        self.assertFalse(self.lancees())  # rien n'a changé
        (self.racine / "tests").mkdir(exist_ok=True)
        (self.racine / "tests/test_calc.py").write_text("import unittest\n")
        self.assertTrue(self.lancees())
        self.assertEqual(config.Projet.charger(self.racine).fichiers_de_tests(["tests/test_calc.py", "notes.txt"]),
                         ["tests/test_calc.py"])

    def test_un_autre_fichier_ne_les_lance_pas(self):
        (self.racine / "notes.txt").write_text("rien\n")
        self.assertFalse(self.lancees())

    def test_un_fichier_de_tests_exclu_ne_les_lance_pas(self):
        # Revue du lot : les exclusions de `[tests]` valent, comme pour
        # `Projet.designes`.
        (self.racine / "tests/donnees").mkdir(parents=True)
        (self.racine / "tests/donnees/test_jeu.py").write_text("x = 1\n")
        self.assertFalse(self.lancees())


class TestFinDeTourApresUneMiseAJour(unittest.TestCase):
    """B-0196 : entre une mise à jour du socle et le push de sa demande, la
    fin de tour refusait l'arbre par une ligne et une commande de remise par
    fichier protégé changé (26 sur chess). Elle le dit en une ligne ; un
    fichier protégé que la mise à jour n'a pas posé garde la sienne, et
    `socle check` les liste tous (ADR-0077)."""

    COMMUNE = "une mise à jour du socle attend sa demande : la poser"
    SKILL = ".claude/skills/socle-resume/SKILL.md"
    HOOK = ".socle/git-hooks/pre-commit"

    def setUp(self):
        # Le projet a le moteur d'avant : une copie du moteur avec un module
        # de plus et un module changé, et des copies des gabarits d'avant.
        self.racine = Path(tempfile.mkdtemp(prefix="socle-maj-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        ancien = Path(tempfile.mkdtemp(prefix="socle-ancien-"))
        self.addCleanup(shutil.rmtree, ancien, ignore_errors=True)
        shutil.copytree(MOTEUR / "socle", ancien / "socle", ignore=shutil.ignore_patterns("__pycache__"))
        (ancien / "socle/ancien.py").write_text('"""Un module que la version nouvelle retire."""\n')
        utils = ancien / "socle/utils.py"
        utils.write_text(utils.read_text() + "# la version d'avant\n")
        self.git("init", "-q", "-b", "main")
        (self.racine / "app").mkdir()
        (self.racine / "app/calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=ancien)
        for chemin in (self.SKILL, self.HOOK):
            p = self.racine / chemin
            p.write_text(p.read_text() + "# la version d'avant\n")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", "--no-verify")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.racine, check=True, capture_output=True)

    def mettre_a_jour(self, source=MOTEUR):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=source)

    def relancer_depuis_le_projet(self):
        # `python3 .socle/socle install --target .` : le moteur reste tel
        # quel, le verrou se récrit.
        self.mettre_a_jour(self.racine / ".socle/engine")

    def fin_de_tour(self) -> str:
        import json

        from socle import verification

        sortie = io.StringIO()
        with unittest.mock.patch.object(verification, "etapes_rapides", lambda *a, **k: None), \
                contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(io.StringIO()):
            hooks.stop(config.Projet.charger(self.racine), {"session_id": "t"})
        reponse = json.loads(sortie.getvalue())
        self.assertEqual(reponse["decision"], "block")
        return reponse["reason"]

    def contexte(self):
        from socle import context as contexte, utils as outils

        return contexte.Contexte(config.Projet.charger(self.racine), etage="agent",
                                 base=outils.base_de_travail(self.racine))

    def erreurs(self) -> list:
        from socle import checks_ratchet
        from socle.report import Rapport

        r = Rapport()
        checks_ratchet.proteges(self.contexte(), r)
        return r.erreurs("protege.fichiers")

    def poses(self) -> set[str]:
        from socle import checks_ratchet

        return checks_ratchet.poses_par_la_mise_a_jour(self.contexte())

    def test_la_fin_de_tour_dit_la_mise_a_jour_en_une_ligne(self):
        self.mettre_a_jour()
        poses = sorted(c.chemin for c in self.erreurs())
        self.assertEqual(poses, sorted([".socle/engine.lock", ".socle/engine/socle/ancien.py",
                                        ".socle/engine/socle/utils.py", self.HOOK, self.SKILL]))
        self.assertLessEqual(set(poses), self.poses())
        self.assertIn(".socle/socle", self.poses())  # le lanceur, que l'empreinte couvre
        raison = self.fin_de_tour()
        self.assertEqual(raison.count(self.COMMUNE), 1)
        self.assertIn("5 fichier(s) protégé(s) qu'elle a posé(s)", raison)
        self.assertIn("--only protege.fichiers` les liste avec leurs empreintes", raison)
        self.assertNotIn("git restore", raison)
        for chemin in poses:
            self.assertNotIn(chemin + " —", raison)
        # La liste reste entière à la demande, sans commande de remise, et
        # `socle approve` les trouve tous.
        from socle.report import Rapport

        liste = Rapport(constats=self.erreurs()).texte()
        self.assertNotIn(self.COMMUNE, liste)
        self.assertNotIn("git restore", liste)
        for chemin in poses:
            self.assertIn(f"{chemin} — fichier protégé posé par la mise à jour du socle", liste)
        self.assertEqual(cli.fichiers_a_approuver(config.Projet.charger(self.racine)), poses)
        # Le verrou nomme ce que l'installeur a posé hors du moteur.
        installes = config.Projet.charger(self.racine).lock["installed"]
        self.assertEqual(sorted(installes), sorted([self.HOOK, self.SKILL]))
        # Relancé, l'installeur ne change plus ces fichiers : leurs entrées
        # restent, puisqu'elles valent encore.
        self.mettre_a_jour()
        self.assertEqual(config.Projet.charger(self.racine).lock["installed"], installes)
        self.assertEqual(self.fin_de_tour().count(self.COMMUNE), 1)

    def test_un_fichier_que_la_mise_a_jour_n_a_pas_pose_garde_sa_ligne(self):
        # Changé avant l'installeur, qui le fusionne ensuite : il ne compte
        # pas à la mise à jour. Changés après : non plus.
        reglages = self.racine / ".claude/settings.json"
        reglages.write_text(reglages.read_text().replace("{", '{"permissions": {"allow": ["Bash(*)"]},', 1))
        self.mettre_a_jour()
        self.assertNotIn(".claude/settings.json", config.Projet.charger(self.racine).lock["installed"])
        politique = self.racine / ".socle/policy.toml"
        politique.write_text(politique.read_text() + "# changé pendant la mise à jour\n")
        skill = self.racine / self.SKILL
        skill.write_text(skill.read_text() + "# changé après la mise à jour\n")
        raison = self.fin_de_tour()
        self.assertEqual(raison.count(self.COMMUNE), 1)
        self.assertIn("4 fichier(s) protégé(s) qu'elle a posé(s)", raison)
        for chemin in (".socle/policy.toml", self.SKILL):
            self.assertIn(f"{chemin} — fichier protégé modifié sans validation humaine", raison)
            self.assertIn(f"git restore --source=HEAD --staged --worktree -- {chemin}", raison)
        self.assertIn(".claude/settings.json — fichier protégé modifié sans validation humaine", raison)

    def test_hors_mise_a_jour_chaque_fichier_garde_sa_ligne(self):
        for chemin in (".socle/policy.toml", self.HOOK):
            p = self.racine / chemin
            p.write_text(p.read_text() + "# changé hors mise à jour\n")
        self.assertEqual(self.poses(), set())
        raison = self.fin_de_tour()
        self.assertNotIn(self.COMMUNE, raison)
        for chemin in (".socle/policy.toml", self.HOOK):
            self.assertIn(f"git restore --source=HEAD --staged --worktree -- {chemin}", raison)

    def test_un_moteur_change_apres_la_mise_a_jour_ne_regroupe_rien(self):
        self.mettre_a_jour()
        utils = self.racine / ".socle/engine/socle/utils.py"
        utils.write_text(utils.read_text() + "# changé après la mise à jour\n")
        self.assertEqual(self.poses(), set())
        raison = self.fin_de_tour()
        self.assertNotIn(self.COMMUNE, raison)
        self.assertIn("git restore --source=HEAD --staged --worktree -- .socle/engine/socle/utils.py", raison)
        self.assertIn("git restore --source=HEAD --staged --worktree -- .socle/engine.lock", raison)

    def test_l_installeur_relance_depuis_le_projet_ne_couvre_pas_un_moteur_change(self):
        """Revue du lot : lancé depuis le projet, l'installeur garde le moteur
        tel quel et récrit le verrou avec son empreinte ; un module changé
        par l'agent passait dans la ligne commune, sans sa remise."""
        utils = self.racine / ".socle/engine/socle/utils.py"
        utils.write_text(utils.read_text() + "# reformaté par l'agent\n")
        self.relancer_depuis_le_projet()
        self.assertNotIn("copied", config.Projet.charger(self.racine).lock)
        self.assertEqual(self.poses(), set())
        raison = self.fin_de_tour()
        self.assertNotIn(self.COMMUNE, raison)
        self.assertIn("git restore --source=HEAD --staged --worktree -- .socle/engine/socle/utils.py", raison)

    def test_une_relance_depuis_le_projet_apres_la_mise_a_jour(self):
        # Le moteur copié, inchangé : la relance garde la mise à jour.
        self.mettre_a_jour()
        self.relancer_depuis_le_projet()
        verrou = config.Projet.charger(self.racine).lock
        self.assertEqual(verrou.get("copied"), verrou["fingerprint"])
        self.assertEqual(self.fin_de_tour().count(self.COMMUNE), 1)
        # Un module changé ensuite, puis une relance : plus rien ne compte à
        # la mise à jour, et le module garde sa ligne.
        rapport = self.racine / ".socle/engine/socle/report.py"
        rapport.write_text(rapport.read_text() + "# reformaté par l'agent\n")
        self.relancer_depuis_le_projet()
        self.assertNotIn("copied", config.Projet.charger(self.racine).lock)
        self.assertEqual(self.poses(), set())
        raison = self.fin_de_tour()
        self.assertNotIn(self.COMMUNE, raison)
        self.assertIn("git restore --source=HEAD --staged --worktree -- .socle/engine/socle/report.py", raison)


class TestHooksGitPendantUneMiseAJour(unittest.TestCase):
    """B-0357, ADR-0115 : chez chess, le 26 novembre, la mise à jour a migré
    le backlog dans l'arbre ; le hook avant commit, qui juge l'index avec le
    moteur neuf de l'arbre, a refusé le commit de la demande seule pour le
    backlog d'avant, déjà commité, et le hook avant push de même. Pendant
    une mise à jour pas encore commitée, ils ne refusent que les constats
    que le commit ou le push apporte."""

    def setUp(self):
        self.enterContext(unittest.mock.patch.dict(os.environ))
        os.environ.pop("CLAUDECODE", None)
        self.racine = Path(tempfile.mkdtemp(prefix="socle-maj-git-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        ancien = Path(tempfile.mkdtemp(prefix="socle-ancien-"))
        self.addCleanup(shutil.rmtree, ancien, ignore_errors=True)
        shutil.copytree(MOTEUR / "socle", ancien / "socle", ignore=shutil.ignore_patterns("__pycache__"))
        utils = ancien / "socle/utils.py"
        utils.write_text(utils.read_text() + "# la version d'avant\n")
        self.git("init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=ancien)
        self.journal = next((self.racine / "memory/journal").glob("*.md")).read_text().split("## ", 2)[1].split()[0]
        # Un lot au format d'avant ADR-0083, commité sous le moteur d'avant :
        # le moteur neuf le refuse (`memoire.formes`).
        self.lot("B-0001")
        self.git("add", "-A")
        self.git("commit", "-qm", "base", "--no-verify")
        self.git("checkout", "-q", "-b", "maj")

    def git(self, *args) -> str:
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.racine,
                              check=True, capture_output=True, text=True).stdout

    def lot(self, ident: str) -> str:
        chemin = f"memory/backlog/{ident}-essai.md"
        (self.racine / chemin).write_text(f"<!-- socle: couche=backlog zone=publique -->\n# {ident} — Un lot d'avant"
                                          f"\n\n> statut : ouvert · origine : {self.journal} · forme : lot\n\n"
                                          "Pour l'essai.\n")
        return chemin

    def mettre_a_jour(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)

    def poser_la_demande(self) -> str:
        """La demande de la mise à jour, qui cite le fichier protégé changé
        avec son empreinte, seule dans l'index."""
        from socle import fingerprint as empreinte
        from socle.selftest import DEMANDE_BONNE

        cite = empreinte.fichier(self.racine / ".socle/engine/socle/utils.py")
        chemin = "memory/requests/D-0001-mise-a-jour.md"
        (self.racine / chemin).parent.mkdir(parents=True, exist_ok=True)
        (self.racine / chemin).write_text(DEMANDE_BONNE.replace(
            "- B-0001 — le sujet du backlog qui demande d'ajouter une fonction triple au module.",
            f"- `.socle/engine/socle/utils.py` — `{cite}`"))
        self.git("add", chemin)
        return chemin

    def avant_commit(self) -> tuple[int, str]:
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            code = hooks.git_pre_commit(config.Projet.charger(self.racine))
        return code, sortie.getvalue()

    def avant_push(self) -> tuple[int, str]:
        from socle import verification

        tete = self.git("rev-parse", "HEAD").strip()
        sortie = io.StringIO()
        with unittest.mock.patch("sys.stdin", io.StringIO(f"refs/heads/maj {tete} refs/heads/maj {'0' * 40}\n")), \
                unittest.mock.patch.object(verification, "etapes_rapides", lambda *a, **k: None), \
                contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            code = hooks.git_pre_push(config.Projet.charger(self.racine))
        return code, sortie.getvalue()

    def test_le_hook_avant_commit_accepte_la_demande_seule_et_refuse_un_constat_qu_il_apporte(self):
        self.mettre_a_jour()
        self.assertTrue(hooks.mise_a_jour_en_cours(config.Projet.charger(self.racine)))
        self.poser_la_demande()
        code, sortie = self.avant_commit()
        self.assertEqual(code, 0, sortie)
        self.assertIn("mise à jour du moteur en cours, pas encore commitée : 1 constat(s) déjà présent(s)", sortie)
        self.git("add", self.lot("B-0002"))
        code, sortie = self.avant_commit()
        self.assertEqual(code, 1)
        self.assertIn("memory/backlog/B-0002-essai.md", sortie)
        self.assertNotIn("memory/backlog/B-0001-essai.md", sortie)
        self.assertIn("Commit refusé", sortie)

    def test_le_hook_avant_push_accepte_le_commit_de_la_demande_seule(self):
        self.mettre_a_jour()
        self.poser_la_demande()
        self.git("commit", "-qm", "La demande de la mise à jour", "--no-verify")
        code, sortie = self.avant_push()
        self.assertEqual(code, 0, sortie)
        self.assertIn("laissé(s) à la CI", sortie)
        # Un constat que le push apporte reste refusé.
        self.git("add", self.lot("B-0002"))
        self.git("commit", "-qm", "Un lot d'avant de plus", "--no-verify")
        code, sortie = self.avant_push()
        self.assertEqual(code, 1)
        self.assertIn("memory/backlog/B-0002-essai.md", sortie)

    def test_hors_d_une_mise_a_jour_et_en_mode_amont_un_constat_deja_commite_est_refuse(self):
        """Le témoin sain : sans copie du moteur changée, rien ne s'écarte ;
        en mode amont, où le moteur est la source, non plus."""
        self.poser_la_demande()
        self.assertFalse(hooks.mise_a_jour_en_cours(config.Projet.charger(self.racine)))
        code, sortie = self.avant_commit()
        self.assertEqual(code, 1)
        self.assertIn("memory/backlog/B-0001-essai.md", sortie)
        self.assertNotIn("mise à jour du moteur en cours", sortie)
        self.mettre_a_jour()
        self.git("reset", "-q")
        self.poser_la_demande()
        with unittest.mock.patch.object(config.Projet, "mode", new_callable=unittest.mock.PropertyMock,
                                        return_value=config.MODE_AMONT):
            self.assertFalse(hooks.mise_a_jour_en_cours(config.Projet.charger(self.racine)))
            code, sortie = self.avant_commit()
        self.assertEqual(code, 1)
        self.assertIn("memory/backlog/B-0001-essai.md", sortie)

    def test_l_ecart_compte_les_constats_un_a_un(self):
        """Une erreur de plus, sous le même contrôle, le même chemin et le
        même message qu'une erreur déjà commitée, reste refusée."""
        from socle.report import Rapport

        rapport, reference = Rapport(), Rapport()
        for _ in range(2):
            rapport.erreur("memoire.formes", "écrit `forme : lot`", "memory/backlog/B-0001-essai.md", 3)
        reference.erreur("memoire.formes", "écrit `forme : lot`", "memory/backlog/B-0001-essai.md", 2)
        rapport.avertir("memoire.formes", "écrit `forme : lot`", "memory/backlog/B-0001-essai.md", 3)
        self.assertEqual(hooks.ecarter_deja_commites(rapport, reference), 1)
        self.assertEqual(len(rapport.erreurs()), 1)
        self.assertEqual(len(rapport.constats), 2)


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

    def test_les_outils_recoivent_le_reste_du_delai_du_demarrage(self):
        """ADR-0105 (revue de B-0202, B-0219) : l'historique d'abord, au plus
        120 secondes et 10 pour s'arrêter ; les outils ont le reste des 270
        du démarrage, au moins 140, et les 270 quand l'historique n'a rien à
        faire. Le tout laisse à l'état 30 secondes sous la borne du hook que
        pose l'installeur."""
        import json
        import types

        horloge = types.SimpleNamespace(t=1000.0)
        horloge.monotonic = lambda: horloge.t
        lancer, recu = subprocess.run, {}

        def historique(racine, fin):
            recu["historique"] = fin - horloge.t
            horloge.t += recu["duree"]
            return []

        def commande(c, *args, **kwargs):
            if not kwargs.get("shell"):
                return lancer(c, *args, **kwargs)  # git, pour la marque
            recu["outils"] = kwargs["timeout"]
            return subprocess.CompletedProcess(c, 0, "", "")

        def demarrer(duree_historique: float):
            recu.clear()
            recu["duree"] = duree_historique
            (config.chemin_trace(self.racine).parent / "outils-installes").unlink(missing_ok=True)
            with unittest.mock.patch.object(hooks, "time", horloge), \
                    unittest.mock.patch.object(hooks, "completer_historique", historique), \
                    unittest.mock.patch.object(hooks.subprocess, "run", commande), \
                    unittest.mock.patch.dict("os.environ", {hooks.SESSION_CLOUD: "true"}), \
                    contextlib.redirect_stdout(io.StringIO()):
                hooks.session_start(self.projet, {})
            return recu["historique"], recu["outils"]

        # L'historique prend son pire : son délai, puis son arrêt.
        self.assertEqual(demarrer(hooks.DELAI_HISTORIQUE + hooks.ARRET_HISTORIQUE), (270, 140))
        # Un clone complet : l'historique ne prend rien, les outils ont tout.
        self.assertEqual(demarrer(0), (270, 270))
        reglages = json.loads((MOTEUR / "socle/templates/settings.json").read_text(encoding="utf-8"))
        borne = reglages["hooks"]["SessionStart"][0]["hooks"][0]["timeout"]
        self.assertLessEqual(hooks.DELAI_DEMARRAGE + 30, borne)


class TestHistoriqueEnSessionCloud(unittest.TestCase):
    """B-0202 : le clone d'une session cloud était superficiel, et
    `memoire.references` refusait le premier commit, faute des commits que
    le journal cite ; le hook de démarrage complète l'historique."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-historique-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        self.origine, self.clone = self.dossier / "origine", self.dossier / "clone"
        self.origine.mkdir()
        git(self.origine, "init", "-q", "-b", "main")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.origine, "python-pytest", "@essai", source=MOTEUR)
        for n in range(3):
            (self.origine / f"f{n}.txt").write_text(f"{n}\n")
            git(self.origine, "add", "-A")
            git(self.origine, "commit", "-qm", f"commit {n}", "--no-verify")
        # `file://` : un clone local ignorerait `--depth`.
        git(self.dossier, "clone", "-q", "--depth", "1", f"file://{self.origine}", str(self.clone))
        self.assertTrue(self.superficiel())

    def superficiel(self) -> bool:
        return git(self.clone, "rev-parse", "--is-shallow-repository").strip() == "true"

    def completer(self, cloud: str = "true") -> list[str]:
        with unittest.mock.patch.dict("os.environ", {hooks.SESSION_CLOUD: cloud}):
            return hooks.completer_historique(self.clone)

    def test_hors_session_cloud_le_clone_reste_superficiel(self):
        self.assertEqual(self.completer(""), [])
        self.assertTrue(self.superficiel())

    def test_en_session_cloud_le_demarrage_complete_l_historique(self):
        projet = config.Projet.charger(self.clone)
        projet.adaptateur["ci_setup"] = "      - name: Outils\n        run: true\n"
        sortie = io.StringIO()
        with unittest.mock.patch.dict("os.environ", {hooks.SESSION_CLOUD: "true"}), \
                contextlib.redirect_stdout(sortie):
            hooks.session_start(projet, {})
        self.assertIn("historique du clone complété (session cloud) : `git fetch --unshallow`", sortie.getvalue())
        self.assertIn("== ", sortie.getvalue())  # l'état suit
        self.assertFalse(self.superficiel())
        self.assertEqual(git(self.clone, "rev-list", "--count", "HEAD").strip(), "3")
        # Complet, il n'y a plus rien à faire, ni à dire.
        self.assertEqual(self.completer(), [])

    def test_un_echec_se_dit_sans_bloquer_et_se_retente(self):
        shutil.rmtree(self.origine)
        lignes = self.completer()
        self.assertEqual(len(lignes), 1)
        self.assertTrue(lignes[0].startswith("!! clone superficiel : `git fetch --unshallow` a rendu 128"), lignes)
        self.assertLessEqual(len(lignes[0].encode()), 400)
        self.assertTrue(self.superficiel())
        self.assertIn("a rendu 128", self.completer()[0])

    def test_le_delai_epuise_se_dit_sans_bloquer_ni_laisser_de_verrou(self):
        """Un vrai fetch, ralenti par un relais devant `git upload-pack` :
        tué d'emblée au délai, git laissait `.git/shallow.lock`, et le clone
        restait superficiel, la commande relancée à la main comprise (revue
        de B-0202)."""
        for n in range(40):
            (self.origine / "lourd.bin").write_bytes(os.urandom(20_000))
            git(self.origine, "add", "-A")
            git(self.origine, "commit", "-qm", f"lourd {n}", "--no-verify")
        shutil.rmtree(self.clone)
        git(self.dossier, "clone", "-q", "--depth", "1", f"file://{self.origine}", str(self.clone))
        relais = self.dossier / "relais.py"
        relais.write_text(
            "import subprocess, sys, time\n"
            "p = subprocess.Popen(['git', 'upload-pack'] + sys.argv[1:], stdout=subprocess.PIPE)\n"
            "while True:\n"
            "    b = p.stdout.read1(2048)\n"
            "    if not b:\n"
            "        break\n"
            "    sys.stdout.buffer.write(b)\n"
            "    sys.stdout.buffer.flush()\n"
            "    time.sleep(0.2)\n"
            "sys.exit(p.wait())\n", encoding="utf-8")
        git(self.clone, "config", "remote.origin.uploadpack", f"{sys.executable} {relais}")
        debut = time.monotonic()
        with unittest.mock.patch.dict("os.environ", {hooks.SESSION_CLOUD: "true"}):
            lignes = hooks.completer_historique(self.clone, time.monotonic() + 3)
        self.assertEqual(len(lignes), 1)
        self.assertIn("`git fetch --unshallow` dépasse le délai du démarrage", lignes[0])
        self.assertFalse((self.clone / ".git" / "shallow.lock").exists())
        self.assertLess(time.monotonic() - debut, 3 + hooks.ARRET_HISTORIQUE + 5)
        self.assertTrue(self.superficiel())
        # Le remède que la ligne donne marche, et le démarrage suivant aussi.
        git(self.clone, "config", "--unset", "remote.origin.uploadpack")
        self.assertIn("historique du clone complété", self.completer()[0])
        self.assertFalse(self.superficiel())

    def ralentir(self) -> str:
        """Un clone superficiel neuf d'une origine lourde, dont le vrai fetch
        passe par un relais lent devant `git upload-pack` (plus d'une minute
        pour l'historique entier). Rend le réglage qui pose le relais."""
        for n in range(8):
            (self.origine / "lourd.bin").write_bytes(os.urandom(100_000))
            git(self.origine, "add", "-A")
            git(self.origine, "commit", "-qm", f"lourd {n}", "--no-verify")
        shutil.rmtree(self.clone)
        git(self.dossier, "clone", "-q", "--depth", "1", f"file://{self.origine}", str(self.clone))
        relais = self.dossier / "relais.py"
        relais.write_text(
            "import subprocess, sys, time\n"
            "p = subprocess.Popen(['git', 'upload-pack'] + sys.argv[1:], stdout=subprocess.PIPE)\n"
            "while True:\n"
            "    b = p.stdout.read1(2048)\n"
            "    if not b:\n"
            "        break\n"
            "    sys.stdout.buffer.write(b)\n"
            "    sys.stdout.buffer.flush()\n"
            "    time.sleep(0.2)\n"
            "sys.exit(p.wait())\n", encoding="utf-8")
        reglage = f"{sys.executable} {relais}"
        git(self.clone, "config", "remote.origin.uploadpack", reglage)
        return reglage

    def reprendre(self) -> tuple[list[str], float]:
        """Le démarrage suivant, dans le même conteneur, avec le délai entier
        du démarrage ; le délai court d'une reprise réduit à une seconde."""
        debut = time.monotonic()
        with unittest.mock.patch.object(hooks, "DELAI_HISTORIQUE_REPRISE", 1):
            lignes = self.completer()
        return lignes, time.monotonic() - debut

    def test_un_delai_depasse_ne_se_repaie_pas_au_demarrage_suivant(self):
        """T-0078 (B-0219, ADR-0105) : un fetch qui pend coûtait son délai
        entier à chaque démarrage du même conteneur, une reprise ou un
        compactage ; marqué, il ne se retente que sous un délai court."""
        self.assertEqual(hooks.DELAI_HISTORIQUE_REPRISE, 15)
        self.ralentir()
        with unittest.mock.patch.dict("os.environ", {hooks.SESSION_CLOUD: "true"}):
            premier = hooks.completer_historique(self.clone, time.monotonic() + 2)
        self.assertIn("`git fetch --unshallow` dépasse le délai du démarrage", premier[0])
        lignes, duree = self.reprendre()
        # Le délai entier aurait laissé finir ce fetch, en plus d'une minute.
        self.assertLess(duree, 1 + hooks.ARRET_HISTORIQUE + 5)
        self.assertEqual(len(lignes), 1)
        self.assertTrue(lignes[0].startswith("!! clone superficiel : `git fetch --unshallow` dépasse le délai du "
                                             "démarrage ; le relancer avant de commiter"), lignes)
        self.assertFalse((self.clone / ".git" / "shallow.lock").exists())
        self.assertTrue(self.superficiel())
        # La commande que la ligne dit de relancer à la main complète l'historique.
        git(self.clone, "config", "--unset", "remote.origin.uploadpack")
        git(self.clone, "fetch", "--quiet", "--unshallow")
        self.assertFalse(self.superficiel())

    def delai_du_fetch(self, fin: float, marque: bool = False) -> float:
        """Le délai que `completer_historique` passe au fetch, lu sur un fetch
        factice qui réussit aussitôt ; le reste de git est le vrai."""
        if marque:
            chemin = config.chemin_trace(self.clone).parent / "historique-echoue"
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text("!! clone superficiel\n", encoding="utf-8")
        delais, vrai = [], subprocess.Popen

        class Fetch:
            returncode = 0

            def communicate(self, timeout=None):
                delais.append(timeout)
                return "", ""

        def popen(args, *a, **k):
            return Fetch() if list(args[:2]) == ["git", "fetch"] else vrai(args, *a, **k)

        with unittest.mock.patch.dict("os.environ", {hooks.SESSION_CLOUD: "true"}), \
                unittest.mock.patch.object(hooks.subprocess, "Popen", popen):
            lignes = hooks.completer_historique(self.clone, fin)
        self.assertIn("historique du clone complété", lignes[0])
        (delai,) = delais
        return delai

    def test_au_premier_demarrage_le_fetch_recoit_ses_120_secondes(self):
        """T-0158 (B-0331, ADR-0105) : sans marque d'échec, le fetch reçoit
        120 secondes, ou le reste du délai du démarrage s'il est moindre ; le
        délai court de la reprise y laisserait superficiel tout clone dont
        l'historique prend plus de 15 secondes."""
        self.assertEqual((hooks.DELAI_HISTORIQUE, hooks.DELAI_HISTORIQUE_REPRISE), (120, 15))
        self.assertEqual(self.delai_du_fetch(time.monotonic() + hooks.DELAI_DEMARRAGE), 120)
        reste = self.delai_du_fetch(time.monotonic() + 50)
        self.assertTrue(45 < reste <= 50, reste)
        # Le délai court n'est que celui d'un démarrage marqué.
        self.assertEqual(self.delai_du_fetch(time.monotonic() + hooks.DELAI_DEMARRAGE, marque=True), 15)

    def test_un_code_non_nul_ne_se_repaie_pas_non_plus(self):
        """T-0078 : un fetch qui a rendu un code non nul se marque de même ; le
        démarrage suivant, où l'origine répond mais pend, ne lui redonne pas
        son délai entier."""
        relais = self.ralentir()
        git(self.clone, "config", "remote.origin.uploadpack", "false")
        premier = self.completer()
        self.assertTrue(premier[0].startswith("!! clone superficiel : `git fetch --unshallow` a rendu 128"), premier)
        git(self.clone, "config", "remote.origin.uploadpack", relais)
        lignes, duree = self.reprendre()
        self.assertLess(duree, 1 + hooks.ARRET_HISTORIQUE + 5)
        self.assertIn("`git fetch --unshallow` dépasse le délai du démarrage ; le relancer avant de commiter", lignes[0])
        self.assertTrue(self.superficiel())


DECISION_ARBRE = """<!-- socle: couche=decisions zone=publique -->
# ADR-0002 — Écrire dans le worktree

> statut : acceptée · date : 2026-11-11

## Décision

Le travail se fait dans un worktree.
"""


class TestArbreJuge(Projet):
    """B-0164 : un hook de l'agent juge l'arbre où l'action a lieu. Une
    entrée créée dans un worktree du même dépôt, que la copie principale
    n'a pas encore, n'y est pas une référence inventée."""

    def setUp(self):
        super().setUp()
        dehors = Path(tempfile.mkdtemp(prefix="socle-arbre-"))
        self.addCleanup(shutil.rmtree, dehors, ignore_errors=True)
        self.dehors = dehors.resolve()
        # Là où Claude Code pose le worktree d'un sous-agent : sous la copie principale.
        self.arbre = self.racine.resolve() / ".claude/worktrees/arbre"
        git(self.racine, "worktree", "add", "-q", "-b", "travail", str(self.arbre))
        (self.arbre / "memory/decisions/ADR-0002-ecrire-dans-le-worktree.md").write_text(
            DECISION_ARBRE, encoding="utf-8")

    def hook(self, entree: dict, evt: str = "pre-tool-use") -> tuple[int, str]:
        import json
        import sys

        sortie = io.StringIO()
        with unittest.mock.patch.object(sys, "stdin", io.StringIO(json.dumps(entree))), \
                contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            code = cli.main(["--root", str(self.racine), "hook", evt])
        return code, sortie.getvalue()

    def bash(self, commande: str, cwd: Path) -> str:
        return self.hook({"tool_name": "Bash", "cwd": str(cwd), "session_id": "s",
                          "tool_input": {"command": commande}})[1]

    def ecrire(self, ou: Path, cwd: Path) -> dict:
        return {"tool_name": "Write", "cwd": str(cwd), "session_id": "s",
                "tool_input": {"file_path": str(ou / "docs/suite.md"),
                               "content": "La suite applique ADR-0002.\n"}}


    def test_un_dossier_illisible_rend_la_racine(self):
        """En CI, le dossier des réglages d'un autre utilisateur ne se lit
        pas : le lire lève une erreur de permission, et un hook qui planterait
        laisserait passer la commande qu'il devait juger."""
        from unittest import mock
        entree = {"tool_name": "Write", "tool_input": {"file_path": "/root/.claude/settings.json"}}
        with mock.patch.object(Path, "is_dir", side_effect=PermissionError(13, "Permission denied")):
            self.assertEqual(hooks.arbre_juge(self.racine, entree), self.racine)

    def test_une_entree_creee_dans_le_worktree_s_y_cite(self):
        code, sortie = self.hook(self.ecrire(self.arbre, self.arbre))
        self.assertEqual((code, sortie), (0, ""))
        # Le même fichier, depuis la session principale : l'arbre du fichier.
        code, sortie = self.hook(self.ecrire(self.arbre, self.racine))
        self.assertEqual((code, sortie), (0, ""))

    def test_la_copie_principale_reste_jugee_contre_sa_memoire(self):
        code, sortie = self.hook(self.ecrire(self.racine, self.arbre))
        self.assertIn('"deny"', sortie)
        self.assertIn("ADR-0002", sortie)

    def test_depuis_le_worktree_la_copie_principale_reste_protegee(self):
        """Revue de B-0164 : le dossier courant ne lève aucun refus. Ce que
        la racine de la session refuse, elle le refuse depuis un worktree."""
        racine = self.racine.resolve()
        options = "--no-" + "verify"
        for commande in (f"echo x > {racine}/.socle/policy.toml",
                         f"cd {racine} && rm .socle/policy.toml",
                         f"git -C {racine} commit {options} -m x"):
            for cwd in (racine, self.arbre):
                self.assertIn('"deny"', self.bash(commande, cwd), (commande, cwd))
        # Un fichier protégé du worktree lui-même reste refusé, d'où qu'on écrive.
        for cwd in (racine, self.arbre):
            code, sortie = self.hook({"tool_name": "Write", "cwd": str(cwd), "session_id": "s",
                                      "tool_input": {"file_path": str(self.arbre / ".socle/policy.toml"),
                                                     "content": "x"}})
            self.assertIn('"deny"', sortie, cwd)
            self.assertIn("policy.toml", sortie)
            self.assertIn('"deny"', self.bash("echo x > .socle/policy.toml", self.arbre))

    def test_la_fin_de_tour_juge_la_racine_de_la_session(self):
        """Revue de B-0164 : une faute dans la copie principale bloque la fin
        de tour, que le dossier courant soit la racine ou un worktree."""
        notes = self.racine / "docs/notes.md"
        notes.write_text(notes.read_text() + "\nVoir F-0099.\n")
        for cwd in (self.racine.resolve(), self.arbre):
            code, sortie = self.hook({"session_id": "s", "cwd": str(cwd), "stop_hook_active": False}, "stop")
            self.assertIn('"block"', sortie, cwd)
            self.assertIn("F-0099", sortie)

    def test_l_arbre_juge(self):
        racine = self.racine.resolve()
        self.assertEqual(hooks.arbre_juge(racine, {"cwd": str(self.arbre / "docs")}), self.arbre)
        self.assertEqual(hooks.arbre_juge(racine, {"cwd": str(racine)}), racine)
        self.assertEqual(hooks.arbre_juge(racine, {}), racine)
        # Un dossier hors de tout dépôt, ou un autre dépôt : rien ne change.
        self.assertEqual(hooks.arbre_juge(racine, {"cwd": str(self.dehors)}), racine)
        autre = self.dehors / "autre"
        (autre / ".socle").mkdir(parents=True)
        git(autre, "init", "-q")
        self.assertEqual(hooks.arbre_juge(racine, {"cwd": str(autre)}), racine)
        # Un fichier écrit l'emporte sur le dossier courant, même s'il est neuf.
        entree = {"tool_name": "Edit", "cwd": str(racine),
                  "tool_input": {"file_path": str(self.arbre / "neuf/dossier/x.md")}}
        self.assertEqual(hooks.arbre_juge(racine, entree), self.arbre)
        # Un worktree du même dépôt sans le socle : la racine.
        nu = self.dehors / "nu"
        git(self.racine, "worktree", "add", "-q", "--detach", str(nu), "HEAD")
        shutil.rmtree(nu / ".socle")
        self.assertEqual(hooks.arbre_juge(racine, {"cwd": str(nu)}), racine)

