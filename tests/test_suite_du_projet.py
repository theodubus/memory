"""B-0274 (D-0127) : la suite du projet d'un coup d'œil, `socle roadmap` —
les jalons et leurs besoins clos, les lots dans leur ordre d'exécution et
leurs tâches, les besoins, ce qui n'est dans aucun lot ; le format compact
et le format détaillé, par lot et par besoin ; l'alerte de deux lots qui
attendent le même lot sans ordre entre eux."""

import argparse
import contextlib
import io
import re
import types
import unittest
from pathlib import Path
from unittest import mock

from socle import cli, memory as memoire, messages, roadmap as suite
from tests.test_structure import Projet, entree, memoire_de


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


# Les titres du backlog des exemples validés, dans chaque langue ; une
# entrée qui n'y est pas garde celui de `entree`.
TITRES = {
    "fr": {"JA-0005": "Fini avant les nouvelles fonctions : les lots qui restent",
           "JA-0002": "Le pilote équipé : son installation",
           "L-0013": "Structure du backlog, chantier en rond : les deux suites",
           "L-0012": "Durée de la vérification", "L-0014": "Suite de la structure du backlog",
           "T-0046": "La structure en quatre formes : besoin, tâche, lot, jalon",
           "T-0047": "Le format de la mémoire", "T-0048": "La forme exotique dans la liste du guide",
           "T-0043": "Mesurer la durée de chaque étape",
           "T-0044": "La suite sur plusieurs cœurs : un lanceur parallèle",
           "B-0265": "Un mot pour une chose dans le backlog", "B-0257": "La vérification dure trop"},
    "en": {"JA-0005": "Done before the new features: the remaining batches",
           "JA-0002": "The pilot equipped: its installation",
           "L-0013": "Backlog structure, going in circles: the two follow-ups",
           "L-0012": "Duration of the verification", "L-0014": "Rest of the backlog structure",
           "T-0046": "The structure in four forms: need, task, batch, milestone",
           "T-0047": "The memory format", "T-0048": "The exotic form in the guide's list",
           "T-0043": "Measure the duration of each step",
           "T-0044": "The suite on several cores: a parallel runner",
           "B-0265": "One word for one thing in the backlog", "B-0257": "The verification takes too long"},
}
CACHES = range(6, 11)


def titree(ident: str, titre: str, statut: str = "ouvert", meta: str = "") -> tuple[str, str]:
    """Une entrée du backlog sous son titre."""
    chemin, texte = entree(ident, statut, meta)
    return chemin, texte.replace(f"L'entrée {ident}", titre, 1)


def backlog_de_l_exemple(lg: str = "fr") -> memoire.Memoire:
    """Le backlog des deux exemples que Théo a validés (T-0088, D-0127) : un
    jalon dont le lot en cours et les deux suivants se lisent tâche par tâche
    et cinq autres lots se résument ; un jalon sans lot, venu avant lui ;
    des besoins sans tâche, un bloqué, deux hors des jalons. Chaque état et
    chaque priorité d'une tâche y sont."""
    def e(ident: str, statut: str = "ouvert", meta: str = "") -> tuple[str, str]:
        defaut = f"L'entrée {ident}" if lg == "fr" else f"Entry {ident}"
        return titree(ident, TITRES[lg].get(ident, defaut), statut, meta)

    return memoire_de(
        e("B-0257", meta="priorité : haute"), e("B-0264", "fait"), e("B-0265"), e("B-0270"), e("B-0179", "bloqué"),
        e("B-0271"), e("B-0126"), e("B-0055"), e("B-0101"), *(e(f"B-03{n:02d}") for n in CACHES),
        e("T-0046", "fait", "besoin : B-0265"), e("T-0047", "fait", "besoin : B-0265"), e("T-0048", meta="besoin : B-0270"),
        e("T-0043", meta="besoin : B-0257"), e("T-0044", meta="besoin : B-0257 · après : T-0043"),
        e("T-0049", "abandonné", "besoin : B-0265"), e("T-0050", "bloqué", "besoin : B-0265"),
        e("T-0051", meta="besoin : B-0265 · priorité : basse"), e("T-0052", meta="besoin : B-0265"),
        e("T-0053", meta="besoin : B-0265 · après : T-0052"),
        *(e(f"T-0{c}{n:02d}", meta=f"besoin : B-03{n:02d}") for n in CACHES for c in (1, 2)),
        e("L-0013", "en cours", "après : T-0046, T-0047, T-0048"),
        e("L-0012", meta="après : L-0013, T-0043, T-0044"),
        e("L-0014", meta="après : L-0012, T-0049, T-0050, T-0051, T-0052, T-0053"),
        *(e(f"L-00{n:02d}", meta=f"après : {'L-0014' if n == 6 else f'L-00{n - 1:02d}'}, T-01{n:02d}, T-02{n:02d}")
          for n in CACHES),
        e("JA-0002", meta="après : B-0126"),
        e("JA-0005", meta="après : B-0257, B-0264, B-0265, B-0270, B-0179, B-0271, "
                          + ", ".join(f"B-03{n:02d}" for n in CACHES)),
    )


