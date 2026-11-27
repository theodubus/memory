"""B-0368 (D-0219) : la mise à jour de chess, rejouée avant de lui donner son
prompt. L'étape de la demande seule a cassé aux deux mises à jour réelles,
chaque fois autrement (B-0196, B-0357), et les tests de T-0201 simulent
l'ancien moteur par une copie de celui de la tête.

Ici, le moteur que chess a reçu, pris dans l'historique de ce dépôt par
`git archive`, installe un projet et sa mémoire, que ses propres hooks git
commitent et poussent vers un dépôt nu ; le moteur de la tête le met à jour,
comme en session cloud ; puis, dans l'ordre que disent les étapes « Et
maintenant » de l'installeur, la demande seule se commite et se pousse par
les vrais hooks git, et après la réponse de l'humain, les fichiers de la
mise à jour."""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import verification
from socle.selftest import DEMANDE_BONNE

RACINE = Path(__file__).resolve().parent.parent

# Le commit de ce dépôt dont le moteur est celui qu'a chess : la fusion de
# la PR #101, la dernière qui a changé `engine/` et que la distribution a
# publiée avant la mise à jour de chess du 26 novembre (J-2026-11-26-Z,
# docs/fabrication/chess/mise-a-jour-2026-11-26.md). La mise à jour suivante
# de chess l'avance au commit dont elle aura reçu le moteur.
MOTEUR_DE_CHESS = "da13e0578e610975409f0116b27813f97ec4f245"

ETAPES_RAPIDES = bool(os.environ.get(verification.RAPIDE))

TEST = ("import unittest\n\nfrom calc import double\n\n\nclass T(unittest.TestCase):\n"
        "    def test_double(self):\n        self.assertEqual(double(2), 4)\n")


