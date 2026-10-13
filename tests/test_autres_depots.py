"""B-0052, mesuré à R6 : la forme `depot:chemin`, faite pour citer un autre
dépôt, laissait passer n'importe quelle chaîne `x:chemin` sans rien
vérifier. Un dépôt cité se déclare dans `[references] repos` des garde-fous,
et l'humain seul en ajoute ; un dépôt non déclaré est signalé."""

import contextlib
import io
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, contexte, controles_memoire, installeur
from socle.controles_cliquet import assouplissements
from socle.rapport import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "moteur"


class TestAutresDepots(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-depots-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)

    def avertissements(self, texte: str, repos=None) -> list[str]:
        (self.racine / "docs").mkdir(exist_ok=True)
        (self.racine / "docs/notes.md").write_text(texte)
        projet = config.Projet.charger(self.racine)
        if repos is not None:
            projet.garde_fous["references"]["repos"] = repos
        r = Rapport()
        controles_memoire.references(contexte.Contexte(projet, etage="agent"), r)
        self.assertEqual([c.message for c in r.erreurs()], [])
        return [c.message for c in r.constats if c.gravite == "avertissement"]

    def test_un_depot_non_declare_est_signale_une_fois(self):
        avertis = self.avertissements("Créés par la rustine : `x.patch:engine/a.rs` et `x.patch:engine/b.rs`.\n")
        self.assertEqual(len(avertis), 1, avertis)
        self.assertIn("dépôt « x.patch » non déclaré, 2 chemin(s)", avertis[0])

    def test_un_depot_declare_passe(self):
        self.assertEqual(self.avertissements("Voir `chess:tools/etat.sh`.\n", repos=["chess"]), [])

    def test_une_url_une_reference_ou_une_revision_ne_sont_pas_des_depots(self):
        texte = "`https://exemple.org/a/b`, `HEAD:refs/heads/main`, `1f6dab2:docs/a.md`, `std::fs`\n"
        self.assertEqual(self.avertissements(texte), [])
        for jeton in ("https://exemple.org/a/b", "HEAD:refs/heads/main", "fichier:src/x.rs:12", "std::fs"):
            self.assertIsNone(controles_memoire.depot_non_declare(None, jeton), jeton)

    def test_declarer_un_depot_est_un_assouplissement(self):
        avant = {"references": {"scan": ["**/*.md"], "exclude": [], "repos": []}}
        apres = {"references": {"scan": ["**/*.md"], "exclude": [], "repos": ["chess"]}}
        self.assertEqual([c for c, _ in assouplissements(avant, apres)], ["references.repos"])
        self.assertEqual(assouplissements(apres, avant), [])


if __name__ == "__main__":
    unittest.main()
