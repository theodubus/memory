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


def _compactage(secondes, avant=1200):
    return {"type": "system", "subtype": "compact_boundary", "timestamp": _h(secondes), "compactMetadata": {
        "trigger": "manual", "preTokens": avant, "postTokens": 300, "durationMs": 5000}}


def _limite(secondes, fin_s):
    return {"type": "assistant", "timestamp": _h(secondes), "quotaLimits": {
        "rateLimitType": "five_hour", "resetsAt": int((T0 + timedelta(seconds=fin_s)).timestamp())}}


def _a(secondes, modele="m", **k):
    """Un appel déjà lu : entrée, écritures, lecture et sortie nommées."""
    return conso.Appel(T0 + timedelta(seconds=secondes), modele, k.get("entree", 0), k.get("e5m", 0),
                       k.get("e1h", 0), k.get("lecture", 0), k.get("sortie", 0))


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
    _limite(7260, 3 * 3600),
    _compactage(7320),
    {"type": "user", "timestamp": _h(7320), "isCompactSummary": True, "message": {"content": "z" * 350}},
    _appel(7380, "r4", e1h=300, sortie=5),
]

SOUS_AGENT = [
    _appel(300, "s1", e5m=500, sortie=10, modele="claude-test-2"),
    _appel(1200, "s2", e5m=600, lecture=500, sortie=10, modele="claude-test-2"),
]


def _ecrire(chemin: Path, lignes: list) -> Path:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("\n".join(json.dumps(o) for o in lignes) + "\n")
    return chemin


