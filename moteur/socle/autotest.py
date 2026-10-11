"""Auto-test du dispositif : un garde-fou qu'on n'a jamais vu échouer ne
prouve rien.

On fabrique un petit projet Python, on y installe le moteur courant, puis on
injecte un à un les défauts connus du cadrage. Chacun doit être attrapé par
le contrôle prévu, à l'étage prévu, en passant par le vrai point d'entrée
(hook de l'agent, hook git, commande de CI). Des témoins sains doivent passer,
sans quoi un contrôle qui échoue toujours passerait pour un contrôle qui
marche.

Chaque cas tourne dans un clone jetable du projet de base, avec un `origin`
comme dans la vraie vie : la base des contrôles est `origin/main`.
"""

from __future__ import annotations

import json
import re
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from socle.rapport import Rapport

CALC = '''"""Calculs du projet d'essai."""

FACTEUR = 2


def double(x):
    return FACTEUR * x
'''
TEST_CALC = '''import unittest

from calc import double


class TestCalc(unittest.TestCase):
    def test_double(self):
        self.assertEqual(double(2), 4)
'''
DOC_CALC = """# Calcul

`double` multiplie par <!-- valeur:facteur -->2<!-- /valeur -->, la
constante `FACTEUR` de `calc.py`.
"""
GARDE_FOUS_ESSAI = '''
[[docmap]]
code = ["calc.py"]
docs = ["docs/calc.md"]

[[values]]
name = "facteur"
file = "calc.py"
regex = '^FACTEUR = (\\d+)'
'''
CANONIQUE_ESSAI = """
## F-0001 — `double` multiplie par la constante du module

> statut : mesuré · preuve : fichier:tests/test_calc.py

Le test unitaire l'établit.
"""
CANONIQUE_PRIVEE = """<!-- socle: couche=canonique zone=privee -->
# Mémoire canonique privée

## PF-0001 — Le module de calcul servira au projet Mistral

> statut : supposé · source : F-0001
"""
FILTRE_ESSAI = """import base64, sys
donnees = sys.stdin.buffer.read()
if sys.argv[1] == "clean":
    sys.stdout.buffer.write(donnees if donnees.startswith(b"ESSAI:") else b"ESSAI:" + base64.b64encode(donnees))
else:
    sys.stdout.buffer.write(base64.b64decode(donnees[6:]) if donnees.startswith(b"ESSAI:") else donnees)
"""
BACKLOG_ESSAI = """
## B-0001 — Ajouter une fonction triple

> statut : ouvert · origine : {journal}

Demandé pour l'essai.
"""


@dataclass
class Cas:
    id: str
    defaut: str
    etage: str
    controle: str
    fonction: Callable


class Atelier:
    """Un projet d'essai : un dépôt `origine` et des clones jetables."""

    def __init__(self, moteur: Path, bavard: bool):
        self.moteur = moteur
        self.bavard = bavard
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-autotest-"))
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
        self.env.update({
            "GIT_AUTHOR_NAME": "autotest", "GIT_AUTHOR_EMAIL": "autotest@socle",
            "GIT_COMMITTER_NAME": "autotest", "GIT_COMMITTER_EMAIL": "autotest@socle",
            "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(self.dossier),
        })
        self.n = 0

    def run(self, cwd: Path, *args, entree: str | None = None, env: dict | None = None):
        e = dict(self.env)
        if env:
            e.update(env)
        return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, input=entree, env=e)

    def git(self, cwd, *args, env=None):
        r = self.run(cwd, "git", *args, env=env)
        if r.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} : {r.stderr.strip()}")
        return r.stdout

    def socle(self, cwd, *args, entree=None, env=None):
        return self.run(cwd, sys.executable, str(cwd / ".socle/socle"), *args, entree=entree, env=env)

    def preparer(self):
        origine = self.dossier / "origine"
        origine.mkdir()
        self.git(origine, "init", "-q", "-b", "main")
        (origine / "calc.py").write_text(CALC)
        (origine / "tests").mkdir()
        (origine / "tests/__init__.py").write_text("")
        (origine / "tests/test_calc.py").write_text(TEST_CALC)
        r = self.run(origine, sys.executable, "-c",
                     "import sys; sys.path.insert(0, sys.argv[1]); from socle.cli import main; "
                     "sys.exit(main(sys.argv[2:]))", str(self.moteur),
                     "install", "--target", ".", "--adapter", "python", "--owner", "@essai")
        if r.returncode != 0:
            raise RuntimeError(f"installation du projet d'essai : {r.stdout[-3000:]}{r.stderr[-3000:]}")
        # La doc qui cite une valeur liée vient après sa déclaration : posée
        # avant, l'audit d'installation la refuserait, à raison.
        (origine / "docs").mkdir()
        (origine / "docs/calc.md").write_text(DOC_CALC)
        gf = origine / ".socle/guardrails.toml"
        texte = gf.read_text().replace('[mutation.caps]\n', '[mutation.caps]\n"calc.py" = { max = 0 }\n')
        gf.write_text(texte + GARDE_FOUS_ESSAI)
        journal = sorted((origine / "memory/journal").glob("*.md"))[0]
        ident = journal.read_text().split("## ", 2)[1].split(" ", 1)[0]
        self._ajouter(origine / "memory/canonical.md", CANONIQUE_ESSAI)
        self._ajouter(origine / "memory/backlog.md", BACKLOG_ESSAI.format(journal=ident))
        # L'origine est un dossier local : l'adresse web où l'humain lirait
        # se règle dans la politique, comme pour un relais.
        pol = origine / ".socle/policy.toml"
        pol.write_text(pol.read_text().replace("[human]\n", f'[human]\nrepo_url = "{DEPOT_ESSAI}"\n', 1))
        self.journal = ident
        self.git(origine, "add", "-A")
        r = self.run(origine, "git", "commit", "-q", "-m", "Projet d'essai")
        if r.returncode != 0:
            raise RuntimeError(f"le témoin de base ne passe pas le hook pre-commit :\n{r.stdout}{r.stderr}")
        self.origine = origine

    @staticmethod
    def _ajouter(p: Path, bloc: str):
        p.write_text(p.read_text().rstrip("\n") + "\n" + bloc)

    def clone(self, origine: Path | None = None, config: tuple[str, ...] = ()) -> Path:
        self.n += 1
        c = self.dossier / f"cas-{self.n:02d}"
        options = [x for cle in config for x in ("-c", cle)]
        self.git(self.dossier, "clone", "-q", *options, str(origine or self.origine), str(c))
        self.git(c, "config", "core.hooksPath", ".socle/git-hooks")
        self.git(c, "checkout", "-q", "-b", "travail")
        return c

    def origine_privee(self, mode: str) -> Path:
        """Une origine d'essai avec une mémoire privée, préparée une fois par
        mode : le projet d'essai, plus la politique qui choisit le mode."""
        o = self.dossier / f"origine-{mode}"
        if o.is_dir():
            return o
        self.git(self.dossier, "clone", "-q", *(x for cle in self.filtre() for x in ("-c", cle)), str(self.origine), str(o))
        pol = o / ".socle/policy.toml"
        relecture = 'review = "lots"\n' if mode == "compagnon" else ""
        pol.write_text(pol.read_text() + f'\n[private]\nmode = "{mode}"\n' + relecture)
        if mode == "compagnon":
            depot = self.dossier / "prive-origine"
            if not depot.is_dir():
                (depot / "journal").mkdir(parents=True)
                (depot / "canonical.md").write_text(CANONIQUE_PRIVEE)
                (depot / "terms.txt").write_text("# socle: termes privés\nMistral\n")
                self.git(depot, "init", "-q", "-b", "main")
                self.git(depot, "add", "-A")
                self.git(depot, "commit", "-q", "-m", "mémoire privée d'essai")
            (o / ".gitignore").write_text(((o / ".gitignore").read_text() if (o / ".gitignore").is_file() else "")
                                          + "memory/private/\n")
            sha = self.git(depot, "rev-parse", "HEAD").strip()
            (o / ".socle/private.lock").write_text(f'commit = "{sha}"\n')
        else:
            (o / ".gitattributes").write_text("memory/private/** filter=essai\n")
            (o / "memory/private").mkdir(parents=True)
            (o / "memory/private/canonical.md").write_text(CANONIQUE_PRIVEE)
        self.git(o, "add", "-A")
        self.git(o, "commit", "-q", "--no-verify", "-m", f"Mémoire privée, mode {mode}")
        return o

    def filtre(self) -> tuple[str, ...]:
        """Le « chiffrement » d'essai : un filtre git réversible, comme
        git-crypt en pose un ; le moteur ne connaît pas l'outil."""
        f = self.dossier / "filtre.py"
        if not f.is_file():
            f.write_text(FILTRE_ESSAI)
        return (f"filter.essai.clean={sys.executable} {f} clean", f"filter.essai.smudge={sys.executable} {f} smudge")

    def clone_prive(self, mode: str, cle: bool = True, compagnon: bool = True) -> Path:
        """Un clone d'une origine à mémoire privée : avec la clé du filtre
        (mode chiffré) ou le clone du dépôt privé (mode compagnon), ou sans."""
        o = self.origine_privee(mode)
        c = self.clone(o, self.filtre() if mode == "chiffre" and cle else ())
        if mode == "compagnon" and compagnon:
            self.git(c, "clone", "-q", str(self.dossier / "prive-origine"), "memory/private")
        return c

    def commit(self, c: Path, message: str, verifier: bool = False, env=None):
        self.git(c, "add", "-A")
        args = ["commit", "-q", "-m", message] + ([] if verifier else ["--no-verify"])
        return self.run(c, "git", *args, env=env)

    def nettoyer(self):
        shutil.rmtree(self.dossier, ignore_errors=True)


