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

from socle import config, context as contexte, checks_memory as controles_memoire, installer as installeur
from socle.checks_ratchet import assouplissements
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"


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

    def test_un_depot_que_le_projet_lie_est_connu(self):
        """Théo, J-2026-10-13-L : l'outil s'adapte au projet, il ne demande
        pas ce que le projet dit déjà. Un dépôt lié par son adresse est
        connu, dans un texte lu ou dans `.gitmodules`."""
        texte = "Repris de [chess](https://github.com/theodubus/chess) : `chess:tools/etat.sh`.\n"
        self.assertEqual(self.avertissements(texte), [])
        (self.racine / ".gitmodules").write_text('[submodule "ui"]\n\turl = git@github.com:theodubus/ui.git\n')
        self.assertEqual(self.avertissements("Voir `ui:src/main.ts`.\n"), [])
        self.assertEqual(len(self.avertissements("Voir `x.patch:engine/a.rs`.\n")), 1)
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent")
        self.assertEqual(controles_memoire.depots_connus(ctx, ["https://github.com/theodubus/chess."]), {"chess", "ui"})

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
