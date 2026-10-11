import re
import unittest
from pathlib import Path

from socle import config, demandes

MODELE = (Path(__file__).resolve().parent.parent / "moteur/socle/modeles/demande.md").read_text(encoding="utf-8")

CONFORME = """<!-- socle: couche=demandes zone=publique -->
# D-0004 — Faut-il relever le plafond de mutants de search.rs de 3 à 5 ?

> date : 2026-10-10

## Décision demandée

Relever le plafond de mutants survivants de search.rs de 3 à 5.

## Contexte

Le balayage hebdomadaire signale deux survivants nouveaux depuis le commit cité.
Un survivant est une modification du code que tous les tests acceptent : ici,
deux changements de la marge d'élagage de la recherche, qui ne modifient aucun
coup sur les positions des tests mais pourraient changer la force de jeu. Le
plafond actuel de trois survivants pour ce fichier a été mesuré le mois dernier
et il casse désormais, ce qui bloque la CI hebdomadaire jusqu'à décision.

## Où regarder

- Le journal du balayage : [le verdict](https://exemple.org/verdict), section « survivants de search.rs ».

## Éléments cités

- 3f2a9c1 — le commit qui a introduit la marge d'élagage où vivent les deux mutants.
- B-0012 — le sujet du backlog qui demande de mesurer cette marge par un match.

## Options

Relever : effort nul, risque de masquer un vrai trou, réversible. Écrire deux tests : effort d'une heure, risque nul, réversible.

## Conséquences

Si tu valides, le plafond passe à 5. Si tu refuses, j'écris les tests. Sans réponse, le cliquet reste rouge et je travaille sur autre chose.

## Recommandation

Refuser. Vérifié : les deux mutants changent un seuil d'élagage. Supposé : qu'aucun test unitaire ne les tue sans match.

## Réponses possibles

- `valider` — le plafond passe à 5.
- `refuser` — j'écris les tests.
- `contexte-insuffisant` — je réécris la demande.
"""


def _demande(texte):
    return demandes.Demande(chemin="memory/requests/D-0004-plafond.md", texte=texte,
                            entree=demandes.memoire.analyser("x.md", texte).entrees[0],
                            sections=demandes.decouper_sections(texte))


class TestContrat(unittest.TestCase):
    def setUp(self):
        self.projet = config.Projet(racine=Path("."))

    def test_une_demande_conforme_passe(self):
        self.assertEqual(demandes.linter(_demande(CONFORME), self.projet), [])

    def test_identifiant_nu_refuse(self):
        texte = CONFORME.replace("Le balayage hebdomadaire signale", "Comme évoqué en B-0007, le balayage signale")
        fautes = demandes.linter(_demande(texte), self.projet)
        self.assertEqual(len(fautes), 1)
        self.assertIn("B-0007", fautes[0])

    def test_description_trop_courte_refusee(self):
        texte = CONFORME.replace("- B-0012 — le sujet du backlog qui demande de mesurer cette marge par un match.", "- B-0012 — voir backlog")
        self.assertTrue(any("B-0012" in f for f in demandes.linter(_demande(texte), self.projet)))

    def test_motif_du_projet(self):
        texte = CONFORME.replace("Relever le plafond", "Relever, comme pour A13, le plafond")
        self.assertEqual(demandes.linter(_demande(texte), self.projet), [])
        self.projet.garde_fous = {"requests": {"internal_id_patterns": [r"\b[A-Z]\d{1,3}\b"]}}
        self.assertTrue(any("A13" in f for f in demandes.linter(_demande(texte), self.projet)))

    def test_sans_lien_ou_regarder_refuse(self):
        texte = CONFORME.replace("[le verdict](https://exemple.org/verdict)", "le verdict")
        self.assertTrue(any("Où regarder" in f for f in demandes.linter(_demande(texte), self.projet)))

    def test_contexte_d_une_ligne_refuse(self):
        texte = re.sub(r"## Contexte\n\n.*?\n\n## ", "## Contexte\n\nDeux survivants nouveaux.\n\n## ",
                       CONFORME, flags=re.S)
        self.assertTrue(any("Contexte » trop court" in f for f in demandes.linter(_demande(texte), self.projet)))

    def test_champs_manquants(self):
        texte = CONFORME.split("## Conséquences")[0]
        fautes = demandes.linter(_demande(texte), self.projet)
        self.assertTrue(any("Conséquences" in f for f in fautes))
        self.assertTrue(any("Réponses possibles" in f for f in fautes))

    def test_le_gabarit_brut_ne_passe_pas(self):
        texte = MODELE.format(id="D-0004", titre="Choisir le format des fichiers de politique", date="2026-10-10")
        fautes = demandes.linter(_demande(texte), self.projet)
        self.assertTrue(any("gabarit laissé tel quel" in f for f in fautes), fautes)


class TestReponse(unittest.TestCase):
    def test_reponse_gelee(self):
        d = _demande(CONFORME)
        d.reponse = {"reponse": "refuser", "empreinte": "sha256:" + demandes.outils.sha256(CONFORME)}
        self.assertEqual(demandes.verifier_reponse(d), [])
        d.texte = CONFORME + "\nAjout après coup.\n"
        self.assertTrue(any("gelée" in f for f in demandes.verifier_reponse(d)))

    def test_reponse_hors_liste(self):
        d = _demande(CONFORME)
        d.reponse = {"reponse": "peut-etre", "empreinte": "sha256:" + demandes.outils.sha256(CONFORME)}
        self.assertTrue(any("absente des réponses possibles" in f for f in demandes.verifier_reponse(d)))


if __name__ == "__main__":
    unittest.main()
