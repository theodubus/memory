"""ADR-0025 : au format 3, le backlog est un dossier, un fichier par sujet.
La migration du format 2 découpe le fichier unique, sans rien perdre, et se
relance sans dommage ; ce qui le lisait (création d'un sujet, liens,
archivage, bascule, état) suit."""

import io
import contextlib
import unittest

from socle import archivage, config, controles_cliquet, contexte, etat, memoire, migrations
from socle.rapport import Rapport
from tests.test_bascule import P, Projet, git

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
        detaille = (self.racine / "memory/backlog/B-0002-un-sujet-detaille.md").read_text()
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

    def test_un_sujet_clos_reste_dans_son_fichier(self):
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            self.assertEqual(archivage.archiver_backlog(self.projet), 0)
        self.assertIn("rien ne s'archive", sortie.getvalue())
        self.assertTrue((self.racine / "memory/backlog/B-0002-un-sujet-detaille.md").is_file())
        ligne = next(l for l in etat.calculer(self.projet, contenus=False).splitlines() if l.startswith("backlog"))
        self.assertTrue(ligne.endswith("1 clos"), ligne)

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


if __name__ == "__main__":
    unittest.main()
