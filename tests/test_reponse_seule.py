"""B-0142, la gêne 6 de chess : une réponse consignée aussitôt, pas encore
commitée, n'est plus « en attente » dans l'état. L'avertissement de la
réponse poussée seule (`demandes.reponse-seule`) s'est retiré avec ses
tests (D-0189) : une réponse poussée avant le changement qu'elle autorise le
couvre désormais (`tests/test_reponse_avant_le_lot.py`)."""

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from socle import cli, config, installer as installeur, state as etat
from tests.test_attendus import MOTEUR, TEST, git

DEMANDE = """<!-- socle: couche=demandes zone=publique -->
# D-0001 — Le facteur passe à 3 ?

> date : 2026-11-14

## Décision demandée

{objet}

## Réponses possibles

- `valider` — je fais le changement.
- `refuser` — je garde tout tel quel.
"""


class TestReponsePousseeSeule(unittest.TestCase):
    """Un projet installé, poussé sur une origine locale, et une branche de
    travail qui y a poussé sa demande ; l'humain y répond `valider`."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-reponse-seule-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        origine = self.racine.parent / (self.racine.name + "-origine.git")
        self.addCleanup(shutil.rmtree, origine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        (self.racine / "tests").mkdir()
        (self.racine / "tests/test_calc.py").write_text(TEST.format(attendu=4))
        (self.racine / "docs").mkdir()
        (self.racine / "docs/double.cas.json").write_text('[\n  {"entree": 2, "attendu": 4}\n]\n')
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(gf.read_text().replace("spec_paths =", 'case_paths = ["docs/*.cas.json"]\nspec_paths =', 1))
        pol = self.racine / ".socle/policy.toml"
        pol.write_text(pol.read_text().replace("[human]\n", '[human]\nrepo_url = "https://github.com/x/y"\n', 1))
        self.commit("base")
        git(self.racine.parent, "init", "-q", "--bare", str(origine))
        git(self.racine, "remote", "add", "origin", str(origine))
        git(self.racine, "push", "-q", "--no-verify", "origin", "main")
        git(self.racine, "checkout", "-qb", "travail")

    def commit(self, message):
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", message, "--no-verify")

    def demander(self, objet: str):
        """La demande, commitée et poussée telle quelle : l'humain l'a lue."""
        (self.racine / "memory/requests").mkdir(parents=True, exist_ok=True)
        (self.racine / "memory/requests/D-0001-facteur.md").write_text(DEMANDE.format(objet=objet))
        self.commit("La demande")
        git(self.racine, "push", "-q", "--no-verify", "-u", "origin", "travail")

    def repondre(self):
        """La réponse donnée dans la conversation, consignée aussitôt par
        l'agent, dans l'arbre, pas encore commitée."""
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as erreurs:
            code = cli.main(["--root", str(self.racine), "answer", "D-0001", "valider", "--relayed", "--by", "Théo",
                             "--quote", "oui, valide"])
        self.assertEqual(code, 0, erreurs.getvalue())

    def test_une_reponse_consignee_mais_pas_commitee_n_est_plus_en_attente(self):
        """La gêne 6 de chess : l'état lit l'arbre, fichiers non suivis
        compris ; la réponse consignée aussitôt y est répondue."""
        self.demander("Valider que `test_double` attende 6.")
        projet = config.Projet.charger(self.racine)
        avant = etat.calculer(projet, contenus=False)
        self.assertIn("demandes humaines en attente : 1", avant)
        self.repondre()
        self.assertEqual(git(self.racine, "status", "--porcelain", "--", "memory/requests").count("??"), 1)
        apres = etat.calculer(config.Projet.charger(self.racine), contenus=False)
        self.assertIn("demandes humaines en attente : 0", apres)
        self.assertNotIn("D-0001 — Le facteur passe à 3", apres)


if __name__ == "__main__":
    unittest.main()