def tableaux(md: str) -> list[tuple[str, list[str], str]]:
    """Chaque tableau d'un texte Markdown : (la ligne d'avant, ses lignes, la
    ligne d'après)."""
    lignes, res, k = md.splitlines(), [], 0
    while k < len(lignes):
        if not lignes[k].startswith("|"):
            k += 1
            continue
        debut = k
        while k < len(lignes) and lignes[k].startswith("|"):
            k += 1
        res.append((lignes[debut - 1] if debut else "", lignes[debut:k], lignes[k] if k < len(lignes) else ""))
    return res


def sans_numeros(texte: str) -> str:
    """Un texte, ses identifiants écrits `X-NNNN`, comme le guide les montre :
    il ne cite aucun identifiant d'une mémoire."""
    return memoire.ID_RE.sub(lambda m: f"{m.group('type')}-NNNN", texte)


class TestCalcul(unittest.TestCase):
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
        attendu = "!! ordre ambigu : L-0002 et L-0003 attendent tous deux L-0001, sans ordre entre eux — que l'un " \
                  "attende l'autre"
        self.assertIn(attendu, suite.texte(s).splitlines())
        self.assertIn("> **!!** " + attendu.removeprefix("!! "), suite.markdown(s).splitlines())
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


class TestFormats(unittest.TestCase):
    def test_le_format_compact_une_ligne_par_jalon_et_par_lot_le_lot_en_cours_marque(self):
        s = suite.calculer(backlog_d_essai())
        self.assertEqual(suite.texte(s).splitlines(), [
            "La suite du projet, calculée depuis le backlog — détaillée : `python3 .socle/socle roadmap --format "
            "markdown`",
            "jalons, dans leur ordre :",
            "  JA-0001 — L'entrée JA-0001 : 0 besoin(s) clos sur 2 — le prochain",
            "  JA-0002 — L'entrée JA-0002 : 0 besoin(s) clos sur 1",
            "lots, dans leur ordre (▶ en cours) :",
            "▶ L-0001 — L'entrée L-0001 : 1 tâche(s) close(s) sur 2 · 1 en cours",
            "  L-0002 — L'entrée L-0002 : 0 tâche(s) close(s) sur 1 · 1 qui attend(ent) · 1 demande(s) sans réponse",
            "  L-0003 — L'entrée L-0003 : 0 tâche(s) close(s) sur 2 · 1 prête(s), 1 qui attend(ent)",
            "hors des lots : 1 tâche(s) ouverte(s), 1 besoin(s) à découper, 1 à fermer, 1 entrée(s) bloquée(s), 1 pour "
            "l'humain, 1 demande(s) en attente",
            "après les jalons : 4 besoin(s) ouvert(s) dans aucun jalon",
        ])

    def test_le_format_compact_ne_nomme_aucune_demande(self):
        """Collé dans le récap de la clôture d'un lot, il ne cite pas une
        demande en attente sans son lien, que le hook de fin de tour
        refuserait."""
        s = suite.calculer(backlog_d_essai())
        for par in suite.LECTURES:
            self.assertNotIn("D-0001", suite.texte(s, par))
        self.assertIn("D-0001", suite.markdown(s))

    def test_le_format_compact_par_besoin(self):
        lignes = suite.texte(suite.calculer(backlog_d_essai()), "need").splitlines()
        debut = lignes.index("besoins, dans l'ordre des lots :")
        self.assertEqual(lignes[debut + 1:debut + 5], [
            "  B-0001 — L'entrée B-0001 : 1 tâche(s) close(s) sur 2 — lot(s) : L-0001",
            "  B-0002 — L'entrée B-0002 : 0 tâche(s) close(s) sur 1 — lot(s) : L-0002",
            "  B-0003 — L'entrée B-0003 : 0 tâche(s) close(s) sur 2 — lot(s) : L-0003",
            "  B-0005 — L'entrée B-0005 : 0 tâche(s) close(s) sur 1 — dans aucun lot",
        ])
        self.assertFalse(any(l.startswith("lots, dans leur ordre") for l in lignes))

    def test_le_format_detaille_par_lot(self):
        s = suite.calculer(backlog_d_essai())
        lignes = suite.markdown(s).splitlines()
        self.assertEqual(lignes[0], "## La suite du projet")
        for ligne in ("- **JA-0001** — L'entrée JA-0001 : 0 besoin(s) clos sur 2 — le prochain",
                      "#### ▶ L-0001 — L'entrée L-0001 — en cours",
                      "1 tâche(s) close(s) sur 2 · 1 en cours",
                      "- T-0001 — L'entrée T-0001 · besoin B-0001 · priorité haute · en cours",
                      "- T-0002 — L'entrée T-0002 · besoin B-0001 · priorité haute · faite",
                      "#### L-0002 — L'entrée L-0002",
                      "0 tâche(s) close(s) sur 1 · 1 qui attend(ent) · attend D-0001",
                      "- T-0003 — L'entrée T-0003 · besoin B-0002 · attend : T-0001",
                      "- T-0004 — L'entrée T-0004 · besoin B-0003 · attend : D-0001",
                      "### Hors des lots",
                      "- **Tâches dans aucun lot**",
                      "  - T-0006 — L'entrée T-0006 · besoin B-0005 · prête",
                      "  - B-0004 — L'entrée B-0004",
                      "  - B-0008 — L'entrée B-0008",
                      "  - B-0006 — L'entrée B-0006",
                      "  - T-0005 — L'entrée T-0005",
                      "  - D-0001 — Une demande",
                      "- **Après les jalons**, dans aucun jalon : B-0004, B-0005, B-0006, B-0008"):
            self.assertIn(ligne, lignes)
        self.assertNotIn("#### Les lots suivants", lignes)

    def test_le_format_detaille_suit_le_lot_en_cours_et_les_deux_suivants_all_les_suit_tous(self):
        mem = memoire_de(*(entree(f"T-000{n}", meta="besoin : B-0001") for n in range(1, 6)), entree("B-0001"),
                         entree("L-0001", "en cours", meta="après : T-0001"),
                         *(entree(f"L-000{n}", meta=f"après : L-000{n - 1}, T-000{n}") for n in range(2, 6)))
        s = suite.calculer(mem)
        self.assertEqual([lot.entree.id for lot in suite.detailles(s, tout=False)], ["L-0001", "L-0002", "L-0003"])
        self.assertEqual(len(suite.detailles(s, tout=True)), 5)
        defaut = suite.markdown(s).splitlines()
        self.assertEqual([l for l in defaut if l.startswith("#### ")],
                         ["#### ▶ L-0001 — L'entrée L-0001 — en cours", "#### L-0002 — L'entrée L-0002",
                          "#### L-0003 — L'entrée L-0003", "#### Les lots suivants"])
        self.assertIn("- L-0004 — L'entrée L-0004 : 0 tâche(s) close(s) sur 1 · 1 prête(s)", defaut)
        self.assertNotIn("- T-0004 — L'entrée T-0004 · besoin B-0001 · prête", defaut)
        tout = suite.markdown(s, tout=True).splitlines()
        self.assertEqual(len([l for l in tout if l.startswith("#### L-")]), 4)
        self.assertIn("- T-0005 — L'entrée T-0005 · besoin B-0001 · prête", tout)
        self.assertNotIn("#### Les lots suivants", tout)

    def test_le_format_detaille_par_besoin_chaque_tache_avec_son_lot(self):
        lignes = suite.markdown(suite.calculer(backlog_d_essai()), "need").splitlines()
        for ligne in ("### Besoins, dans l'ordre des lots",
                      "#### B-0001 — L'entrée B-0001 : 1 tâche(s) close(s) sur 2 — lot(s) : L-0001",
                      "- T-0001 — L'entrée T-0001 · lot L-0001 · priorité haute · en cours",
                      "- T-0004 — L'entrée T-0004 · lot L-0003 · attend : D-0001",
                      "#### Les autres besoins",
                      "- B-0005 — L'entrée B-0005 : 0 tâche(s) close(s) sur 1 — dans aucun lot"):
            self.assertIn(ligne, lignes)
        self.assertFalse(any(l.startswith("### Lots") for l in lignes))
        tout = suite.markdown(suite.calculer(backlog_d_essai()), "need", tout=True).splitlines()
        self.assertIn("- T-0006 — L'entrée T-0006 · dans aucun lot · prête", tout)
        self.assertNotIn("#### Les autres besoins", tout)

    def test_le_format_detaille_donne_le_lien_de_chaque_demande_et_de_ce_qui_revient_a_l_humain(self):
        s = suite.calculer(backlog_d_essai())
        url = "https://github.com/o/r/blob/abc/{}"
        with mock.patch("socle.links.lien", side_effect=lambda projet, chemin: (url.format(chemin), "")):
            liens = suite.liens_pour_l_humain(types.SimpleNamespace(), s)
        self.assertEqual(liens, {"T-0005": url.format("memory/backlog/T-0005-essai.md"),
                                 "D-0001": url.format("memory/requests/D-0001-essai.md")})
        lignes = suite.markdown(s, liens=liens).splitlines()
        self.assertIn(f"  - [D-0001 — Une demande]({url.format('memory/requests/D-0001-essai.md')})", lignes)
        self.assertIn(f"  - [T-0005 — L'entrée T-0005]({url.format('memory/backlog/T-0005-essai.md')})", lignes)
        with mock.patch("socle.links.lien", side_effect=RuntimeError("hors ligne")):
            self.assertEqual(suite.liens_pour_l_humain(types.SimpleNamespace(), s), {})

    def test_un_backlog_sans_lot_ni_jalon(self):
        s = suite.calculer(memoire_de(entree("B-0001")))
        self.assertIn("ni jalon ni lot au backlog", suite.texte(s))
        self.assertIn("Ni jalon ni lot au backlog.", suite.markdown(s))
        self.assertEqual(s.sans_jalon, [])

    def test_en_anglais(self):
        s = suite.calculer(backlog_d_essai())
        with messages.dans("en"):
            lignes = suite.texte(s).splitlines()
            detail = suite.markdown(s, "need")
        self.assertEqual(lignes[0], "The project's roadmap, computed from the backlog — detailed: `python3 "
                                    ".socle/socle roadmap --format markdown`")
        self.assertIn("▶ L-0001 — L'entrée L-0001: 1 task(s) closed out of 2 · 1 in progress", lignes)
        self.assertIn("## The project's roadmap", detail)
        self.assertIn("- T-0004 — L'entrée T-0004 · batch L-0003 · waiting: D-0001", detail)
        for ligne in lignes + detail.splitlines():
            self.assertNotRegex(ligne, r"\b(?:tâche|besoin|lot|jalon)s?\b")


