"""La mémoire, relevé de la passe de recul, section D : une décision se
réécrivait dans ses lignes en citation ; le journal acceptait un ajout au
milieu d'une phrase ; un titre mal formé faisait disparaître l'entrée de
toute lecture."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, contexte, controles_memoire, installeur
from socle.rapport import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "moteur"
ADR = ("<!-- socle: couche=decisions zone=publique -->\n# ADR-0001 — Une seule constante\n\n"
       "> statut : acceptée · date : 2026-10-10\n\n## Décision\n\n> Le facteur vit dans `FACTEUR`.\n\nRien d'autre.\n")
JOURNAL = ("<!-- socle: couche=journal zone=publique -->\n# Journal — 2026-10\n\n"
           "## J-2026-10-10-A — Le départ\n\n> type : événement\n\nLe projet commence ici.\n")


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestMemoire(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-memoire-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        self.ecrire("memory/decisions/ADR-0001-une-seule-constante.md", ADR)
        self.ecrire("memory/journal/2026-10.md", JOURNAL)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def ecrire(self, rel, texte):
        (self.racine / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.racine / rel).write_text(texte)

    def erreurs(self, controle, nom) -> list[str]:
        r = Rapport()
        controle(contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.base), r)
        return [c.message for c in r.erreurs(nom)]

    def test_une_citation_de_la_decision_ne_se_reecrit_pas(self):
        self.ecrire("memory/decisions/ADR-0001-une-seule-constante.md",
                    ADR.replace("> Le facteur vit dans `FACTEUR`.", "> Le facteur vit où l'on veut."))
        self.assertTrue(any("réécrite" in e for e in self.erreurs(controles_memoire.ajout_seul, "memoire.ajout-seul")))

    def test_seul_le_statut_d_une_decision_change(self):
        self.ecrire("memory/decisions/ADR-0001-une-seule-constante.md",
                    ADR.replace("statut : acceptée", "statut : dépréciée"))
        self.assertFalse(any("réécrite" in e for e in self.erreurs(controles_memoire.ajout_seul, "memoire.ajout-seul")))

    def test_un_ajout_au_journal_commence_sur_une_ligne_nouvelle(self):
        self.ecrire("memory/journal/2026-10.md", JOURNAL.replace("commence ici.", "commence ici. Ou pas."))
        self.assertTrue(any("modifiée" in e for e in self.erreurs(controles_memoire.ajout_seul, "memoire.ajout-seul")))
        self.ecrire("memory/journal/2026-10.md", JOURNAL + "\n### B-0001 — Archivé\n\n> statut : fait · origine : J-2026-10-10-A\n")
        self.assertEqual(self.erreurs(controles_memoire.ajout_seul, "memoire.ajout-seul"), [])

    def test_un_titre_d_entree_illisible_est_signale(self):
        self.ecrire("memory/journal/2026-10.md", JOURNAL + "\n## J-2026-10-11 La suite, sans sa lettre\n\nTexte.\n")
        erreurs = self.erreurs(controles_memoire.format_memoire, "memoire.format")
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("titre d'entrée illisible", erreurs[0])


if __name__ == "__main__":
    unittest.main()
