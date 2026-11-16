"""ADR-0025 : le backlog est un dossier, un fichier par sujet ; ce qui le
lit (création d'un sujet, rangement des clos, bascule, état) suit."""

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from socle import (archive as archivage, selftest as autotest, config, checks_memory as controles_memoire,
                   context as contexte, state as etat, installer as installeur, memory as memoire)
from socle.report import Rapport
from tests.test_bascule import MOTEUR, P, Projet, git

DEUX_SUJETS = """
## B-0002 — Un sujet détaillé

> statut : fait · origine : fichier:calc.py · ref : fichier:calc.py

Son mode d'emploi :

### Les commandes

```sh
## pas un titre, un commentaire du shell
```
"""


class Format3(Projet):
    """Le projet de la bascule, avec un second sujet clos et détaillé, rangé
    avec les clos, et commité."""

    def setUp(self):
        super().setUp()
        autotest.ajouter_sujet(self.racine, DEUX_SUJETS)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "un second sujet", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        self.projet = config.Projet.charger(self.racine)


class TestBacklogEnDossier(Format3):
    def test_un_sujet_nouveau_a_son_fichier(self):
        code, sortie = self.socle("new", "need", "Un troisième sujet", "--public")
        self.assertEqual(code, 0, sortie)
        self.assertIn("B-0003\tmemory/backlog/B-0003-un-troisieme-sujet.md", sortie)
        texte = (self.racine / "memory/backlog/B-0003-un-troisieme-sujet.md").read_text()
        self.assertTrue(texte.startswith("<!-- socle: couche=backlog zone=publique -->\n# B-0003 — Un troisième sujet\n"))

    def test_un_sujet_clos_se_range_avec_les_clos(self):
        # ADR-0030 (D-0028) : B-0002, clos, est rangé ; un sujet qu'on clôt
        # ensuite attend `socle archive`, qui le range.
        self.assertTrue((self.racine / "memory/backlog/closed/B-0002-un-sujet-detaille.md").is_file())
        sujet = next((self.racine / "memory/backlog").glob("B-0001-*.md"))
        sujet.write_text(sujet.read_text().replace("> statut : ouvert", "> statut : fait · ref : fichier:calc.py", 1))
        self.assertIn("`B-0001` est clos (« fait ») mais reste parmi les sujets ouverts : `python3 .socle/socle "
                      "archive` le range dans `closed/`", self.erreurs())
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            self.assertEqual(archivage.archiver_backlog(self.projet), 0)
        self.assertIn("1 sujet(s) rangé(s)", sortie.getvalue())
        self.assertFalse(sujet.exists())
        self.assertTrue((self.racine / "memory/backlog/closed" / sujet.name).is_file())
        self.assertIn(f"memory/backlog/closed/{sujet.name}", git(self.racine, "diff", "--cached", "--name-only"))
        # Un document qui n'est pas de la mémoire gelée suit le déplacement.
        self.assertEqual(self.erreurs(), [f"lien mort : ../memory/backlog/{sujet.name}"])
        notes = self.racine / "docs/notes.md"
        notes.write_text(notes.read_text().replace("backlog/B-0001", "backlog/closed/B-0001"))
        self.assertEqual(self.erreurs(), [])
        ligne = next(l for l in etat.calculer(self.projet, contenus=False).splitlines() if l.startswith("backlog"))
        self.assertTrue(ligne.endswith("2 clos"), ligne)

    def test_un_sujet_bascule_comme_une_decision(self):
        code, sortie = self.socle("private", "move", "B-0001")
        self.assertEqual(code, 0, sortie)
        self.assertFalse(list((self.racine / "memory/backlog").glob("B-0001-demarcher*")))
        pierre = (self.racine / "memory/backlog/B-0001-basculee.md").read_text()
        self.assertIn(f"# B-0001 — {memoire.TITRE_BASCULEE}", pierre)
        self.assertNotIn("Orion", pierre)
        copie = (self.racine / f"memory/private/backlog/{P}B-0001-demarcher-le-client-orion.md").read_text()
        self.assertIn(f"# {P}B-0001 — Démarcher le client Orion", copie)
        self.assertIn("depuis : B-0001", copie)
        self.assertEqual(self.erreurs(), [])



