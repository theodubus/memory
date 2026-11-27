"""B-0364 (D-0212, D-0214) : la suite du projet, `socle roadmap`, en une
seule forme, A2-d, pour que l'humain pilote son projet, lue sur un
téléphone : « Maintenant », « Ensuite » en `X. [K/N] titre` alignés, seul
le premier jalon ouvert déplié en ses besoins, « Pour toi », « En
réserve » ; un seul texte, que `--format markdown` met dans un bloc de
code (D-0228). Le calcul de la suite
(B-0274), dont l'alerte de deux lots qui attendent le même lot sans ordre
entre eux, ne change pas. Sa spécification :
`docs/fabrication/feuille-de-route-specification.md`."""

import argparse
import contextlib
import datetime
import io
import re
import unittest
from pathlib import Path

from socle import cli, memory as memoire, messages, roadmap as suite
from tests.test_structure import Projet, entree, memoire_de

JOUR = datetime.date(2026, 11, 27)


def demande(mem: memoire.Memoire, ident: str = "D-0001") -> memoire.Memoire:
    chemin = f"memory/requests/{ident}-essai.md"
    mem.fichiers[chemin] = memoire.analyser(chemin, "<!-- socle: couche=demandes zone=publique -->\n"
                                                    f"# {ident} — Une demande\n\n> date : 2026-11-17\n")
    return mem


def backlog_d_essai() -> memoire.Memoire:
    """Deux jalons, trois lots, et des besoins hors des lots : un à découper,
    un dont la tâche n'est dans aucun lot, un bloqué, un à fermer."""
    return demande(memoire_de(
        entree("B-0001", meta="priorité : haute"), entree("B-0002"), entree("B-0003"), entree("B-0004"),
        entree("B-0005"), entree("B-0006", "bloqué"), entree("B-0008"),
        entree("T-0001", "en cours", meta="besoin : B-0001"),
        entree("T-0002", "fait", meta="besoin : B-0001"),
        entree("T-0003", meta="besoin : B-0002 · après : T-0001"),
        entree("T-0004", meta="besoin : B-0003 · après : D-0001"),
        entree("T-0005", meta="besoin : B-0003 · pour : humain"),
        entree("T-0006", meta="besoin : B-0005"),
        entree("T-0007", "fait", meta="besoin : B-0008"),
        entree("L-0001", "en cours", meta="après : T-0001, T-0002"),
        entree("L-0002", meta="après : L-0001, T-0003, D-0001"),
        entree("L-0003", meta="après : L-0002, T-0004, T-0005"),
        entree("JA-0001", meta="après : B-0001, B-0002"),
        entree("JA-0002", meta="après : JA-0001, B-0003"),
    ))


# Les titres du backlog de la maquette que Théo a validée (D-0214), dans
# chaque langue.
TITRES = {
    "fr": {"L-0001": "Finir l'adoption du socle : le reste de la mise à jour",
           "T-0001": "Passer CLAUDE.md dans AGENTS.md", "B-0001": "L'adoption du socle",
           "B-0002": "Copier les données d'entraînement sur un disque dur",
           "JA-0001": "Embarquer le réseau N10", "B-0011": "Entraîner N10 sur les parties de novembre",
           "B-0012": "Mesurer N10 contre N8 : 2 000 parties", "B-0013": "Embarquer N10 dans le binaire",
           "B-0014": "Situer le moteur sur la liste CCRL", "JA-0002": "Régler la recherche par SPSA",
           "JA-0003": "Accélérer la recherche", "JA-0004": "Nouvelle architecture de réseau"},
    "en": {"L-0001": "Finish adopting the socle: the rest of the update",
           "T-0001": "Move CLAUDE.md into AGENTS.md", "B-0001": "Adopting the socle",
           "B-0002": "Copy the training data to a hard drive",
           "JA-0001": "Ship the N10 network", "B-0011": "Train N10 on the November games",
           "B-0012": "Measure N10 against N8: 2,000 games", "B-0013": "Ship N10 in the binary",
           "B-0014": "Place the engine on the CCRL list", "JA-0002": "Tune the search with SPSA",
           "JA-0003": "Speed up the search", "JA-0004": "New network architecture"},
}


def titree(ident: str, titre: str, statut: str = "ouvert", meta: str = "") -> tuple[str, str]:
    """Une entrée du backlog sous son titre."""
    chemin, texte = entree(ident, statut, meta)
    return chemin, texte.replace(f"L'entrée {ident}", titre, 1)


def backlog_de_la_maquette(lg: str = "fr") -> memoire.Memoire:
    """Le backlog de la maquette A2-d (D-0214) : un lot en cours hors des
    jalons ; quatre jalons qui se suivent, le premier avec un besoin clos sur
    quatre ; un besoin pour l'humain ; douze besoins d'aucun jalon, dont
    deux de priorité haute."""
    def e(ident: str, statut: str = "ouvert", meta: str = "") -> tuple[str, str]:
        defaut = f"L'entrée {ident}" if lg == "fr" else f"Entry {ident}"
        return titree(ident, TITRES[lg].get(ident, defaut), statut, meta)

    return memoire_de(
        e("B-0001"), e("T-0001", meta="besoin : B-0001"), e("L-0001", "en cours", "après : T-0001"),
        e("B-0002", meta="pour : humain"),
        e("B-0011", "fait"), *(e(f"B-00{n}") for n in (12, 13, 14, 21, 22, 23, 31, 32, 41, 42, 43)),
        e("JA-0001", meta="après : B-0011, B-0012, B-0013, B-0014"),
        e("JA-0002", meta="après : JA-0001, B-0021, B-0022, B-0023"),
        e("JA-0003", meta="après : JA-0002, B-0031, B-0032"),
        e("JA-0004", meta="après : JA-0003, B-0041, B-0042, B-0043"),
        *(e(f"B-01{n:02d}", meta="priorité : haute" if n in (1, 2) else "") for n in range(1, 13)),
    )


