"""La mesure de la consommation d'une session (B-0173), sur une transcription
fabriquée ici : aucun contenu réel de transcription n'entre dans le dépôt."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "bench"))

import consumption as conso  # noqa: E402

T0 = datetime(2026, 11, 12, 10, 0, tzinfo=timezone.utc)


def _h(secondes: float) -> str:
    return (T0 + timedelta(seconds=secondes)).isoformat().replace("+00:00", "Z")


def _appel(secondes, requete, *, entree=0, e5m=0, e1h=0, lecture=0, sortie=0, modele="claude-test-1", blocs=None):
    return {"type": "assistant", "timestamp": _h(secondes), "requestId": requete,
            "message": {"model": modele, "content": blocs or [],
                        "usage": {"input_tokens": entree, "cache_creation_input_tokens": e5m + e1h,
                                  "cache_read_input_tokens": lecture, "output_tokens": sortie,
                                  "cache_creation": {"ephemeral_5m_input_tokens": e5m,
                                                     "ephemeral_1h_input_tokens": e1h}}}}


def _resultat(secondes, outil, texte, erreur=False):
    return {"type": "user", "timestamp": _h(secondes), "message": {"content": [
        {"type": "tool_result", "tool_use_id": outil, "is_error": erreur, "content": texte}]}}


PRINCIPALE = [
    {"type": "attachment", "timestamp": _h(0), "attachment": {
        "type": "hook_success", "hookEvent": "SessionStart", "hookName": "SessionStart:startup", "content": "é" * 350}},
    _appel(10, "r1", entree=10, e1h=1000, sortie=100),
    # la même réponse, en un second bloc : même requête, même usage, un appel d'outil
    _appel(10, "r1", entree=10, e1h=1000, sortie=100, blocs=[
        {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "python3 .socle/socle state"}}]),
    _resultat(11, "t1", "x" * 350),
    _appel(60, "r2", lecture=1000, e1h=50, sortie=10),
    {"type": "assistant", "timestamp": _h(61), "requestId": "r9",
     "message": {"model": "<synthetic>", "usage": {"input_tokens": 0, "output_tokens": 0}}},
    _appel(7200, "r3", e1h=1100, sortie=10),
    _resultat(7210, "t2", "PreToolUse:Bash hook error: refusé", erreur=True),
    {"type": "assistant", "timestamp": _h(7260), "quotaLimits": {
        "rateLimitType": "five_hour", "resetsAt": int((T0 + timedelta(hours=3)).timestamp())}},
    {"type": "system", "subtype": "compact_boundary", "timestamp": _h(7320), "compactMetadata": {
        "trigger": "manual", "preTokens": 1200, "postTokens": 300, "durationMs": 5000}},
    {"type": "user", "timestamp": _h(7320), "isCompactSummary": True, "message": {"content": "z" * 350}},
    _appel(7380, "r4", e1h=300, sortie=5),
]

SOUS_AGENT = [
    _appel(300, "s1", e5m=500, sortie=10, modele="claude-test-2"),
    _appel(1200, "s2", e5m=600, lecture=500, sortie=10, modele="claude-test-2"),
]


class Transcription(unittest.TestCase):
    def setUp(self):
        self._dossier = tempfile.TemporaryDirectory()
        self.dossier = Path(self._dossier.name)
        (self.dossier / "sess.jsonl").write_text("\n".join(json.dumps(o) for o in PRINCIPALE) + "\n")
        sous = self.dossier / "sess" / "subagents"
        sous.mkdir(parents=True)
        (sous / "agent-a.jsonl").write_text("\n".join(json.dumps(o) for o in SOUS_AGENT) + "\n")
        self.convs = conso.lire_dossier(self.dossier)
        self.principale, self.sous_agent = self.convs

    def tearDown(self):
        self._dossier.cleanup()


class TestLecture(Transcription):
    def test_lire_dossier_trouve_la_principale_et_ses_sous_agents(self):
        self.assertEqual([c.sous_agent for c in self.convs], [False, True])
        self.assertEqual(conso.lire_dossier(self.dossier, session="autre"), [])

    def test_lire_conversation_compte_un_appel_par_requete_et_ignore_le_synthetique(self):
        conv = conso.lire_conversation(self.dossier / "sess.jsonl")
        self.assertEqual(len(conv.appels), 4)
        self.assertEqual(conv.appels[0].ecriture_1h, 1000)
        self.assertEqual(conv.appels[0].contexte, 1010)
        self.assertEqual(len(conv.limites), 1)
        self.assertEqual(conv.compactages[0]["avant"], 1200)
        self.assertEqual(conv.compactages[0]["resume_octets"], 350)
        natures = [i["nature"] for i in conv.injections]
        self.assertEqual(natures, ["SessionStart:startup", "commande socle state", "refus PreToolUse"])
        self.assertEqual(conv.injections[0]["octets"], 700)

    def test_tronquer_fige_la_mesure_a_un_instant(self):
        figees = conso.tronquer(self.convs, T0 + timedelta(seconds=90))
        self.assertEqual(len(figees), 1)
        self.assertEqual(len(figees[0].appels), 2)
        self.assertEqual(len(figees[0].injections), 2)

    def test_lire_point(self):
        instant, part = conso.lire_point("2026-11-12T18:07:25Z,0.39")
        self.assertEqual(instant, datetime(2026, 11, 12, 18, 7, 25, tzinfo=timezone.utc))
        self.assertEqual(part, 0.39)


class TestCouts(Transcription):
    def test_cout_pondere_par_categorie(self):
        r1 = self.principale.appels[0]
        self.assertAlmostEqual(conso.cout(r1), 10 + 1000 * 2 + 100 * 5)
        self.assertAlmostEqual(conso.cout(r1, conso.Poids(ecriture_1h=1, sortie=1)), 1110)

    def test_resume_par_jour_par_modele_et_par_portee(self):
        table = conso.resume_par_jour(self.convs)
        principale = table[("2026-11-12", "claude-test-1", "principale")]
        self.assertEqual(principale["appels"], 4)
        self.assertEqual(principale["ecriture_1h"], 2450)
        sous = table[("2026-11-12", "claude-test-2", "sous-agents")]
        self.assertEqual((sous["conversations"], sous["appels"]), (1, 2))
        self.assertAlmostEqual(sous["maximum"], sous["cout"])

    def test_pauses_et_leur_resume(self):
        longues = conso.pauses(self.principale, seuil_s=conso.UNE_HEURE)
        self.assertEqual(len(longues), 1)
        self.assertGreater(longues[0]["rapport"], 1)
        lignes = {(l["portee"], l["seuil_s"]): l for l in conso.resume_pauses(self.convs)}
        self.assertEqual(lignes[("principale", conso.UNE_HEURE)]["reprises"], 1)
        self.assertEqual(lignes[("sous-agents", conso.CINQ_MINUTES)]["reprises"], 1)
        self.assertEqual(lignes[("sous-agents", conso.UNE_HEURE)]["reprises"], 0)
        self.assertEqual(conso.resume_pauses(self.convs, jours={"2026-01-01"})[0]["reprises"], 0)

    def test_compactages_et_leur_cout_estime(self):
        (c,) = conso.compactages(self.principale)
        self.assertAlmostEqual(c["resume_jetons"], 100)
        self.assertAlmostEqual(c["cout_estime"], 1200 * 0.1 + 100 * 5)
        self.assertAlmostEqual(c["cout_appel_suivant"], 300 * 2 + 5 * 5)

    def test_taille_contexte_concurrence_et_premiers_appels(self):
        taille = conso.taille_contexte(self.principale)["2026-11-12"]
        self.assertEqual((taille["appels"], taille["maximum"], taille["au_dela_400k"]), (4, 1100, 0))
        self.assertEqual(conso.concurrence(self.convs), {"2026-11-12": 1})
        self.assertEqual(conso.premiers_appels(self.convs)["contexte_median"], 500)

    def test_injections_socle_par_jour_et_leur_presence_jusqu_au_compactage(self):
        inj = conso.injections_socle(self.convs)
        jour = inj["par_jour"]["2026-11-12"]
        self.assertEqual(jour["commande socle state"], {"nombre": 1, "octets": 350})
        self.assertEqual(jour["refus PreToolUse"]["nombre"], 1)
        self.assertGreater(inj["presence"]["part_contexte"], 0)
        self.assertLess(inj["presence"]["part_cout"], 1)

    def test_fenetres_limitees(self):
        (f,) = conso.fenetres_limitees(self.convs)
        self.assertEqual(f["debut"], T0 - timedelta(hours=2))
        self.assertEqual(f["appels"], 5)
        self.assertAlmostEqual(f["cout"], f["par_modele"]["claude-test-1"] + f["cout_sous_agents"])


class TestEtalonnage(unittest.TestCase):
    def setUp(self):
        a = lambda s, **k: conso.Appel(T0 + timedelta(seconds=s), "m", k.get("entree", 0), 0, k.get("e1h", 0),
                                       k.get("lecture", 0), 0)
        self.conv = conso.Conversation("c", False, [a(10, e1h=1000), a(70, lecture=40000), a(130, entree=1)])
        self.points = [(T0, 0.0), (T0 + timedelta(seconds=60), 0.10), (T0 + timedelta(seconds=120), 0.20)]

    def test_etalonner_avec_et_sans_decalage(self):
        sans = conso.etalonner([self.conv], self.points, decalage=False)
        self.assertEqual([t["appels"] for t in sans], [1, 1])
        self.assertAlmostEqual(sans[0]["par_point"], 200)
        avec = conso.etalonner([self.conv], self.points, decalage=True)
        self.assertEqual([t["appels"] for t in avec], [0, 1])

    def test_ajuster_lecture_retrouve_le_poids_qui_explique_les_releves(self):
        lecture, par_point = conso.ajuster_lecture([self.conv], self.points, decalage=False)
        self.assertAlmostEqual(lecture, 0.05, places=3)
        self.assertAlmostEqual(par_point, 200, delta=1)


class TestRapport(Transcription):
    def test_rapport_ne_porte_que_des_agregats(self):
        texte = conso.rapport(self.convs, points=[(T0, 0.0), (T0 + timedelta(seconds=65), 0.1)])
        for titre in ("## Par jour, par modèle", "## Reprises après une pause", "## Compactages",
                      "## Ce que le socle injecte", "## Étalonnage", "## Fenêtres de cinq heures"):
            self.assertIn(titre, texte)
        for contenu in ("xxx", "zzz", "refusé"):
            self.assertNotIn(contenu, texte)

    def test_main_lit_le_dossier_en_argument(self):
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            self.assertEqual(conso.main([str(self.dossier), "--day", "2026-11-12", "--until", _h(90)]), 0)
        self.assertIn("claude-test-1", sortie.getvalue())
        with tempfile.TemporaryDirectory() as vide, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(conso.main([vide]), 1)


if __name__ == "__main__":
    unittest.main()
