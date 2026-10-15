"""ADR-0025 : au format 3, le backlog est un dossier, un fichier par sujet.
La migration du format 2 découpe le fichier unique, sans rien perdre, et se
relance sans dommage ; ce qui le lisait (création d'un sujet, liens,
archivage, bascule, état) suit."""

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from socle import (archive as archivage, selftest as autotest, config, checks_memory as controles_memoire,
                   checks_ratchet as controles_cliquet,
                   context as contexte, state as etat, installer as installeur, memory as memoire, migrations)
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
    """Le projet de la bascule, au format 2, avec un second sujet clos et
    détaillé, puis migré au format 3 et commité."""

    def setUp(self):
        super().setUp()
        backlog = self.racine / config.FORMAT_2.backlog
        backlog.write_text(backlog.read_text().rstrip("\n") + "\n" + DEUX_SUJETS)
        git(self.racine, "commit", "-qam", "un second sujet", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        self.avant = {e.id: e.corps for e in memoire.Memoire.charger(self.racine).entrees("B")}
        self.journal = migrations._vers_format_3(self.racine)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "format 3", "--no-verify")
        config.oublier_formats()
        self.projet = config.Projet.charger(self.racine)


class TestMigration(Format3):
    def test_un_fichier_par_sujet_sans_rien_perdre(self):
        self.assertEqual(self.projet.chemins.format, 3)
        self.assertFalse((self.racine / config.FORMAT_2.backlog).exists())
        detaille = (self.racine / "memory/backlog/closed/B-0002-un-sujet-detaille.md").read_text()
        self.assertTrue(detaille.startswith("<!-- socle: couche=backlog zone=publique -->\n# B-0002 — Un sujet détaillé\n"))
        self.assertIn("\n## Les commandes\n", detaille, "les sous-titres remontent avec le sujet")
        self.assertIn("\n## pas un titre, un commentaire du shell\n", detaille, "un bloc de code ne bouge pas")
        apres = {e.id: e.corps for e in memoire.Memoire.charger(self.racine).entrees("B")}
        self.assertEqual(apres.keys(), self.avant.keys())
        self.assertEqual(apres["B-0001"], self.avant["B-0001"])
        self.assertIn('"memory/backlog/*.md" = { max_bytes = 8000 }', (self.racine / ".socle/guardrails.toml").read_text())
        self.assertEqual(self.journal[0], "memory/backlog.md → memory/backlog/ : 2 sujet(s), un fichier chacun")

    def test_relancee_elle_ne_fait_rien(self):
        self.assertEqual(migrations._vers_format_3(self.racine), [])
        self.assertEqual(git(self.racine, "status", "--porcelain"), "")

    def test_la_memoire_migree_passe_les_controles(self):
        # Le lien vers l'ancre du sujet dans le fichier unique reste valide,
        # et le plafond du fichier disparu se retire sans assouplir.
        self.assertEqual(self.erreurs(), [])
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base)
        r = Rapport()
        controles_cliquet.cliquet(ctx, r)
        self.assertEqual([c.message for c in r.erreurs()], [])

    def test_un_lien_vers_un_sujet_qui_n_existe_pas_reste_mort(self):
        (self.racine / "docs/notes.md").write_text("[mort](../memory/backlog.md#b-0099--un-autre)\n")
        self.assertEqual(self.erreurs(), ["ancre morte : ../memory/backlog.md#b-0099--un-autre"])


