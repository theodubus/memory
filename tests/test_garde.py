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
import unittest.mock
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
    ("approve, lanceur entre guillemets", B(f'python3 "{L}" approve --text x --yes')),
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
    ("verrouiller la mémoire privée", B(f"python3 {L} private lock")),
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

    def test_un_chemin_protege_que_le_shell_developperait_est_refuse(self):
        """B-0171 : le hook jugeait les chemins tels qu'ils sont tapés ;
        `echo x > $F`, `rm .socle/pol*` ou un `pushd` passaient."""
        illisible = "un chemin que le hook ne sait pas développer"
        protege = "écriture d'un fichier protégé"
        with unittest.mock.patch.dict(os.environ, {"TMPDIR": "/tmp", "HOME": str(self.racine)}):
            for nom in ("F", "X", "D"):
                os.environ.pop(nom, None)
            for cmd, raison in (
                    ("echo x > $F", illisible),
                    ("echo x > \"${F}\"", illisible),
                    ("echo x > .socle/$X", illisible),
                    ("echo x > $(mktemp)", illisible),
                    ("echo x > `cat cible`", illisible),
                    ("cd $D && echo x > policy.toml", illisible),
                    ("cd /tmp && echo x > $X", illisible),
                    ("echo x > ~/$X", illisible),
                    ("F=.socle/policy.toml; echo x > $F", protege),
                    ("export F=.socle/policy.toml && echo x >> \"$F\"", protege),
                    ("D=.socle; cd $D && echo x > policy.toml", protege),
                    ("F=/tmp/x; F=.socle/policy.toml; rm $F", protege),
                    ("echo x > $PWD/.socle/policy.toml", protege),
                    ("echo x > ~/.socle/policy.toml", protege),
                    ("rm .socle/pol*", protege),
                    ("rm -rf .so*", protege),
                    ("sed -i s/3/9/ .socle/p?licy.toml", protege),
                    ("echo x > .socle/[op]olicy.toml", protege),
                    ("echo x > .socle/{policy,notes}.toml", protege),
                    ("echo x > .socle/git-hooks/post-*", protege),
                    ("pushd .socle && echo x > policy.toml", protege),
                    ("pushd /tmp && pushd .. && popd && popd && echo x > .socle/policy.toml", protege),
                    ("cd .socle && cd /tmp && cd - && echo x > policy.toml", protege),
                    ("F=.claude/settings.local.json; echo '{}' > $F", "réglages de Claude Code"),
            ):
                with self.subTest(cmd):
                    self.assertIn(raison, hooks.refus_bash(self.projet, cmd) or "")
                    self.assertEqual(self.decide(*B(cmd)), "refus")
            self.assertEqual(hooks.ecriture_protegee(self.projet, "rm .socle/pol*"),
                             ".socle/policy.toml, par `.socle/pol*`")
            self.assertEqual(hooks.ecritures_jugees(self.projet, "echo x > $X; echo y > notes.txt; rm .socle/pol*"),
                             [("illisible", "`$X`"), ("protege", ".socle/policy.toml, par `.socle/pol*`")])
            # Un jugement qui lèverait laisserait passer la commande : il refuse.
            with unittest.mock.patch.object(hooks.glob, "glob", side_effect=OSError("illisible")):
                self.assertEqual(hooks.ecritures_jugees(self.projet, "rm -f build/*.o"),
                                 [("illisible", "`build/*.o`")])

    def test_un_chemin_developpe_hors_du_projet_ou_libre_passe(self):
        """B-0171 : ce qui ne se développe pas passe quand une part écrite en
        toutes lettres le place hors du projet ; une variable affectée, un
        motif ou une accolade qui ne nomment aucun fichier protégé passent."""
        # Un dossier voisin du projet : le dossier temporaire, lui, le contient,
        # et `/tmp/$X` y pourrait viser le projet.
        ailleurs = f"{self.racine}-ailleurs"
        with unittest.mock.patch.dict(os.environ, {"TMPDIR": ailleurs}):
            for nom in ("F", "X"):
                os.environ.pop(nom, None)
            for cmd in (f"echo x > {ailleurs}/$X", "echo x > \"$TMPDIR/x\"", f"ls > {ailleurs}/x-$(date +%s).txt",
                        f"F={ailleurs}/x; echo y > $F", "F=notes.txt; echo y > \"$F\"",
                        f"export F={ailleurs}/y && rm -f $F", "rm -f build/*.o *.pyc",
                        "echo x > .socle/{notes,brouillon}.txt", f"cd {ailleurs} && echo x > rapport-$X.txt",
                        f"pushd {ailleurs} && echo x > rapport-$X.txt; popd",
                        "pushd .socle && popd && echo x > policy.toml", "F=; rm -f $F", "rm -rf */policy.toml",
                        'sed -i -e "s/$OLD/$NEW/" notes.md'):
                with self.subTest(cmd):
                    self.assertIsNone(hooks.refus_bash(self.projet, cmd))
            self.assertIn("ne sait pas développer", hooks.refus_bash(self.projet, f"echo x > {self.racine}/../$X"))

    def test_remise_en_etat_d_un_fichier_protege(self):
        """D-0098 (B-0165) : l'agent remet un fichier protégé changé par
        erreur à son état du dernier commit, et supprime un fichier apparu
        sous un chemin protégé que git ne suit pas ; rien d'autre."""
        politique = self.racine / ".socle/policy.toml"
        avant = politique.read_text()
        apparu = self.racine / ".socle/git-hooks/post-merge"
        politique.write_text(avant + "# changé par erreur\n")
        apparu.write_text("#!/bin/sh\n")
        self.addCleanup(politique.write_text, avant)
        self.addCleanup(apparu.unlink)
        passe = [f"{G} restore --source=HEAD --staged --worktree -- .socle/policy.toml",
                 f"{G} restore --source=HEAD .socle/policy.toml .github/CODEOWNERS",
                 f"{G} checkout HEAD -- .github/CODEOWNERS",
                 f"cd .socle && {G} checkout HEAD -- policy.toml",
                 "rm .socle/git-hooks/post-merge",
                 "rm -f .socle/git-hooks/post-merge"]
        for commande in passe:
            with self.subTest(commande):
                self.assertEqual(self.decide(*B(commande)), "passe")
                c, = [c for c in commandes.analyser(commande) if c.programme in ("git", "rm")]
                self.assertIsNone(hooks.remise_en_etat(self.projet, c)[1])
        refus = [f"{G} restore .socle/policy.toml",
                 f"{G} checkout -- .socle/policy.toml",
                 f"{G} restore --source=HEAD~1 -- .socle/policy.toml",
                 f"{G} checkout HEAD~1 -- .socle/policy.toml",
                 f"{G} checkout main -- .socle/policy.toml",
                 f"{G} restore --source=HEAD -- .",
                 f"{G} restore --source=HEAD -- .socle",
                 f"{G} checkout HEAD -- .github",
                 f"{G} restore --source=HEAD -- '.socle/git-hooks/*'",
                 f"{G} restore --source=HEAD -- .socle/git-hooks/$NOM",
                 f"{G} -C . restore --source=HEAD -- .socle/policy.toml",
                 "rm .socle/policy.toml",
                 "rm .socle/git-hooks/post-*",
                 # La revue de B-0165 : une remise admise ne dispense que de
                 # ce qu'elle remet, ses redirections se jugent.
                 f"{G} restore --source=HEAD -- .socle/policy.toml > .socle/git-hooks/pre-commit",
                 f"{G} restore --source=HEAD -- .socle/policy.toml > .github/CODEOWNERS",
                 f"{G} checkout HEAD -- .socle/policy.toml > .claude/settings.local.json",
                 "rm .socle/git-hooks/post-merge > .github/CODEOWNERS",
                 f"{G} restore --source=HEAD -- .socle/policy.toml .socle/policy.toml > .socle/policy.toml",
                 "rm .socle/git-hooks/post-merge .claude/settings.local.json",
                 # Un autre dépôt, un autre environnement.
                 f"GIT_DIR=/tmp/autre/.git {G} checkout HEAD -- .socle/policy.toml",
                 f"env GIT_WORK_TREE=/tmp {G} restore --source=HEAD -- .socle/policy.toml",
                 f"export GIT_DIR=/tmp/autre/.git; {G} checkout HEAD -- .socle/policy.toml",
                 # `checkout` sans `--`, chemins lus dans un fichier.
                 f"{G} checkout HEAD~1 .socle/policy.toml",
                 f"{G} checkout main .socle/policy.toml",
                 f"{G} checkout .socle/policy.toml",
                 f"{G} restore --source=HEAD --pathspec-from-file=/tmp/chemins.txt",
                 f"{G} checkout HEAD --pathspec-from-file=/tmp/chemins.txt --pathspec-file-nul"]
        for commande in refus:
            with self.subTest(commande):
                self.assertEqual(self.decide(*B(commande)), "refus")
        self.assertIsNone(hooks.remise_en_etat(self.projet, commandes.analyser(f"{G} restore calc.py")[0]))
        self.assertEqual(self.decide(*B(f"{G} checkout HEAD .socle/policy.toml")), "passe")
        self.assertEqual(self.decide(*B(f"{G} checkout travail")), "passe")

    def test_remise_en_etat_des_reglages_de_claude_code_refusee(self):
        """La réponse de Théo sur B-0165, « Exclure » : les réglages de Claude
        Code ne se remettent pas par l'agent ; le refus est celui des
        réglages. Un autre fichier protégé se remet toujours."""
        for commande in (f"{G} restore --source=HEAD -- .claude/settings.json",
                         f"{G} checkout HEAD -- .claude/settings.json"):
            with self.subTest(commande):
                self.assertIn("les réglages de Claude Code commandent ses hooks", self.raison(commande))
        self.assertEqual(self.decide(*B(f"{G} restore --source=HEAD -- .socle/policy.toml")), "passe")

    def test_remise_en_etat_jugee_dans_les_deux_arbres(self):
        """B-0164 et B-0165 : une remise lancée dans un worktree se juge
        contre la racine et contre lui ; refusée dans l'un, elle est
        refusée (une demande en attente que seul le worktree porte)."""
        arbre = self.racine / ".claude/worktrees/remise"
        subprocess.run(["git", "worktree", "add", "-q", "-b", "remise", str(arbre)], cwd=self.racine, check=True)
        self.addCleanup(subprocess.run, ["git", "worktree", "remove", "--force", str(arbre)], cwd=self.racine)

        def decide(commande):
            flux = io.StringIO()
            with contextlib.redirect_stdout(flux):
                hooks.pre_tool_use(self.projet, {"session_id": "garde", "tool_name": "Bash", "cwd": str(arbre),
                                                 "tool_input": {"command": commande}})
            return flux.getvalue()

        self.assertNotIn('"deny"', decide(f"{G} checkout HEAD -- .socle/policy.toml"))
        self.assertIn('"deny"', decide(f"{G} checkout HEAD~1 .socle/policy.toml"))
        (arbre / "memory/requests/D-0001-politique.md").write_text(
            "# D-0001 — Changer la politique\n\n> date : 2026-11-11\n\n## Question\n\n`.socle/policy.toml` change.\n")
        self.assertIn("D-0001", decide(f"{G} checkout HEAD -- .socle/policy.toml"))

    def test_checkout_sans_tirets_ecrit_ses_chemins(self):
        """La revue de B-0165 : `git checkout <révision> <chemins>` sans `--`
        écrit ses chemins comme avec."""
        c, = commandes.analyser(f"{G} checkout HEAD~1 .socle/policy.toml")
        self.assertEqual(hooks.ecrits(c), [".socle/policy.toml"])
        self.assertEqual(hooks.ecriture_protegee(self.projet, f"{G} checkout HEAD~1 .socle/policy.toml"),
                         ".socle/policy.toml")
        self.assertEqual(commandes.analyser(f"GIT_DIR=x env -u Y {G} status")[0].prefixe,
                         ["GIT_DIR=x", "env", "-u", "Y"])

    def raison(self, commande: str) -> str:
        flux = io.StringIO()
        with contextlib.redirect_stdout(flux):
            hooks.pre_tool_use(self.projet, {"session_id": "garde", "tool_name": "Bash",
                                             "tool_input": {"command": commande}})
        return flux.getvalue()

    def demande(self, nom: str, cite: str, reponse: str | None = None) -> Path:
        d = self.racine / f"memory/requests/{nom}.md"
        d.write_text(f"# {nom[:6]} — Changer la politique\n\n> date : 2026-11-11\n\n## Question\n\n{cite} change.\n")
        self.addCleanup(d.unlink, missing_ok=True)
        if reponse is not None:
            r = self.racine / f"memory/requests/{nom}.answer.toml"
            r.write_text(f'reponse = "{reponse}"\npar = "Théo"\n')
            self.addCleanup(r.unlink, missing_ok=True)
        return d

    def test_remise_en_etat_d_un_fichier_cite_par_une_demande_en_attente(self):
        """D-0098 : un fichier protégé que cite une demande en attente porte
        peut-être la modification que l'humain y soumet ; il ne se remet pas."""
        self.demande("D-0001-politique", "`.socle/policy.toml`")
        remise = f"{G} restore --source=HEAD --staged --worktree -- .socle/policy.toml"
        self.assertIn("est cité par la demande D-0001, en attente", self.raison(remise))
        self.assertEqual(self.decide(*B(f"{G} checkout HEAD -- .github/CODEOWNERS")), "passe")

    def test_remise_en_etat_d_un_fichier_dont_une_demande_cite_le_dossier(self):
        """La revue de B-0165 : une demande qui cite le dossier épargne ses
        fichiers ; un autre chemin qui commence comme lui, non."""
        self.demande("D-0001-politique", "Tout `.socle/` ")
        self.assertIn("D-0001", self.raison(f"{G} checkout HEAD -- .socle/policy.toml"))
        self.assertEqual(self.decide(*B(f"{G} checkout HEAD -- .github/CODEOWNERS")), "passe")
        self.assertTrue(hooks._cite_chemin("le dossier `.github/**`", ".github/CODEOWNERS"))
        self.assertFalse(hooks._cite_chemin("`.github/workflows/socle.yml`", ".github/CODEOWNERS"))

    def test_remise_en_etat_sous_une_demande_validee_pas_encore_commitee(self):
        """La revue de B-0165 : une demande validée dont la réponse attend
        son commit, ou dont l'empreinte citée est celle du fichier présent,
        épargne le fichier ; validée et commitée, plus."""
        from socle import fingerprint as empreinte

        self.demande("D-0001-politique", "`.socle/policy.toml`", "valider")
        self.assertIn("D-0001", self.raison(f"{G} checkout HEAD -- .socle/policy.toml"))
        self.demande("D-0001-politique", "`.socle/policy.toml`", "refuser")
        self.assertEqual(self.decide(*B(f"{G} checkout HEAD -- .socle/policy.toml")), "passe")
        # Validée et commitée : le fichier n'est épargné que si l'arbre porte
        # la version qu'elle approuve.
        codeowners = self.racine / ".github/CODEOWNERS"
        avant = codeowners.read_text()
        self.addCleanup(codeowners.write_text, avant)
        codeowners.write_text(avant + "* @autre\n")
        cite = empreinte.courte(empreinte.fichier(codeowners))
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t"}
        env.pop("CLAUDECODE", None)
        self.demande("D-0002-codeowners", f"`.github/CODEOWNERS` et `{cite}`", "valider")
        subprocess.run(["git", "add", "memory/requests"], cwd=self.racine, check=True, env=env)
        subprocess.run(["git", "commit", "-qm", "D-0002", "--no-verify"], cwd=self.racine, check=True, env=env)
        self.assertIn("D-0002", self.raison(f"{G} checkout HEAD -- .github/CODEOWNERS"))
        codeowners.write_text(avant + "* @erreur\n")
        self.assertEqual(self.decide(*B(f"{G} checkout HEAD -- .github/CODEOWNERS")), "passe")

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

    def test_analyser_suit_les_variables_affectees_et_pushd(self):
        """B-0171 : une affectation seule vaut pour la suite, devant une
        commande pour elle seule ; `pushd`, `popd` et `cd -` se suivent."""
        simples = commandes.analyser("F=a; export G=b H; I=c ls; read J; echo > $F")
        self.assertEqual(simples[-1].affectations, [("F", "a"), ("G", "b"), ("J", None)])
        simples = commandes.analyser("pushd .socle && echo > a; pushd /tmp; popd; popd; echo > b; cd x; cd -")
        self.assertEqual([(c.programme, c.dossier) for c in simples],
                         [("pushd", ""), ("echo", ".socle"), ("pushd", ".socle"), ("popd", "/tmp"),
                          ("popd", ".socle"), ("echo", ""), ("cd", ""), ("cd", "x")])
        self.assertEqual(commandes.analyser("cd x; cd -; ls")[-1].dossier, "")

    def test_developper_comme_le_shell(self):
        variables = {"HOME": "/maison", "F": "/tmp/f"}
        I = commandes.INCONNU
        self.assertEqual(commandes.developper("~/x", variables), ("/maison/x", []))
        self.assertEqual(commandes.developper("$F.bak", variables), ("/tmp/f.bak", []))
        self.assertEqual(commandes.developper("${F}/y", variables), ("/tmp/f/y", []))
        self.assertEqual(commandes.developper("a/$X/b", variables), (f"a/{I}/b", ["$X"]))
        self.assertEqual(commandes.developper("${F:-z}", variables), (I, ["${F:-z}"]))
        self.assertEqual(commandes.developper("x-$(date)`id`$1$", variables)[1], ["$(date)", "`id`", "$1", "$"])
        self.assertEqual(commandes.developper("prix$/€", variables), ("prix$/€", []))
        c = commandes.analyser("G=$F/g; read H; echo > $G")[-1]
        self.assertEqual(commandes.variables_de(c, variables)["G"], "/tmp/f/g")
        self.assertEqual(commandes.variables_de(c, variables)["H"], I)

    def test_accolades(self):
        self.assertEqual(commandes.accolades("a{b,c{d,e}}f"), ["abf", "acdf", "acef"])
        self.assertEqual(commandes.accolades("x{1..3}"), ["x1", "x2", "x3"])
        self.assertEqual(commandes.accolades("${F}{a}"), ["${F}{a}"])
        self.assertEqual(commandes.accolades("x{1..100000}"), ["x{1..100000}"])

    def test_un_motif_du_shell_croise_un_motif_de_chemin(self):
        for shell, chemin, dessous, attendu in (
                (".socle/pol*", ".socle/policy.toml", False, True),
                (".socle/p?licy.[st]oml", ".socle/policy.toml", False, True),
                (".socle/[!p]olicy.toml", ".socle/policy.toml", False, False),
                ("*/policy.toml", ".socle/policy.toml", False, False),  # `*` ne rend pas le `.` d'un nom
                (".so*", ".socle/policy.toml", False, False),
                (".so*", ".socle/policy.toml", True, True),
                (".socle/pol*", ".socle/policy.toml", True, True),
                ("build/*.o", ".socle/**", True, False),
                (".socle/git-hooks/post-*", ".socle/git-hooks/**", False, True),
                ("memory/requests/D-*.toml", "memory/requests/*.answer.toml", False, True),
                ("x/*.toml", "**/.claude/settings.json", False, False),
                (".claude/sett*", "**/.claude/settings.json", False, True)):
            with self.subTest(shell=shell, chemin=chemin):
                self.assertEqual(commandes.se_croisent(shell, chemin, dessous), attendu)

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
        c = commandes.analyser("cd .socle && echo x > $F")[-1]
        self.assertEqual((hooks.ecrits(c), hooks.ecrits_bruts(c)), ([".socle/$F"], ["$F"]))
        # B-0171 : le script d'un `sed -i` ou d'un `perl -i` n'est pas un
        # chemin écrit ; une variable qu'il cite ne fait rien refuser.
        for cmd in ('sed -i -e "s/$A/b/" -e s/c/d/ f', "sed -ne s/a/b/p -i f", "sed -i -f $SCRIPT f",
                    "sed --expression=s/a/b/ -i f", 'perl -i -p -e "s/$x/y/" f', "perl -pi -e s/a/b/ f",
                    "sed -i.bak s/a/b/ f", "sed -i -- s/a/b/ f"):
            with self.subTest(cmd):
                self.assertEqual(hooks.ecrits(commandes.analyser(cmd)[0]), ["f"])

    def test_irreversible_et_commande_humaine(self):
        racine = Path(".")
        self.assertEqual(hooks.irreversible(racine, commandes.analyser(f"{G} {P} -fu o b")[0]), "push forcé")
        self.assertIsNone(hooks.irreversible(racine, commandes.analyser("echo push")[0]))
        h = hooks.commande_humaine(commandes.analyser(f'python3 "{L}" --root . answer D-1 x')[0])
        self.assertEqual(h[0], "answer")
        self.assertIsNone(hooks.commande_humaine(commandes.analyser("grep -n 'socle answer' AGENTS.md")[0]))


if __name__ == "__main__":
    unittest.main()
