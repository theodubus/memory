"""ADR-0118 (B-0365, D-0213, D-0235 point 8) : un besoin naît rangé, dans
un jalon ouvert ou en réserve avec sa raison et son tri, sans appel de
plus : `socle new need --milestone` ou `--reserve` ; le contrôle
`memoire.reserve` ne fait que rattraper l'oubli d'un besoin nouveau, ou
sorti d'un jalon, quand un jalon est ouvert."""

import unittest

from socle import config, context as contexte, memory as memoire, messages
from tests.test_bascule import P
from tests.test_structure import Projet, entree, memoire_de

SANS_PLACE = "`B-0002`, un besoin nouveau, n'a pas de place : l'ajouter à l'`après` d'un jalon ouvert (JA-0001)"


class Reserve(Projet):
    """Un projet installé, sa base commitée : B-0001 ouvert, que le jalon
    ouvert JA-0001 attend ; un lot clos, L-0001, et un ouvert, L-0002."""

    jalon = "ouvert"

    def setUp(self):
        super().setUp()
        self.poser("B-0001")
        self.poser("JA-0001", "après : B-0001", self.jalon)
        self.poser("L-0001", "ref : fichier:calc.py", "fait")
        self.poser("L-0002")
        self.base = self.commiter("la base")

    def besoin(self, ident: str = "B-0002") -> memoire.Entree:
        return memoire.Memoire.charger(self.racine).entree(ident)

    def constats(self) -> list[str]:
        """Les erreurs du contrôle de la réserve, l'arbre contre la base."""
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="git", base=self.base)
        return [c.message for c in contexte.executer(ctx, ["memoire.reserve"]).erreurs()]


class TestNaissance(Reserve):
    def test_milestone_ajoute_le_besoin_a_la_fin_de_l_apres_du_jalon(self):
        code, sortie = self.socle("new", "need", "Mesurer le moteur", "--milestone", "JA-0001")
        self.assertEqual(code, 0, sortie)
        self.assertIn("`B-0002` rangé dans le jalon `JA-0001`, à la fin de son `après`", sortie)
        self.assertEqual(memoire.dependances(self.besoin("JA-0001")), ["B-0001", "B-0002"])
        self.assertNotIn("reserve", self.besoin().meta)
        self.assertEqual(self.constats(), [])

    def test_milestone_cree_l_apres_qui_manque(self):
        self.poser("JA-0002", "lu : backlog@00000000")
        code, sortie = self.socle("new", "need", "Mesurer le moteur", "--milestone", "JA-0002")
        self.assertEqual(code, 0, sortie)
        texte = (self.racine / "memory/backlog/JA-0002-essai.md").read_text()
        self.assertIn(" · lu : backlog@00000000 · après : B-0002\n", texte)
        self.assertEqual(memoire.dependances(self.besoin("JA-0002")), ["B-0002"])

    def test_reserve_ecrit_la_raison_et_le_plus_haut_lot(self):
        code, sortie = self.socle("new", "need", "Mesurer le moteur", "--reserve", "attend la mesure de JA-0003")
        self.assertEqual(code, 0, sortie)
        self.assertIn("`B-0002` en réserve : réserve : attend la mesure de JA-0003 · trié : L-0002", sortie)
        e = self.besoin()
        self.assertEqual(memoire.raison_de_reserve(e), "attend la mesure de JA-0003")
        self.assertEqual((e.meta["trie"], memoire.tri_de(e)), ("L-0002", 2))
        self.assertEqual(self.constats(), [])

    def test_avec_task_le_besoin_se_range_et_sa_tache_le_sert(self):
        code, sortie = self.socle("new", "need", "Mesurer le moteur", "--reserve", "après JA-0001",
                                  "--task", "Lancer la mesure")
        self.assertEqual(code, 0, sortie)
        self.assertEqual(memoire.raison_de_reserve(self.besoin()), "après JA-0001")
        self.assertEqual(memoire.besoin_de(self.besoin("T-0001")), "B-0002")
        self.assertNotIn("reserve", self.besoin("T-0001").meta)

    def test_sans_l_un_ni_l_autre_une_ligne_dit_comment_le_ranger_sans_refus(self):
        code, sortie = self.socle("new", "need", "Mesurer le moteur")
        self.assertEqual(code, 0, sortie)
        self.assertIn("`B-0002` n'a pas de place, que le commit exige : l'ajouter à l'`après` d'un jalon ouvert "
                      "(JA-0001), ou écrire sur sa ligne de métadonnées `réserve : <raison> · trié : L-0002`",
                      sortie)
        self.assertEqual(sortie.splitlines()[-2].split("\t")[0], "B-0002")

    def test_refus_avant_toute_ecriture(self):
        self.poser("JA-0002", "ref : fichier:calc.py", "fait")
        for args, attendu in (
                (("need", "X", "--milestone", "JA-0099"), "`--milestone JA-0099` : aucun jalon ouvert de ce nom"),
                (("need", "X", "--milestone", "JA-0002"), "`--milestone JA-0002` : aucun jalon ouvert de ce nom"),
                (("need", "X", "--milestone", "B-0001"), "`--milestone B-0001` : aucun jalon ouvert de ce nom"),
                (("need", "X", "--reserve", "  "), "`--reserve` : une raison, non vide et sans « · »"),
                (("need", "X", "--reserve", "a · b"), "`--reserve` : une raison, non vide et sans « · »"),
                (("batch", "X", "--reserve", "r"), "`--milestone` et `--reserve` ne valent que pour un besoin")):
            with self.subTest(args=args):
                avant = sorted(p.name for p in (self.racine / "memory/backlog").glob("*.md"))
                code, sortie = self.socle("new", *args)
                self.assertEqual(code, 2, sortie)
                self.assertIn(attendu, sortie)
                self.assertEqual(sorted(p.name for p in (self.racine / "memory/backlog").glob("*.md")), avant)
                self.assertIn("après : B-0001\n", (self.racine / "memory/backlog/JA-0001-essai.md").read_text())

    def test_les_deux_s_excluent(self):
        with self.assertRaises(SystemExit) as fin:
            self.socle("new", "need", "X", "--milestone", "JA-0001", "--reserve", "r")
        self.assertEqual(fin.exception.code, 2)


