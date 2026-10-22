import re
import unittest
from pathlib import Path

from socle import config, requests as demandes

MODELE = (Path(__file__).resolve().parent.parent / "engine/socle/templates/request.md").read_text(encoding="utf-8")

CONFORME = """<!-- socle: couche=demandes zone=publique -->
# D-0004 — Faut-il relever le plafond de mutants de parser.rs de 3 à 5 ?

> date : 2026-10-10

## Décision demandée

Relever le plafond de mutants survivants de parser.rs de 3 à 5.

## Contexte

Le balayage hebdomadaire signale deux survivants nouveaux depuis le commit cité.
Un survivant est une modification du code que tous les tests acceptent : ici,
deux changements du seuil de tolérance de l'analyseur, qui ne modifient aucun
résultat sur les fichiers des tests mais pourraient changer ses performances. Le
plafond actuel de trois survivants pour ce fichier a été mesuré le mois dernier
et il casse désormais, ce qui bloque la CI hebdomadaire jusqu'à décision.

## Où regarder

- Le journal du balayage : [le verdict](https://exemple.org/verdict), section « survivants de parser.rs ».

## Éléments cités

- 3f2a9c1 — le commit qui a introduit le seuil de tolérance où vivent les deux mutants.
- B-0012 — le sujet du backlog qui demande de mesurer ce seuil par un banc.

## Options

Relever : effort nul, risque de masquer un vrai trou, réversible. Écrire deux tests : effort d'une heure, risque nul, réversible.

## Conséquences

Si tu valides, le plafond passe à 5. Si tu refuses, j'écris les tests. Sans réponse, le cliquet reste rouge et je travaille sur autre chose.

## Recommandation

Refuser. Vérifié : les deux mutants changent un seuil de tolérance. Supposé : qu'aucun test unitaire ne les tue sans banc.

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
        texte = CONFORME.replace("- B-0012 — le sujet du backlog qui demande de mesurer ce seuil par un banc.", "- B-0012 — voir backlog")
        self.assertTrue(any("B-0012" in f for f in demandes.linter(_demande(texte), self.projet)))

    def test_motif_du_projet(self):
        texte = CONFORME.replace("Relever le plafond", "Relever, comme pour A13, le plafond")
        self.assertEqual(demandes.linter(_demande(texte), self.projet), [])
        self.projet.garde_fous = {"requests": {"internal_id_patterns": [r"\b[A-Z]\d{1,3}\b"]}}
        self.assertTrue(any("A13" in f for f in demandes.linter(_demande(texte), self.projet)))

    def test_sans_lien_ou_regarder_refuse(self):
        texte = CONFORME.replace("[le verdict](https://exemple.org/verdict)", "le verdict")
        self.assertTrue(any("Où regarder" in f for f in demandes.linter(_demande(texte), self.projet)))

    def test_sans_lien_le_refus_dit_comment_en_mettre_un(self):
        # B-0027 : sans adresse de dépôt, `socle url` échoue et l'agent
        # écrivait des chemins nus ; le refus dit qu'un lien relatif suffit.
        texte = CONFORME.replace("[le verdict](https://exemple.org/verdict)", "le verdict")
        faute = next(f for f in demandes.linter(_demande(texte), self.projet) if "Où regarder" in f)
        self.assertIn("un lien relatif depuis la demande", faute)

    def test_contexte_d_une_ligne_refuse(self):
        texte = re.sub(r"## Contexte\n\n.*?\n\n## ", "## Contexte\n\nDeux survivants nouveaux.\n\n## ",
                       CONFORME, flags=re.S)
        self.assertTrue(any("Contexte » trop court" in f for f in demandes.linter(_demande(texte), self.projet)))

    def test_champs_manquants(self):
        texte = CONFORME.split("## Conséquences")[0]
        fautes = demandes.linter(_demande(texte), self.projet)
        self.assertTrue(any("Conséquences" in f for f in fautes))
        self.assertTrue(any("Réponses possibles" in f for f in fautes))

    def test_une_comparaison_ou_du_code_cite_ne_sont_pas_des_trous(self):
        # Relevé de la passe de recul, E : « < 5 » ou un extrait de code
        # étaient pris pour un trou du gabarit.
        texte = CONFORME.replace("Supposé : qu'aucun test",
                                 "Si le compte reste < 5 et > 2, ou a <= b, `git log <a b>` le montre. Supposé : qu'aucun test")
        fautes = demandes.linter(_demande(texte), self.projet)
        self.assertFalse(any("gabarit laissé" in f for f in fautes), fautes)

    def test_le_gabarit_brut_ne_passe_pas(self):
        texte = MODELE.format(id="D-0004", titre="Choisir le format des fichiers de politique", date="2026-10-10")
        fautes = demandes.linter(_demande(texte), self.projet)
        self.assertTrue(any("gabarit laissé tel quel" in f for f in fautes), fautes)


class TestUneDemandeQuiAutorise(unittest.TestCase):
    """D-0040 (B-0081) : une demande aux réponses `tout`, `compatibilite-seule`
    et `refuser` nommait les tests à supprimer ; la réponse `tout` n'en
    autorisait aucun, et rien ne l'avait dit à la rédaction."""

    def setUp(self):
        import shutil
        import tempfile
        import tomllib

        self.racine = Path(tempfile.mkdtemp(prefix="socle-demande-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        (self.racine / "tests").mkdir()
        (self.racine / "tests/test_parser.py").write_text(
            "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_tolerance(self):\n"
            "        self.assertEqual(2 * 2, 4)\n")
        adaptateur = tomllib.loads((Path(demandes.__file__).parent / "adapters/python.toml").read_text())
        self.projet = config.Projet(racine=self.racine, adaptateur=adaptateur,
                                    garde_fous={"mutation": {"caps": {"parser.rs": {"max": 3}}}})

    def _sans_valider(self, texte):
        return texte.replace("- `valider` — le plafond passe à 5.", "- `relever` — le plafond passe à 5.")

    def test_qui_nomme_un_test_sans_proposer_valider_est_refusee(self):
        texte = self._sans_valider(CONFORME.replace("pourraient changer ses performances.",
                                                    "pourraient changer ses performances (`test_tolerance`)."))
        self.assertEqual(demandes.gestes_nommes(_demande(texte), self.projet), ["test_tolerance"])
        fautes = demandes.linter(_demande(texte), self.projet)
        self.assertEqual(len(fautes), 1)
        self.assertIn("`test_tolerance`", fautes[0])
        self.assertIn("ne propose pas `valider`", fautes[0])

    def test_qui_nomme_une_cle_des_seuils_sans_proposer_valider_est_refusee(self):
        texte = self._sans_valider(CONFORME.replace("de 3 à 5.\n\n## Contexte",
                                                    'de 3 à 5 (`mutation.caps."parser.rs".max`).\n\n## Contexte'))
        fautes = demandes.linter(_demande(texte), self.projet)
        self.assertEqual(len(fautes), 1)
        self.assertIn('`mutation.caps."parser.rs".max`', fautes[0])

    def test_qui_propose_valider_ou_ne_nomme_rien_passe(self):
        nomme = CONFORME.replace("pourraient changer ses performances.",
                                 "pourraient changer ses performances (`test_tolerance`).")
        self.assertEqual(demandes.linter(_demande(nomme), self.projet), [])
        self.assertEqual(demandes.linter(_demande(self._sans_valider(CONFORME)), self.projet), [])
        # Un mot qui contient le nom d'un test sans l'être ne compte pas.
        voisin = self._sans_valider(CONFORME.replace("pourraient changer ses performances.",
                                                     "pourraient changer ses performances (`test_tolerance_2`)."))
        self.assertEqual(demandes.linter(_demande(voisin), self.projet), [])


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