def sans_numeros(texte: str) -> str:
    """Un texte, ses identifiants écrits `X-NNNN`, comme le guide les montre :
    il ne cite aucun identifiant d'une mémoire."""
    return memoire.ID_RE.sub(lambda m: f"{m.group('type')}-NNNN", texte)


class TestCalcul(unittest.TestCase):
    def test_un_besoin_pour_l_humain_ne_se_decoupe_pas(self):
        """B-0363 : un besoin « pour : humain » sans tâche n'est plus parmi les
        besoins à découper, ni dans l'état ni dans la feuille de route : il
        n'y paraît que sous « Pour toi »."""
        mem = memoire_de(entree("B-0001", meta="pour : humain"), entree("B-0002"), entree("B-0003"),
                         entree("T-0001", meta="besoin : B-0003"))
        self.assertEqual([e.id for e in memoire.ordre(mem).a_decouper], ["B-0002"])
        etat = [l for l in memoire.lignes_ordre(mem) if l.startswith("besoins à découper")]
        self.assertEqual(etat, ["besoins à découper en tâches : B-0002"])
        s = suite.calculer(mem)
        self.assertEqual([e.id for e in s.a_decouper], ["B-0002"])
        self.assertEqual([e.id for e in s.pour_l_humain], ["B-0001"])
        texte = suite.texte(s)
        self.assertIn("Pour toi : L'entrée B-0001 (B-0001)", texte.splitlines())
        self.assertNotIn("B-0002", texte)
        self.assertEqual(suite.markdown(s), f"```text\n{texte}\n```\n")

    def test_les_lots_et_les_jalons_dans_leur_ordre_avec_leur_avancement(self):
        s = suite.calculer(backlog_d_essai())
        self.assertEqual([(j.entree.id, j.clos, j.total) for j in s.jalons], [("JA-0001", 0, 2), ("JA-0002", 0, 1)])
        self.assertEqual([lot.entree.id for lot in s.lots], ["L-0001", "L-0002", "L-0003"])
        self.assertEqual(s.courant, 0)
        self.assertEqual([(t.entree.id, t.avancement, t.attend) for lot in s.lots for t in lot.taches], [
            ("T-0001", "en-cours", []), ("T-0002", "fait", []), ("T-0003", "attend", ["T-0001"]),
            ("T-0004", "attend", ["D-0001"]), ("T-0005", "pret", [])])
        self.assertEqual(s.lots[1].demandes, ["D-0001"])
        self.assertEqual([(lot.en_cours, lot.closes) for lot in s.lots], [(True, 1), (False, 0), (False, 0)])
        self.assertEqual([(t.besoin, t.close) for t in s.lots[0].taches], [("B-0001", False), ("B-0001", True)])
        self.assertTrue(memoire.pour_l_humain(s.taches["T-0005"].entree))
        self.assertFalse(memoire.pour_l_humain(s.taches["T-0006"].entree))
        self.assertEqual([t.entree.id for t in s.hors_lot], ["T-0006"])
        self.assertEqual([[e.id for e in x] for x in (s.a_decouper, s.a_fermer, s.bloques, s.pour_l_humain,
                                                      s.demandes, s.sans_jalon)],
                         [["B-0004"], ["B-0008"], ["B-0006"], ["T-0005"], ["D-0001"],
                          ["B-0004", "B-0005", "B-0006", "B-0008"]])
        self.assertEqual(suite.besoins_dans_l_ordre(s), ["B-0001", "B-0002", "B-0003", "B-0005"])
        self.assertEqual([t.entree.id for t in suite.taches_du_besoin(s, "B-0003")], ["T-0004", "T-0005"])
        self.assertEqual(s.alertes, [])

    def test_l_ordre_d_execution_vient_des_apres_et_non_des_numeros(self):
        """Le graphe que l'état lit donne l'ordre : un lot d'un numéro plus
        petit, qui attend un autre, vient après lui ; à choix égal, l'en
        cours d'abord."""
        mem = memoire_de(entree("L-0001", meta="après : L-0003"), entree("L-0002", meta="après : L-0001"),
                         entree("L-0003"), entree("L-0004", "en cours"))
        g = memoire.Graphe(mem)
        self.assertEqual(g.dans_l_ordre(memoire.est_lot), ["L-0004", "L-0003", "L-0001", "L-0002"])
        self.assertEqual(g.premier(memoire.est_lot), ["L-0004", "L-0003"])
        self.assertEqual(g.attendus("L-0002"), {"L-0001", "L-0003"})
        self.assertEqual((g.deps("L-0002"), g.attend("L-0002"), g.ou_en_est("L-0003")), (["L-0001"], ["L-0001"], "pret"))
        self.assertTrue(g.ouvert("L-0001"))
        self.assertIsNotNone(memoire.ordre_de(g))
        self.assertEqual(memoire.ordre(mem).lot.id, "L-0004")

    def test_deux_lots_qui_attendent_le_meme_lot_sans_ordre_entre_eux_sont_signales(self):
        ambigu = memoire_de(entree("L-0001", "en cours"), entree("L-0002", meta="après : L-0001"),
                            entree("L-0003", meta="après : L-0001"))
        s = suite.calculer(ambigu)
        self.assertEqual(s.alertes, [("L-0002", "L-0003", "L-0001")])
        self.assertEqual(suite.alertes(memoire.Graphe(ambigu), ["L-0001", "L-0002", "L-0003"]),
                         [("L-0002", "L-0003", "L-0001")])
        attendu = "ordre ambigu : L-0002 et L-0003 attendent tous deux L-0001, sans ordre entre eux — que l'un " \
                  "attende l'autre"
        self.assertIn("Attention : " + attendu, " ".join(suite.texte(s).split()))
        self.assertIn("Attention : " + attendu, " ".join(suite.markdown(s).split()))
        self.assertNotIn("\n\n\n", suite.markdown(s))
        # Le même lot attendu, clos : l'ordre des deux reste à choisir.
        clos = memoire_de(entree("L-0001", "fait"), entree("L-0002", meta="après : L-0001"),
                          entree("L-0003", meta="après : L-0001"))
        self.assertEqual(suite.calculer(clos).alertes, [("L-0002", "L-0003", "L-0001")])
        # L'un attend l'autre, de proche en proche : aucune alerte.
        ordonne = memoire_de(entree("L-0001", "en cours"), entree("L-0002", meta="après : L-0001"),
                             entree("L-0004", meta="après : L-0002"), entree("L-0003", meta="après : L-0001, L-0004"))
        self.assertEqual(suite.calculer(ordonne).alertes, [])
        self.assertNotIn("ordre ambigu", suite.texte(suite.calculer(ordonne)))


