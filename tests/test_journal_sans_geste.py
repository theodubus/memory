"""B-0349 (D-0179) : une entrée du journal ne note aucun geste futur pour
l'humain, l'état seul calculant ce qui lui revient ; le format de la
mémoire et la section du socle d'AGENTS.md le disent, en français et en
anglais."""

import unittest
from pathlib import Path

MOTEUR = Path(__file__).resolve().parent.parent / "engine" / "socle"


def lire(rel: str) -> str:
    return " ".join((MOTEUR / rel).read_text(encoding="utf-8").split())


class TestLeJournalNeNoteAucunGesteFutur(unittest.TestCase):
    def test_le_format_le_dit_dans_la_section_du_journal(self):
        texte = (MOTEUR / "FORMAT.md").read_text(encoding="utf-8")
        section = texte.split("### Journal — `J-`", 1)[1].split("\n### ", 1)[0]
        section = " ".join(section.split())
        self.assertIn("elle ne note aucun geste futur pour l'humain", section)
        self.assertIn("l'état seul le calcule", section)

    def test_la_section_du_socle_d_agents_le_dit_en_francais_et_en_anglais(self):
        for rel, ligne in (("templates/AGENTS.md", "| Journal | `memory/journal/` | une entrée datée par événement ; "
                                                   "ajout seul ; aucun geste futur de l'humain |"),
                           ("templates/AGENTS.en.md", "| Journal | `memory/journal/` | one dated entry per event; "
                                                      "append only; no future step for the human |")):
            with self.subTest(gabarit=rel):
                self.assertIn(ligne, lire(rel))


if __name__ == "__main__":
    unittest.main()