# --------------------------------------------------------------------------
# Les étages, par leurs vrais points d'entrée
# --------------------------------------------------------------------------


def etage_git(a: Atelier, c: Path) -> str:
    """Le hook pre-commit, sur un commit réel : rend la sortie s'il refuse."""
    a.git(c, "add", "-A")
    r = a.run(c, "git", "commit", "-q", "-m", "essai")
    return "" if r.returncode == 0 else r.stdout + r.stderr


def etage_ci(a: Atelier, c: Path, message: str = "essai", env=None) -> str:
    if a.run(c, "git", "status", "--porcelain").stdout.strip():
        r = a.commit(c, message, env=env)
        if r.returncode != 0:
            raise RuntimeError(r.stderr)
    r = a.socle(c, "check", "--stage", "ci", "--base", "origin/main")
    return "" if r.returncode == 0 else r.stdout + r.stderr


def etage_stop(a: Atelier, c: Path, dernier_message: str | None = None) -> str:
    """Le hook de fin de tour. Avec `dernier_message`, un transcript au format
    de Claude Code lui donne le dernier message de l'agent à lire."""
    entree = {"session_id": "autotest", "stop_hook_active": False}
    if dernier_message is not None:
        transcript = c.parent / f"{c.name}-transcript.jsonl"
        transcript.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in (
            {"type": "user", "message": {"role": "user", "content": "fais le travail"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": dernier_message}]}},
        )) + "\n")
        entree["transcript_path"] = str(transcript)
    r = a.socle(c, "hook", "stop", entree=json.dumps(entree))
    if not r.stdout.strip():
        return ""
    sortie = json.loads(r.stdout)
    return sortie.get("reason", "") if sortie.get("decision") == "block" else ""


def etage_demarrage(a: Atelier, c: Path) -> str:
    """Le hook de démarrage de session : il imprime l'état dérivé."""
    return a.socle(c, "hook", "session-start", entree=json.dumps({"session_id": "autotest", "source": "startup"})).stdout


def etage_outil(a: Atelier, c: Path, outil: str, args: dict) -> str:
    r = a.socle(c, "hook", "pre-tool-use", entree=json.dumps({"session_id": "autotest", "tool_name": outil, "tool_input": args}))
    if not r.stdout.strip():
        return ""
    sortie = json.loads(r.stdout).get("hookSpecificOutput", {})
    return sortie.get("permissionDecisionReason", "") if sortie.get("permissionDecision") == "deny" else ""


def ajouter(c: Path, rel: str, bloc: str):
    p = c / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text((p.read_text() if p.is_file() else "").rstrip("\n") + "\n" + bloc)


def remplacer(c: Path, rel: str, avant: str, apres: str):
    p = c / rel
    t = p.read_text()
    if avant not in t:
        raise RuntimeError(f"injection impossible : « {avant} » absent de {rel}")
    p.write_text(t.replace(avant, apres, 1))


def empreinte(a: Atelier, c: Path, cible: str) -> str:
    """L'empreinte d'une entrée ou d'un index, lue comme l'agent la lit :
    dans la sortie de `socle show`."""
    args = ["show", "--index", cible] if cible in ("decisions", "backlog") else ["show", cible]
    sortie = a.socle(c, *args).stdout
    m = re.search(rf"{re.escape(cible)}@([0-9a-f]{{8}})", sortie)
    if not m:
        raise RuntimeError(f"pas d'empreinte pour {cible} : {sortie[:200]}")
    return m.group(1)


