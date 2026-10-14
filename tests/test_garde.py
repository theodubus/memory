"""B-0044, L2 : le hook de l'agent juge ce qu'une commande fait, découpée en
commandes simples, et non le texte qu'elle cite. La table vient du banc de
la passe de recul : 25 contournements y passaient, et 6 citations y étaient
refusées à tort."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import commands as commandes, config, hooks, installer as installeur

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
# En morceaux : ce fichier ne lance rien, il ne fait que citer.
L = ".socle/" + "socle"
G = "gi" + "t"
P = "pu" + "sh"


def B(commande: str):
    return ("Bash", {"command": commande})


REFUS = [
    ("force-push", B(f"{G} {P} --force origin travail")),
    ("git -C . push --force", B(f"{G} -C . {P} --force origin travail")),
    ("git -c x=y push -f", B(f"{G} -c color.ui=never {P} -f origin travail")),
    ("push -fu, drapeaux groupés", B(f"{G} {P} -fu origin travail")),
    ("suppression distante par :ref", B(f"{G} {P} origin :travail")),
    ("push vers HEAD:refs/heads/main", B(f"{G} {P} origin HEAD:refs/heads/main")),
    ("push main", B(f"{G} {P} origin main")),
    ("twine upload", B("python3 -m twine upload dist/*")),
    ("gem push", B(f"gem {P} socle-0.1.gem")),
    ("gh api DELETE", B("gh api -X DELETE repos/o/r/git/refs/heads/travail")),
    ("gh pr merge", B("gh pr merge 3 --squash")),
    ("rm -rf ~/", B("rm -rf ~/")),
    ("rm -r -f /", B("rm -r -f /")),
    ("rm -rf .git", B("rm -rf .git")),
    ("bash -c", B("bash -c 'rm -rf /'")),
    ("answer", B(f"python3 {L} answer D-0001 valider")),
    ("answer, lanceur entre guillemets", B(f'python3 "{L}" answer D-0001 valider')),
    ("answer après cd .socle", B("cd .socle && python3 socle answer D-0001 valider")),
    ("answer, drapeaux du relais dans une autre commande",
     B(f"python3 {L} answer D-0001 valider; echo --relayed --quote-file x")),
    ("approve, lanceur entre guillemets", B(f'python3 "{L}" approve --text x --oui')),
    ("approve par python -m socle", B("PYTHONPATH=moteur python3 -m socle approve --text x")),
    ("écriture >", B("echo x > .socle/policy.toml")),
    ("écriture 1>", B("echo x 1> .socle/policy.toml")),
    ("écriture >|", B("echo x >| .socle/policy.toml")),
    ("rm -rf du dossier .socle", B("rm -rf .socle")),
    ("mv du dossier .github", B("mv .github /tmp/gh")),
    ("git rm d'un fichier protégé", B(f"{G} rm -q .socle/policy.toml")),
    ("git checkout -- d'un fichier protégé", B(f"{G} checkout HEAD~1 -- .socle/policy.toml")),
    ("sed --in-place", B("sed --in-place 's/3/9/' .socle/policy.toml")),
    ("env rm", B("env LC_ALL=C rm .socle/policy.toml")),
    ("cd puis >", B("cd .socle && echo x > policy.toml")),
    ("réglage local de Claude Code, par le shell", B("echo '{}' > .claude/settings.local.json")),
    ("réglage local de Claude Code, par Write", ("Write", {"file_path": ".claude/settings.local.json",
                                                         "content": '{"disableAllHooks": true}'})),
    ("réglages de l'utilisateur, hors du dépôt", ("Write", {"file_path": "/root/.claude/settings.json",
                                                           "content": "{}"})),
    ("commit qui saute les hooks", B(f"{G} commit -q -m x --no-verify")),
    ("commit -n, drapeaux groupés", B(f"{G} commit -qnm x")),
    ("push qui saute les hooks, par -C .", B(f"{G} -C . {P} --no-verify origin travail")),
    ("merge qui saute les hooks", B(f"{G} merge --no-verify travail")),
    ("outil GitHub qui commite sans hook", ("mcp__github__create_or_update_file", {"path": "x", "branch": "main"})),
]

PASSE = [
    ("message de commit qui cite answer",
     B(f'{G} commit -m "Consigner la réponse : python3 {L} answer D-0001 valider --relayed"')),
    ("heredoc de doc qui cite approve", B(f"cat > docs/guide.md <<'EOF'\nL'humain lance python3 {L} approve --text x\nEOF")),
    ("echo qui cite push --force", B(f'echo "ne jamais faire {G} {P} --force"')),
    ("grep qui cite reset --hard", B(f"grep -rn '{G} reset --hard' docs/")),
    ("commit qui cite rm -rf /", B(f'{G} commit -m "doc: interdire rm -rf / dans les scripts"')),
    ("heredoc python qui cite push --force", B(f"cat > /tmp/x.py <<'EOF'\nCAS = ['{G} {P} --force origin travail']\nEOF")),
    ("push de la branche de travail", B(f"{G} {P} -u origin travail")),
    ("commit sans hooks dans un dépôt jetable, après cd", B(f"cd /tmp/jetable && {G} commit -q -m x --no-verify")),
    ("commit sans hooks dans un dépôt jetable, par -C", B(f"{G} -C /tmp/jetable commit -q -m x --no-verify")),
    ("commit dont le message cite le drapeau", B(f'{G} commit -m "doc: jamais --no-verify"')),
    ("push -n, à blanc", B(f"{G} {P} -n origin travail")),
    ("push vers une branche de maintenance", B(f"{G} {P} origin maintenance-x")),
    ("push d'une branche nommée main-fix", B(f"{G} {P} origin main-fix")),
    ("relais avec sa citation", B(f"python3 {L} answer D-0001 valider --relayed --by Théo --quote-file /tmp/c.txt")),
    ("verrouiller la mémoire privée", B(f"python3 {L} prive verrouiller")),
    ("rm d'un fichier ordinaire", B("rm -f /tmp/x.txt && touch calc.py")),
    ("lire un réglage", B("cat .claude/settings.json")),
]


class TestGarde(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.racine = Path(tempfile.mkdtemp(prefix="socle-garde-"))
        env = {**os.environ, "HOME": str(cls.racine), "GIT_CONFIG_NOSYSTEM": "1"}
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=cls.racine, check=True, env=env)
        (cls.racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(cls.racine, "python", "@essai", source=MOTEUR)
        env = {**env, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t"}
        env.pop("CLAUDECODE", None)
        subprocess.run(["git", "add", "-A"], cwd=cls.racine, check=True, env=env)
        subprocess.run(["git", "commit", "-qm", "installation", "--no-verify"], cwd=cls.racine, check=True, env=env)
        subprocess.run(["git", "checkout", "-q", "-b", "travail"], cwd=cls.racine, check=True)
        cls.projet = config.Projet.charger(cls.racine)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.racine, ignore_errors=True)

    def decide(self, outil, args) -> str:
        if "file_path" in args and not args["file_path"].startswith("/"):
            args = {**args, "file_path": str(self.racine / args["file_path"])}
        flux = io.StringIO()
        with contextlib.redirect_stdout(flux):
            hooks.pre_tool_use(self.projet, {"session_id": "garde", "tool_name": outil, "tool_input": args})
        return "refus" if '"deny"' in flux.getvalue() else "passe"

    def test_les_contournements_sont_refuses(self):
        for nom, (outil, args) in REFUS:
            with self.subTest(nom):
                self.assertEqual(self.decide(outil, args), "refus")

    def test_ce_qui_cite_ou_travaille_passe(self):
        for nom, (outil, args) in PASSE:
            with self.subTest(nom):
                self.assertEqual(self.decide(outil, args), "passe")

    def test_le_contournement_se_juge_sur_le_depot_vise(self):
        # B-0023 : le dossier de départ de la commande décide du dépôt visé.
        nv = "--no-" + "verify"
        commit, = commandes.analyser(f"{G} commit -q -m x {nv}")
        self.assertEqual(hooks.contournement(self.racine, commit), f"git commit {nv}")
        self.assertEqual(hooks.contournement(self.racine, commit, str(self.racine / "tests")), f"git commit {nv}")
        self.assertIsNone(hooks.contournement(self.racine, commit, "/tmp"))
        a_blanc, = commandes.analyser(f"{G} {P} -n origin travail")
        self.assertIsNone(hooks.contournement(self.racine, a_blanc))

    def test_ecriture_protegee_d_un_dossier(self):
        self.assertIn(".socle/", hooks.ecriture_protegee(self.projet, "rm -rf .socle"))
        self.assertIsNone(hooks.ecriture_protegee(self.projet, "touch calc.py"))

    def test_un_push_sans_destination_depuis_la_branche_par_defaut(self):
        subprocess.run(["git", "checkout", "-q", "main"], cwd=self.racine, check=True)
        try:
            self.assertEqual(self.decide(*B(f"{G} {P}")), "refus")
        finally:
            subprocess.run(["git", "checkout", "-q", "travail"], cwd=self.racine, check=True)
        self.assertEqual(self.decide(*B(f"{G} {P}")), "passe")

    def test_le_refus_d_une_action_externe_la_rend_a_l_humain(self):
        # D-0026 : une demande validée ne débloque pas l'action ; le refus le
        # dit, et demande la commande exacte pour l'humain.
        for outil, args in (B(f"{G} {P} origin main"), ("mcp__github__merge_pull_request", {})):
            with self.subTest(outil):
                flux = io.StringIO()
                with contextlib.redirect_stdout(flux):
                    hooks.pre_tool_use(self.projet, {"session_id": "garde", "tool_name": outil, "tool_input": args})
                self.assertIn("une demande validée ne la débloque pas", flux.getvalue())
        flux = io.StringIO()
        with contextlib.redirect_stdout(flux):
            hooks.pre_tool_use(self.projet, {"session_id": "garde", "tool_name": "Bash",
                                             "tool_input": {"command": f"{G} {P} origin main"}})
        self.assertIn("sa commande exacte", flux.getvalue())


class TestDecoupage(unittest.TestCase):
    def test_analyser_suit_separateurs_redirections_et_cd(self):
        simples = commandes.analyser("cd .socle && echo x > policy.toml; ls 2>&1 | head")
        self.assertEqual([c.argv for c in simples], [["cd", ".socle"], ["echo", "x"], ["ls"], ["head"]])
        self.assertEqual(simples[1].redirige, ["policy.toml"])
        self.assertEqual(simples[1].chemin("policy.toml"), ".socle/policy.toml")

    def test_jetons_et_heredocs(self):
        self.assertEqual(commandes.jetons('echo "a b" > f'), ["echo", "a b", ">", "f"])
        self.assertEqual(commandes.sans_heredocs("cat <<'EOF'\ncorps\nEOF\nls"), "cat <<'EOF'\nls")

    def test_prefixes_et_bash_c(self):
        self.assertEqual([c.argv for c in commandes.analyser("x=1 sudo -u root env A=b rm f")], [["rm", "f"]])
        self.assertIn(["rm", "-rf", "/"], [c.argv for c in commandes.analyser("bash -c 'rm -rf /'")])

    def test_options_drapeaux_et_sous_commande_git(self):
        options, args = commandes.options_et_arguments(["-fu", "origin", "--", "-x"])
        self.assertEqual((options, args), (["-fu"], ["origin", "-x"]))
        self.assertTrue(commandes.drapeau(["-fu"], "f"))
        self.assertTrue(commandes.drapeau(["--force-with-lease=x"], "", ("--force-with-lease",)))
        self.assertFalse(commandes.drapeau(["-u"], "f"))
        self.assertEqual(commandes.git_sous_commande(["git", "-C", ".", "-c", "a=b", "push", "-f"]), ("push", ["-f"]))


class TestJugements(unittest.TestCase):
    def test_programme(self):
        self.assertEqual(commandes.analyser("/usr/bin/git status")[0].programme, "git")

    def test_ecrits(self):
        c = commandes.analyser(f"{G} mv a .socle/b")[0]
        self.assertEqual(hooks.ecrits(c), ["a", ".socle/b"])

    def test_irreversible_et_commande_humaine(self):
        racine = Path(".")
        self.assertEqual(hooks.irreversible(racine, commandes.analyser(f"{G} {P} -fu o b")[0]), "push forcé")
        self.assertIsNone(hooks.irreversible(racine, commandes.analyser("echo push")[0]))
        h = hooks.commande_humaine(commandes.analyser(f'python3 "{L}" --root . answer D-1 x')[0])
        self.assertEqual(h[0], "answer")
        self.assertIsNone(hooks.commande_humaine(commandes.analyser("grep -n 'socle answer' AGENTS.md")[0]))


if __name__ == "__main__":
    unittest.main()