class TestLaForme(unittest.TestCase):
    """T-0207 : la forme, point par point, comme la spécification les
    énumère, en ses deux rendus."""

    def test_la_forme_comme_la_maquette_validee_dans_le_terminal(self):
        attendus = {
            "fr": ["La suite de Fou — 27 novembre", "",
                   "Maintenant",
                   " ▶ Finir l'adoption du socle (L-0001)",
                   "   besoin : L'adoption du socle (B-0001)",
                   "     reste : Passer CLAUDE.md dans",
                   "             AGENTS.md (T-0001)", "",
                   "Ensuite",
                   "1. [1/4] Embarquer le réseau N10 (JA-0001)",
                   "         ✓ Entraîner N10 sur les parties de",
                   "           novembre (B-0011)",
                   "         · Mesurer N10 contre N8 (B-0012)",
                   "         · Embarquer N10 dans le",
                   "           binaire (B-0013)",
                   "         · Situer le moteur sur la liste",
                   "           CCRL (B-0014)",
                   "2. [0/3] Régler la recherche par SPSA (JA-0002)",
                   "3. [0/2] Accélérer la recherche (JA-0003)",
                   "4. [0/3] Nouvelle architecture de",
                   "         réseau (JA-0004)", "",
                   "Pour toi : Copier les données d'entraînement sur",
                   "           un disque dur (B-0002)",
                   "En réserve : 12 besoins, dont 2 prioritaires"],
            "en": ["The roadmap of Fou — 27 November", "",
                   "Now",
                   " ▶ Finish adopting the socle (L-0001)",
                   "   need: Adopting the socle (B-0001)",
                   "     left: Move CLAUDE.md into",
                   "           AGENTS.md (T-0001)", "",
                   "Next",
                   "1. [1/4] Ship the N10 network (JA-0001)",
                   "         ✓ Train N10 on the November",
                   "           games (B-0011)",
                   "         · Measure N10 against N8 (B-0012)",
                   "         · Ship N10 in the binary (B-0013)",
                   "         · Place the engine on the CCRL",
                   "           list (B-0014)",
                   "2. [0/3] Tune the search with SPSA (JA-0002)",
                   "3. [0/2] Speed up the search (JA-0003)",
                   "4. [0/3] New network architecture (JA-0004)", "",
                   "For you: Copy the training data to a hard",
                   "         drive (B-0002)",
                   "In reserve: 12 needs, 2 of them high priority"]}
        for lg, lignes in attendus.items():
            with self.subTest(lg), messages.dans(lg):
                self.assertEqual(suite.texte(suite.calculer(backlog_de_la_maquette(lg)), nom="Fou", jour=JOUR)
                                 .splitlines(), lignes)

    def test_le_bloc_de_code_porte_le_texte_du_terminal(self):
        """D-0228 : rendue en Markdown, la forme n'était pas lisible sur un
        téléphone ; dans un bloc de code, elle garde son alignement."""
        for lg in ("fr", "en"):
            with self.subTest(lg), messages.dans(lg):
                s = suite.calculer(backlog_de_la_maquette(lg))
                self.assertEqual(suite.markdown(s, nom="Fou", jour=JOUR),
                                 f"```text\n{suite.texte(s, nom='Fou', jour=JOUR)}\n```\n")
                self.assertEqual(suite.markdown(s, True, "Fou", JOUR),
                                 f"```text\n{suite.texte(s, True, 'Fou', JOUR)}\n```\n")
        # Un titre qui porte trois accents graves allonge la clôture : le
        # bloc ne se ferme pas en route.
        code = suite.calculer(memoire_de(entree("B-0001"), titree("T-0001", "Coller ```text ici", "en cours",
                                                                  meta="besoin : B-0001"),
                                         entree("L-0001", "en cours", meta="après : T-0001")))
        md = suite.markdown(code)
        self.assertTrue(md.startswith("````text\n") and md.endswith("\n````\n"), md)

    def test_les_parties_dans_leur_ordre_et_l_alerte_d_une_entree_bloquee(self):
        s = suite.calculer(backlog_d_essai())
        self.assertEqual(suite.texte(s, nom="calc", jour=JOUR).splitlines(), [
            "La suite de calc — 27 novembre", "",
            "Maintenant",
            " ▶ L'entrée L-0001 (L-0001)",
            "   besoin : L'entrée B-0001 (B-0001)",
            "     reste : L'entrée T-0001 (T-0001)", "",
            "Ensuite",
            "1. [0/2] L'entrée JA-0001 (JA-0001)",
            "         ▶ L'entrée B-0001 (B-0001)",
            "         · L'entrée B-0002 (B-0002)",
            "2. [0/1] L'entrée JA-0002 (JA-0002)", "",
            "Pour toi : L'entrée T-0005 (T-0005)",
            "           Une demande",
            "En réserve : 4 besoins",
            "Attention : bloqué : L'entrée B-0006 (B-0006)"])

    def test_les_crochets_ont_la_meme_largeur_et_les_titres_s_alignent_un_total_a_deux_chiffres_compris(self):
        mem = memoire_de(*(entree(f"B-{n:04d}", "fait" if n == 3 else "ouvert") for n in range(1, 13)),
                         entree("JA-0001", meta="après : B-0012"),
                         entree("JA-0002", meta="après : JA-0001, " + ", ".join(f"B-{n:04d}" for n in range(1, 12))))
        s = suite.calculer(mem)
        lignes = suite.texte(s).splitlines()
        self.assertIn("1. [ 0/1 ] L'entrée JA-0001 (JA-0001)", lignes)
        self.assertIn("2. [ 1/11] L'entrée JA-0002 (JA-0002)", lignes)
        self.assertIn("           · L'entrée B-0012 (B-0012)", lignes)
        # Dix étapes et plus : les numéros s'alignent à droite, les titres
        # commencent tous à la même colonne.
        dix = memoire_de(*(entree(f"B-{n:04d}") for n in range(1, 11)),
                         *(entree(f"JA-{n:04d}", meta="après : " + (f"JA-{n - 1:04d}, " if n > 1 else "")
                                  + f"B-{n:04d}") for n in range(1, 11)))
        etapes = [l for l in suite.texte(suite.calculer(dix)).splitlines() if re.match(r"^ ?\d+\. ", l)]
        self.assertEqual(len(etapes), 10)
        self.assertEqual((etapes[0], etapes[-1]), (" 1. [0/1] L'entrée JA-0001 (JA-0001)",
                                                   "10. [0/1] L'entrée JA-0010 (JA-0010)"))
        self.assertEqual({l.index("L'entrée") for l in etapes}, {10})

    def test_seul_le_premier_jalon_est_deplie_all_les_deplie_tous(self):
        s = suite.calculer(backlog_d_essai())
        self.assertNotIn("B-0003", suite.texte(s))
        self.assertNotIn("B-0003", suite.markdown(s))
        tout = suite.texte(s, tout=True).splitlines()
        jalon = tout.index("2. [0/1] L'entrée JA-0002 (JA-0002)")
        self.assertEqual(tout[jalon + 1], "         · L'entrée B-0003 (B-0003)")
        self.assertIn("2. [0/1] L'entrée JA-0002 (JA-0002)\n         · L'entrée B-0003 (B-0003)\n",
                      suite.markdown(s, tout=True))

    def test_les_trois_marques_d_un_besoin_dans_l_ordre_de_l_apres_du_jalon(self):
        """✓ clos, ▶ servi par une tâche d'un lot en cours, · autre ; une tâche
        en cours hors d'un lot en cours ne fait pas ▶."""
        mem = memoire_de(entree("B-0001", "fait"), entree("B-0002"), entree("B-0003"), entree("B-0004"),
                         entree("T-0001", "en cours", meta="besoin : B-0002"),
                         entree("T-0002", "en cours", meta="besoin : B-0004"),
                         entree("L-0001", "en cours", meta="après : T-0001"),
                         entree("JA-0001", meta="après : B-0003, B-0001, B-0002, B-0004"))
        s = suite.calculer(mem)
        self.assertEqual(suite.besoins_du_jalon(s.jalons[0]), ["B-0003", "B-0001", "B-0002", "B-0004"])
        self.assertEqual(suite.texte(s).splitlines()[8:13], [
            "1. [1/4] L'entrée JA-0001 (JA-0001)",
            "         · L'entrée B-0003 (B-0003)",
            "         ✓ L'entrée B-0001 (B-0001)",
            "         ▶ L'entrée B-0002 (B-0002)",
            "         · L'entrée B-0004 (B-0004)"])

    def test_le_travail_hors_jalon_est_sous_maintenant_et_nulle_part_ailleurs(self):
        mem = memoire_de(entree("B-0001"), entree("B-0002"), entree("B-0003"),
                         entree("T-0001", "en cours", meta="besoin : B-0002"), entree("T-0002", meta="besoin : B-0001"),
                         entree("L-0001", "en cours", meta="après : T-0001"), entree("JA-0001", meta="après : B-0001"))
        s = suite.calculer(mem)
        texte, md = suite.texte(s), suite.markdown(s)
        self.assertEqual(texte.splitlines()[2:6], ["Maintenant", " ▶ L'entrée L-0001 (L-0001)",
                                                    "   besoin : L'entrée B-0002 (B-0002)",
                                                    "     reste : L'entrée T-0001 (T-0001)"])
        self.assertEqual(texte.count("(L-0001)"), 1)
        self.assertEqual(texte.count("B-0002"), 2)
        self.assertEqual(md.count("L'entrée B-0002"), 1)
        # B-0003, d'aucun jalon et que rien ne mène, reste seul en réserve.
        self.assertEqual(texte.splitlines()[-1], "En réserve : 1 besoin")
        # Sans aucun jalon, il n'y a pas d'« Ensuite ».
        sans = suite.calculer(memoire_de(entree("B-0001"), entree("T-0001", meta="besoin : B-0001"),
                                         entree("L-0001", "en cours", meta="après : T-0001")))
        self.assertEqual(suite.texte(sans, nom="calc", jour=JOUR).splitlines(), [
            "La suite de calc — 27 novembre", "", "Maintenant", " ▶ L'entrée L-0001 (L-0001)",
            "   besoin : L'entrée B-0001 (B-0001)", "     reste : L'entrée T-0001 (T-0001)"])
        self.assertNotIn("Ensuite", suite.markdown(sans))

    def test_sans_lot_en_cours_la_premiere_tache_prete_sinon_rien_en_cours(self):
        prete = suite.calculer(memoire_de(entree("B-0001"), entree("T-0002", meta="besoin : B-0001"),
                                          entree("T-0001", meta="besoin : B-0001 · après : T-0002"),
                                          entree("L-0001", meta="après : T-0001")))
        self.assertEqual(suite.texte(prete).splitlines()[2:4], ["Maintenant", "   prête : L'entrée T-0002 (T-0002)"])
        self.assertIn("\nMaintenant\n   prête : L'entrée T-0002 (T-0002)\n", suite.markdown(prete))
        rien = suite.calculer(memoire_de(entree("B-0001")))
        self.assertEqual(suite.texte(rien, nom="calc", jour=JOUR).splitlines(),
                         ["La suite de calc — 27 novembre", "", "Maintenant : rien en cours"])
        self.assertEqual(suite.markdown(rien, nom="calc", jour=JOUR),
                         "```text\nLa suite de calc — 27 novembre\n\nMaintenant : rien en cours\n```\n")

    def test_un_lot_en_cours_nomme_ses_besoins_puis_leurs_taches(self):
        """D-0230 : « Maintenant » nomme le lot, puis chaque besoin qu'il
        mène, dans l'ordre de ses tâches, puis les tâches ouvertes de ce
        besoin dans le lot ; un besoin dont les tâches du lot sont closes
        se nomme sans « reste »."""
        mem = memoire_de(entree("B-0001"), entree("B-0002"), entree("B-0003"),
                         entree("T-0001", "en cours", meta="besoin : B-0002"),
                         entree("T-0002", meta="besoin : B-0001"), entree("T-0003", meta="besoin : B-0002"),
                         entree("T-0004", "fait", meta="besoin : B-0003"),
                         entree("L-0001", "en cours", meta="après : T-0001, T-0002, T-0003, T-0004"))
        self.assertEqual(suite.texte(suite.calculer(mem)).splitlines()[2:], [
            "Maintenant",
            " ▶ L'entrée L-0001 (L-0001)",
            "   besoin : L'entrée B-0002 (B-0002)",
            "     reste : L'entrée T-0001 (T-0001)",
            "             L'entrée T-0003 (T-0003)",
            "   besoin : L'entrée B-0001 (B-0001)",
            "     reste : L'entrée T-0002 (T-0002)",
            "   besoin : L'entrée B-0003 (B-0003)"])
        with messages.dans("en"):
            self.assertIn("   need: L'entrée B-0002 (B-0002)", suite.texte(suite.calculer(mem)).splitlines())

    def test_un_lot_en_cours_nomme_trois_taches_ouvertes_au_plus_puis_compte_les_autres(self):
        def lot(ouvertes: int) -> suite.Suite:
            return suite.calculer(memoire_de(
                entree("B-0001"), entree("T-0009", "fait", meta="besoin : B-0001"),
                *(entree(f"T-000{n}", meta="besoin : B-0001") for n in range(1, ouvertes + 1)),
                entree("L-0001", "en cours", meta="après : T-0009, "
                       + ", ".join(f"T-000{n}" for n in range(1, ouvertes + 1)))))

        self.assertEqual(suite.texte(lot(5)).splitlines()[3:9], [
            " ▶ L'entrée L-0001 (L-0001)",
            "   besoin : L'entrée B-0001 (B-0001)",
            "     reste : L'entrée T-0001 (T-0001)",
            "             L'entrée T-0002 (T-0002)",
            "             L'entrée T-0003 (T-0003)",
            "             et 2 autres"])
        self.assertEqual(suite.texte(lot(4)).splitlines()[8], "             et 1 autre")
        self.assertNotIn("autre", suite.texte(lot(3)))

    def test_aucun_rendu_ne_nomme_une_demande_par_son_identifiant(self):
        """Collé dans le récap de la clôture d'un lot ou dans une réponse, le
        texte ne cite pas une demande en attente sans son lien, que le hook
        de fin de tour refuserait : il la dit par son titre."""
        s = suite.calculer(backlog_d_essai())
        for tout in (False, True):
            for sortie in (suite.texte(s, tout), suite.markdown(s, tout)):
                self.assertNotIn("D-0001", sortie)
                self.assertIn("           Une demande\n", sortie + "\n")

    def test_aucune_ligne_vide_de_pour_toi_ni_de_la_reserve(self):
        s = suite.calculer(memoire_de(entree("B-0001"), entree("JA-0001", meta="après : B-0001")))
        for sortie in (suite.texte(s), suite.markdown(s)):
            self.assertNotIn("Pour toi", sortie)
            self.assertNotIn("En réserve", sortie)
            self.assertNotIn("Attention", sortie)
            self.assertNotIn("\n\n\n", sortie)
        self.assertEqual(suite.texte(s).splitlines()[-1], "         · L'entrée B-0001 (B-0001)")
        un = suite.calculer(memoire_de(entree("B-0001"), entree("B-0002", meta="priorité : haute"),
                                       entree("JA-0001", meta="après : B-0001")))
        self.assertEqual(suite.texte(un).splitlines()[-1], "En réserve : 1 besoin, dont 1 prioritaire")

    def test_ni_tableau_ni_legende_ni_ancien_format(self):
        sorties = []
        for mem in (backlog_d_essai(), backlog_de_la_maquette(), backlog_de_la_maquette("en")):
            s = suite.calculer(mem)
            for lg in ("fr", "en"):
                for tout in (False, True):
                    with messages.dans(lg):
                        sorties += [suite.texte(s, tout), suite.markdown(s, tout)]
        for sortie in sorties:
            self.assertFalse([l for l in sortie.splitlines() if l.lstrip().startswith("|")], sortie)
            for ancien in ("Légende", "Key:", "Hors lot", "Outside the batches", "besoins clos", "needs closed",
                           "⏳", "○", "###"):
                self.assertNotIn(ancien, sortie)
        self.assertEqual(suite.FORMATS, ("text", "markdown"))
        self.assertFalse(hasattr(suite, "LECTURES"))

    def test_une_ligne_longue_passe_a_la_suivante_sous_sa_colonne(self):
        long = "Un titre sans deux-points qui dépasse la largeur de la ligne lue sur un téléphone"
        mem = memoire_de(entree("B-0001"), titree("B-0002", long),
                         titree("T-0001", long, "en cours", meta="besoin : B-0001"),
                         titree("L-0001", long, "en cours", meta="après : T-0001"),
                         titree("JA-0001", long, meta="après : B-0002"))
        lignes = suite.texte(suite.calculer(mem)).splitlines()
        self.assertTrue(all(len(l) <= suite.LARGEUR for l in lignes), lignes)
        # La tête du titre se coupe à `TITRE` caractères ; l'identifiant
        # reste collé au dernier mot.
        self.assertEqual(lignes[3:5], [" ▶ Un titre sans deux-points qui dépasse la",
                                       "   largeur de la ligne lue sur un… (L-0001)"])
        self.assertEqual(lignes[5], "   besoin : L'entrée B-0001 (B-0001)")
        self.assertTrue(lignes[6].startswith("     reste : Un titre"))
        self.assertTrue(lignes[7].startswith("             ") and lignes[7][13] != " ")
        etape = next(k for k, l in enumerate(lignes) if l.startswith("1. [0/1] "))
        self.assertTrue(lignes[etape + 1].startswith("         ") and lignes[etape + 1][9] != " ")
        besoin = next(k for k, l in enumerate(lignes) if l.startswith("         · "))
        self.assertTrue(lignes[besoin + 1].startswith("           ") and lignes[besoin + 1][11] != " ")
        self.assertEqual(" ".join(l.strip() for l in lignes[besoin:]), f"· {suite.court(long)} (B-0002)")

    def test_l_en_tete_nomme_le_projet_et_le_jour(self):
        s = suite.calculer(memoire_de(entree("B-0001")))
        self.assertEqual(suite.entete("calc", JOUR), "La suite de calc — 27 novembre")
        self.assertEqual(suite.entete("atelier", datetime.date(2026, 2, 1)), "La suite d'atelier — 1 février")
        self.assertEqual(suite.entete("", JOUR), "La suite — 27 novembre")
        with messages.dans("en"):
            self.assertEqual(suite.entete("atelier", datetime.date(2026, 8, 3)), "The roadmap of atelier — 3 August")
        aujourd_hui = datetime.date.today()
        self.assertEqual(suite.texte(s, nom="calc").splitlines()[0], suite.entete("calc", aujourd_hui))
        self.assertEqual(len({suite.entete("calc", datetime.date(2026, m, 1)) for m in range(1, 13)}), 12)

    def test_un_titre_se_lit_jusqu_a_son_premier_deux_points_et_se_coupe_a_sa_colonne(self):
        self.assertEqual(suite.court("Fini avant les nouvelles fonctions : les lots qui restent", 46),
                         "Fini avant les nouvelles fonctions")
        self.assertEqual(suite.court("Done before the new features: the remaining batches", 46),
                         "Done before the new features")
        self.assertEqual(suite.court("Un titre court", 46), "Un titre court")
        self.assertEqual(suite.court("Lire https://exemple.org/a : la suite", 46), "Lire https://exemple.org/a")
        self.assertEqual(suite.court("abcdefghij klmnop", 10), "abcdefghi…")
        self.assertEqual(len(suite.court("é" * 80, 46)), 46)
        self.assertEqual(suite.court(" : rien avant", 46), ": rien avant")

    def test_un_deux_points_entre_guillemets_ou_dans_du_code_ne_coupe_pas_le_titre(self):
        self.assertEqual(suite.court("Un besoin « pour : humain » est listé : à corriger"),
                         "Un besoin « pour : humain » est listé")
        self.assertEqual(suite.court("La clé `a : b` se lit : ensuite"), "La clé `a : b` se lit")
        self.assertEqual(suite.court("Les empreintes « lu : backlog@… » que socle new fait citer"),
                         "Les empreintes « lu : backlog@… » que socle new fait citer")
        self.assertEqual(len(suite.court("x" * 100)), suite.TITRE)

    def test_en_anglais_la_suite_ne_garde_aucun_mot_francais(self):
        maquette, essai = suite.calculer(backlog_de_la_maquette("en")), suite.calculer(backlog_d_essai())
        sorties = []
        with messages.dans("en"):
            for tout in (False, True):
                sorties += [suite.texte(maquette, tout, "Fou", JOUR), suite.markdown(maquette, tout, "Fou", JOUR),
                            *(x.replace("L'entrée", "").replace("Une demande", "")
                              for x in (suite.texte(essai, tout, "calc", JOUR),
                                        suite.markdown(essai, tout, "calc", JOUR)))]
            sorties.append(suite.texte(suite.calculer(memoire_de(entree("B-0001")))))
        self.assertIn("Warning: blocked:  B-0006 (B-0006)", sorties[2])
        for sortie in sorties:
            self.assertNotRegex(sortie, r"[àâçéèêëîïôûùœ«»]")
            self.assertNotRegex(sortie, r"\b(?:tâches?|besoins?|lots?|jalons?|Maintenant|Ensuite|reste|prête|toi|"
                                        r"réserve|dont|autres?|bloqué|rien|Attention|suite)\b")


