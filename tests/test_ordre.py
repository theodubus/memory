"""L'ordre du backlog : un sujet attend d'autres sujets (`après`), un jalon
attend ses tâches, et ce qui vient ensuite se calcule (D-0052)."""

import types
import unittest
from pathlib import Path

from socle import checks_memory as controles_memoire, memory as memoire
from socle.report import Rapport


def sujet(ident: str, statut: str = "ouvert", apres: str = "", forme: str = "", en: bool = False) -> str:
    if en:
        meta = f"> status: {statut} · origin: J-2026-10-30-A" + (f" · after: {apres}" if apres else "") + \
               (f" · form: {forme}" if forme else "")
    else:
        meta = f"> statut : {statut} · origine : J-2026-10-30-A" + (f" · après : {apres}" if apres else "") + \
               (f" · forme : {forme}" if forme else "")
        if statut in ("fait", "abandonné"):
            meta += " · ref : J-2026-10-30-B"
    return f"<!-- socle: couche=backlog zone=publique -->\n# {ident} — Le sujet {ident}\n\n{meta}\n\nPour l'essai.\n"


def memoire_de(*textes: str) -> memoire.Memoire:
    mem = memoire.Memoire(Path("."), None)
    for i, texte in enumerate(textes):
        chemin = f"memory/backlog/B-{i:04d}.md"
        mem.fichiers[chemin] = memoire.analyser(chemin, texte)
    return mem


def erreurs(mem: memoire.Memoire) -> list[str]:
    r = Rapport()
    controles_memoire.ordre(types.SimpleNamespace(memoire=mem), r)
    return [c.message for c in r.erreurs("memoire.ordre")]


class TestLecture(unittest.TestCase):
    def test_dependances_et_est_jalon_se_lisent_dans_les_deux_langues(self):
        fr = memoire_de(sujet("B-0003", apres="B-0001, B-0002", forme="jalon")).entree("B-0003")
        en = memoire_de(sujet("B-0003", "open", apres="B-0001, B-0002", forme="milestone", en=True)).entree("B-0003")
        for e in (fr, en):
            self.assertEqual(memoire.dependances(e), ["B-0001", "B-0002"])
            self.assertTrue(memoire.est_jalon(e))
        self.assertFalse(memoire.est_jalon(memoire_de(sujet("B-0001")).entree("B-0001")))


class TestCalcul(unittest.TestCase):
    def test_sans_apres_ni_jalon_le_backlog_n_a_pas_d_ordre(self):
        mem = memoire_de(sujet("B-0001"), sujet("B-0002"))
        self.assertIsNone(memoire.ordre(mem))
        self.assertEqual(memoire.lignes_ordre(mem), [])

    def test_ordre_donne_les_prets_le_prochain_jalon_et_ce_qui_lui_reste(self):
        mem = memoire_de(
            sujet("B-0001", "fait"),
            sujet("B-0002", apres="B-0001"),           # prêt : B-0001 est clos
            sujet("B-0003", apres="B-0002"),           # attend B-0002
            sujet("B-0004"),                           # prêt, hors du jalon
            sujet("B-0005", forme="jalon", apres="B-0003"),
            sujet("B-0006", forme="jalon", apres="B-0005, B-0004"),
            sujet("B-0007", "en cours"),               # en cours : pas à prendre
        )
        o = memoire.ordre(mem)
        self.assertIsInstance(o, memoire.Ordre)
        self.assertEqual(o.jalon.id, "B-0005")
        self.assertEqual(o.restants, ["B-0002", "B-0003"])
        # Les prêts du prochain jalon d'abord.
        self.assertEqual([e.id for e in o.prets], ["B-0002", "B-0004"])
        self.assertEqual(o.en_attente, 1)
        self.assertEqual(memoire.lignes_ordre(mem), [
            "prochain jalon : B-0005 — Le sujet B-0005 ; reste : B-0002, B-0003",
            "prêt : B-0002 — Le sujet B-0002",
            "prêt : B-0004 — Le sujet B-0004",
            "1 sujet(s) attendent un sujet ouvert",
        ])

    def test_un_jalon_dont_tout_est_clos_se_dit_a_clore(self):
        mem = memoire_de(sujet("B-0001", "abandonné"), sujet("B-0002", forme="jalon", apres="B-0001"))
        self.assertEqual(memoire.lignes_ordre(mem), ["prochain jalon : B-0002 — Le sujet B-0002 ; reste : rien, il se clôt"])

    def test_au_dela_du_plafond_les_prets_se_comptent(self):
        mem = memoire_de(*[sujet(f"B-{i:04d}") for i in range(1, 5)], sujet("B-0005", apres="B-0001"))
        self.assertEqual(memoire.lignes_ordre(mem, plafond=2)[-2:],
                         ["… et 2 autre(s) prêt(s)", "1 sujet(s) attendent un sujet ouvert"])


class TestControle(unittest.TestCase):
    def test_un_ordre_sain_passe(self):
        mem = memoire_de(sujet("B-0001", "fait"), sujet("B-0002", apres="B-0001"),
                         sujet("B-0003", "fait", forme="jalon", apres="B-0001"))
        self.assertEqual(erreurs(mem), [])

    def test_un_cycle_est_refuse_une_fois(self):
        mem = memoire_de(sujet("B-0001", apres="B-0003"), sujet("B-0002", apres="B-0001"),
                         sujet("B-0003", apres="B-0002"))
        self.assertEqual(erreurs(mem), ["`B-0001` s'attend lui-même : B-0001 → B-0003 → B-0002 → B-0001"])
        self.assertEqual(len(erreurs(memoire_de(sujet("B-0001", apres="B-0001")))), 1)

    def test_un_jalon_clos_sur_une_tache_ouverte_est_refuse(self):
        mem = memoire_de(sujet("B-0001"), sujet("B-0002", "fait", forme="jalon", apres="B-0001"))
        self.assertEqual(erreurs(mem), ["`B-0002` est fait avant `B-0001`, qu'il attend, encore « ouvert »"])

    def test_un_sujet_abandonne_peut_laisser_ce_qu_il_attendait(self):
        self.assertEqual(erreurs(memoire_de(sujet("B-0001"), sujet("B-0002", "abandonné", apres="B-0001"))), [])

    def test_apres_ne_nomme_que_des_sujets_du_backlog(self):
        for valeur in ("F-0001", "demain", "commit:abc1234"):
            with self.subTest(valeur=valeur):
                self.assertEqual(len(erreurs(memoire_de(sujet("B-0001", apres=valeur)))), 1)


if __name__ == "__main__":
    unittest.main()