class Transcription(unittest.TestCase):
    def setUp(self):
        self._dossier = tempfile.TemporaryDirectory()
        self.dossier = Path(self._dossier.name)
        _ecrire(self.dossier / "sess.jsonl", PRINCIPALE)
        _ecrire(self.dossier / "sess" / "subagents" / "agent-a.jsonl", SOUS_AGENT)
        self.convs = conso.lire_dossier(self.dossier)
        self.principale, self.sous_agent = self.convs

    def tearDown(self):
        self._dossier.cleanup()

    def lire(self, lignes: list, sous_agent: bool = False) -> conso.Conversation:
        return conso.lire_conversation(_ecrire(self.dossier / "autre.jsonl", lignes), sous_agent)


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

    def test_lire_conversation_sans_request_id_compte_chaque_uuid(self):
        lignes = [_appel(10, None, lecture=100), _appel(20, None, lecture=200)]
        lignes[0]["uuid"], lignes[1]["uuid"] = "u1", "u2"
        self.assertEqual([a.lecture for a in self.lire(lignes).appels], [100, 200])

    def test_lire_conversation_sans_detail_du_cache_ecrit_sur_cinq_minutes(self):
        ligne = _appel(10, "r", e1h=300)
        usage = ligne["message"]["usage"]
        usage["cache_creation_input_tokens"] = 1000
        usage["cache_creation"] = {"ephemeral_1h_input_tokens": 300}
        (a,) = self.lire([ligne]).appels
        self.assertEqual((a.ecriture_5m, a.ecriture_1h), (700, 300))

    def test_lire_conversation_reconnait_ce_que_le_socle_injecte(self):
        agents = "# Projet\n\nrègles du projet\n\n" + conso.SECTIONS_SOCLE[0] + "\n\n" + "s" * 100 + "\n## Après\n\nautre"
        relue = {"type": "tool_use", "id": "h1", "name": "Bash",
                 "input": {"command": "sed -n 1,40p /racine/tool-results/hook-abc.txt"}}
        dossier = conso.TETES_REVUE[0] + "\n\n" + "d" * 200
        conv = self.lire([
            {"type": "attachment", "timestamp": _h(0), "attachment": {
                "type": "hook_success", "hookEvent": "SessionStart", "hookName": "SessionStart:resume",
                "content": "a" * 20, "stdout": "a" * 900}},
            {"type": "attachment", "timestamp": _h(1), "attachment": {"type": "instructions", "files": [
                {"path": "/p/CLAUDE.md", "content": "@AGENTS.md"}, {"path": "/p/AGENTS.md", "content": agents}]}},
            {"type": "user", "timestamp": _h(2), "message": {"content": dossier}},
            _appel(10, "r1", e1h=100, blocs=[relue]),
            _resultat(11, "h1", "h" * 30),
            {"type": "attachment", "timestamp": _h(12), "attachment": {"type": "hook_blocking_error", "x": "y"}},
            _appel(20, "r2", lecture=100, blocs=[{"type": "tool_use", "id": "l1", "name": "Read",
                                                  "input": {"file_path": "/tmp/dossier.md"}}]),
            _resultat(21, "l1", dossier),
        ])
        natures = [i["nature"] for i in conv.injections]
        self.assertEqual(natures, ["SessionStart:resume", conso.AGENTS_SOCLE, "dossier de revue",
                                   "sortie de hook relue", "refus Stop", "dossier de revue"])
        octets = [i["octets"] for i in conv.injections]
        self.assertEqual(octets[0], 20)
        self.assertEqual(conv.injections[0]["sortie_octets"], 900)
        self.assertEqual(octets[1], len((conso.SECTIONS_SOCLE[0] + "\n\n" + "s" * 100).encode()))
        self.assertEqual(octets[3], 30)

    def test_ni_un_chemin_cite_ni_un_entete_cite_ne_sont_des_relectures(self):
        # écrire le fichier d'une sortie de hook, ou chercher son chemin, n'est pas le relire ;
        # l'en-tête d'un dossier cité au milieu d'une sortie de grep n'en fait pas un dossier
        ecrit = {"type": "tool_use", "id": "w1", "name": "Write",
                 "input": {"file_path": "/racine/tool-results/hook-abc.txt", "content": "x"}}
        cherche = {"type": "tool_use", "id": "g1", "name": "Bash",
                   "input": {"command": "grep -rn tool-results/hook- engine/"}}
        lu = {"type": "tool_use", "id": "r1", "name": "Read",
              "input": {"file_path": "/racine/tool-results/hook-abc.txt"}}
        cite = "engine/socle/review.py:12:    " + conso.TETES_REVUE[0]
        numerote = "     1\t" + conso.TETES_REVUE[0] + "\n\n" + "d" * 50
        conv = self.lire([
            _appel(10, "a1", e1h=100, blocs=[ecrit, cherche, lu]),
            _resultat(11, "w1", "écrit"),
            _resultat(12, "g1", cite),
            _resultat(13, "r1", "h" * 30),
            _appel(20, "a2", lecture=100, blocs=[{"type": "tool_use", "id": "l1", "name": "Read",
                                                  "input": {"file_path": "/tmp/dossier.md"}}]),
            _resultat(21, "l1", numerote),
        ])
        self.assertEqual([i["nature"] for i in conv.injections], ["sortie de hook relue", "dossier de revue"])
        self.assertEqual(conv.injections[0]["octets"], 30)

    def test_la_section_du_socle_en_fin_de_fichier(self):
        texte = "# Projet\n\nrègles\n\n" + conso.SECTIONS_SOCLE[1] + "\n\nfin"
        self.assertEqual(conso._section_socle(texte), conso.SECTIONS_SOCLE[1] + "\n\nfin")

    def test_les_entetes_reconnus_sont_ceux_que_le_moteur_ecrit(self):
        moteur = RACINE / "engine" / "socle"
        self.assertIn(conso.TETES_REVUE[0], (moteur / "review.py").read_text(encoding="utf-8"))
        self.assertIn(conso.TETES_REVUE[1], (moteur / "messages_en.py").read_text(encoding="utf-8"))
        self.assertIn(conso.SECTIONS_SOCLE[0], (moteur / "templates" / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn(conso.SECTIONS_SOCLE[1], (moteur / "templates" / "AGENTS.en.md").read_text(encoding="utf-8"))

    def test_tronquer_fige_la_mesure_a_un_instant(self):
        figees = conso.tronquer(self.convs, T0 + timedelta(seconds=90))
        self.assertEqual(len(figees), 1)
        self.assertEqual(len(figees[0].appels), 2)
        self.assertEqual(len(figees[0].injections), 2)

    def test_un_horodatage_sans_fuseau_vaut_utc(self):
        ligne = _appel(10, "r", lecture=1)
        ligne["timestamp"] = "2026-11-12T10:00:10"
        conv = self.lire([ligne])
        self.assertEqual(conv.appels[0].horodatage, T0 + timedelta(seconds=10))
        self.assertEqual(len(conso.tronquer([conv], T0 + timedelta(seconds=20))[0].appels), 1)

    def test_lire_point(self):
        instant, part, semaine = conso.lire_point("2026-11-12T18:07:25.6Z,0.39/0.59")
        self.assertEqual(instant, datetime(2026, 11, 12, 18, 7, 25, 600000, tzinfo=timezone.utc))
        self.assertEqual((part, semaine), (0.39, 0.59))
        self.assertEqual(conso.lire_point("2026-11-12T18:07:25,0.39")[1:], (0.39, None))
        self.assertEqual(conso.lire_point("2026-11-12T18:07:25,0.39")[0].tzinfo, timezone.utc)
        with self.assertRaisesRegex(ValueError, "point décimal"):
            conso.lire_point("2026-11-12T18:07:25Z,0,39")


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

    def test_compactages_et_la_borne_basse_de_leur_cout(self):
        (c,) = conso.compactages(self.principale)
        self.assertAlmostEqual(c["resume_jetons"], 100)
        self.assertAlmostEqual(c["borne_basse"], 1200 * 0.1 + 100 * 5)
        self.assertAlmostEqual(c["cout_appel_suivant"], 300 * 2 + 5 * 5)

    def test_taille_contexte_au_90e_centile(self):
        conv = conso.Conversation("c", False, [_a(i, lecture=1000 * i) for i in range(1, 12)])
        taille = conso.taille_contexte(conv)["2026-11-12"]
        self.assertEqual((taille["appels"], taille["mediane"], taille["p90"], taille["maximum"]),
                         (11, 6000, 10_000, 11_000))
        self.assertEqual(conso.taille_contexte(self.principale)["2026-11-12"]["au_dela_400k"], 0)

    def test_premiers_appels_cout_median_et_ecrit_pour_une_heure(self):
        sous = [conso.Conversation(f"s{i}", True, [_a(0, e5m=e)]) for i, e in enumerate((100, 400, 1000))]
        neuf = conso.premiers_appels(sous + [self.principale])
        self.assertEqual((neuf["nombre"], neuf["contexte_median"], neuf["contexte_max"]), (3, 400, 1000))
        self.assertAlmostEqual(neuf["cout_median"], 400 * 1.25)
        self.assertAlmostEqual(neuf["cout_median_1h"], 400 * 2)

    def test_concurrence_coupe_a_cinq_minutes_d_inactivite(self):
        # a travaille à 0 s puis à 1200 s ; b à 600 s seulement : ils ne travaillent jamais ensemble
        a = conso.Conversation("a", True, [_a(0), _a(1200)])
        b = conso.Conversation("b", True, [_a(600)])
        self.assertEqual(conso.concurrence([a, b, self.principale]), {"2026-11-12": 1})
        self.assertEqual(conso.concurrence([a, b], inactivite_s=3600), {"2026-11-12": 2})
        # deux sous-agents qui se touchent à la même seconde comptent ensemble
        c = conso.Conversation("c", True, [_a(1200), _a(1300)])
        self.assertEqual(conso.concurrence([a, c]), {"2026-11-12": 2})
        self.assertEqual(conso.concurrence(self.convs), {"2026-11-12": 1})

    def test_appels_tiedes_et_cout_selon_contexte(self):
        conv = conso.Conversation("c", False, [
            _a(0, e1h=90_000), _a(600, lecture=100_000, e1h=2000, sortie=100), _a(4000, lecture=500_000, sortie=10),
            _a(8000, lecture=510_000), _a(8200, e1h=40_000)])
        conv.compactages = [{"horodatage": T0 + timedelta(seconds=8100)}]
        self.assertEqual([a.horodatage for a in conso.appels_tiedes(conv)],
                         [T0 + timedelta(seconds=600), T0 + timedelta(seconds=4000)])
        sous = conso.Conversation("s", True, [_a(0, e5m=1000), _a(400, lecture=100_000)])
        self.assertEqual(conso.appels_tiedes(sous), [])
        cent, trois_cents, cinq_cents = conso.cout_selon_contexte([conv, sous], modele="m")
        self.assertEqual((cent["centre"], cent["appels"]), (100_000, 1))
        self.assertAlmostEqual(cent["cout"], 100_000 * 0.1 + 2000 * 2 + 100 * 5)
        self.assertAlmostEqual(cent["lecture"], 100_000 * 0.1)
        self.assertEqual(trois_cents["appels"], 0)
        self.assertAlmostEqual(cinq_cents["cout"], 500_000 * 0.1 + 10 * 5)
        self.assertEqual(conso.cout_selon_contexte([conv], modele="autre")[0]["appels"], 0)

    def test_injections_socle_par_jour(self):
        inj = conso.injections_socle(self.convs)
        jour = inj["par_jour"]["2026-11-12"]
        self.assertEqual(jour["commande socle state"], {"nombre": 1, "octets": 350, "max": 350})
        self.assertEqual(jour["refus PreToolUse"]["nombre"], 1)
        self.assertIsNone(inj["sorties_de_hook"])
        self.principale.injections[0]["sortie_octets"] = 900
        self.assertEqual(conso.injections_socle(self.convs)["sorties_de_hook"], (900, 900))

    def test_presence_socle_remise_a_zero_au_compactage_et_hors_sortie(self):
        conv = conso.Conversation("c", False, [_a(10, lecture=1000, sortie=10), _a(30, lecture=1000)])
        conv.injections = [{"horodatage": T0, "nature": "n", "octets": 350}]
        conv.compactages = [{"horodatage": T0 + timedelta(seconds=20)}]
        presence = conso.presence_socle([conv])
        n = presence["natures"]["n"]
        # 100 jetons sur 1 000 au premier appel, rien après le compactage
        self.assertAlmostEqual(n["part_contexte"], 0.05)
        # la part de l'entrée du premier appel (1 000 × 0,1), pas de sa sortie
        self.assertAlmostEqual(n["cout"], 0.1 * 100)
        self.assertEqual(n["conversations"], 1)
        self.assertAlmostEqual(presence["total"], 100 + 50 + 100)
        self.assertEqual(conso.presence_socle([conv], sous_agents=True)["natures"], {})

    def test_part_du_socle_avec_et_sans_une_nature(self):
        presence = {"total": 1000.0, "natures": {"a": {"part_contexte": 0.02, "cout": 10.0},
                                                 conso.AGENTS_SOCLE: {"part_contexte": 0.03, "cout": 40.0}}}
        for obtenu, attendu in ((conso.part_du_socle(presence), (0.05, 0.05)),
                                (conso.part_du_socle(presence, exclure=(conso.AGENTS_SOCLE,)), (0.02, 0.01))):
            self.assertAlmostEqual(obtenu[0], attendu[0])
            self.assertAlmostEqual(obtenu[1], attendu[1])

    def test_tailles_par_injection_ou_par_conversation(self):
        a = conso.Conversation("a", True, [_a(0)])
        a.injections = [{"horodatage": T0, "nature": "dossier de revue", "octets": o} for o in (10, 30)]
        b = conso.Conversation("b", True, [_a(0)])
        b.injections = [{"horodatage": T0, "nature": "dossier de revue", "octets": 25}]
        self.assertEqual(conso.tailles([a, b], "dossier de revue"), [10, 25, 30])
        self.assertEqual(conso.tailles([a, b, self.principale], "dossier de revue", par_conversation=True), [25, 40])
        self.assertEqual(conso.tailles([a, b], "dossier de revue", sous_agents=False), [])

    def test_fenetres_limitees_prennent_le_premier_refus(self):
        (f,) = conso.fenetres_limitees(self.convs)
        self.assertEqual(f["debut"], T0 - timedelta(hours=2))
        self.assertEqual(f["appels"], 5)
        self.assertAlmostEqual(f["cout"], f["par_modele"]["claude-test-1"] + f["cout_sous_agents"])
        tard = conso.Conversation("t", True, [], limites=[{"horodatage": T0 + timedelta(seconds=9000), "type": "five_hour",
                                                           "fin": T0 + timedelta(hours=3)}])
        (g,) = conso.fenetres_limitees(self.convs + [tard])
        self.assertEqual(g["refus"], T0 + timedelta(seconds=7260))

    def test_valeur_du_point_des_autres_modeles(self):
        fenetres = [{"cout": 300.0, "par_modele": {"A": 100.0, "B": 200.0}},
                    {"cout": 300.0, "par_modele": {"A": 300.0}},
                    {"cout": 500.0, "par_modele": {"A": 250.0, "B": 250.0}}]
        deux, seul, trop = conso.valeur_du_point_des_autres(fenetres, "A", 2.0)
        self.assertAlmostEqual(deux["points_du_modele"], 50)
        self.assertAlmostEqual(deux["autres_par_point"], 200 / 50)
        self.assertIsNone(seul["autres_par_point"])
        self.assertIsNone(trop["autres_par_point"])


class TestEtalonnage(unittest.TestCase):
    def setUp(self):
        self.conv = conso.Conversation("c", False, [_a(10, e1h=1000), _a(70, lecture=40000), _a(130, entree=1)])
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

    def test_ajuster_lecture_avec_decalage(self):
        # chaque relevé est porté par la réponse de l'appel qui vient de finir : il compte les appels d'avant
        conv = conso.Conversation("c", False, self.conv.appels + [_a(190, entree=1)])
        points = [(T0 + timedelta(seconds=s), p) for s, p in ((15, 0.0), (75, 0.10), (135, 0.20))]
        lecture, par_point = conso.ajuster_lecture([conv], points)
        self.assertAlmostEqual(lecture, 0.05, places=3)
        self.assertAlmostEqual(par_point, 200, delta=1)
        self.assertEqual([t["appels"] for t in conso.etalonner([conv], points)], [1, 1])

    def test_un_compactage_n_a_pas_de_valeur_du_point_et_coupe_les_releves(self):
        conv = conso.Conversation("c", False, [_a(10, e1h=1000), _a(30, lecture=40000), _a(50, entree=1)],
                                  compactages=[{"horodatage": T0 + timedelta(seconds=20)}])
        # sous le décalage : le relevé de 25 s est porté par le compactage, celui de 35 s par l'appel de 30 s
        (t,) = conso.etalonner([conv], [(T0 + timedelta(seconds=25), 0.0), (T0 + timedelta(seconds=35), 0.05)])
        self.assertEqual((t["appels"], t["compactages"], t["par_point"]), (0, 1, None))
        # un appel chiffré ne donne pas sa valeur du point à l'intervalle qui contient aussi un compactage
        (t,) = conso.etalonner([conv], [(T0 + timedelta(seconds=5), 0.0), (T0 + timedelta(seconds=25), 0.5)],
                               decalage=False)
        self.assertEqual((t["appels"], t["compactages"], t["par_point"]), (1, 1, None))
        points = [(T0 + timedelta(seconds=s), p) for s, p in ((5, 0.0), (15, 0.10), (25, 0.50), (35, 0.60))]
        self.assertEqual([t["compactages"] for t in conso.etalonner([conv], points, decalage=False)], [0, 1, 0])
        lecture, par_point = conso.ajuster_lecture([conv], points, decalage=False)
        self.assertAlmostEqual(lecture, 0.05, places=3)
        marge = conso.fourchette([conv], points, decalage=False)
        self.assertLessEqual(marge["lecture"][0], 0.05)
        self.assertGreaterEqual(marge["lecture"][1], 0.05)

    def test_fourchette_a_l_arrondi_des_releves(self):
        marge = conso.fourchette([self.conv], self.points, decalage=False)
        (bas, haut), (p0, p1) = marge["lecture"], marge["par_point"]
        self.assertTrue(0.035 < bas < 0.05 < haut < 0.07, (bas, haut))
        self.assertTrue(p0 < 200 < p1)
        self.assertLess(haut - bas, conso.fourchette([self.conv], self.points, decalage=False, arrondi=3)["lecture"][1]
                        - conso.fourchette([self.conv], self.points, decalage=False, arrondi=3)["lecture"][0])

    def test_un_etalonnage_impossible_se_dit(self):
        # trois points relevés sur une période sans appel : ni division par zéro, ni poids inventé
        vide = [(T0 + timedelta(seconds=20), 0.0), (T0 + timedelta(seconds=50), 0.03)]
        self.assertIsNone(conso.ajuster_lecture([self.conv], vide, decalage=False))
        self.assertIsNone(conso.fourchette([self.conv], vide, decalage=False))
        # aucun intervalle n'atteint un point
        plat = [(T0, 0.0), (T0 + timedelta(seconds=120), 0.0)]
        self.assertIsNone(conso.ajuster_lecture([self.conv], plat, decalage=False))
        texte = conso.rapport([self.conv], points=plat)
        self.assertIn("Étalonnage impossible", texte)
        self.assertNotIn("explique le mieux", texte)
        # deux relevés par suite s'ajustent exactement à tout poids : aucun n'est identifiable
        deux = [(T0 + timedelta(seconds=15), 0.0), (T0 + timedelta(seconds=135), 0.20)]
        self.assertIsNone(conso.ajuster_lecture([self.conv], deux, decalage=False))

    def test_points_de_semaine_et_leur_arrondi(self):
        semaine = conso.points_de_semaine([(T0, 0.0, 0.53), (T0 + timedelta(seconds=60), 0.39, 0.59),
                                           (T0 + timedelta(seconds=120), 0.62, 0.62)])
        self.assertAlmostEqual(semaine["rapport"], 62 / 9)
        self.assertAlmostEqual(semaine["bas"], 6.1)
        self.assertAlmostEqual(semaine["haut"], 63 / 8)
        self.assertIsNone(conso.points_de_semaine([(T0, 0.5, 0.5), (T0 + timedelta(seconds=60), 0.1, 0.6)]))
        self.assertIsNone(conso.points_de_semaine(self.points))

    def test_modele_etalonne_et_prediction_par_modele(self):
        conv = conso.Conversation("c", False, [_a(10, "A", e1h=1000), _a(20, "B", e1h=500), _a(30, "A", entree=1)])
        tranches = conso.etalonner([conv], [(T0, 0.0), (T0 + timedelta(seconds=25), 0.1)], decalage=False)
        self.assertEqual(conso.modele_etalonne(tranches), "A")
        # sous le décalage, le relevé de 35 s compte les appels de 10 et 20 s
        p = conso.predire([conv], (T0, 0.0), (T0 + timedelta(seconds=35), 0.2), conso.Poids(), {"A": 100.0}, 50.0)
        self.assertAlmostEqual(p["predits"], 2000 / 100 + 1000 / 50)
        self.assertEqual(p["releves"], 20)


class TestRapport(Transcription):
    def test_rapport_ne_porte_que_des_agregats(self):
        texte = conso.rapport(self.convs, points=[(T0, 0.0), (T0 + timedelta(seconds=65), 0.1)])
        for titre in ("## Par jour, par modèle", "## Reprises après une pause", "## Compactages",
                      "## Ce que le socle injecte", "## Étalonnage", "## Fenêtres de cinq heures",
                      "## Coût d'un appel tiède"):
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

    def test_main_refuse_une_virgule_decimale(self):
        erreurs = io.StringIO()
        with contextlib.redirect_stderr(erreurs), self.assertRaises(SystemExit) as fin:
            conso.main([str(self.dossier), "--point", "2026-11-12T10:00:00Z,0,39"])
        self.assertEqual(fin.exception.code, 2)
        self.assertIn("point décimal", erreurs.getvalue())

    def test_main_predit_un_controle_hors_echantillon(self):
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            conso.main([str(self.dossier), "--point", f"{_h(0)},0.0", "--point", f"{_h(65)},0.1",
                        "--control", f"{_h(65 + 7000)},0.2"])
        self.assertIn("Contrôle hors échantillon", sortie.getvalue())
        # un seul intervalle ne départage aucun poids : le poids donné est gardé, et dit tel
        self.assertIn("ne départagent aucun poids de lecture", sortie.getvalue())
        self.assertNotIn("explique le mieux", sortie.getvalue())


if __name__ == "__main__":
    unittest.main()