class TestLesFormatsValides(unittest.TestCase):
    """T-0088 (D-0127) : les deux formats que Théo a validés, recopiés au
    backlog mot pour mot. Le détaillé, un tableau Markdown par lot, l'état
    de chaque tâche et sa priorité en symboles ; lu par besoin, le tableau
    des tâches de chaque besoin, avec le lot de chacune ; le compact aligné
    en colonnes, le lot en cours marqué ▶, fini par « Hors lot » et
    « Ensuite »."""

    def test_le_format_detaille_un_tableau_par_lot_comme_l_exemple_valide(self):
        s = suite.calculer(backlog_de_l_exemple())
        md = suite.markdown(s)
        lignes = md.splitlines()
        self.assertEqual(lignes[:5], [
            "## La suite du projet", "",
            "Calculée depuis le backlog par `python3 .socle/socle roadmap --format markdown` : rien n'y est écrit "
            "à la main.", "",
            "Légende : ✓ faite · ▶ en cours · ○ prête · ⏳ attend · ✗ bloquée · ⊘ abandonnée · ↑ priorité haute · "
            "↓ priorité basse"])
        debut = lignes.index("### JA-0005 — Fini avant les nouvelles fonctions · 1/11 besoins clos")
        self.assertEqual(lignes[debut:debut + 41], [
            "### JA-0005 — Fini avant les nouvelles fonctions · 1/11 besoins clos", "",
            "**1. L-0013 — Structure du backlog, chantier en rond** · en cours · 2/3", "",
            "| | Tâche | Besoin | |",
            "| --- | --- | --- | --- |",
            "| ✓ | T-0046 | B-0265 | La structure en quatre formes |",
            "| ✓ | T-0047 | B-0265 | Le format de la mémoire |",
            "| ○ | T-0048 | B-0270 | La forme exotique dans la liste du guide |", "",
            "**2. L-0012 — Durée de la vérification** · 0/2", "",
            "| | Tâche | Besoin | |",
            "| --- | --- | --- | --- |",
            "| ○ | T-0043 | B-0257 ↑ | Mesurer la durée de chaque étape |",
            "| ⏳ | T-0044 | B-0257 ↑ | La suite sur plusieurs cœurs · attend T-0043 |", "",
            "**3. L-0014 — Suite de la structure du backlog** · 1/5", "",
            "| | Tâche | Besoin | |",
            "| --- | --- | --- | --- |",
            "| ⊘ | T-0049 | B-0265 | L'entrée T-0049 |",
            "| ✗ | T-0050 | B-0265 | L'entrée T-0050 |",
            "| ○ | T-0051 | B-0265 ↓ | L'entrée T-0051 |",
            "| ○ | T-0052 | B-0265 | L'entrée T-0052 |",
            "| ⏳ | T-0053 | B-0265 | L'entrée T-0053 · attend T-0052 |", "",
            "- **4.** L-0006 — L'entrée L-0006 · 0/2",
            "- **5.** L-0007 — L'entrée L-0007 · 0/2",
            "- **6.** L-0008 — L'entrée L-0008 · 0/2",
            "- **7.** L-0009 — L'entrée L-0009 · 0/2",
            "- **8.** L-0010 — L'entrée L-0010 · 0/2", "",
            "(`--all` pour tout le détail)", "",
            "### Ensuite", "",
            "- JA-0002 — Le pilote équipé · 0/1 besoins clos : B-0126", "",
            "### Hors des lots", ""])
        # Hors des lots, chaque section en tableau de même forme.
        self.assertIn("**Besoins à découper en tâches**\n\n| | Besoin | |\n| --- | --- | --- |\n"
                      "| ○ | B-0126 | L'entrée B-0126 |\n", md)
        self.assertIn("**Bloqués**\n\n| | Entrée | |\n| --- | --- | --- |\n| ✗ | B-0179 | L'entrée B-0179 |\n", md)
        self.assertIn("- **Après les jalons**, dans aucun jalon : B-0055, B-0101", lignes)
        # `--all` : chaque lot a son tableau, aucun ne se résume.
        tout = suite.markdown(s, tout=True)
        self.assertIn("**8. L-0010 — L'entrée L-0010** · 0/2\n\n| | Tâche | Besoin | |\n| --- | --- | --- | --- |\n"
                      "| ○ | T-0110 | B-0310 | L'entrée T-0110 |\n| ○ | T-0210 | B-0310 | L'entrée T-0210 |\n", tout)
        self.assertNotIn("(`--all` pour tout le détail)", tout)
        self.assertEqual(len(tableaux(tout)), 8 + 2)

    def test_un_lot_arrete_nomme_les_demandes_qu_il_attend_dans_le_detaille(self):
        lignes = suite.markdown(suite.calculer(backlog_d_essai())).splitlines()
        self.assertIn("**2. L-0002 — L'entrée L-0002** · attend D-0001 · 0/1", lignes)
        self.assertIn("| ⏳ | T-0004 | B-0003 | L'entrée T-0004 · attend D-0001 |", lignes)
        # Bloqué, il le dit à la place de « en cours ».
        bloque = memoire_de(entree("B-0001"), entree("T-0001", meta="besoin : B-0001"),
                            entree("L-0001", "bloqué", meta="après : T-0001"))
        s = suite.calculer(bloque)
        self.assertIn("**1. L-0001 — L'entrée L-0001** · bloqué · 0/1", suite.markdown(s).splitlines())
        self.assertIn(" L-0001  L'entrée L-0001  0/1  bloqué", suite.texte(s).splitlines()[0])

    def test_chaque_tableau_markdown_est_bien_forme(self):
        """Une ligne vide avant et après, sa ligne de séparation, sans
        laquelle GitHub ne le dessine pas, et autant de cellules à chaque
        ligne ; la barre d'un titre s'échappe, un titre long se coupe."""
        long = "Un titre sans deux-points qui dépasse de loin la largeur de la colonne des titres du tableau"
        mem = memoire_de(entree("B-0001"), titree("T-0001", "Le hook juge find | xargs rm : la suite", meta="besoin : B-0001"),
                         titree("T-0002", long, meta="besoin : B-0001"),
                         entree("L-0001", "en cours", meta="après : T-0001, T-0002"))
        lignes = suite.markdown(suite.calculer(mem)).splitlines()
        self.assertIn("| ○ | T-0001 | B-0001 | Le hook juge find \\| xargs rm |", lignes)
        coupe = "Un titre sans deux-points qui dépasse de loin la largeur de la colonne…"
        self.assertIn(f"| ○ | T-0002 | B-0001 | {coupe} |", lignes)
        self.assertLessEqual(len(coupe), suite.TITRE_DETAILLE)
        for nom, s in (("essai", suite.calculer(backlog_d_essai())), ("exemple", suite.calculer(backlog_de_l_exemple())),
                       ("barre", suite.calculer(mem))):
            for par in suite.LECTURES:
                for tout in (False, True):
                    for lg in ("fr", "en"):
                        with messages.dans(lg):
                            md = suite.markdown(s, par, tout)
                        self.assertTrue(tableaux(md), (nom, par))
                        for avant, tableau, apres in tableaux(md):
                            with self.subTest(nom=nom, par=par, tout=tout, lg=lg, tableau=tableau[0]):
                                self.assertEqual((avant, apres), ("", ""))
                                self.assertRegex(tableau[1], r"^\|(?: --- \|)+$")
                                cellules = {len(re.findall(r"(?<!\\)\|", l)) for l in tableau}
                                self.assertEqual(len(cellules), 1, tableau)
                                self.assertTrue(all(l.endswith("|") for l in tableau), tableau)

    def test_lu_par_besoin_chaque_besoin_a_le_tableau_de_ses_taches_et_le_lot_de_chacune(self):
        lignes = suite.markdown(suite.calculer(backlog_de_l_exemple()), "need").splitlines()
        debut = lignes.index("### JA-0005 — Fini avant les nouvelles fonctions · 1/11 besoins clos")
        self.assertEqual(lignes[debut:debut + 35], [
            "### JA-0005 — Fini avant les nouvelles fonctions · 1/11 besoins clos", "",
            "**B-0265 — Un mot pour une chose dans le backlog** · 3/7 · L-0013, L-0014", "",
            "| | Tâche | Lot | |",
            "| --- | --- | --- | --- |",
            "| ✓ | T-0046 | L-0013 | La structure en quatre formes |",
            "| ✓ | T-0047 | L-0013 | Le format de la mémoire |",
            "| ⊘ | T-0049 | L-0014 | L'entrée T-0049 |",
            "| ✗ | T-0050 | L-0014 | L'entrée T-0050 |",
            "| ○ | T-0051 | L-0014 ↓ | L'entrée T-0051 |",
            "| ○ | T-0052 | L-0014 | L'entrée T-0052 |",
            "| ⏳ | T-0053 | L-0014 | L'entrée T-0053 · attend T-0052 |", "",
            "**B-0270 — L'entrée B-0270** · 0/1 · L-0013", "",
            "| | Tâche | Lot | |",
            "| --- | --- | --- | --- |",
            "| ○ | T-0048 | L-0013 | La forme exotique dans la liste du guide |", "",
            "**B-0257 — La vérification dure trop** · 0/2 · L-0012", "",
            "| | Tâche | Lot | |",
            "| --- | --- | --- | --- |",
            "| ○ | T-0043 | L-0012 ↑ | Mesurer la durée de chaque étape |",
            "| ⏳ | T-0044 | L-0012 ↑ | La suite sur plusieurs cœurs · attend T-0043 |", "",
            "- B-0306 — L'entrée B-0306 · 0/2 · L-0006",
            "- B-0307 — L'entrée B-0307 · 0/2 · L-0007",
            "- B-0308 — L'entrée B-0308 · 0/2 · L-0008",
            "- B-0309 — L'entrée B-0309 · 0/2 · L-0009",
            "- B-0310 — L'entrée B-0310 · 0/2 · L-0010", "",
            "(`--all` pour tout le détail)", ""])
        self.assertFalse(any(l.startswith("**1. ") for l in lignes))
        # Une tâche d'aucun lot le dit dans sa cellule ; `--all` détaille chaque besoin.
        tout = suite.markdown(suite.calculer(backlog_d_essai()), "need", tout=True).splitlines()
        self.assertIn("**B-0005 — L'entrée B-0005** · 0/1 · dans aucun lot", tout)
        self.assertIn("| ○ | T-0006 | — | L'entrée T-0006 |", tout)
        self.assertNotIn("(`--all` pour tout le détail)", tout)

    def test_le_format_compact_aligne_en_colonnes_comme_l_exemple_valide(self):
        s = suite.calculer(backlog_de_l_exemple())
        lignes = suite.texte(s).splitlines()
        self.assertEqual(lignes, [
            "JA-0005  Fini avant les nouvelles fonctions        1/11 besoins clos",
            " ▶ L-0013  Structure du backlog, chantier en rond  2/3   en cours",
            "   L-0012  Durée de la vérification                0/2",
            "   L-0014  Suite de la structure du backlog        1/5",
            "   …  L-0006 à L-0010                              0/10",
            "Hors lot : 4 besoins sans tâche · 1 bloqué (B-0179)",
            "Ensuite : JA-0002 Le pilote équipé (B-0126) · puis B-0055, B-0101",
        ])
        # Aligné en caractères, et non en octets : l'avancement de chaque
        # jalon et de chaque lot commence à la même colonne.
        self.assertEqual({re.search(r" (\d+/\d+)", l).start(1) for l in lignes[:5]}, {51})
        # Le jalon du lot en cours vient d'abord, avant celui qui le précède
        # dans l'ordre des jalons, qui n'a pas de lot et va à « Ensuite ».
        self.assertEqual([j.entree.id for j in s.jalons], ["JA-0002", "JA-0005"])
        rangs = suite.groupes(s)
        self.assertEqual([(j.entree.id, [lot.entree.id for lot in lots]) for j, lots in rangs],
                         [("JA-0005", ["L-0013", "L-0012", "L-0014", "L-0006", "L-0007", "L-0008", "L-0009",
                                       "L-0010"])])
        self.assertEqual([j.entree.id for j in suite.ensuite(s, rangs)], ["JA-0002"])
        self.assertEqual(suite.besoins_du_jalon(s.jalons[0]), ["B-0126"])
        # `--all` : chaque lot en sa ligne, aucun résumé.
        tout = suite.texte(s, tout=True).splitlines()
        self.assertIn("   L-0010  L'entrée L-0010                         0/2", tout)
        self.assertFalse(any("…  " in l for l in tout))
        self.assertEqual(len(tout), 11)

    def test_le_format_compact_par_besoin_une_ligne_alignee_par_besoin(self):
        lignes = suite.texte(suite.calculer(backlog_de_l_exemple()), "need").splitlines()
        self.assertEqual(lignes[:4], [
            "JA-0005  Fini avant les nouvelles fonctions       1/11 besoins clos",
            "   B-0265  Un mot pour une chose dans le backlog  3/7  L-0013, L-0014",
            "   B-0270  L'entrée B-0270                        0/1  L-0013",
            "   B-0257  La vérification dure trop              0/2  L-0012"])
        self.assertEqual(lignes[-2:], ["Hors lot : 4 besoins sans tâche · 1 bloqué (B-0179)",
                                       "Ensuite : JA-0002 Le pilote équipé (B-0126) · puis B-0055, B-0101"])
        essai = suite.texte(suite.calculer(backlog_d_essai()), "need").splitlines()
        self.assertEqual(essai[5:7], ["Hors des jalons", "   B-0005  L'entrée B-0005  0/1  dans aucun lot"])

    def test_les_lots_d_aucun_jalon_viennent_apres_sous_hors_des_jalons(self):
        mem = memoire_de(entree("B-0001"), entree("B-0002"),
                         entree("T-0001", meta="besoin : B-0001"), entree("T-0002", meta="besoin : B-0002"),
                         entree("L-0001", "en cours", meta="après : T-0002"),
                         entree("L-0002", meta="après : L-0001, T-0001"), entree("JA-0001", meta="après : B-0001"))
        s = suite.calculer(mem)
        self.assertEqual(suite.texte(s).splitlines(), [
            "JA-0001  L'entrée JA-0001   0/1 besoins clos",
            "   L-0002  L'entrée L-0002  0/1",
            "Hors des jalons",
            " ▶ L-0001  L'entrée L-0001  0/1  en cours",
            "Hors lot : rien",
            "Ensuite : B-0002"])
        lignes = suite.markdown(s).splitlines()
        self.assertLess(lignes.index("**2. L-0002 — L'entrée L-0002** · 0/1"), lignes.index("### Hors des jalons"))
        self.assertLess(lignes.index("### Hors des jalons"), lignes.index("**1. L-0001 — L'entrée L-0001** · en cours · 0/1"))
        # Sans aucun jalon, ni groupe ni « Ensuite ».
        sans = suite.calculer(memoire_de(entree("B-0001"), entree("T-0001", meta="besoin : B-0001"),
                                         entree("L-0001", "en cours", meta="après : T-0001")))
        self.assertEqual(suite.texte(sans).splitlines(), [" ▶ L-0001  L'entrée L-0001  0/1  en cours", "Hors lot : rien"])
        self.assertIn("### Lots, dans leur ordre d'exécution", suite.markdown(sans).splitlines())

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

    def test_en_anglais_la_suite_ne_garde_aucun_mot_francais(self):
        s = suite.calculer(backlog_de_l_exemple("en"))
        essai = suite.calculer(backlog_d_essai())
        with messages.dans("en"):
            compact = suite.texte(s)
            sorties = [compact, suite.texte(s, "need"), suite.texte(s, tout=True), suite.markdown(s),
                       suite.markdown(s, "need"), suite.markdown(s, tout=True),
                       *(x.replace("L'entrée", "").replace("Une demande", "")
                         for x in (suite.texte(essai), suite.markdown(essai), suite.markdown(essai, "need", tout=True)))]
        self.assertEqual(compact.splitlines(), [
            "JA-0005  Done before the new features           1/11 needs closed",
            " ▶ L-0013  Backlog structure, going in circles  2/3   in progress",
            "   L-0012  Duration of the verification         0/2",
            "   L-0014  Rest of the backlog structure        1/5",
            "   …  L-0006 to L-0010                          0/10",
            "Outside the batches: 4 needs with no task · 1 blocked (B-0179)",
            "Next: JA-0002 The pilot equipped (B-0126) · then B-0055, B-0101"])
        self.assertIn("| | Task | Need | |", sorties[3])
        self.assertIn("| | Task | Batch | |", sorties[4])
        self.assertIn("Key: ✓ done · ▶ in progress · ○ ready · ⏳ waiting · ✗ blocked · ⊘ abandoned · ↑ high priority "
                      "· ↓ low priority", sorties[3])
        for sortie in sorties:
            self.assertNotRegex(sortie, r"[àâçéèêëîïôûùœ«»]")
            self.assertNotRegex(sortie, r"\b(?:tâches?|besoins?|lots?|jalons?|attend|clos|Hors|Ensuite|puis|rien|"
                                        r"aucun|Légende|détail|bloqués?|demandes?)\b")

    def test_le_guide_montre_les_deux_formats_et_une_note_de_version_le_dit(self):
        """Le guide, en français et en anglais, montre la sortie des deux
        formats sur le backlog des exemples, ses identifiants écrits
        `X-NNNN` ; la note de version la plus récente le dit, et le prompt
        de mise à jour de chess le reprend."""
        paquet = Path(suite.__file__).parent
        for lg, nom in (("fr", "HELP.md"), ("en", "HELP.en.md")):
            guide = (paquet / nom).read_text(encoding="utf-8")
            s = suite.calculer(backlog_de_l_exemple(lg))
            with messages.dans(lg):
                compact, md = suite.texte(s), suite.markdown(s)
            with self.subTest(lg):
                self.assertIn(f"```text\n{sans_numeros(compact)}\n```", guide)
                lignes = md.splitlines()
                # De la légende au tableau du deuxième lot.
                extrait = lignes[4:next(k for k, l in enumerate(lignes) if l.startswith("**3. ")) - 1]
                self.assertIn("```markdown\n" + sans_numeros("\n".join(extrait)) + "\n", guide)
        for nom, titre in (("CHANGES.md", "La suite du projet aux formats validés"),
                           ("CHANGES.en.md", "The project's roadmap in the approved formats")):
            notes = (paquet / nom).read_text(encoding="utf-8")
            premiere = notes[notes.index("\n## "):].split("\n## ")[1]
            self.assertIn(titre, premiere.splitlines()[0], nom)
            self.assertIn("socle roadmap", " ".join(premiere.split()), nom)
        prompt = Path(__file__).resolve().parent.parent / "docs/fabrication/chess/prompt-mise-a-jour.md"
        texte = " ".join(prompt.read_text(encoding="utf-8").split())
        self.assertIn("17. La suite du projet se lit désormais en colonnes et en tableaux", texte)


