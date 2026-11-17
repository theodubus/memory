"""B-0274 (D-0127) : la suite du projet d'un coup d'œil, `socle roadmap` —
les jalons et leurs besoins clos, les lots dans leur ordre d'exécution et
leurs tâches, les besoins, ce qui n'est dans aucun lot ; le format compact
et le format détaillé, par lot et par besoin ; l'alerte de deux lots qui
attendent le même lot sans ordre entre eux."""

import argparse
import contextlib
import io
import types
import unittest
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

    def projet(self):
        from socle import config

        return config.Projet.charger(self.racine)


if __name__ == "__main__":
    unittest.main()