def environnement(**plus: str) -> dict:
    """Ni session d'agent, ni réglage hérité du socle, de git ou de Python :
    le projet se juge comme dans un terminal neuf."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_", "GITHUB_", "SOCLE_", "PYTHON"))}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
               GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", PYTHONDONTWRITEBYTECODE="1", **plus)
    return env


@unittest.skipIf(ETAPES_RAPIDES, "trop long pour une étape rapide : la CI le joue à chaque push")
class TestMiseAJourDeChessRejouee(unittest.TestCase):
    """Chaque commit et chaque push passe par les hooks git que l'installeur
    a branchés (`core.hooksPath`) : un refus fait échouer le test, avec la
    sortie du hook."""

    ANCIEN = MOTEUR_DE_CHESS  # le commit dont le moteur installe le projet
    NEUF = RACINE / "engine"  # le moteur qui le met à jour

    def setUp(self):
        present = subprocess.run(["git", "cat-file", "-e", self.ANCIEN + "^{commit}"], cwd=RACINE,
                                 env=environnement(), capture_output=True)
        if present.returncode:
            self.skipTest(f"l'historique de ce dépôt n'a pas {self.ANCIEN[:10]}, le moteur qu'a chess (un clone "
                          "superficiel ?) : `git fetch --unshallow` le donne")
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-chess-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        self.ancien, self.racine = self.dossier / "ancien", self.dossier / "projet"
        self.ancien.mkdir()
        self.racine.mkdir()
        archive = subprocess.run(["git", "archive", self.ANCIEN, "engine/socle"], cwd=RACINE,
                                 env=environnement(), capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(self.ancien)], input=archive, check=True)

    def lancer(self, *commande: str, attendu: int | None = 0, **env: str) -> str:
        p = subprocess.run(list(commande), cwd=self.racine, env=environnement(**env), capture_output=True,
                           text=True)
        if attendu is not None:
            self.assertEqual(p.returncode, attendu, f"`{' '.join(commande)}` :\n{p.stdout}{p.stderr}")
        return p.stdout + p.stderr

    def socle(self, *args: str, **env: str) -> str:
        return self.lancer("python3", ".socle/socle", *args, **env)

    def installer(self, moteur: Path, *options: str, **env: str) -> str:
        # Comme chez chess : `PYTHONPATH=<moteur> python3 -m socle install`.
        # Son code de sortie n'est pas jugé : les commits et les pushs qui
        # suivent jugent ce qu'il a posé.
        return self.lancer("python3", "-m", "socle", "install", "--target", ".", *options, attendu=None,
                           PYTHONPATH=str(moteur), **env)

    def poser_la_memoire(self, journal: str):
        """Un besoin et sa tâche, écrits par l'ancien moteur (`socle new`),
        leurs gabarits remplis."""
        self.socle("new", "need", "Le module de calcul triple aussi")
        self.socle("new", "task", "Ajouter la fonction triple", "--need", "B-0001")
        for f, corps in (("B-0001", "Le module double ses entrées ; il doit aussi les tripler."),
                         ("T-0001", "La fonction `triple` dans `calc.py`.\n\n## Fait quand\n\n"
                                    "- [ ] `triple` est dans `calc.py`, nommée par un test")):
            chemin = next((self.racine / "memory/backlog").glob(f"{f}-*.md"))
            texte = re.sub(r"origine : <[^>]*>", f"origine : {journal}", chemin.read_text())
            texte = re.sub(r"(?m)^<(?!!--)[^>]*>$", corps, texte)
            chemin.write_text(texte.replace("<un résultat, jamais une implémentation>", "`triple(2)` rend 6"))

    def test_la_demande_seule_puis_les_fichiers_passent_les_hooks_git(self):
        # Le projet, installé par le moteur de chess ; sa mémoire, commitée
        # et poussée par les hooks git de ce moteur.
        self.lancer("git", "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        (self.racine / "tests").mkdir()
        (self.racine / "tests/__init__.py").write_text("")
        (self.racine / "tests/test_calc.py").write_text(TEST)
        sortie = self.installer(self.ancien / "engine", "--adapter", "python", "--owner", "@essai", "--human", "Théo")
        self.poser_la_memoire(re.search(r"journal ouvert par (J-[\w-]+)", sortie)[1])
        self.lancer("git", "add", "-A")
        self.lancer("git", "commit", "-qm", "Installer le socle")
        self.lancer("git", "init", "-q", "--bare", str(self.dossier / "origine.git"))
        self.lancer("git", "remote", "add", "origin", str(self.dossier / "origine.git"))
        self.lancer("git", "push", "-q", "-u", "origin", "main")
        self.lancer("git", "remote", "set-head", "origin", "main")

        # La mise à jour par le moteur neuf, en session cloud, sur une
        # branche neuve : la demande seule d'abord, commitée et poussée.
        self.lancer("git", "checkout", "-q", "-b", "maj")
        sortie = self.installer(self.NEUF, CLAUDE_CODE_REMOTE="true")
        self.assertIn("d'abord la demande seule", sortie)
        verdict = self.lancer("python3", ".socle/socle", "check", "--stage", "agent", "--only", "protege.fichiers",
                              attendu=1)
        cites = re.findall(r"doit citer `([^`]+)` et `([^`]+)`", verdict)
        self.assertIn(".socle/engine.lock", dict(cites), verdict)

        demande = re.search(r"memory/requests/D-\d+\S*\.md", self.socle("new", "request", "La mise à jour"))[0]
        ident = re.search(r"D-\d+", demande)[0]
        (self.racine / demande).write_text(DEMANDE_BONNE.replace("D-0001", ident).replace(
            "- B-0001 — le sujet du backlog qui demande d'ajouter une fonction triple au module.",
            "\n".join(f"- `{chemin}` — `{empreinte}`" for chemin, empreinte in cites)))
        self.lancer("git", "add", demande)
        self.lancer("git", "commit", "-qm", "Demande : approuver la mise à jour du socle")
        self.assertEqual(self.lancer("git", "show", "--name-only", "--format=", "HEAD").split(), [demande])
        self.lancer("git", "push", "-q", "-u", "origin", "maj")

        # Hors de GitHub, la branche par défaut n'exige pas la CI du socle :
        # les fichiers attendent la réponse de l'humain, puis se commitent
        # avec elle et se poussent (« Et maintenant »).
        self.socle("answer", ident, "valider", "--by", "Théo")
        self.lancer("git", "add", "-A")
        self.lancer("git", "commit", "-qm", "Mettre à jour le socle")
        self.lancer("git", "push", "-q")
        self.assertEqual(self.lancer("git", "status", "--porcelain"), "")
        self.assertEqual(self.lancer("git", "rev-parse", "origin/maj"), self.lancer("git", "rev-parse", "HEAD"))


if __name__ == "__main__":
    unittest.main()