class TestSansLot(Projet):
    def test_sans_lot_la_reserve_n_a_pas_de_tri(self):
        self.poser("JA-0001")
        self.commiter("la base")
        code, sortie = self.socle("new", "need", "Mesurer le moteur", "--reserve", "plus tard")
        self.assertEqual(code, 0, sortie)
        e = memoire.Memoire.charger(self.racine).entree("B-0001")
        self.assertEqual((memoire.raison_de_reserve(e), memoire.tri_de(e)), ("plus tard", None))
        self.assertNotIn("trie", e.meta)


class TestSansJalon(Projet):
    def test_sans_jalon_ouvert_ni_ligne_ni_refus(self):
        self.poser("B-0001")
        self.poser("JA-0001", "après : B-0001 · ref : fichier:calc.py", "fait")
        base = self.commiter("la base")
        code, sortie = self.socle("new", "need", "Mesurer le moteur")
        self.assertEqual(code, 0, sortie)
        self.assertNotIn("n'a pas de place", sortie)
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="git", base=base)
        self.assertEqual(contexte.executer(ctx, ["memoire.reserve"]).erreurs(), [])


class TestLeControle(Reserve):
    def test_refuse_un_besoin_nouveau_sans_place(self):
        self.poser("B-0002")
        constats = self.constats()
        self.assertEqual(len(constats), 1, constats)
        self.assertIn(SANS_PLACE, constats[0])
        self.assertIn("ou écrire sur sa ligne de métadonnées `réserve : <raison> · trié : L-0002` ; à sa "
                      "création, `socle new need \"…\" --milestone JA-NNNN` ou `--reserve \"<raison>\"`", constats[0])

    def test_passe_un_besoin_nouveau_en_reserve_ou_dans_un_jalon(self):
        self.poser("B-0002", "réserve : attend la mesure · trié : L-0002")
        self.poser("B-0004")
        self.poser("JA-0001", "après : B-0001, B-0004")
        self.assertEqual(self.constats(), [])

    def test_un_besoin_d_avant_sans_raison_n_est_pas_refuse(self):
        self.poser("B-0003")
        self.base = self.commiter("un besoin d'avant, sans raison")
        self.assertEqual([e.id for e in memoire.reserve(memoire.Graphe(memoire.Memoire.charger(self.racine)))],
                         ["B-0003"])
        self.assertEqual(self.constats(), [])
        # Changé ensuite, il reste d'avant.
        self.poser("B-0003", corps="Pour l'essai, précisé.")
        self.assertEqual(self.constats(), [])

    def test_refuse_un_besoin_sorti_d_un_jalon_ouvert(self):
        self.poser("JA-0001")
        constats = self.constats()
        self.assertEqual(len(constats), 1, constats)
        self.assertIn("`B-0001`, un besoin sorti d'un jalon ouvert, n'a pas de place", constats[0])
        self.poser("B-0001", "réserve : remis après la mesure · trié : L-0002")
        self.assertEqual(self.constats(), [])

    def test_un_besoin_pour_l_humain_ou_clos_ne_se_range_pas(self):
        self.poser("B-0002", "pour : humain")
        self.poser("B-0003", "ref : fichier:calc.py", "fait")
        self.assertEqual(self.constats(), [])

    def test_en_anglais(self):
        self.poser("B-0002")
        with messages.dans("en"):
            constats = self.constats()
        self.assertIn("`B-0002`, a new need, has no place: add it to the `after` of an open milestone (JA-0001), "
                      "or write on its metadata line `reserve : <reason> · sorted : L-0002`", constats[0])


