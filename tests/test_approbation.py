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
import unittest.mock
from pathlib import Path

from socle import cli, config, contexte, controles_memoire, installeur, memoire
from socle.rapport import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "moteur"


def git(cwd, *args):
    # Sans `CLAUDECODE` : un commit de ces tests est celui d'un humain, même
    # lancé depuis une session d'agent, dont le hook git le marquerait.
    env = {**{k: v for k, v in os.environ.items() if k != "CLAUDECODE"}, "GIT_AUTHOR_NAME": "t",
           "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
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

    def test_sans_liste_les_fichiers_changes_se_trouvent_seuls(self):
        """B-0034, P3 : une mise à jour faisait recopier à l'humain chaque
        fichier protégé changé dans `--files`."""
        self.assertEqual(cli.fichiers_a_approuver(config.Projet.charger(self.racine)), [".github/workflows/socle.yml"])
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(io.StringIO()):
            code = cli.cmd_approve(argparse.Namespace(root=str(self.racine), files=None, keys=None,
                                                      text="Mise à jour du socle", oui=True))
        self.assertEqual(code, 0)
        self.assertIn("  - .github/workflows/socle.yml", sortie.getvalue())
        self.assertEqual(cli.fichiers_a_approuver(config.Projet.charger(self.racine)), [])
        demande = next((self.racine / "memory/requests").glob("D-*-approbation-humaine.md")).read_text()
        self.assertIn("`.github/workflows/socle.yml`", demande)

    def test_l_etat_rappelle_l_approbation_jusqu_au_commit_suivant_de_l_agent(self):
        """B-0034, P7 : Théo a approuvé D-0012 dans son terminal, et ne
        retrouvait pas ce numéro dans la conversation : l'état le liste à
        l'agent, qui le cite, jusqu'à son commit suivant."""
        from socle import etat, humain

        git(self.racine, "commit", "-qm", "travail\n\nCo-Authored-By: Claude <noreply@anthropic.com>", "--allow-empty",
            "--no-verify")
        projet = config.Projet.charger(self.racine)
        self.assertIsNotNone(humain.dernier_commit_agent(projet))
        self.assertEqual(humain.fait_par_l_humain(projet), [])
        self.assertEqual(self.approuver(".github/workflows/socle.yml")[0], 0)
        faits = humain.fait_par_l_humain(projet)
        self.assertEqual(len(faits), 1)
        self.assertIn("D-0001 — ", faits[0].quoi)
        self.assertIn("écrit par l'humain lui-même depuis le dernier commit de l'agent : 1",
                      etat.calculer(projet, contenus=False))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "approbation", "--no-verify")  # un commit de l'humain
        self.assertEqual(len(humain.fait_par_l_humain(projet)), 1)
        git(self.racine, "commit", "-qm", "suite\n\nSocle-Agent: claude-code", "--allow-empty", "--no-verify")
        self.assertEqual(humain.fait_par_l_humain(projet), [])

    def test_sans_liste_ni_confirmation_rien_n_est_approuve(self):
        erreurs = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(erreurs), \
                unittest.mock.patch("sys.stdin", io.StringIO("")):
            code = cli.cmd_approve(argparse.Namespace(root=str(self.racine), files=None, keys=None, text="x"))
        self.assertEqual(code, 2)
        self.assertIn("--oui", erreurs.getvalue())
        self.assertEqual(list((self.racine / "memory/requests").glob("D-*-approbation-humaine.md")), [])

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