class TestCommande(Projet):
    def test_socle_roadmap_et_ses_options(self):
        self.poser("B-0001", titre="Ajouter triple")
        self.poser("T-0001", "besoin : B-0001", titre="Écrire triple")
        self.poser("L-0001", "après : T-0001", "en cours", titre="Le premier lot")
        self.poser("JA-0001", "après : B-0001", titre="Le premier jalon")
        self.commiter("backlog")
        code, sortie = self.socle("roadmap")
        self.assertEqual(code, 0, sortie)
        self.assertIn("▶ L-0001 — Le premier lot : 0 tâche(s) close(s) sur 1 · 1 prête(s)\n", sortie)
        self.assertIn("  JA-0001 — Le premier jalon : 0 besoin(s) clos sur 1 — le prochain\n", sortie)
        code, sortie = self.socle("roadmap", "--format", "markdown", "--by", "need", "--all")
        self.assertEqual(code, 0, sortie)
        self.assertIn("#### B-0001 — Ajouter triple : 0 tâche(s) close(s) sur 1 — lot(s) : L-0001\n", sortie)
        self.assertIn("- T-0001 — Écrire triple · lot L-0001 · prête\n", sortie)
        with contextlib.redirect_stdout(io.StringIO()) as flux:
            self.assertEqual(cli.cmd_roadmap(argparse.Namespace(root=str(self.racine), format="text", by="need",
                                                                all=False)), 0)
        self.assertIn("  B-0001 — Ajouter triple : 0 tâche(s) close(s) sur 1 — lot(s) : L-0001\n", flux.getvalue())
        code, sortie = self.socle("roadmap", "--format", "markdown")
        self.assertIn("#### ▶ L-0001 — Le premier lot — en cours\n", sortie)
        self.assertEqual(suite.rendre(self.projet(), "markdown").rstrip("\n"), sortie.rstrip("\n"))

    def test_by_prend_batch_ou_need_et_batch_par_defaut_sans_synonyme(self):
        """D-0131 : `--by` prend `batch|need`, `batch` par défaut, et `lot`
        n'en est pas un synonyme."""
        self.poser("B-0001", titre="Ajouter triple")
        self.poser("T-0001", "besoin : B-0001", titre="Écrire triple")
        self.poser("L-0001", "après : T-0001", "en cours", titre="Le premier lot")
        self.commiter("backlog")
        self.assertEqual(suite.LECTURES, ("batch", "need"))
        code, par_defaut = self.socle("roadmap", "--format", "markdown")
        self.assertEqual(code, 0, par_defaut)
        code, par_lot = self.socle("roadmap", "--format", "markdown", "--by", "batch")
        self.assertEqual(code, 0, par_lot)
        self.assertEqual(par_lot, par_defaut)
        self.assertIn("#### ▶ L-0001 — Le premier lot — en cours\n", par_lot)
        erreur = io.StringIO()
        with contextlib.redirect_stderr(erreur), self.assertRaises(SystemExit) as refus:
            cli.main(["--root", str(self.racine), "roadmap", "--by", "lot"])
        self.assertEqual(refus.exception.code, 2)
        self.assertIn("'lot'", erreur.getvalue())

    def projet(self):
        from socle import config

        return config.Projet.charger(self.racine)