class TestCommande(Projet):
    def test_socle_roadmap_et_ses_options(self):
        self.poser("B-0001", titre="Ajouter triple")
        self.poser("T-0001", "besoin : B-0001", titre="Écrire triple")
        self.poser("L-0001", "après : T-0001", "en cours", titre="Le premier lot")
        self.poser("JA-0001", "après : B-0001", titre="Le premier jalon")
        self.commiter("backlog")
        code, sortie = self.socle("roadmap")
        self.assertEqual(code, 0, sortie)
        lignes = sortie.splitlines()
        self.assertEqual(lignes[0], suite.entete(self.racine.name, datetime.date.today()))
        for ligne in (" ▶ Le premier lot (L-0001)", "   besoin : Ajouter triple (B-0001)",
                      "     reste : Écrire triple (T-0001)",
                      "1. [0/1] Le premier jalon (JA-0001)", "         ▶ Ajouter triple (B-0001)"):
            self.assertIn(ligne, lignes)
        code, sortie = self.socle("roadmap", "--format", "markdown", "--all")
        self.assertEqual(code, 0, sortie)
        self.assertTrue(sortie.startswith(f"```text\n{suite.entete(self.racine.name, datetime.date.today())}\n"),
                        sortie)
        self.assertIn("\n         ▶ Ajouter triple (B-0001)\n", sortie)
        self.assertTrue(sortie.rstrip("\n").endswith("\n```"), sortie)
        with contextlib.redirect_stdout(io.StringIO()) as flux:
            self.assertEqual(cli.cmd_roadmap(argparse.Namespace(root=str(self.racine), format="text", all=True)), 0)
        self.assertIn("1. [0/1] Le premier jalon (JA-0001)\n", flux.getvalue())
        code, sortie = self.socle("roadmap", "--format", "markdown")
        self.assertEqual(suite.rendre(self.projet(), "markdown").rstrip("\n"), sortie.rstrip("\n"))

    def test_l_option_by_et_les_anciens_formats_sont_refuses(self):
        """C-0019 : aucune compatibilité avec l'ancien appel ; `--by` est une
        option inconnue."""
        for args in (["--by", "batch"], ["--by", "need"], ["--format", "compact"]):
            erreur = io.StringIO()
            with contextlib.redirect_stderr(erreur), self.assertRaises(SystemExit) as refus:
                cli.main(["--root", str(self.racine), "roadmap", *args])
            self.assertEqual(refus.exception.code, 2, args)
            self.assertIn(args[0], erreur.getvalue())

    def projet(self):
        from socle import config

        return config.Projet.charger(self.racine)


