"""Le banc du jalon 9 : ses juges laissent passer un agent qui fait bien et
arrêtent un agent fautif, et une limite d'usage n'est jamais un échec — le
passage est rejoué après la remise à zéro, sur un projet neuf."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

RACINE = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("banc", RACINE / "banc/banc.py")
banc = sys.modules["banc"] = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(banc)


class Dossier(unittest.TestCase):
    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-test-banc-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)


class TestJuges(Dossier):
    """Chaque scénario, joué par l'agent simulé : bon, il passe ; fautif, il
    échoue. Un juge qui ne voit pas la faute ne prouve rien."""

    def jouer(self, scenario, passage, bon):
        return banc.jouer(scenario, passage, self.dossier / f"{scenario.id}-{passage}-{bon}", "simule", 0, bon=bon)

    def test_chaque_scenario_departage_le_bon_agent_du_fautif(self):
        for s in banc.SCENARIOS:
            with self.subTest(scenario=s.id):
                bon = self.jouer(s, 1, True)
                self.assertEqual(bon["statut"], "passe", bon.get("raisons"))
                fautif = self.jouer(s, 1, False)
                self.assertEqual(fautif["statut"], "echec")
                self.assertTrue(fautif["raisons"])

    def test_le_scenario_6_change_d_entree_a_chaque_passage(self):
        s6 = next(s for s in banc.SCENARIOS if s.id == "s6")
        for passage in (2, 3):
            with self.subTest(passage=passage):
                self.assertEqual(self.jouer(s6, passage, True)["statut"], "passe")
        projet = self.dossier / "s6-3-True/s6-p3"
        self.assertTrue((projet / "memoire/archives/cadrage-calc.md").is_file())
        # L'audit du dépôt : des faits mesurés, chacun avec son fichier.
        self.assertIn("statut : mesuré · preuve : fichier:README.md", (projet / "memoire/canonique.md").read_text())

    def test_les_mesures_sont_relevees(self):
        r = self.jouer(banc.SCENARIOS[0], 1, True)
        m = r["mesures"]
        self.assertTrue(m["verify"]["ok"])
        self.assertGreater(m["etat_octets"], 500)
        self.assertEqual(m["refus"], [])


class TestLimites(unittest.TestCase):
    MAINTENANT = datetime(2026, 10, 11, 10, 0, tzinfo=timezone.utc)

    def test_heure_de_reprise_en_horodatage(self):
        self.assertEqual(banc.heure_de_reprise("Claude AI usage limit reached|1760000000"), 1760000000)

    def test_heure_de_reprise_en_heure_du_jour(self):
        r = banc.heure_de_reprise("5-hour limit reached ∙ resets 3pm", self.MAINTENANT)
        self.assertEqual(r, int(datetime(2026, 10, 11, 15, 0, tzinfo=timezone.utc).timestamp()))
        r = banc.heure_de_reprise("You've hit your limit · resets 9:30am", self.MAINTENANT)
        self.assertEqual(r, int(datetime(2026, 10, 12, 9, 30, tzinfo=timezone.utc).timestamp()))

    def test_heure_de_reprise_dans_un_fuseau(self):
        r = banc.heure_de_reprise("limit reached · resets 15:00 (Europe/Paris)", self.MAINTENANT)
        self.assertEqual(r, int(datetime(2026, 10, 11, 13, 0, tzinfo=timezone.utc).timestamp()))

    def test_sans_heure_lisible(self):
        self.assertIsNone(banc.heure_de_reprise("usage limit reached", self.MAINTENANT))

    def test_une_session_reussie_n_est_jamais_une_limite(self):
        self.assertIsNone(banc.limite_atteinte(0, {"result": "le rate limiter est documenté"}, ""))

    def test_limite_et_surcharge(self):
        lim = banc.limite_atteinte(1, {"is_error": True, "result": "Claude AI usage limit reached|1760000000"}, "")
        self.assertEqual((lim["genre"], lim["reprise"]), ("limite", 1760000000))
        sur = banc.limite_atteinte(1, {}, "API Error: 529 Overloaded")
        self.assertEqual(sur["genre"], "surcharge")
        self.assertIsNone(banc.limite_atteinte(1, {"is_error": True, "result": "erreur de syntaxe"}, ""))

    def test_attente(self):
        self.assertEqual(banc.attente({"genre": "limite", "reprise": 10_000}, 4_000), 6_000 + banc.MARGE)
        self.assertEqual(banc.attente({"genre": "limite", "reprise": None}, 0), banc.PAUSE_LIMITE)
        self.assertEqual(banc.attente({"genre": "surcharge", "reprise": None}, 0), banc.PAUSE_SURCHARGE)


class TestReprise(Dossier):
    """Une session qui bute sur une limite : le banc attend, puis rejoue le
    passage sur un projet neuf ; ou il s'arrête, et `--reprendre` le rejoue."""

    def setUp(self):
        super().setUp()
        self.appels = 0

    def session(self, limites: int):
        def lancer(projet, consigne, budget):
            self.appels += 1
            if self.appels <= limites:
                return {"code": 1, "duree": 1, "reponse": "", "cout": 0, "tours": 1, "usage": None,
                        "sous_type": "success", "erreur": True, "stderr": "",
                        "limite": {"genre": "limite", "reprise": None, "extrait": "usage limit"}}
            subprocess.run([sys.executable, str(projet / ".socle/socle"), "hook", "session-start"], cwd=projet,
                           input=json.dumps({"session_id": "essai", "source": "startup"}), capture_output=True,
                           text=True, env=banc.env_neuf())
            return {"code": 0, "duree": 1, "reponse": banc.s1_simuler(projet, True, 1), "cout": 0.1, "tours": 3,
                    "usage": None, "sous_type": "success", "erreur": False, "limite": None, "stderr": ""}
        return lancer

    def lancer(self, *options):
        sortie = self.dossier / "resultats"
        with mock.patch.object(banc, "lancer_claude", self.session(1)), \
                mock.patch.object(banc.time, "sleep") as dormir, mock.patch("builtins.print"):
            code = banc.main(["--agent", "claude", "--scenarios", "s1", "--reprendre", str(sortie), *options])
        return code, json.loads((sortie / "resultats.json").read_text()), dormir

    def test_attendre_puis_rejouer(self):
        code, res, dormir = self.lancer("--attendre", "8")
        self.assertEqual(code, 0)
        self.assertEqual(res["passages"]["s1-p1"]["statut"], "passe")
        self.assertEqual(len(res["interruptions"]), 1)
        dormir.assert_called_once_with(banc.PAUSE_LIMITE)
        self.assertEqual(self.appels, 2)

    def test_s_arreter_puis_reprendre(self):
        code, res, dormir = self.lancer()
        self.assertEqual(code, 3)
        self.assertEqual(res["passages"]["s1-p1"]["statut"], "interrompu")
        dormir.assert_not_called()
        code, res, _ = self.lancer()
        self.assertEqual(code, 0)
        self.assertEqual(res["passages"]["s1-p1"]["statut"], "passe")
        self.assertIn("Interruptions", (self.dossier / "resultats/rapport.md").read_text())


if __name__ == "__main__":
    unittest.main()
