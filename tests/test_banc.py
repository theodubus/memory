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
                if s.faute:
                    # La faute livrée par l'agent fautif est arrêtée par la CI ;
                    # le bon agent ne la tente pas.
                    self.assertEqual(bon["systeme"]["verdict"], "non tentée")
                    self.assertEqual(fautif["systeme"]["verdict"], "arrêtée par la CI", fautif["systeme"])

    def test_les_suites_couvrent_chaque_scenario_une_fois(self):
        ids = ",".join(banc.SUITES.values()).split(",")
        self.assertEqual(sorted(ids), sorted(s.id for s in banc.SCENARIOS))

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


class TestCompactageRealiste(Dossier):
    """s14 : un long compte rendu où trois consignes sont noyées, et la mesure
    de ce que l'agent en a écrit dans la mémoire."""

    def test_le_compte_rendu_noie_les_trois_consignes(self):
        texte = banc.compte_rendu(1, cible=40_000)
        places = [texte.find(c) for c in banc.CONSIGNES_S14.values()]
        self.assertTrue(all(p > 0 for p in places))
        self.assertEqual(places, sorted(places))
        self.assertGreater(len(texte), 40_000)
        self.assertEqual(texte, banc.compte_rendu(1, cible=40_000))

    def test_les_consignes_ecrites_ne_comptent_que_ce_que_l_agent_ajoute(self):
        s14 = next(s for s in banc.SCENARIOS if s.id == "s14")
        bon = banc.jouer(s14, 1, self.dossier / "bon", "simule", 0, bon=True)
        fautif = banc.jouer(s14, 1, self.dossier / "fautif", "simule", 0, bon=False)
        self.assertEqual(banc.consignes_ecrites(Path(bon["projet"])), ["negatifs", "commits", "double"])
        self.assertEqual(banc.consignes_ecrites(Path(fautif["projet"])), [])


class TestSysteme(Dossier):
    """Le verdict du dispositif, à part de celui de l'agent."""

    def setUp(self):
        super().setUp()
        self.projet = banc.jouer(banc.SCENARIOS[0], 1, self.dossier / "s1", "simule", 0)["projet"]

    def scenario(self, faute):
        return banc.Scenario("sx", "essai", None, None, None, None, faute=lambda p: faute, signes=r"tests\.creux")

    def test_une_faute_que_rien_n_arrete_passe_a_travers(self):
        v = banc.systeme(self.scenario("une faute que les contrôles ne voient pas"), Path(self.projet), [])
        self.assertEqual(v["verdict"], "passée à travers")

    def test_une_faute_corrigee_apres_un_refus_est_attrapee(self):
        v = banc.systeme(self.scenario(None), Path(self.projet), ["Stop:tests.creux", "PreToolUse:Bash — autre"])
        self.assertEqual((v["verdict"], v["etages"]), ("attrapée", ["Stop"]))

    def test_garder_ce_qu_il_faut_pour_relire_un_passage(self):
        garde = self.dossier / "garde"
        banc.garder(Path(self.projet), garde)
        self.assertIn("--- git status ---", (garde / "commits.txt").read_text())
        self.assertTrue((garde / "trace.tsv").is_file())


class TestSession(Dossier):
    """La session lancée : sa transcription entière gardée, son résultat lu
    dans le dernier événement."""

    def test_lancer_claude_lit_le_resultat_et_garde_la_transcription(self):
        flux = "\n".join(json.dumps(e) for e in (
            {"type": "system", "subtype": "init"},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "…"}]}},
            {"type": "result", "subtype": "success", "result": "Fait.\nPour toi : rien.", "total_cost_usd": 0.2,
             "num_turns": 4, "is_error": False, "usage": {"output_tokens": 9}}))
        fini = subprocess.CompletedProcess([], 0, stdout=flux + "\n", stderr="")
        with mock.patch.object(banc.subprocess, "run", return_value=fini) as lance:
            s = banc.lancer_claude(self.dossier, "consigne", 2.0, self.dossier / "garde")
        self.assertIn("stream-json", lance.call_args.args[0])
        self.assertEqual((s["cout"], s["tours"], s["limite"]), (0.2, 4, None))
        self.assertTrue(s["reponse"].startswith("Fait."))
        self.assertEqual((self.dossier / "garde/session.jsonl").read_text(), flux + "\n")


class TestVerifications(unittest.TestCase):
    def test_une_verification_lancee_par_l_agent_est_un_etage(self):
        resultat = {"type": "user", "message": {"content": [{"type": "tool_result", "content": [
            {"type": "text", "text": "  tests.creux    ECHEC\n\nECHEC — 1 contrôle(s) : tests.creux\nrc=1"}]}]}}
        autre = {"type": "user", "message": {"content": [{"type": "tool_result", "content": "TOUT PASSE"}]}}
        flux = "\n".join(json.dumps(e) for e in (resultat, autre)) + "\nligne illisible"
        self.assertEqual(banc.verifications(flux), ["verify:tests.creux"])