def demande_bonne(a: Atelier, c: Path) -> str:
    return DEMANDE_BONNE.replace("- B-0001 —", f"- B-0001@{empreinte(a, c, 'B-0001')} —")


ADR_ESSAI = """<!-- socle: couche=decisions zone=publique -->
# ADR-0001 — Garder une seule fonction de multiplication

> statut : acceptée · date : 2026-10-10{lu}

## Contexte

Le fait {fait} établit que `double` multiplie par une constante.

## Décision

Toute nouvelle multiplication passe par la même constante.
"""


MESSAGE_AGENT = ("Travail d'agent\n\nCo-Authored-By: Claude <noreply@anthropic.com>\nSocle-Agent: claude-code\n"
                 "Socle-Hooks: SessionStart=1 PreToolUse=4 Stop=1")


def _adr_test_double(a: "Atelier", c: Path) -> str:
    """Une décision qui nomme le test `test_double`, et prouve ses lectures."""
    return ("<!-- socle: couche=decisions zone=publique -->\n# ADR-0001 — Le test de double compare à un flottant\n\n"
            f"> statut : acceptée · date : 2026-10-10 · lu : decisions@{empreinte(a, c, 'decisions')}\n\n"
            "## Décision\n\n`test_double` compare désormais le résultat à un flottant.\n")


DEPOT_ESSAI = "https://github.com/essai/calc"
RECAP = "\n\nPour toi : rien.\nEnsuite : rien."


def pousser(a: Atelier, c: Path, message: str = "essai"):
    """Commit et push de la branche de travail vers l'origine d'essai, sous
    le nom du clone : les cas partagent la même origine."""
    if a.run(c, "git", "status", "--porcelain").stdout.strip():
        r = a.commit(c, message)
        if r.returncode != 0:
            raise RuntimeError(r.stderr)
    a.git(c, "push", "-q", "--no-verify", "-u", "origin", f"travail:{c.name}")


def maj_memoire(c: Path, texte: str = "Travail en cours sur l'essai."):
    remplacer(c, "memory/active.md", "## En cours\n\nRien pour l'instant.", f"## En cours\n\n{texte}")


# --------------------------------------------------------------------------
# Les défauts du cadrage, puis quelques autres
# --------------------------------------------------------------------------

DEMANDE_BONNE = """<!-- socle: couche=demandes zone=publique -->
# D-0001 — Faut-il refondre le module de calcul avant d'ajouter la fonction triple ?

> date : 2026-10-10

## Décision demandée

Refondre le module de calcul avant d'y ajouter la fonction triple, ou ajouter
la fonction telle quelle.

## Contexte

Le backlog demande une fonction triple dans le module de calcul. Le module ne
contient aujourd'hui qu'une fonction, double, qui multiplie son argument par
une constante du module. Ajouter triple sur le même modèle dupliquerait cette
logique ; une refonte introduirait une fonction générique qui multiplie par
un facteur donné, dont double et triple deviendraient deux cas. La refonte
touche une fonction publique, donc tout appelant existant.

## Éléments cités

- B-0001 — le sujet du backlog qui demande d'ajouter une fonction triple au module.

## Où regarder

- Le module : [calc.py](../../calc.py), fonction `double` ; ce qu'il faut voir : qu'elle est seule et publique.

## Options

Refondre : effort d'une heure, risque faible sur les appelants, réversible.
Ajouter tel quel : effort de dix minutes, risque nul, réversible.

## Conséquences

Si tu valides, je refonds puis j'ajoute ; si tu refuses, j'ajoute tel quel ;
sans réponse, j'ajoute tel quel et je note la refonte au backlog.

## Recommandation

Ajouter tel quel. Vérifié : un seul appelant. Supposé : que d'autres
facteurs ne viendront pas.

## Réponses possibles

- `valider` — je refonds d'abord.
- `refuser` — j'ajoute tel quel.
- `contexte-insuffisant` — je réécris la demande.
"""

DEMANDE_NUE = """<!-- socle: couche=demandes zone=publique -->
# D-0001 — Valider le refactor du module de calcul

> date : 2026-10-10

## Décision demandée

Je propose un refactor du code évoqué en B-0001, tu valides ?

## Contexte

Le refactor évoqué en B-0001 simplifierait la suite.

## Éléments cités

Voir le backlog.

## Options

Refactor ou pas : effort faible, risque faible, réversible.

## Conséquences

Si tu valides, je le fais ; si tu refuses, rien ; sans réponse, j'attends.

## Recommandation

Vérifié : rien. Supposé : que c'est mieux.

## Réponses possibles

- `valider` — je fais le refactor.
- `contexte-insuffisant` — je réécris la demande.
"""


