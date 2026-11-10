import unittest
from pathlib import Path

from socle import config, memory as memoire, requests as demandes, utils as outils

CANONIQUE = """<!-- socle: couche=canonique zone=publique -->
# Mémoire canonique

## F-0001 — Le traitement par lots lit 70 452 lignes

> statut : mesuré · preuve : cmd:`cargo run -- lots 7, taille 7` · date : 2026-10-10

Mesuré sur le binaire de base.

## F-0002 — ~~La copie des tampons coûte 20 %~~

> statut : Réfuté
> Réfutation : F-0001

Corps conservé.

```markdown
## F-0099 — un exemple dans un bloc de code
```
"""


class TestAnalyse(unittest.TestCase):
    def test_entete_et_entrees(self):
        f = memoire.analyser("memory/canonical.md", CANONIQUE)
        self.assertEqual((f.couche, f.zone), ("canonique", "publique"))
        self.assertEqual([e.id for e in f.entrees], ["F-0001", "F-0002"])

    def test_metadonnees_et_commande_avec_virgule(self):
        e = memoire.analyser("memory/canonical.md", CANONIQUE).entrees[0]
        self.assertEqual(e.statut, "mesure")
        self.assertEqual(e.refs("preuve"), [("cmd", "cargo run -- lots 7, taille 7")])

    def test_fait_barre_et_meta_sur_deux_lignes(self):
        e = memoire.analyser("memory/canonical.md", CANONIQUE).entrees[1]
        self.assertTrue(e.barre)
        self.assertEqual(e.titre, "La copie des tampons coûte 20 %")
        self.assertEqual(e.statut, "refute")
        self.assertEqual(e.refs("refutation"), [("id", "F-0001")])

    def test_rien_n_est_lu_dans_un_bloc_de_code(self):
        self.assertNotIn("F-0099", [i for i, _ in memoire.mentions(CANONIQUE)])

    def test_archive_imbriquee_dans_le_journal(self):
        texte = ("<!-- socle: couche=journal zone=publique -->\n# Journal\n\n"
                 "## J-2026-10-12-A — Backlog clos\n\n### B-0003 — Lien mort\n\n> statut : fait\n")
        f = memoire.analyser("memory/journal/2026-10.md", texte)
        b = [e for e in f.entrees if e.type == "B"][0]
        self.assertEqual(b.parent, "J-2026-10-12-A")
        self.assertTrue(b.archivee)

    def test_identifiants_valides_seulement(self):
        prive = "P" + "B-0002"  # construit : écrit en clair, ce fichier public fuirait
        texte = f"F-0001, J-2026-10-10-A, {prive}, ADR-0003 ; pas F-12 ni J-0001 ni XF-0001."
        self.assertEqual([i for i, _ in memoire.mentions(texte)], ["F-0001", "J-2026-10-10-A", prive, "ADR-0003"])

    def test_les_chemins_de_la_memoire(self):
        self.assertTrue(memoire.est_memoire("memory/canonical.md"))
        self.assertFalse(memoire.est_memoire("docs/memory/notes.md"))
        reponse = "memory/requests/D-0001-essai.answer.toml"
        self.assertTrue(memoire.est_reponse(reponse))
        self.assertFalse(memoire.est_reponse("memory/requests/D-0001-essai.md"))
        self.assertEqual(memoire.demande_de_reponse(reponse), "memory/requests/D-0001-essai.md")
        self.assertEqual(demandes.chemin_reponse("memory/requests/D-0001-essai.md"), reponse)
        self.assertEqual(memoire.hors_zone_privee("memory/private/backlog/PB-0001-x.md"), "backlog/PB-0001-x.md")
        self.assertEqual(memoire.hors_zone_privee("memory/backlog/B-0001-x.md"), "memory/backlog/B-0001-x.md")
        self.assertEqual(config.FORMAT_ACTUEL.dans_prive("memory/backlog"), "memory/private/backlog")
        self.assertEqual(config.FORMAT_ACTUEL.dans_prive("docs/a.md"), "docs/a.md")

    def test_couche_imposee_par_l_emplacement(self):
        self.assertEqual(memoire.couche_attendue("memory/journal/2026-10.md"), "journal")
        self.assertEqual(memoire.couche_attendue("memory/private/canonical.md"), "canonique")
        self.assertIsNone(memoire.couche_attendue("memory/archives/cadrage.md"))
        self.assertEqual(memoire.couche_attendue("memory/notes.md"), "inconnue")


