"""Relevé de la passe de recul, D : une seule `Dispense-doc` couvrait toute
la plage et toute la table de correspondance. Elle ne vaut plus que pour le
code du commit qui la porte."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, context as contexte, checks_docs as controles_docs, installer as installeur
from socle import language as langue, utils as outils
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
DISPENSE = "\n\nDispense-doc: un renommage interne, rien de visible à documenter"
SIGNATURE = "Co-Authored-By: Un Agent <agent@exemple.org>"


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestDispenseDoc(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-dispense-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        for rel in ("src/a.py", "src/b.py", "docs/a.md", "docs/b.md"):
            (self.racine / rel).parent.mkdir(exist_ok=True)
            (self.racine / rel).write_text("x = 1\n" if rel.endswith(".py") else "# Doc\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(gf.read_text() + '\n[[docmap]]\ncode = ["src/a.py"]\ndocs = ["docs/a.md"]\n\n'
                      '[[docmap]]\ncode = ["src/b.py"]\ndocs = ["docs/b.md"]\n')
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def commit(self, rel, message):
        (self.racine / rel).write_text("x = 2\n")
        git(self.racine, "commit", "-qam", message, "--no-verify")

    def erreurs(self) -> list[str]:
        r = Rapport()
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete="HEAD")
        controles_docs.correspondance(ctx, r)
        return [c.message for c in r.erreurs("docs.correspondance")]

    def test_la_dispense_couvre_son_commit(self):
        self.commit("src/a.py", "Renommage" + DISPENSE)
        self.assertEqual(self.erreurs(), [])

    def test_la_dispense_ne_couvre_pas_un_autre_commit(self):
        self.commit("src/a.py", "Renommage" + DISPENSE)
        self.commit("src/b.py", "Un vrai changement")
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("src/b.py", erreurs[0])
        self.assertNotIn("src/a.py", erreurs[0])
        self.assertEqual(list(controles_docs.fichiers_dispenses(
            contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete="HEAD"))), ["src/a.py"])

    def sha(self) -> str:
        return git(self.racine, "rev-parse", "--short=7", "HEAD").strip()

    def test_une_dispense_hors_du_bloc_final_est_nommee_dans_le_refus(self):
        # B-0275 : la dispense dans un paragraphe à part, avant celui des
        # lignes d'attribution. Git ne la lit pas ; le refus le dit.
        self.commit("src/a.py", "Renommage" + DISPENSE + "\n\n" + SIGNATURE)
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("src/a.py", erreurs[0])
        self.assertIn(f"le commit {self.sha()} porte une ligne `Dispense-doc:` hors du dernier paragraphe", erreurs[0])
        self.assertIn("la mettre dans ce dernier paragraphe, avec les autres trailers", erreurs[0])

    def test_une_dispense_dans_le_bloc_final_vaut_toujours(self):
        self.commit("src/a.py", "Renommage" + DISPENSE + "\n" + SIGNATURE)
        self.assertEqual(self.erreurs(), [])

    def test_le_refus_ne_nomme_pas_un_commit_qui_ne_change_pas_ce_code(self):
        (self.racine / "docs/a.md").write_text("# Doc changée\n")
        self.commit("src/a.py", "a et sa doc" + DISPENSE + "\n\n" + SIGNATURE)
        self.commit("src/b.py", "Un vrai changement")
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("src/b.py", erreurs[0])
        self.assertNotIn("hors du dernier paragraphe", erreurs[0])


class TestTrailersHorsBloc(unittest.TestCase):
    """Les lignes d'un trailer que git ne lit pas, hors du dernier paragraphe."""

    def test_le_paragraphe_avant_les_signatures(self):
        message = "Sujet\n\nCorps.\n\nDispense-doc: une raison assez longue\n\n" + SIGNATURE + "\n"
        self.assertEqual(outils.trailers_hors_bloc(message), {"dispense-doc": ["une raison assez longue"]})
        self.assertEqual(langue.trailers_hors_bloc(message)["dispense-doc"], ["une raison assez longue"])
        self.assertNotIn("dispense-doc", langue.trailers(message))

    def test_le_nom_anglais_se_traduit(self):
        message = "Subject\n\nWaive-test: f — an English reason\n\n" + SIGNATURE
        self.assertEqual(langue.trailers_hors_bloc(message), {"dispense-test": ["f — an English reason"]})

    def test_le_bloc_final_et_le_sujet_n_en_sont_pas(self):
        self.assertEqual(outils.trailers_hors_bloc("Dispense-doc: le sujet\n\nDispense-doc: une raison\n" + SIGNATURE),
                         {})

    def test_un_message_d_un_seul_paragraphe_n_a_pas_de_bloc_final(self):
        self.assertEqual(langue.trailers_hors_bloc("Sujet\nDispense-doc: une raison"), {"dispense-doc": ["une raison"]})
        self.assertEqual(langue.trailers("Sujet\nDispense-doc: une raison"), {})


if __name__ == "__main__":
    unittest.main()
