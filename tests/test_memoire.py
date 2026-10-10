import unittest

from socle import memoire, outils

CANONIQUE = """<!-- socle: couche=canonique zone=publique -->
# Mémoire canonique

## F-0001 — Le bench explore 70 452 nœuds

> statut : mesuré · preuve : cmd:`cargo run -- bench 7, profondeur 7` · date : 2026-10-10

Mesuré sur le binaire de base.

## F-0002 — ~~Le copy-make coûte 20 %~~

> statut : Réfuté
> Réfutation : F-0001

Corps conservé.

```markdown
## F-0099 — un exemple dans un bloc de code
```
"""


class TestAnalyse(unittest.TestCase):
    def test_entete_et_entrees(self):
        f = memoire.analyser("memoire/canonique.md", CANONIQUE)
        self.assertEqual((f.couche, f.zone), ("canonique", "publique"))
        self.assertEqual([e.id for e in f.entrees], ["F-0001", "F-0002"])

    def test_metadonnees_et_commande_avec_virgule(self):
        e = memoire.analyser("memoire/canonique.md", CANONIQUE).entrees[0]
        self.assertEqual(e.statut, "mesure")
        self.assertEqual(e.refs("preuve"), [("cmd", "cargo run -- bench 7, profondeur 7")])

    def test_fait_barre_et_meta_sur_deux_lignes(self):
        e = memoire.analyser("memoire/canonique.md", CANONIQUE).entrees[1]
        self.assertTrue(e.barre)
        self.assertEqual(e.titre, "Le copy-make coûte 20 %")
        self.assertEqual(e.statut, "refute")
        self.assertEqual(e.refs("refutation"), [("id", "F-0001")])

    def test_rien_n_est_lu_dans_un_bloc_de_code(self):
        self.assertNotIn("F-0099", [i for i, _ in memoire.mentions(CANONIQUE)])

    def test_archive_imbriquee_dans_le_journal(self):
        texte = ("<!-- socle: couche=journal zone=publique -->\n# Journal\n\n"
                 "## J-2026-10-12-A — Backlog clos\n\n### B-0003 — Lien mort\n\n> statut : fait\n")
        f = memoire.analyser("memoire/journal/2026-10.md", texte)
        b = [e for e in f.entrees if e.type == "B"][0]
        self.assertEqual(b.parent, "J-2026-10-12-A")
        self.assertTrue(b.archivee)

    def test_identifiants_valides_seulement(self):
        prive = "P" + "B-0002"  # construit : écrit en clair, ce fichier public fuirait
        texte = f"F-0001, J-2026-10-10-A, {prive}, ADR-0003 ; pas F-12 ni J-0001 ni XF-0001."
        self.assertEqual([i for i, _ in memoire.mentions(texte)], ["F-0001", "J-2026-10-10-A", prive, "ADR-0003"])

    def test_couche_imposee_par_l_emplacement(self):
        self.assertEqual(memoire.couche_attendue("memoire/journal/2026-10.md"), "journal")
        self.assertEqual(memoire.couche_attendue("memoire/prive/canonique.md"), "canonique")
        self.assertIsNone(memoire.couche_attendue("memoire/archives/cadrage.md"))
        self.assertEqual(memoire.couche_attendue("memoire/notes.md"), "inconnue")


class TestReferences(unittest.TestCase):
    def test_types_de_reference(self):
        refs = memoire.references("commit:3f2a9c1, fichier:src/x.rs:12 ; J-2026-10-10-A et url:https://exemple.org")
        self.assertEqual(refs, [("commit", "3f2a9c1"), ("fichier", "src/x.rs:12"),
                                ("url", "https://exemple.org"), ("id", "J-2026-10-10-A")])

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