ETAPE_DE_LA_CI = 'run: python3 .socle/socle roadmap --format markdown >> "$GITHUB_STEP_SUMMARY"'


class TestDeclencheurs(Projet):
    """T-0058 : le guide, les instructions du socle, la clôture d'un lot, le
    résumé de la CI, une ligne de l'état, et le skill de l'atelier qui mène
    un lot ; T-0208 : ce qui les dit suit la forme unique."""

    def test_l_etat_a_une_ligne_qui_renvoie_a_la_commande(self):
        from socle import state as etat

        mem = backlog_d_essai()
        bloc = etat._backlog(mem)[0][1]
        self.assertTrue(bloc[0].startswith("backlog  : "))
        self.assertEqual(bloc[1], "  la suite : `python3 .socle/socle roadmap`")
        with messages.dans("en"):
            self.assertEqual(etat._backlog(mem)[0][1][1], "  the roadmap: `python3 .socle/socle roadmap`")
        self.commiter("base")
        from socle import config

        self.assertIn("\n  la suite : `python3 .socle/socle roadmap`\n",
                      etat.calculer(config.Projet.charger(self.racine), contenus=False))

    def test_la_ci_posee_ecrit_le_rendu_markdown_dans_le_resume_de_son_execution(self):
        import os
        import subprocess
        from socle.templates import gabarit

        for lg in ("fr", "en"):
            ci = gabarit("socle.yml" if lg == "fr" else "socle.en.yml", lg)
            etape = ci.index(ETAPE_DE_LA_CI)
            # Une étape qui informe : son échec ne fait pas échouer la CI.
            self.assertIn("continue-on-error: true\n        " + ETAPE_DE_LA_CI, ci, lg)
            # Avant la mémoire privée : rien de privé n'entre dans le résumé.
            self.assertLess(etape, ci.index("private recover"), lg)
            self.assertLess(etape, ci.index("socle ci --base"), lg)
        # Posée dans le projet, elle écrit la suite, en Markdown, dans le résumé.
        posee = (self.racine / ".github/workflows/socle.yml").read_text(encoding="utf-8")
        self.assertIn(ETAPE_DE_LA_CI, posee)
        self.poser("B-0001", titre="Ajouter triple")
        self.poser("T-0001", "besoin : B-0001", titre="Écrire triple")
        self.poser("L-0001", "après : T-0001", "en cours", titre="Le premier lot")
        self.commiter("backlog")
        resume = self.racine.parent / f"{self.racine.name}-resume.md"
        self.addCleanup(resume.unlink, missing_ok=True)
        commande = ETAPE_DE_LA_CI.removeprefix("run: ")
        env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
        sortie = subprocess.run(["bash", "-c", commande], cwd=self.racine, capture_output=True, text=True,
                                env={**env, "GITHUB_STEP_SUMMARY": str(resume)})
        self.assertEqual(sortie.returncode, 0, sortie.stderr)
        texte = resume.read_text(encoding="utf-8")
        self.assertTrue(texte.startswith(f"```text\n{suite.entete(self.racine.name, datetime.date.today())}\n"),
                        texte)
        self.assertIn("\n ▶ Le premier lot (L-0001)\n   besoin : Ajouter triple (B-0001)\n"
                      "     reste : Écrire triple (T-0001)\n", texte)
        self.assertFalse([l for l in texte.splitlines() if l.startswith("|")], texte)

    def test_le_skill_socle_batch_colle_le_format_compact_au_recap_de_la_cloture(self):
        from socle import installer as installeur

        attendus = {"fr": "le récap de la clôture colle la sortie de `python3 .socle/socle roadmap`",
                    "en": "the closing recap pastes the output of `python3 .socle/socle roadmap`"}
        for lg, phrase in attendus.items():
            installeur.poser_skills(self.racine, lg)
            texte = (self.racine / installeur.SKILLS / "socle-batch" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(phrase, " ".join(texte.split()), lg)
            self.assertLessEqual(len(texte.encode("utf-8")), 10000, lg)
            self.assertNotIn("--format markdown", texte, lg)

    def test_les_instructions_disent_de_coller_le_format_detaille_quand_l_humain_demande_la_suite(self):
        from socle.templates import gabarit

        attendus = {"fr": "la suite, quand l'humain la demande : coller dans la réponse la sortie de "
                          "`python3 .socle/socle roadmap --format markdown`",
                    "en": "the roadmap, when the human asks for it: paste into the reply the output of "
                          "`python3 .socle/socle roadmap --format markdown`"}
        for lg, phrase in attendus.items():
            self.assertIn(phrase, " ".join(gabarit("AGENTS.md", lg).split()), lg)
        agents = " ".join((self.racine / "AGENTS.md").read_text(encoding="utf-8").split())
        self.assertIn(attendus["fr"], agents)

    def test_le_guide_le_dit_en_une_phrase(self):
        from socle import cli as ligne

        for nom, phrase in (("HELP.md", "La suite entière, d'un coup d'œil, se lit dans un terminal par "
                                        "`python3 .socle/socle roadmap`"),
                            ("HELP.en.md", "The whole roadmap, at a glance, reads in a terminal with "
                                           "`python3 .socle/socle roadmap`")):
            guide = (Path(ligne.__file__).parent / nom).read_text(encoding="utf-8")
            self.assertIn(phrase, " ".join(guide.split()), nom)
            self.assertIn("| `roadmap` |", guide, nom)

    def test_le_guide_montre_la_forme_et_une_note_de_version_le_dit(self):
        """Le guide, en français et en anglais, montre la forme sur la
        maquette, ses identifiants écrits `X-NNNN`, dit que `--format
        markdown` la met dans un bloc de code, et ne parle plus de deux
        formats ; la note de version du changement, 2026-11-27-b, le dit, et
        que `--by` n'existe plus."""
        paquet = Path(suite.__file__).parent
        phrases = {"fr": "Avec `--format markdown`, le même texte vient dans un bloc de code",
                   "en": "With `--format markdown`, the same text comes in a code block"}
        for lg, nom in (("fr", "HELP.md"), ("en", "HELP.en.md")):
            guide = (paquet / nom).read_text(encoding="utf-8")
            s = suite.calculer(backlog_de_la_maquette(lg))
            with messages.dans(lg):
                terminal = suite.texte(s, nom="Fou", jour=JOUR)
            with self.subTest(lg):
                self.assertIn(f"```text\n{sans_numeros(terminal)}\n```", guide)
                self.assertIn(phrases[lg], " ".join(guide.split()))
                self.assertNotIn("```markdown", guide)
                for ancien in ("--by need", "--by batch", "format compact", "format détaillé", "compact format",
                               "detailed format", "Légende", "Key:"):
                    self.assertNotIn(ancien, guide)
        for nom, titre in (("CHANGES.md", "La feuille de route en une seule forme"),
                           ("CHANGES.en.md", "The roadmap in a single form")):
            notes = (paquet / nom).read_text(encoding="utf-8")
            note = next(n for n in notes.split("\n## ")[1:] if n.startswith("2026-11-27-b "))
            self.assertIn(titre, note.splitlines()[0], nom)
            self.assertIn("socle roadmap", " ".join(note.split()), nom)
            self.assertIn("--by", note, nom)

    def test_format_md_ne_prend_plus_la_feuille_de_route_pour_exemple_de_consigne(self):
        """T-0208 : l'exemple de consigne de `FORMAT.md` contredisait la
        section installée ; son paragraphe sur `socle roadmap` dit la forme
        unique."""
        texte = " ".join((Path(suite.__file__).parent / "FORMAT.md").read_text(encoding="utf-8").split())
        self.assertNotIn("format court", texte)
        self.assertNotIn("La roadmap demandée", texte)
        self.assertIn("`socle roadmap` en tire la suite", texte)
        self.assertIn("seul le premier déplié en ses besoins", texte)

    def test_le_skill_de_l_atelier_l_appelle_a_l_annonce_et_a_la_cloture_d_un_lot(self):
        racine = Path(__file__).resolve().parent.parent
        skill = " ".join((racine / ".claude/skills/delegate-lot/SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn("À l'annonce d'un lot, puis à sa clôture, lancer `python3 .socle/socle roadmap`", skill)
        self.assertIn("« Tu implémentes une tâche du socle dans ton worktree du dépôt memory.", skill)
        self.assertNotRegex(skill, r"\bsujets?\b")

    def test_le_skill_de_l_atelier_borne_la_revue_d_un_lot_du_hook_sans_liste_des_formes(self):
        # T-0061 (ADR-0099) : la règle d'ADR-0098, qui remplace ADR-0082, pour la revue d'un lot du hook ; la
        # liste des formes que le hook ne juge pas ne vit plus dans l'atelier.
        racine = Path(__file__).resolve().parent.parent
        skill = " ".join((racine / ".claude/skills/delegate-lot/SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn("ne s'ouvre que sur une preuve (ADR-0098). Son relecteur ne cherche pas de contournements : "
                      "il vérifie que le lot ne casse rien de ce qui marchait", skill)
        self.assertIn("un contournement qu'il trouve s'écarte d'office, sans entrée au backlog", skill)
        self.assertNotIn("ADR-0082", skill)
        self.assertNotIn("formes connues", skill)

    def test_le_skill_de_l_atelier_fait_fusionner_la_branche_de_passation_et_suit_le_circuit_court(self):
        # T-0102 (B-0293) : une branche de passation jamais fusionnée restait sur GitHub sans que l'état la
        # signale ; T-0093 (D-0134) : l'atelier dit son circuit court.
        racine = Path(__file__).resolve().parent.parent
        skill = " ".join((racine / ".claude/skills/delegate-lot/SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn("À l'intégration d'une passation, après l'application de ses correctifs (`git am`), la "
                      "branche de passation se fusionne dans la branche de travail (`git merge --no-edit`), puis "
                      "son dossier se retire", skill)
        self.assertIn("L'orchestrateur implémente, sauf quand un sous-agent paie, selon `socle-batch`", skill)

    def test_les_skills_font_coller_le_compact_dans_un_bloc_de_code_hors_des_deux_lignes_du_recap(self):
        # T-0091 (ADR-0089) : collé en texte, le compact et sa ligne « Ensuite : » tiendraient lieu de celle du
        # récap ; dans un bloc de code, le hook de fin de tour ne les lit pas.
        from socle import installer as installeur

        attendus = {"fr": "colle la sortie de `python3 .socle/socle roadmap` dans un bloc de code",
                    "en": "pastes the output of `python3 .socle/socle roadmap` in a code block"}
        for lg, phrase in attendus.items():
            installeur.poser_skills(self.racine, lg)
            texte = (self.racine / installeur.SKILLS / "socle-batch" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(phrase, " ".join(texte.split()), lg)
        racine = Path(__file__).resolve().parent.parent
        skill = " ".join((racine / ".claude/skills/delegate-lot/SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn("lancer `python3 .socle/socle roadmap` et en coller la sortie dans la réponse, dans un bloc de "
                      "code", skill)


if __name__ == "__main__":
    unittest.main()