class TestApresLaMigration(Format3):
    def test_un_sujet_nouveau_a_son_fichier(self):
        code, sortie = self.socle("new", "backlog", "Un troisième sujet", "--public")
        self.assertEqual(code, 0, sortie)
        self.assertIn("B-0003\tmemory/backlog/B-0003-un-troisieme-sujet.md", sortie)
        texte = (self.racine / "memory/backlog/B-0003-un-troisieme-sujet.md").read_text()
        self.assertTrue(texte.startswith("<!-- socle: couche=backlog zone=publique -->\n# B-0003 — Un troisième sujet\n"))

    def test_un_sujet_clos_se_range_avec_les_clos(self):
        # ADR-0030 (D-0028) : la migration a rangé B-0002, clos ; un sujet
        # qu'on clôt ensuite attend `socle archive`, qui le range.
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
        self.assertEqual(self.erreurs(), [])
        ligne = next(l for l in etat.calculer(self.projet, contenus=False).splitlines() if l.startswith("backlog"))
        self.assertTrue(ligne.endswith("2 clos"), ligne)

    def test_un_sujet_bascule_comme_une_decision(self):
        code, sortie = self.socle("prive", "basculer", "B-0001")
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
        # La base après la migration : ses titres remontés ne sont pas l'objet ici.
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        code, sortie = self.socle("prive", "basculer", "B-0002")
        self.assertEqual(code, 0, sortie)
        self.assertTrue((self.racine / f"memory/private/backlog/closed/{P}B-0001-un-sujet-detaille.md").is_file())
        self.assertTrue((self.racine / "memory/backlog/closed/B-0002-basculee.md").is_file())
        self.assertEqual(self.erreurs(), [])

    def test_la_mise_a_jour_range_un_projet_existant(self):
        # Un projet au format 3 d'avant le rangement : un sujet clos parmi les ouverts.
        clos = self.racine / "memory/backlog/closed/B-0002-un-sujet-detaille.md"
        git(self.racine, "mv", str(clos), str(self.racine / "memory/backlog" / clos.name))
        git(self.racine, "commit", "-qm", "avant le rangement", "--no-verify")
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        self.assertIn("backlog : 1 sujet(s) clos rangé(s) dans `closed/`", sortie.getvalue())
        self.assertTrue(clos.is_file())


class TestInstallation(unittest.TestCase):
    def test_une_installation_au_format_3(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-format-3-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        git(racine, "init", "-q", "-b", "main")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(racine, "python", "@essai", source=MOTEUR, format_memoire=3)
        config.oublier_formats()
        self.assertEqual(config.chemins(racine).format, 3)
        self.assertTrue((racine / "memory/backlog/.gitkeep").is_file())
        self.assertFalse((racine / "memory/backlog.md").exists())
        self.assertIn("format = 3", (racine / ".socle/engine.lock").read_text())
        gf = (racine / ".socle/guardrails.toml").read_text()
        self.assertIn('"memory/backlog/*.md" = { max_bytes = 8000 }', gf)
        self.assertNotIn('"memory/backlog.md"', gf)
        self.assertIn("| `memory/backlog/` |", (racine / "AGENTS.md").read_text())
        # L'auto-test et le banc ajoutent un sujet dans l'un ou l'autre format.
        autotest.ajouter_sujet(racine, "\n## B-0001 — Un sujet\n\n> statut : ouvert · origine : fichier:calc.py\n")
        self.assertEqual((racine / "memory/backlog/B-0001-un-sujet.md").read_text(),
                         "<!-- socle: couche=backlog zone=publique -->\n# B-0001 — Un sujet\n\n"
                         "> statut : ouvert · origine : fichier:calc.py\n")

    def test_la_mise_a_jour_d_un_backlog_vide(self):
        # B-0061 : sans sujet, le dossier n'était pas créé, et l'ajout du
        # dossier à l'index faisait échouer la mise à jour.
        racine = Path(tempfile.mkdtemp(prefix="socle-format-2-vide-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        git(racine, "init", "-q", "-b", "main")
        (racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(racine, "python", "@essai", source=MOTEUR, format_memoire=2)
        git(racine, "add", "-A")
        git(racine, "commit", "-qm", "base", "--no-verify")
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            # 1 : l'audit attend l'approbation des fichiers protégés mis à
            # jour, comme toute mise à jour ; 2 serait un refus.
            self.assertEqual(installeur.installer(racine, "python", "@essai", source=MOTEUR), 1, sortie.getvalue())
        self.assertNotIn("refus :", sortie.getvalue())
        self.assertIn("memory/backlog.md → memory/backlog/ : 0 sujet(s)", sortie.getvalue())
        config.oublier_formats()
        self.assertEqual(config.chemins(racine).format, 3)
        self.assertFalse((racine / "memory/backlog.md").exists())
        self.assertIn("memory/backlog/.gitkeep", git(racine, "ls-files", "memory/backlog").split())

    def test_un_sujet_de_plus_au_format_2(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-format-2-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        git(racine, "init", "-q", "-b", "main")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(racine, "python", "@essai", source=MOTEUR, format_memoire=2)
        config.oublier_formats()
        autotest.ajouter_sujet(racine, "\n## B-0001 — Un sujet\n\n> statut : ouvert · origine : fichier:calc.py\n")
        self.assertTrue((racine / "memory/backlog.md").read_text().endswith(
            "\n## B-0001 — Un sujet\n\n> statut : ouvert · origine : fichier:calc.py\n"))

if __name__ == "__main__":
    unittest.main()
