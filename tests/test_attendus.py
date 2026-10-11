"""Le point 2 de la politique, option B (J-2026-10-11-J) : une valeur
attendue ne change que sous une demande validée par l'humain, ou sous une
spécification que l'humain a écrite. Une ADR que l'agent écrit dans le même
travail ne suffit plus : c'est ce qu'un agent sur trois a fait au banc (s9)."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, contexte, controles_tests, installeur
from socle.rapport import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "moteur"
TEST = "import unittest\n\nfrom calc import double\n\n\nclass T(unittest.TestCase):\n" \
       "    def test_double(self):\n        self.assertEqual(double(2), {attendu})\n"
ADR = ("<!-- socle: couche=decisions zone=publique -->\n# ADR-0001 — Le facteur passe à 3\n\n"
       "> statut : acceptée · date : 2026-10-11\n\n## Décision\n\n`test_double` attend désormais 6.\n")
AGENT = "\n\nCo-Authored-By: Claude <noreply@anthropic.com>\nSocle-Agent: claude-code"


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestValeurAttendue(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-attendus-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        (self.racine / "tests").mkdir()
        (self.racine / "tests/test_calc.py").write_text(TEST.format(attendu=4))
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def ecrire(self, rel, texte):
        p = self.racine / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte)

    def commit(self, message):
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", message, "--no-verify")

    def erreurs(self, etage="ci") -> tuple[list[str], list[str]]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage=etage, base=self.base,
                                tete=None if etage == "agent" else "HEAD")
        r = Rapport()
        controles_tests.attendus(ctx, r)
        return [c.message for c in r.erreurs("tests.attendus")], [c.message for c in r.constats if c.gravite == "avertissement"]

    def test_une_adr_de_l_agent_ne_justifie_pas_le_changement(self):
        self.ecrire("memoire/decisions/ADR-0001-facteur.md", ADR)
        self.ecrire("tests/test_calc.py", TEST.format(attendu=6))
        self.commit("Le facteur passe à 3" + AGENT)
        erreurs, _ = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("écrite par l'agent", erreurs[0])

    def test_une_adr_en_cours_d_ecriture_ne_justifie_pas_non_plus(self):
        self.ecrire("memoire/decisions/ADR-0001-facteur.md", ADR)
        self.ecrire("tests/test_calc.py", TEST.format(attendu=6))
        erreurs, _ = self.erreurs("agent")
        self.assertEqual(len(erreurs), 1, erreurs)

    def test_une_specification_commitee_par_l_humain_justifie_le_changement(self):
        self.ecrire("memoire/decisions/ADR-0001-facteur.md", ADR)
        self.commit("Le facteur passe à 3, décidé par Théo")
        self.ecrire("tests/test_calc.py", TEST.format(attendu=6))
        self.commit("Le test suit le facteur" + AGENT)
        erreurs, avertissements = self.erreurs()
        self.assertEqual(erreurs, [])
        self.assertTrue(any("spécification changée par l'humain" in a for a in avertissements), avertissements)


if __name__ == "__main__":
    unittest.main()
