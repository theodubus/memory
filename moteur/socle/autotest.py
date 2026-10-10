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
        gf = origine / ".socle/garde-fous.toml"
        texte = gf.read_text().replace('[mutation.caps]\n', '[mutation.caps]\n"calc.py" = { max = 0 }\n')
        gf.write_text(texte + GARDE_FOUS_ESSAI)
        journal = sorted((origine / "memoire/journal").glob("*.md"))[0]
        ident = journal.read_text().split("## ", 2)[1].split(" ", 1)[0]
        self._ajouter(origine / "memoire/canonique.md", CANONIQUE_ESSAI)
        self._ajouter(origine / "memoire/backlog.md", BACKLOG_ESSAI.format(journal=ident))
        self.journal = ident
        self.git(origine, "add", "-A")
        r = self.run(origine, "git", "commit", "-q", "-m", "Projet d'essai")
        if r.returncode != 0:
            raise RuntimeError(f"le témoin de base ne passe pas le hook pre-commit :\n{r.stdout}{r.stderr}")
        self.origine = origine

    @staticmethod
    def _ajouter(p: Path, bloc: str):
        p.write_text(p.read_text().rstrip("\n") + "\n" + bloc)

    def clone(self) -> Path:
        self.n += 1
        c = self.dossier / f"cas-{self.n:02d}"
        self.git(self.dossier, "clone", "-q", str(self.origine), str(c))
        self.git(c, "config", "core.hooksPath", ".socle/git-hooks")
        self.git(c, "checkout", "-q", "-b", "travail")
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


def etage_stop(a: Atelier, c: Path) -> str:
    r = a.socle(c, "hook", "stop", entree=json.dumps({"session_id": "autotest", "stop_hook_active": False}))
    if not r.stdout.strip():
        return ""
    sortie = json.loads(r.stdout)
    return sortie.get("reason", "") if sortie.get("decision") == "block" else ""


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


def maj_memoire(c: Path, texte: str = "Travail en cours sur l'essai."):
    remplacer(c, "memoire/actif.md", "## En cours\n\nRien pour l'instant.", f"## En cours\n\n{texte}")


# --------------------------------------------------------------------------
# Les défauts du cadrage, puis quelques autres
# --------------------------------------------------------------------------

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
        remplacer(c, ".socle/garde-fous.toml", '"calc.py" = { max = 0 }', '"calc.py" = { max = 3, reason = "équivalents" }')
        return etage_ci(a, c)

    @defaut("budget-releve", "budget de mémoire relevé", "ci", "cliquet.garde-fous")
    def _(a, c):
        remplacer(c, ".socle/garde-fous.toml", '"memoire/actif.md" = { max_bytes = 6000 }', '"memoire/actif.md" = { max_bytes = 60000 }')
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
        ajouter(c, ".socle/moteur/socle/outils.py", "# retouche locale\n")
        return etage_ci(a, c)

    @defaut("politique-alteree", "politique altérée sans validation", "ci", "protege.fichiers")
    def _(a, c):
        remplacer(c, ".socle/politique.toml", "max_attempts = 3", "max_attempts = 30")
        return etage_ci(a, c)

    @defaut("demande-identifiant-nu", "demande humaine avec identifiant nu", "agent", "demandes.contrat")
    def _(a, c):
        return etage_outil(a, c, "Write", {"file_path": str(c / "memoire/demandes/D-0001-refactor.md"), "content": DEMANDE_NUE})

    @defaut("budget-depasse", "couche de mémoire au-delà de son budget", "git", "memoire.budgets")
    def _(a, c):
        ajouter(c, "memoire/actif.md", "\n" + ("Une ligne de remplissage pour dépasser le budget. " * 200) + "\n")
        return etage_git(a, c)

    @defaut("identifiant-prive", "identifiant privé dans un fichier public", "git", "memoire.prive")
    def _(a, c):
        ajouter(c, "docs/calc.md", "Motivation : voir PJ-2026-10-10-A.\n")
        return etage_git(a, c)

    @defaut("memoire-privee-absente", "mémoire privée non accessible", "agent", "jalon-7")
    def _(a, c):
        return None  # jalon 7 : signalé comme non couvert, jamais en silence

    @defaut("backlog-clos-sans-ref", "entrée de backlog close sans référence", "git", "memoire.backlog")
    def _(a, c):
        remplacer(c, "memoire/backlog.md", "> statut : ouvert", "> statut : fait")
        return etage_git(a, c)

    # Au-delà du tableau du cadrage.

    @defaut("journal-reecrit", "entrée de journal réécrite", "git", "memoire.ajout-seul")
    def _(a, c):
        remplacer(c, f"memoire/journal/{a.journal[2:9]}.md", "Le rapport d'installation", "Le compte rendu d'installation")
        return etage_git(a, c)

    @defaut("fait-efface", "fait canonique effacé", "git", "memoire.ajout-seul")
    def _(a, c):
        remplacer(c, "memoire/canonique.md", CANONIQUE_ESSAI.strip(), "")
        return etage_git(a, c)

    @defaut("valeur-attendue", "valeur attendue changée sans spécification", "git", "tests.attendus")
    def _(a, c):
        remplacer(c, "tests/test_calc.py", "self.assertEqual(double(2), 4)", "self.assertEqual(double(2), 4.0)")
        return etage_git(a, c)

    @defaut("test-supprime", "test supprimé sans validation", "ci", "tests.attendus")
    def _(a, c):
        remplacer(c, "tests/test_calc.py", "    def test_double(self):\n        self.assertEqual(double(2), 4)\n",
                  "    def test_placeholder(self):\n        self.assertTrue(callable(double))\n")
        return etage_ci(a, c)

    @defaut("valide-sans-demande", "fait passé à « validé » par l'agent", "agent", "memoire.preuves")
    def _(a, c):
        p = c / "memoire/canonique.md"
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
        return etage_outil(a, c, "Write", {"file_path": str(c / "memoire/demandes/D-0001-x.reponse.toml"), "content": 'reponse = "valider"\n'})

    @defaut("agent-repond", "l'agent lance `socle answer`", "agent", "commande humaine")
    def _(a, c):
        lanceur = ".socle/" + "socle"  # en deux morceaux : ce fichier n'est pas une invocation
        return etage_outil(a, c, "Bash", {"command": f"python3 {lanceur} answer D-0001 valider"})

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

    @temoin("durcir un garde-fou est libre")
    def _(a, c):
        remplacer(c, ".socle/garde-fous.toml", '"memoire/actif.md" = { max_bytes = 6000 }', '"memoire/actif.md" = { max_bytes = 5000 }')
        return etage_ci(a, c)

    @temoin("une demande complète passe le hook de l'agent")
    def _(a, c):
        bonne = DEMANDE_NUE.replace("Je propose un refactor du code évoqué en B-0001, tu valides ?",
                                    "Faut-il refondre le module de calcul avant d'ajouter la fonction triple ?")
        bonne = bonne.replace("Voir le backlog.", "- B-0001 — le sujet du backlog qui demande d'ajouter une fonction triple au module.")
        return etage_outil(a, c, "Write", {"file_path": str(c / "memoire/demandes/D-0001-refactor.md"), "content": bonne})

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
            if cas.controle == "jalon-7":
                r.indisponible(ident, f"{cas.defaut} : non couvert avant le jalon 7 (mémoire privée)")
                continue
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
    "commande humaine": "réservés à l'humain",
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