class TestLectureProuvee(unittest.TestCase):
    def test_l_empreinte_suit_le_texte(self):
        a = memoire.analyser("memory/canonical.md", CANONIQUE).entrees[0]
        b = memoire.analyser("memory/canonical.md", CANONIQUE.replace("binaire de base", "binaire AVX2")).entrees[0]
        self.assertRegex(memoire.empreinte_entree(a), r"^[0-9a-f]{8}$")
        self.assertNotEqual(memoire.empreinte_entree(a), memoire.empreinte_entree(b))
        espaces = memoire.analyser("memory/canonical.md", CANONIQUE.replace("base.", "base.   ")).entrees[0]
        self.assertEqual(memoire.empreinte_entree(a), memoire.empreinte_entree(espaces))
        # La ligne de métadonnées n'y compte pas, mais compte dans celle du
        # texte entier, que portent les citations d'avant D-0086.
        statut = memoire.analyser("memory/canonical.md", CANONIQUE.replace("statut : mesuré", "statut : supposé")
                                  .replace(" · date : 2026-10-10", "")).entrees[0]
        self.assertNotEqual(a.meta, statut.meta)
        self.assertEqual(memoire.empreinte_entree(a), memoire.empreinte_entree(statut))
        self.assertNotEqual(memoire.empreinte_texte_entier(a), memoire.empreinte_texte_entier(statut))

    def test_citations(self):
        texte = "Voir ADR-0003@0a1b2c3d, F-0001 (sans empreinte) et lu : decisions@deadbeef.\n```\nF-0002@11111111\n```"
        self.assertEqual(memoire.citations(texte), [("ADR-0003", "0a1b2c3d", 1)])
        self.assertEqual(memoire.citations_index(texte), [("decisions", "deadbeef", 1)])


class TestReferences(unittest.TestCase):
    def test_types_de_reference(self):
        refs = memoire.references("commit:3f2a9c1, fichier:src/x.rs:12 ; J-2026-10-10-A et url:https://exemple.org")
        self.assertEqual(refs, [("commit", "3f2a9c1"), ("fichier", "src/x.rs:12"),
                                ("url", "https://exemple.org"), ("id", "J-2026-10-10-A")])

    def test_la_ponctuation_finale_n_est_pas_dans_la_reference(self):
        # B-0020 : un SHA suivi d'un point ou d'une parenthèse était refusé.
        refs = memoire.references("(commit:3f2a9c1). Voir fichier:docs/a_(b).md, puis fichier:src/x.rs:12.")
        self.assertEqual(refs, [("commit", "3f2a9c1"), ("fichier", "docs/a_(b).md"), ("fichier", "src/x.rs:12")])
        self.assertEqual(memoire.sans_ponctuation_finale("3f2a9c1)."), "3f2a9c1")

    def test_accent_grave_fermant_n_ouvre_pas_de_reference(self):
        self.assertEqual(memoire.references("les références `commit:` et aux identifiants `x`"), [])


class TestMotifs(unittest.TestCase):
    def test_etoile_ne_traverse_pas_les_repertoires(self):
        self.assertTrue(outils.correspond("src/a.rs", "src/*.rs"))
        self.assertFalse(outils.correspond("src/b/a.rs", "src/*.rs"))

    def test_double_etoile(self):
        self.assertTrue(outils.correspond("a.md", "**/*.md"))
        self.assertTrue(outils.correspond("x/y/a.md", "**/*.md"))
        self.assertTrue(outils.correspond("memoire/archives/x/y.md", "memoire/archives/**"))
        self.assertFalse(outils.correspond("memoire/actif.md", "memoire/archives/**"))

    def test_trailers(self):
        msg = "Sujet\n\nCorps.\n\nCo-Authored-By: Claude <x@y>\nSocle-Hooks: SessionStart=1 PreToolUse=3"
        self.assertEqual(outils.trailers(msg)["socle-hooks"], ["SessionStart=1 PreToolUse=3"])
        self.assertEqual(outils.trailers("Sujet seul"), {})


if __name__ == "__main__":
    unittest.main()


class TestFichierJournal(unittest.TestCase):
    """ADR-0022 : un mois dont le fichier atteindrait son budget continue dans
    le suivant, au lieu de bloquer tout commit qui ajoute au journal."""

    def test_le_mois_continue_dans_un_second_fichier(self):
        import tempfile

        dossier = Path(tempfile.mkdtemp(prefix="socle-journal-"))
        self.addCleanup(__import__("shutil").rmtree, dossier, ignore_errors=True)
        self.assertEqual(memoire.fichier_journal(dossier, "2026-10", 100, 20).name, "2026-10.md")
        (dossier / "2026-10.md").write_text("x" * 90)
        self.assertEqual(memoire.fichier_journal(dossier, "2026-10", None, 20).name, "2026-10.md")
        self.assertEqual(memoire.fichier_journal(dossier, "2026-10", 100, 5).name, "2026-10.md")
        self.assertEqual(memoire.fichier_journal(dossier, "2026-10", 100, 20).name, "2026-10-2.md")
        (dossier / "2026-10-2.md").write_text("y")
        # Le mois a continué : on n'écrit plus dans le premier, même s'il a de la place.
        self.assertEqual(memoire.fichier_journal(dossier, "2026-10", 100, 5).name, "2026-10-2.md")

    def test_le_budget_d_un_fichier_vient_des_garde_fous(self):
        from socle import config

        p = config.Projet(racine=Path("."))
        p.garde_fous = {"budgets": {"memory/journal/*.md": {"max_bytes": 100}}}
        self.assertEqual(p.budget_octets("memory/journal/2026-10.md"), 100)
        self.assertIsNone(p.budget_octets("memory/active.md"))