def _cas() -> list[Cas]:
    cas = []

    def defaut(id_, texte, etage, controle):
        def deco(f):
            cas.append(Cas(id_, texte, etage, controle, f))
            return f
        return deco

    @defaut("valeur-divergente", "valeur de la doc divergente de sa source", "git", "docs.valeurs")
    def _(a, c):
        remplacer(c, "docs/calc.md", "-->2<!--", "-->3<!--")
        return etage_git(a, c)

    @defaut("reference-morte", "lien ou identifiant mort", "git", "memoire.references")
    def _(a, c):
        ajouter(c, "docs/calc.md", "Voir F-0099 et [le guide](guide.md).\n")
        return etage_git(a, c)

    @defaut("code-sans-doc", "code modifié sans doc associée", "agent", "docs.correspondance")
    def _(a, c):
        remplacer(c, "calc.py", "return FACTEUR * x", "return x * FACTEUR")
        maj_memoire(c)
        return etage_stop(a, c)

    @defaut("test-sans-assertion", "test sans assertion", "git", "tests.creux")
    def _(a, c):
        ajouter(c, "tests/test_calc.py", "    def test_rien(self):\n        double(3)\n")
        return etage_git(a, c)

    @defaut("test-tautologique", "assertion tautologique", "git", "tests.creux")
    def _(a, c):
        ajouter(c, "tests/test_calc.py", "    def test_toujours(self):\n        self.assertEqual(double(3), double(3))\n")
        return etage_git(a, c)

    @defaut("test-desactive", "test désactivé sans raison écrite", "git", "tests.creux")
    def _(a, c):
        remplacer(c, "tests/test_calc.py", "    def test_double", "    @unittest.skip\n    def test_double")
        return etage_git(a, c)

    @defaut("plafond-releve", "plafond de mutation relevé", "ci", "cliquet.garde-fous")
    def _(a, c):
        remplacer(c, ".socle/guardrails.toml", '"calc.py" = { max = 0 }', '"calc.py" = { max = 3, reason = "équivalents" }')
        return etage_ci(a, c)

    @defaut("budget-releve", "budget de mémoire relevé", "ci", "cliquet.garde-fous")
    def _(a, c):
        remplacer(c, ".socle/guardrails.toml", '"memory/active.md" = { max_bytes = 6000 }', '"memory/active.md" = { max_bytes = 60000 }')
        return etage_ci(a, c)

    @defaut("correctif-sans-test", "correctif sans test de régression", "ci", "tests.regression")
    def _(a, c):
        remplacer(c, "calc.py", "return FACTEUR * x", "return FACTEUR * int(x)")
        remplacer(c, "docs/calc.md", "la\nconstante", "la constante\nentière")
        maj_memoire(c, "Correctif de `double` sur les chaînes.")
        return etage_ci(a, c, "fix: double accepte une chaîne")

    @defaut("hook-jamais-tire", "hook de l'agent absent ou jamais tiré", "ci", "hooks.trace")
    def _(a, c):
        maj_memoire(c, "Commit d'agent sans hooks.")
        return etage_ci(a, c, "Travail d'agent\n\nCo-Authored-By: Claude <noreply@anthropic.com>")

    @defaut("moteur-altere", "moteur altéré dans le projet", "ci", "moteur.empreinte")
    def _(a, c):
        ajouter(c, ".socle/engine/socle/outils.py", "# retouche locale\n")
        return etage_ci(a, c)

    @defaut("politique-alteree", "politique altérée sans validation", "ci", "protege.fichiers")
    def _(a, c):
        remplacer(c, ".socle/policy.toml", "max_attempts = 3", "max_attempts = 30")
        return etage_ci(a, c)

    @defaut("demande-identifiant-nu", "demande humaine avec identifiant nu", "agent", "demandes.contrat")
    def _(a, c):
        return etage_outil(a, c, "Write", {"file_path": str(c / "memory/requests/D-0001-refactor.md"), "content": DEMANDE_NUE})

    @defaut("demande-sans-lien", "demande qui ne dit pas où regarder", "agent", "où regarder")
    def _(a, c):
        sans = demande_bonne(a, c).replace("[calc.py](../../calc.py)", "le module")
        return etage_outil(a, c, "Write", {"file_path": str(c / "memory/requests/D-0001-refactor.md"), "content": sans})

    @defaut("budget-depasse", "couche de mémoire au-delà de son budget", "git", "memoire.budgets")
    def _(a, c):
        ajouter(c, "memory/active.md", "\n" + ("Une ligne de remplissage pour dépasser le budget. " * 200) + "\n")
        return etage_git(a, c)

    @defaut("identifiant-prive", "identifiant privé dans un fichier public", "git", "memoire.prive")
    def _(a, c):
        ajouter(c, "docs/calc.md", "Motivation : voir PJ-2026-10-10-A.\n")
        return etage_git(a, c)

    @defaut("memoire-privee-absente", "mémoire privée non accessible", "agent", "signal indisponible")
    def _(a, c):
        c = a.clone_prive("compagnon", compagnon=False)
        sortie = etage_demarrage(a, c)
        return sortie if "INDISPONIBLE" in sortie else ""

    @defaut("verrou-perime", "mémoire privée commitée sans avancer le verrou", "git", "prive.verrou")
    def _(a, c):
        c = a.clone_prive("compagnon")
        ajouter(c, "memory/private/canonical.md", "\nPrécision privée.\n")
        a.git(c / "memory/private", "commit", "-q", "-am", "précision")
        maj_memoire(c)
        return etage_git(a, c)

    @defaut("fuite-terme", "terme de la liste privée écrit dans un fichier public", "git", "prive.fuites")
    def _(a, c):
        c = a.clone_prive("compagnon")
        ajouter(c, "docs/calc.md", "Le module servira au projet Mistral.\n")
        return etage_git(a, c)

    @defaut("fuite-message", "identifiant privé dans un message de commit", "git", "fuite")
    def _(a, c):
        c = a.clone_prive("compagnon")
        maj_memoire(c, "Travail du tour.")
        a.git(c, "add", "-A")
        r = a.run(c, "git", "commit", "-q", "-m", "Avancer vers " + "P" + "F-0001")
        return "" if r.returncode == 0 else r.stdout + r.stderr

    @defaut("fuite-ecriture-agent", "l'agent écrit un terme privé dans un fichier public", "agent", "fuite")
    def _(a, c):
        c = a.clone_prive("compagnon")
        return etage_outil(a, c, "Write", {"file_path": str(c / "docs/notes.md"), "content": "Projet Mistral.\n"})

    @defaut("fuite-pull-request", "description de pull request qui cite un identifiant privé", "agent", "fuite")
    def _(a, c):
        c = a.clone_prive("compagnon")
        return etage_outil(a, c, "mcp__github__create_pull_request",
                           {"title": "Essai", "body": "Voir " + "P" + "F-0001 pour le contexte."})

    @defaut("terme-retire", "terme retiré de la liste privée sans validation humaine", "git", "prive.termes")
    def _(a, c):
        c = a.clone_prive("compagnon")
        (c / "memory/private/terms.txt").write_text("# socle: termes privés\n")
        a.git(c / "memory/private", "commit", "-q", "-am", "retrait")
        a.socle(c, "prive", "verrouiller")
        maj_memoire(c, "Liste privée raccourcie.")
        return etage_git(a, c)

    @defaut("publication-sans-relecture", "push vers le dépôt public sans relecture humaine", "agent", "relecture")
    def _(a, c):
        c = a.clone_prive("compagnon")
        return etage_outil(a, c, "Bash", {"command": "git push origin travail"})

    @defaut("prive-en-clair", "fichier privé commité en clair, sans filtre de chiffrement", "git", "prive.chiffre")
    def _(a, c):
        c = a.clone_prive("chiffre", cle=False)
        ajouter(c, "memory/private/journal/2026-10.md", "<!-- socle: couche=journal zone=privee -->\n# Journal privé\n")
        return etage_git(a, c)

    @defaut("backlog-clos-sans-ref", "entrée de backlog close sans référence", "git", "memoire.backlog")
    def _(a, c):
        remplacer(c, "memory/backlog.md", "> statut : ouvert", "> statut : fait")
        return etage_git(a, c)

    # Au-delà du tableau du cadrage.

    @defaut("journal-reecrit", "entrée de journal réécrite", "git", "memoire.ajout-seul")
    def _(a, c):
        remplacer(c, f"memory/journal/{a.journal[2:9]}.md", "Le rapport d'installation", "Le compte rendu d'installation")
        return etage_git(a, c)

    @defaut("fait-efface", "fait canonique effacé", "git", "memoire.ajout-seul")
    def _(a, c):
        remplacer(c, "memory/canonical.md", CANONIQUE_ESSAI.strip(), "")
        return etage_git(a, c)

    @defaut("valeur-attendue", "valeur attendue changée sans spécification", "git", "tests.attendus")
    def _(a, c):
        remplacer(c, "tests/test_calc.py", "self.assertEqual(double(2), 4)", "self.assertEqual(double(2), 4.0)")
        return etage_git(a, c)

    @defaut("valeur-attendue-adr-agent", "valeur attendue changée sous une ADR que l'agent écrit lui-même", "ci",
            "tests.attendus")
    def _(a, c):
        ajouter(c, "memory/decisions/ADR-0001-test-double.md", _adr_test_double(a, c))
        remplacer(c, "tests/test_calc.py", "self.assertEqual(double(2), 4)", "self.assertEqual(double(2), 4.0)")
        maj_memoire(c)
        return etage_ci(a, c, MESSAGE_AGENT)

    @defaut("test-supprime", "test supprimé sans validation", "ci", "tests.attendus")
    def _(a, c):
        remplacer(c, "tests/test_calc.py", "    def test_double(self):\n        self.assertEqual(double(2), 4)\n",
                  "    def test_placeholder(self):\n        self.assertTrue(callable(double))\n")
        return etage_ci(a, c)

    @defaut("valide-sans-demande", "fait passé à « validé » par l'agent", "agent", "memoire.preuves")
    def _(a, c):
        p = c / "memory/canonical.md"
        nouveau = p.read_text().replace("> statut : mesuré · preuve : fichier:tests/test_calc.py", "> statut : validé")
        return etage_outil(a, c, "Write", {"file_path": str(p), "content": nouveau})

    @defaut("sha-fabrique", "SHA complété de tête", "agent", "anti-fabrication")
    def _(a, c):
        vrai = a.git(c, "rev-parse", "HEAD").strip()
        faux = vrai[:7] + "0" * 33
        return etage_outil(a, c, "Bash", {"command": f"git show {faux}"})

    @defaut("action-irreversible", "force-push sans validation humaine", "agent", "politique point 4")
    def _(a, c):
        return etage_outil(a, c, "Bash", {"command": "git push --force origin travail"})

    @defaut("reponse-par-agent", "l'agent écrit une réponse humaine", "agent", "fichier protégé")
    def _(a, c):
        return etage_outil(a, c, "Write", {"file_path": str(c / "memory/requests/D-0001-x.answer.toml"), "content": 'reponse = "valider"\n'})

    @defaut("agent-repond", "l'agent répond à la place de l'humain", "agent", "commande humaine")
    def _(a, c):
        lanceur = ".socle/" + "socle"  # en deux morceaux : ce fichier n'est pas une invocation
        return etage_outil(a, c, "Bash", {"command": f"python3 {lanceur} answer D-0001 valider"})

    @defaut("relais-sans-citation", "réponse relayée sans le texte exact de l'humain", "agent", "commande humaine")
    def _(a, c):
        lanceur = ".socle/" + "socle"
        return etage_outil(a, c, "Bash", {"command": f"python3 {lanceur} answer D-0001 valider --relayed --by Théo"})

    @defaut("relais-demande-non-lue", "réponse relayée à une demande que l'humain n'a pas pu lire", "agent",
            "demande non lue")
    def _(a, c):
        (c / "memory/requests/D-0001-refactor.md").write_text(demande_bonne(a, c))
        (c / "citation.txt").write_text("ok, refonds d'abord")
        r = a.socle(c, "answer", "D-0001", "valider", "--relayed", "--by", "Théo", "--quote-file", "citation.txt")
        return "" if r.returncode == 0 else r.stdout + r.stderr

    @defaut("copie", "paragraphe copié dans deux fichiers", "git", "docs.copie")
    def _(a, c):
        p = ("Ce paragraphe décrit en détail la manière dont le module de calcul multiplie ses entrées "
             "par une constante, et il est assez long pour qu'une copie ailleurs soit un vrai doublon "
             "qui divergera tôt ou tard de sa source.\n")
        ajouter(c, "docs/calc.md", "\n" + p)
        ajouter(c, "docs/autre.md", "# Autre\n\n" + p)
        return etage_git(a, c)

    @defaut("outil-non-documente", "dispositif qu'aucune doc ne nomme", "git", "docs.outillage")
    def _(a, c):
        ajouter(c, ".github/workflows/nuit.yml", "name: Nuit\non: [push]\njobs: {}\n")
        return etage_git(a, c)

    @defaut("fin-sans-recap", "fin d'intervention sans dire ce qui revient à l'humain", "agent", "récap")
    def _(a, c):
        maj_memoire(c, "Travail du tour.")
        return etage_stop(a, c, "J'ai mis à jour le chantier actif. Tout passe.")

    @defaut("fin-sans-suite", "fin d'intervention qui ne dit pas la suite", "agent", "suite")
    def _(a, c):
        maj_memoire(c, "Travail du tour.")
        return etage_stop(a, c, "J'ai mis à jour le chantier actif.\n\nPour toi : rien.")

    @defaut("chemin-inexistant", "chemin donné à l'humain qui n'existe pas dans le dépôt", "agent", "liens")
    def _(a, c):
        maj_memoire(c, "Travail du tour.")
        return etage_stop(a, c, "La doc est dans `docs/calcul.md`." + RECAP)

    @defaut("lien-relatif", "lien relatif, que l'humain ne peut pas suivre hors du conteneur", "agent", "liens")
    def _(a, c):
        return etage_stop(a, c, "Voir [la doc](docs/calc.md)." + RECAP)

    @defaut("lien-non-pousse", "permalien vers un fichier absent de la version poussée", "agent", "liens")
    def _(a, c):
        ajouter(c, "docs/nouveau.md", "# Nouveau\n")
        sha = a.git(c, "rev-parse", "origin/main").strip()
        return etage_stop(a, c, f"Voir [la doc]({DEPOT_ESSAI}/blob/{sha}/docs/nouveau.md)." + RECAP)

    @defaut("demande-sans-lien", "demande en attente citée sans son lien", "agent", "lien de demande")
    def _(a, c):
        (c / "memory/requests/D-0001-refactor.md").write_text(demande_bonne(a, c))
        maj_memoire(c, "Demande D-0001 posée.")
        pousser(a, c)
        return etage_stop(a, c, "J'ai posé la demande D-0001.\n\nPour toi : répondre à D-0001.\nEnsuite : rien.")

    @defaut("fonction-sans-test", "fonction publique ajoutée sans test qui la nomme", "ci", "tests.code-teste")
    def _(a, c):
        ajouter(c, "calc.py", "\n\ndef triple(x):\n    return 3 * x\n")
        ajouter(c, "docs/calc.md", "`triple` multiplie par trois.\n")
        maj_memoire(c, "Ajout de triple.")
        return etage_ci(a, c)

    @defaut("decision-sans-lecture", "décision ajoutée sans avoir consulté l'index des décisions", "git", "memoire.lectures")
    def _(a, c):
        f1 = f"F-0001@{empreinte(a, c, 'F-0001')}"
        ajouter(c, "memory/decisions/ADR-0001-une-seule-multiplication.md", ADR_ESSAI.format(lu="", fait=f1))
        return etage_git(a, c)

    @defaut("citation-perimee", "entrée citée dans une version qu'elle n'a plus", "git", "memoire.lectures")
    def _(a, c):
        perimee = empreinte(a, c, "F-0001")
        remplacer(c, "memory/canonical.md", "Le test unitaire l'établit.", "Le test unitaire l'établit, sur deux cas.")
        ajouter(c, "memory/journal/" + a.journal[2:9] + ".md",
                f"\n## {a.journal[:-1]}B — Constat\n\nVoir F-0001@{perimee}.\n")
        return etage_git(a, c)

    @defaut("backlog-sans-lecture", "sujet ajouté au backlog sans l'avoir consulté", "git", "memoire.lectures")
    def _(a, c):
        ajouter(c, "memory/backlog.md", "\n## B-0002 — Ajouter une fonction quadruple\n\n"
                f"> statut : ouvert · origine : {a.journal}\n\nPour l'essai.\n")
        return etage_git(a, c)

    @defaut("defaut-indexe-masque", "défaut indexé, corrigé seulement sur disque", "git", "memoire.references")
    def _(a, c):
        ajouter(c, "docs/calc.md", "Voir F-0099.\n")
        a.git(c, "add", "docs/calc.md")
        remplacer(c, "docs/calc.md", "Voir F-0099.\n", "")  # corrigé sur disque, pas dans l'index
        r = a.run(c, "git", "commit", "-q", "-m", "essai")
        return "" if r.returncode == 0 else r.stdout + r.stderr

    @defaut("memoire-en-retard", "code changé sans mise à jour de la mémoire", "agent", "memoire.retard")
    def _(a, c):
        remplacer(c, "calc.py", "return FACTEUR * x", "return x * FACTEUR")
        remplacer(c, "docs/calc.md", "la\nconstante", "la constante\nmême")
        return etage_stop(a, c)

    return cas


