"""B-0350 (D-0181) : le skill des lots fait attendre la CI du commit poussé,
par son SHA, et non la ligne « CI » de l'état, qui suit la tête locale
qu'un commit fait pendant l'attente déplace."""

import unittest
from pathlib import Path

MOTEUR = Path(__file__).resolve().parent.parent / "engine" / "socle"


def etape_3(rel: str, section: str) -> str:
    """L'étape 3 de la section de la livraison du gabarit, sur une ligne."""
    texte = (MOTEUR / rel).read_text(encoding="utf-8")
    texte = texte[texte.index(section):]
    debut = texte.index("\n3. ")
    fin = texte.index("\n4. ", debut)
    return " ".join(texte[debut:fin].split())


class TestLAttenteDeLaCi(unittest.TestCase):
    def test_le_skill_des_lots_attend_la_ci_du_commit_pousse_par_son_sha(self):
        # T-0206 (D-0218) : la règle reste dans le skill, sa raison passe au
        # guide, « Pourquoi ces règles ».
        for rel, section, mots, anciens, guide, raison in (
                ("templates/skills/socle-batch/SKILL.md", "## Intégrer, pousser, livrer",
                 ("Attendre la CI du commit poussé (`gh run list --commit <sha>`).",),
                 ("Attendre `success` sur le SHA court du commit de tête",), "HELP.md",
                 "L'agent attend la CI du commit poussé (`gh run list --commit <sha>`) : la ligne « CI » de l'état "
                 "suit la tête."),
                ("templates/skills/socle-batch/SKILL.en.md", "## Integrating, pushing, delivering",
                 ("Wait for the CI of the pushed commit (`gh run list --commit <sha>`).",),
                 ("Wait for the CI of the head commit",), "HELP.en.md",
                 "The agent waits for the CI of the pushed commit (`gh run list --commit <sha>`): the \"CI\" line of "
                 "the state follows the head.")):
            texte = etape_3(rel, section)
            with self.subTest(gabarit=rel):
                for mot in mots:
                    self.assertIn(mot, texte)
                for mot in anciens:
                    self.assertNotIn(mot, texte)
                self.assertIn(raison, " ".join((MOTEUR / guide).read_text(encoding="utf-8").split()))


if __name__ == "__main__":
    unittest.main()
