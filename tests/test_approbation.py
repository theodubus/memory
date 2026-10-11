"""`socle approve`, la commande de l'humain qui valide son propre changement
protégé : la demande qu'elle écrit passe les contrôles de la mémoire, même
quand sa raison cite une entrée, et dans un dépôt amont comme dans un projet.
Le cas d'origine : Théo l'a lancée dans ce dépôt, sa raison citait un sujet
du backlog, et le hook avant commit a refusé la demande écrite."""

import argparse
import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import cli, config, contexte, controles_memoire, installeur, memoire
from socle.rapport import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "moteur"


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestApprobation(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-approbation-"))
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        with open(self.racine / "memory/backlog.md", "a") as f:
            f.write("\n## B-0001 — Accepter le workflow\n\n> statut : ouvert · origine : fichier:calc.py · pour : humain\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "installation", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        workflow = self.racine / ".github/workflows/socle.yml"
        workflow.write_text(workflow.read_text() + "# une étape de plus\n")

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def approuver(self, *fichiers, texte="Accepté (B-0001)") -> tuple[int, str]:
        erreurs = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(erreurs):
            code = cli.cmd_approve(argparse.Namespace(root=str(self.racine), files=list(fichiers), keys=None, text=texte))
        return code, erreurs.getvalue()

    def test_la_demande_ecrite_passe_les_controles_de_la_memoire(self):
        code, _ = self.approuver(".github/workflows/socle.yml")
        self.assertEqual(code, 0)
        demande = next((self.racine / "memory/requests").glob("D-*-approbation-humaine.md")).read_text()
        b1 = memoire.empreinte_entree(memoire.Memoire.charger(self.racine).entree("B-0001"))
        self.assertIn(f"B-0001@{b1}", demande)
        self.assertIn(f"(../../{config.Projet.charger(self.racine).dossier_moteur}/socle/FORMAT.md)", demande)
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base)
        r = Rapport()
        controles_memoire.references(ctx, r)
        controles_memoire.lectures(ctx, r)
        self.assertEqual([c.message for c in r.erreurs()], [])

    def test_rien_n_est_ecrit_pour_une_entree_ou_un_fichier_absents(self):
        code, erreurs = self.approuver(".socle/git-hooks/absent", texte="Accepté (B-0099)")
        self.assertEqual(code, 2)
        self.assertIn("cite B-0099", erreurs)
        self.assertIn("rien à approuver", erreurs)
        self.assertEqual(list((self.racine / "memory/requests").glob("D-*-approbation-humaine.md")), [])


    def test_deux_approbations_sur_une_branche_ne_sont_pas_des_copies(self):
        """Le cas de B-0019 : une approbation pour le workflow et le hook, une
        autre pour le verrou ; le gabarit les fait se ressembler, et
        `docs.copie` refusait le commit."""
        from socle import controles_docs

        self.assertEqual(self.approuver(".github/workflows/socle.yml")[0], 0)
        verrou = self.racine / ".socle/engine.lock"
        verrou.write_text(verrou.read_text() + "# format noté\n")
        self.assertEqual(self.approuver(".socle/engine.lock", texte="Le verrou change (B-0001)")[0], 0)
        self.assertEqual(len(list((self.racine / "memory/requests").glob("D-*-approbation-humaine.md"))), 2)
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="git", base=self.base)
        r = Rapport()
        controles_docs.copie(ctx, r)
        self.assertEqual([c.message for c in r.erreurs()], [])

if __name__ == "__main__":
    unittest.main()