# --------------------------------------------------------------------------
# Les témoins : ce qui est sain doit passer
# --------------------------------------------------------------------------

TEST_REGRESSION = '''import unittest

from calc import double


class TestChaine(unittest.TestCase):
    def test_double_d_une_chaine(self):
        self.assertEqual(double("3"), 6)
'''


def _temoins() -> list[tuple[str, Callable]]:
    t = []

    def temoin(nom):
        def deco(f):
            t.append((nom, f))
            return f
        return deco

    @temoin("un changement complet passe la fin de tour, le commit et la CI")
    def _(a, c):
        remplacer(c, "calc.py", "return FACTEUR * x", "return x * FACTEUR")
        remplacer(c, "docs/calc.md", "la\nconstante", "la constante\nnommée")
        maj_memoire(c)
        return etage_stop(a, c) or etage_git(a, c) or etage_ci(a, c)

    @temoin("un correctif avec son test de régression passe la CI")
    def _(a, c):
        remplacer(c, "calc.py", "return FACTEUR * x", "return FACTEUR * int(x)")
        remplacer(c, "docs/calc.md", "la\nconstante", "la constante\nentière")
        (c / "tests/test_regression.py").write_text(TEST_REGRESSION)
        maj_memoire(c, "Correctif de `double` sur les chaînes, avec son test.")
        return etage_ci(a, c, "fix: double accepte une chaîne")

    @temoin("un commit d'agent qui porte la trace de ses hooks passe la CI")
    def _(a, c):
        maj_memoire(c, "Commit d'agent avec hooks.")
        return etage_ci(a, c, "Travail d'agent\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n"
                        "Socle-Agent: claude-code\nSocle-Hooks: SessionStart=1 PreToolUse=4 Stop=1")

    @temoin("une valeur attendue changée sous une spécification que l'humain a commitée passe la CI")
    def _(a, c):
        ajouter(c, "memory/decisions/ADR-0001-test-double.md", _adr_test_double(a, c))
        a.commit(c, "Spécification : test_double compare à un flottant")  # un commit de l'humain
        remplacer(c, "tests/test_calc.py", "self.assertEqual(double(2), 4)", "self.assertEqual(double(2), 4.0)")
        maj_memoire(c)
        return etage_ci(a, c, MESSAGE_AGENT)

    @temoin("durcir un garde-fou est libre")
    def _(a, c):
        remplacer(c, ".socle/guardrails.toml", '"memory/active.md" = { max_bytes = 6000 }', '"memory/active.md" = { max_bytes = 5000 }')
        return etage_ci(a, c)

    @temoin("une demande complète passe le hook de l'agent")
    def _(a, c):
        return etage_outil(a, c, "Write", {"file_path": str(c / "memory/requests/D-0001-refactor.md"), "content": demande_bonne(a, c)})

    @temoin("une réponse donnée dans la conversation, relayée avec sa citation, passe le hook et la CI")
    def _(a, c):
        (c / "memory/requests/D-0001-refactor.md").write_text(demande_bonne(a, c))
        pousser(a, c)  # l'humain la lit, puis répond dans la conversation
        (c / "citation.txt").write_text("ok, refonds d'abord")
        lanceur = ".socle/" + "socle"
        commande = f"python3 {lanceur} answer D-0001 valider --relayed --by Théo --quote-file citation.txt"
        refus = etage_outil(a, c, "Bash", {"command": commande})
        if refus:
            return refus
        r = a.socle(c, "answer", "D-0001", "valider", "--relayed", "--by", "Théo", "--quote-file", "citation.txt")
        (c / "citation.txt").unlink()
        if r.returncode != 0:
            return r.stdout + r.stderr
        maj_memoire(c, "Refonte validée dans la conversation.")
        return etage_ci(a, c)

    @temoin("une fin d'intervention avec « Pour toi : » et « Ensuite : » passe le hook de fin de tour")
    def _(a, c):
        maj_memoire(c, "Travail du tour.")
        return etage_stop(a, c, "J'ai mis à jour le chantier actif. Tout passe.\n\nPour toi : rien.\n"
                          "Ensuite : le sujet suivant du backlog.")

    @temoin("des liens que l'humain peut suivre passent le hook de fin de tour")
    def _(a, c):
        (c / "memory/requests/D-0001-refactor.md").write_text(demande_bonne(a, c))
        maj_memoire(c, "Demande D-0001 posée.")
        pousser(a, c)
        r = a.socle(c, "url", "D-0001", "docs/calc.md")
        if r.returncode != 0:
            return r.stdout + r.stderr
        return etage_stop(a, c, "J'ai posé la demande D-0001, sur le module `calc.py` et sa doc `docs/calc.md`.\n\n"
                          + r.stdout + "\nPour toi : répondre à D-0001.\nEnsuite : rien.")

    @temoin("une fonction ajoutée avec le test qui la nomme passe la CI")
    def _(a, c):
        ajouter(c, "calc.py", "\n\ndef triple(x):\n    return 3 * x\n")
        ajouter(c, "docs/calc.md", "`triple` multiplie par trois.\n")
        ajouter(c, "tests/test_calc.py", "    def test_triple(self):\n        from calc import triple\n"
                "        self.assertEqual(triple(2), 6)\n")
        maj_memoire(c, "Ajout de triple, avec son test.")
        return etage_ci(a, c)

    @temoin("une fonction privée, ou publique et dispensée avec sa raison, passe la CI")
    def _(a, c):
        ajouter(c, "calc.py", "\n\ndef _aide(x):\n    return x\n\n\ndef triple(x):\n    return 3 * _aide(x)\n")
        ajouter(c, "docs/calc.md", "`triple` multiplie par trois.\n")
        maj_memoire(c, "Ajout de triple, dispensée.")
        return etage_ci(a, c, "Ajout de triple\n\nDispense-test: triple — appelée par l'interface, testée de bout en bout")

    @temoin("mode compagnon : une entrée privée commitée et verrouillée passe la fin de tour, le commit et la CI")
    def _(a, c):
        c = a.clone_prive("compagnon")
        ajouter(c, "memory/private/canonical.md", "\n## PF-0002 — Une seconde idée privée\n\n> statut : supposé · source : PF-0001\n")
        a.git(c / "memory/private", "commit", "-q", "-am", "seconde idée")
        r = a.socle(c, "prive", "verrouiller")
        if r.returncode != 0:
            return r.stdout + r.stderr
        maj_memoire(c, "Mémoire privée avancée.")
        return etage_stop(a, c) or etage_git(a, c) or etage_ci(a, c)

    @temoin("mode chiffré : une entrée privée part chiffrée et passe le commit et la CI")
    def _(a, c):
        c = a.clone_prive("chiffre")
        ajouter(c, "memory/private/canonical.md", "\n## PF-0002 — Une seconde idée privée\n\n> statut : supposé · source : PF-0001\n")
        maj_memoire(c, "Mémoire privée avancée.")
        sortie = etage_git(a, c) or etage_ci(a, c)
        if not sortie and not a.git(c, "show", "HEAD:memory/private/canonical.md").startswith("ESSAI:"):
            sortie = "le fichier privé est commité en clair"
        return sortie

    @temoin("ajouter un terme à la liste privée est libre : le commit et la CI passent")
    def _(a, c):
        c = a.clone_prive("compagnon")
        r = a.socle(c, "prive", "terme", "Zephyr")
        a.git(c / "memory/private", "commit", "-q", "-am", "un terme de plus")
        a.socle(c, "prive", "verrouiller")
        maj_memoire(c, "Un terme privé de plus.")
        return (r.stderr if r.returncode else "") or etage_git(a, c) or etage_ci(a, c)

    @temoin("un push relu par l'humain, son accord relayé avec son texte exact, passe le hook de l'agent")
    def _(a, c):
        c = a.clone_prive("compagnon")
        (c / "accord.txt").write_text("ok, tu peux publier")
        commande = "python3 .socle/" + "socle relu --relayed --by Théo --quote-file accord.txt"
        refus = etage_outil(a, c, "Bash", {"command": commande})
        if refus:
            return refus
        r = a.socle(c, "relu", "--relayed", "--by", "Théo", "--quote-file", "accord.txt")
        if r.returncode:
            return r.stdout + r.stderr
        return etage_outil(a, c, "Bash", {"command": "git push origin travail"})

    @temoin("sans la clé (une CI de fork), la mémoire privée est indisponible et rien n'échoue")
    def _(a, c):
        c = a.clone_prive("chiffre", cle=False)
        maj_memoire(c, "Travail sans la clé.")
        sortie = etage_ci(a, c)
        if not sortie and "INDISPONIBLE" not in etage_demarrage(a, c):
            sortie = "l'état ne signale pas la mémoire privée indisponible"
        return sortie

    @temoin("en CI, un constat de la zone privée échoue sans montrer son contenu")
    def _(a, c):
        c = a.clone_prive("compagnon")
        remplacer(c, "memory/private/canonical.md", "statut : supposé", "statut : inventé")
        a.git(c / "memory/private", "commit", "-q", "-am", "statut faux")
        a.socle(c, "prive", "verrouiller")
        maj_memoire(c, "Statut privé faux.")
        sortie = etage_ci(a, c)
        if not sortie:
            return "la CI passe malgré un statut inconnu dans la zone privée"
        if "Mistral" in sortie or "inventé" in sortie or "canonical.md" in sortie:
            return "la CI montre le contenu de la zone privée :\n" + sortie
        return ""

    @temoin("une fin de tour sans travail n'exige pas de récap")
    def _(a, c):
        etage_stop(a, c, "Pour toi : rien.\nEnsuite : rien.")  # retient l'état de l'arbre
        return etage_stop(a, c, "Réponse à une question, sans rien changer.")

    @temoin("une décision qui prouve ses lectures passe le commit")
    def _(a, c):
        lu = f" · lu : decisions@{empreinte(a, c, 'decisions')}"
        f1 = f"F-0001@{empreinte(a, c, 'F-0001')}"
        ajouter(c, "memory/decisions/ADR-0001-une-seule-multiplication.md", ADR_ESSAI.format(lu=lu, fait=f1))
        ajouter(c, "memory/backlog.md", "\n## B-0002 — Ajouter une fonction quadruple\n\n"
                f"> statut : ouvert · origine : {a.journal} · lu : backlog@{empreinte(a, c, 'backlog')}\n\nPour l'essai.\n")
        return etage_git(a, c)

    @temoin("un commit d'agent fait dans un autre worktree porte la trace des hooks et passe la CI")
    def _(a, c):
        # Les hooks de l'agent tirent dans le dépôt principal…
        entree = {"session_id": "autotest-wt", "source": "startup"}
        a.socle(c, "hook", "session-start", entree=json.dumps(entree))
        a.socle(c, "hook", "pre-tool-use", entree=json.dumps({**entree, "tool_name": "Bash", "tool_input": {"command": "ls"}}))
        # … et le commit se fait dans un autre worktree, comme la pull request
        # de démonstration (B-0015).
        wt = c.parent / f"{c.name}-wt"
        a.git(c, "worktree", "add", "-q", "-b", "autre", str(wt))
        maj_memoire(wt, "Travail fait dans un autre worktree.")
        r = a.commit(wt, "Travail d'agent\n\nCo-Authored-By: Claude <noreply@anthropic.com>", verifier=True,
                     env={"CLAUDECODE": "1"})
        if r.returncode != 0:
            return r.stdout + r.stderr
        r = a.socle(wt, "check", "--stage", "ci", "--base", "origin/main")
        return "" if r.returncode == 0 else r.stdout + r.stderr

    @temoin("un défaut sur disque mais pas dans l'index ne bloque pas le commit de ce qui est indexé")
    def _(a, c):
        maj_memoire(c, "Seul ce changement est indexé.")
        a.git(c, "add", "memory/active.md")
        ajouter(c, "docs/calc.md", "Voir F-0099.\n")  # en cours, non indexé
        r = a.run(c, "git", "commit", "-q", "-m", "essai")
        return "" if r.returncode == 0 else r.stdout + r.stderr

    @temoin("une tautologie voulue, raison écrite, passe le commit")
    def _(a, c):
        ajouter(c, "tests/test_calc.py", "    def test_deterministe(self):\n"
                "        self.assertEqual(double(3), double(3))  # socle: voulu — double est déterministe\n")
        return etage_git(a, c)

    @temoin("une commande qui CITE `socle answer` sans l'appeler passe")
    def _(a, c):
        return etage_outil(a, c, "Bash", {"command": "grep -n 'socle answer' AGENTS.md"})

    @temoin("une écriture ordinaire passe le hook de l'agent")
    def _(a, c):
        return etage_outil(a, c, "Edit", {"file_path": str(c / "docs/calc.md"), "old_string": "# Calcul", "new_string": "# Le calcul"})

    return t