ETAPE_DE_LA_CI = 'run: python3 .socle/socle roadmap --format markdown >> "$GITHUB_STEP_SUMMARY"'


class TestDeclencheurs(Projet):
    """T-0058 : le guide, les instructions du socle, la clôture d'un lot, le
    résumé de la CI, une ligne de l'état, et le skill de l'atelier qui mène
    un lot."""

    def test_l_etat_a_une_ligne_qui_renvoie_a_la_commande(self):
        from socle import state as etat

        mem = backlog_d_essai()
        bloc = etat._backlog(mem)[0][1]
        self.assertTrue(bloc[0].startswith("backlog  : "))
        self.assertEqual(bloc[1], "  la suite : `python3 .socle/socle roadmap` (détaillée : `--format markdown`)")
        with messages.dans("en"):
            self.assertEqual(etat._backlog(mem)[0][1][1],
                             "  the roadmap: `python3 .socle/socle roadmap` (detailed: `--format markdown`)")
        self.commiter("base")
        from socle import config

        self.assertIn("\n  la suite : `python3 .socle/socle roadmap`",
                      etat.calculer(config.Projet.charger(self.racine), contenus=False))

    def test_la_ci_posee_ecrit_le_format_detaille_dans_le_resume_de_son_execution(self):
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
        # Posée dans le projet, elle écrit la suite détaillée dans le résumé.
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
        self.assertTrue(texte.startswith("## La suite du projet\n"), texte)
        self.assertIn("#### ▶ L-0001 — Le premier lot — en cours", texte)
        self.assertIn("- T-0001 — Écrire triple · besoin B-0001 · prête", texte)

    def test_le_skill_socle_batch_colle_le_format_compact_au_recap_de_la_cloture(self):
        from socle import installer as installeur

        attendus = {"fr": "le récap de la clôture colle la sortie de `python3 .socle/socle roadmap`",
                    "en": "the closing recap pastes the output of `python3 .socle/socle roadmap`"}
        for lg, phrase in attendus.items():
            installeur.poser_skills(self.racine, lg)
            texte = (self.racine / installeur.SKILLS / "socle-batch" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn(phrase, " ".join(texte.split()), lg)
            self.assertLessEqual(len(texte.encode("utf-8")), 8000, lg)
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

    def test_le_skill_de_l_atelier_l_appelle_a_l_annonce_et_a_la_cloture_d_un_lot(self):
        racine = Path(__file__).resolve().parent.parent
        skill = " ".join((racine / ".claude/skills/delegate-lot/SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn("À l'annonce d'un lot, puis à sa clôture, lancer `python3 .socle/socle roadmap`", skill)
        self.assertIn("« Tu implémentes une tâche du socle dans ton worktree du dépôt memory.", skill)
        self.assertNotRegex(skill, r"\bsujets?\b")


if __name__ == "__main__":
    unittest.main()