class TestRangement(Format3):
    """ADR-0030 (D-0028) : les sujets clos à l'écart des ouverts."""

    def test_le_sous_dossier_des_clos_est_du_backlog(self):
        clos = "memory/backlog/closed/B-0002-un-sujet-detaille.md"
        self.assertEqual(memoire.couche_attendue(clos), "backlog")
        self.assertEqual(memoire.couche_attendue(f"memory/private/backlog/closed/{P}B-0001-x.md"), "backlog")
        self.assertEqual(memoire.couche_attendue("memory/backlog/autre/B-0002-x.md"), "inconnue")
        self.assertTrue(memoire.parmi_les_clos(clos))
        self.assertFalse(memoire.parmi_les_clos("memory/backlog/B-0001-x.md"))
        self.assertEqual(memoire.hors_des_clos(clos), "memory/backlog/B-0002-un-sujet-detaille.md")
        self.assertEqual(memoire.hors_des_clos("memory/journal/2026-10.md"), "memory/journal/2026-10.md")

    def test_un_sujet_rouvert_revient_parmi_les_ouverts(self):
        clos = self.racine / "memory/backlog/closed/B-0002-un-sujet-detaille.md"
        clos.write_text(clos.read_text().replace("> statut : fait", "> statut : ouvert", 1))
        self.assertIn("`B-0002` est rangé parmi les sujets clos alors qu'il est « ouvert » : `python3 .socle/socle "
                      "archive` le remet parmi les ouverts", self.erreurs())
        self.assertEqual(archivage.ranger_backlog(self.racine),
                         [("memory/backlog/closed/B-0002-un-sujet-detaille.md",
                           "memory/backlog/B-0002-un-sujet-detaille.md")])
        self.assertEqual(self.erreurs(), [])
        self.assertEqual(archivage.ranger_backlog(self.racine), [])

    def test_un_sujet_clos_garde_le_plafond_d_un_sujet(self):
        clos = self.racine / "memory/backlog/closed/B-0002-un-sujet-detaille.md"
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.base)
        r = Rapport()
        controles_memoire.budgets(ctx, r)
        self.assertEqual([c.message for c in r.erreurs()], [])
        clos.write_text(clos.read_text() + "x" * 9000 + "\n")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.base)
        r = Rapport()
        controles_memoire.budgets(ctx, r)
        self.assertEqual([(c.message.split(" octets")[1], c.chemin) for c in r.erreurs()],
                         [(' pour un budget de 8000 (memory/backlog/*.md) : archiver dans le journal',
                           "memory/backlog/closed/B-0002-un-sujet-detaille.md")])

    def test_un_sujet_clos_bascule_parmi_les_clos(self):
        code, sortie = self.socle("private", "move", "B-0002")
        self.assertEqual(code, 0, sortie)
        self.assertTrue((self.racine / f"memory/private/backlog/closed/{P}B-0001-un-sujet-detaille.md").is_file())
        self.assertTrue((self.racine / "memory/backlog/closed/B-0002-basculee.md").is_file())
        self.assertEqual(self.erreurs(), [])


class TestInstallation(unittest.TestCase):
    def test_une_installation_au_format_3(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-format-3-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        git(racine, "init", "-q", "-b", "main")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(racine, "python", "@essai", source=MOTEUR)
        self.assertTrue((racine / "memory/backlog/.gitkeep").is_file())
        self.assertFalse((racine / "memory/backlog.md").exists())
        self.assertIn("format = 3", (racine / ".socle/engine.lock").read_text())
        gf = (racine / ".socle/guardrails.toml").read_text()
        self.assertIn('"memory/backlog/*.md" = { max_bytes = 8000 }', gf)
        self.assertNotIn('"memory/backlog.md"', gf)
        self.assertIn("| `memory/backlog/` |", (racine / "AGENTS.md").read_text())
        # L'auto-test et le banc ajoutent un sujet dans son fichier.
        autotest.ajouter_sujet(racine, "\n## B-0001 — Un sujet\n\n> statut : ouvert · origine : fichier:calc.py\n")
        self.assertEqual((racine / "memory/backlog/B-0001-un-sujet.md").read_text(),
                         "<!-- socle: couche=backlog zone=publique -->\n# B-0001 — Un sujet\n\n"
                         "> statut : ouvert · origine : fichier:calc.py\n")


if __name__ == "__main__":
    unittest.main()