class TestSessionEnPlusieursTemps(Dossier):
    """Une session jouée en plusieurs temps, reprise à chaque fois, avec un
    compactage au milieu : le cas s12."""

    def test_les_temps_se_suivent_dans_la_meme_session(self):
        def temps(cout, compacte=False):
            evenements = ([{"type": "system", "subtype": "compact_boundary"}] if compacte else []) + [
                {"type": "result", "subtype": "success", "result": f"temps à {cout}", "total_cost_usd": cout,
                 "num_turns": 2, "is_error": False, "usage": {}}]
            return subprocess.CompletedProcess([], 0, stdout="\n".join(json.dumps(e) for e in evenements), stderr="")

        with mock.patch.object(banc.subprocess, "run", side_effect=[temps(0.5), temps(0.1, True), temps(0.4)]) as lance:
            s = banc.lancer_claude(self.dossier, ["commence", banc.COMPACTER, "continue"], 2.0)
        appels = [c.args[0] for c in lance.call_args_list]
        ident = appels[0][appels[0].index("--session-id") + 1]
        self.assertEqual([a[a.index("--resume") + 1] for a in appels[1:]], [ident, ident])
        self.assertTrue(all("--no-session-persistence" not in a for a in appels))
        self.assertEqual((s["cout"], s["tours"], s["phases"], s["compactages"]), (1.0, 6, 3, 1))
        self.assertEqual(s["reponse"], "temps à 0.4")

    def test_le_compactage_force_saute_quand_la_session_s_est_compactee_seule(self):
        auto = subprocess.CompletedProcess([], 0, stdout="\n".join(json.dumps(e) for e in (
            {"type": "system", "subtype": "compact_boundary", "compact_metadata": {"trigger": "auto"}},
            {"type": "result", "result": "un", "total_cost_usd": 1.0, "num_turns": 9})), stderr="")
        fini = subprocess.CompletedProcess([], 0, stdout=json.dumps({"type": "result", "result": "deux"}), stderr="")
        with mock.patch.object(banc.subprocess, "run", side_effect=[auto, fini]) as lance:
            s = banc.lancer_claude(self.dossier, ["long", banc.COMPACTER_SI_BESOIN, "suite"], 3.0)
        self.assertEqual(lance.call_count, 2)
        self.assertNotIn(banc.COMPACTER, lance.call_args_list[1].args[0])
        self.assertEqual((s["compactages"], s["compactages_auto"]), (1, 1))

    def test_une_consigne_longue_passe_par_l_entree_standard_avec_une_fenetre_reduite(self):
        longue = "réunion " * 20_000
        fini = subprocess.CompletedProcess([], 0, stdout=json.dumps({"type": "result", "result": "ok"}), stderr="")
        with mock.patch.object(banc.subprocess, "run", return_value=fini) as lance:
            banc.lancer_claude(self.dossier, [longue, "suite"], 3.0, autocompact="100k")
        premier, second = lance.call_args_list
        self.assertNotIn(longue, premier.args[0])
        self.assertEqual(premier.kwargs["input"], longue)
        self.assertIn("suite", second.args[0])
        self.assertIsNone(second.kwargs["input"])
        self.assertEqual(premier.args[0][premier.args[0].index("--autocompact") + 1], "100k")
        self.assertEqual(premier.kwargs["env"]["CLAUDE_AUTOCOMPACT_PCT_OVERRIDE"], "80")

    def test_une_limite_au_milieu_interrompt_la_session(self):
        limite = subprocess.CompletedProcess([], 1, stdout=json.dumps(
            {"type": "result", "is_error": True, "result": "Claude AI usage limit reached|1760000000"}), stderr="")
        fini = subprocess.CompletedProcess([], 0, stdout=json.dumps({"type": "result", "result": "ok"}), stderr="")
        with mock.patch.object(banc.subprocess, "run", side_effect=[fini, limite]) as lance:
            s = banc.lancer_claude(self.dossier, ["commence", banc.COMPACTER, "continue"], 2.0)
        self.assertEqual(lance.call_count, 2)
        self.assertEqual(s["limite"]["reprise"], 1760000000)


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
        def lancer(projet, consigne, budget, garde=None, autocompact=None):
            self.appels += 1
            if self.appels <= limites:
                return {"code": 1, "duree": 1, "reponse": "", "cout": 0, "tours": 1, "usage": None,
                        "sous_type": "success", "erreur": True, "stderr": "",
                        "limite": {"genre": "limite", "reprise": None, "extrait": "usage limit"}}
            subprocess.run([sys.executable, str(projet / ".socle/socle"), "hook", "session-start"], cwd=projet,
                           input=json.dumps({"session_id": "essai", "source": "startup"}), capture_output=True,
                           text=True, env=banc.env_neuf())
            return {"code": 0, "duree": 1, "reponse": banc._s1_simuler(projet, True, 1), "cout": 0.1, "tours": 3,
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