# --------------------------------------------------------------------------


def executer(projet=None, bavard: bool = False) -> Rapport:
    import socle

    r = Rapport()
    moteur = Path(socle.__file__).resolve().parent.parent
    a = Atelier(moteur, bavard)
    try:
        try:
            a.preparer()
        except Exception as e:
            r.execute("autotest")
            r.erreur("autotest", f"projet d'essai impossible à préparer : {e}")
            return r
        for nom, f in _temoins():
            ident = "autotest.temoins"
            r.execute(ident)
            c = a.clone()
            try:
                sortie = f(a, c)
            except Exception as e:
                sortie = f"le témoin a planté : {type(e).__name__}: {e}"
            if sortie:
                r.erreur(ident, f"témoin en échec — {nom} : un contrôle crie sur un cas sain\n        "
                         + "\n        ".join(sortie.strip().splitlines()[-25:]))
            elif bavard:
                print(f"  témoin ok : {nom}", file=sys.stderr)
        for cas in _cas():
            ident = f"autotest.{cas.id}"
            r.execute(ident)
            c = a.clone()
            try:
                sortie = cas.fonction(a, c)
            except Exception as e:
                r.erreur(ident, f"{cas.defaut} : injection impossible — {type(e).__name__}: {e}")
                continue
            if not sortie:
                r.erreur(ident, f"DÉFAUT NON ATTRAPÉ : {cas.defaut} (attendu : {cas.controle}, étage {cas.etage})")
            elif not _attrape_par(cas, sortie):
                r.erreur(ident, f"{cas.defaut} : attrapé, mais pas par {cas.controle}\n        "
                         + "\n        ".join(sortie.strip().splitlines()[-15:]))
            elif bavard:
                print(f"  attrapé : {cas.defaut} — {cas.controle}, étage {cas.etage}", file=sys.stderr)
    finally:
        a.nettoyer()
    return r