class TestSansJalonOuvert(Reserve):
    jalon = "fait"

    def test_tout_besoin_d_un_projet_sans_jalon_ouvert_passe(self):
        self.poser("B-0002")
        self.assertEqual(self.constats(), [])
        self.assertEqual(memoire.jalons_ouverts(memoire.Graphe(memoire.Memoire.charger(self.racine))), [])


class TestLaDefinition(unittest.TestCase):
    def test_la_reserve_les_besoins_ouverts_d_aucun_jalon_ouvert(self):
        g = memoire.Graphe(memoire_de(
            entree("B-0001"), entree("B-0002"), entree("B-0003", "fait"), entree("B-0004", "en cours"),
            entree("B-0005"), entree("JA-0001", meta="après : B-0001"),
            entree("JA-0002", "fait", meta="après : B-0003, B-0005 · ref : fichier:calc.py")))
        self.assertEqual([e.id for e in memoire.reserve(g)], ["B-0002", "B-0004", "B-0005"])
        self.assertEqual(memoire.jalons_ouverts(g), ["JA-0001"])
        self.assertEqual(memoire.attendus_des_jalons(g), {"B-0001"})

    def test_comment_ranger_nomme_les_jalons_de_sa_zone_et_le_tri(self):
        g = memoire.Graphe(memoire_de(entree("JA-0001"), entree("JA-0002", meta="après : JA-0001"),
                                      entree("L-0004", "fait")))
        self.assertEqual(memoire.comment_ranger(g), "l'ajouter à l'`après` d'un jalon ouvert (JA-0001, JA-0002), "
                                                    "ou écrire sur sa ligne de métadonnées `réserve : <raison> · "
                                                    "trié : L-0004`")
        self.assertEqual(memoire.comment_ranger(memoire.Graphe(memoire_de(entree("B-0001")))),
                         "l'ajouter à l'`après` d'un jalon ouvert, ou écrire sur sa ligne de métadonnées "
                         "`réserve : <raison>`")

    def test_les_champs_se_lisent_dans_les_deux_langues(self):
        _, texte = entree("B-0001", meta="reserve : after the measure · sorted : L-0012")
        e = memoire.analyser("memory/backlog/B-0001-essai.md", texte).entrees[0]
        self.assertEqual((memoire.raison_de_reserve(e), memoire.tri_de(e)), ("after the measure", 12))
        # Un `trié` qui ne nomme pas un lot de sa zone ne compte pas.
        for valeur in ("B-0012", P + "L-0012", "L-12", "plus tard"):
            _, texte = entree("B-0001", meta=f"trié : {valeur}")
            self.assertIsNone(memoire.tri_de(memoire.analyser("memory/backlog/B-0001-essai.md", texte).entrees[0]))

    def test_le_plus_haut_lot_ouvert_ou_clos(self):
        mem = memoire_de(entree("L-0003", "fait"), entree("L-0007"), entree("L-0002"))
        self.assertEqual((memoire.plus_haut_lot(mem), memoire.tri_a_ecrire(mem)), (7, "L-0007"))
        self.assertIsNone(memoire.tri_a_ecrire(memoire_de(entree("B-0001"))))


if __name__ == "__main__":
    unittest.main()