# Le hook PreToolUse ne nomme pas de contrôle : il rend sa raison, qu'on
# reconnaît à ces mots.
RAISONS_AGENT = {
    "demandes.contrat": "demande hors contrat",
    "memoire.preuves": "sans demande validée par l'humain",
    "anti-fabrication": "SHA fabriqué",
    "politique point 4": "politique, point 4",
    "fichier protégé": "est protégé par la politique",
    "commande humaine": "ne répond jamais à la place de l'humain",
    "où regarder": "« Où regarder » doit donner un lien",
    "récap": "pas Pour toi :",
    "suite": "pas Ensuite :",
    "liens": "liens que l'humain ne pourra pas suivre",
    "lien de demande": "sans son lien",
    "signal indisponible": "mémoire privée : INDISPONIBLE",
    "fuite": "fuite de la mémoire privée",
    "relecture": "relecture avant publication",
    "demande non lue": "n'a pas pu être lue par l'humain",
}


def _attrape_par(cas: Cas, sortie: str) -> bool:
    """Le défaut est-il attrapé par le contrôle ATTENDU ? Le rapport liste
    tous les contrôles exécutés, réussis compris : seule la ligne de synthèse
    `ECHEC — n contrôle(s) : …` dit lesquels ont échoué."""
    if cas.controle in RAISONS_AGENT:
        return RAISONS_AGENT[cas.controle] in sortie
    for ligne in sortie.splitlines():
        if ligne.startswith("ECHEC — ") and " : " in ligne:
            echecs = [x.strip() for x in ligne.split(" : ", 1)[1].split(",")]
            return cas.controle in echecs
    return False
