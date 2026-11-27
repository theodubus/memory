"""ADR-0118 (B-0365, D-0213, D-0235 point 8) : un besoin naît rangé, dans
un jalon ouvert ou en réserve avec sa raison et son tri, sans appel de
plus : `socle new need --milestone` ou `--reserve` ; le contrôle
`memoire.reserve` ne fait que rattraper l'oubli d'un besoin nouveau, ou
sorti d'un jalon, quand un jalon est ouvert."""

import unittest

from socle import config, context as contexte, memory as memoire, messages, roadmap as suite, state as etat
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

    def test_champs_de_reserve_avec_le_tri_s_il_y_a_un_lot(self):
        self.assertEqual(memoire.champs_de_reserve(memoire_de(entree("L-0009", "fait"))),
                         "`réserve : <raison> · trié : L-0009`")
        self.assertEqual(memoire.champs_de_reserve(memoire_de(entree("B-0001"))), "`réserve : <raison>`")
        with messages.dans("en"):
            self.assertEqual(memoire.champs_de_reserve(memoire_de(entree("L-0009"))),
                             "`reserve : <reason> · sorted : L-0009`")


def backlog_trie(clos: int, tri: str = "trié : L-0001", jalon: str = "ouvert") -> memoire.Memoire:
    """Un jalon, B-0001 qu'il attend, B-0002 en réserve avec sa raison et
    `tri` ; L-0001, puis `clos` lots clos après lui, et un lot ouvert."""
    lots = [entree(f"L-{n:04d}", "fait") for n in range(1, clos + 2)]
    return memoire_de(entree("B-0001"), entree("B-0002", meta=f"réserve : après la mesure · {tri}"),
                      entree("JA-0001", jalon, meta="après : B-0001"), *lots, entree(f"L-{clos + 2:04d}"))


def ligne_a_placer(mem: memoire.Memoire) -> list[str]:
    return [l for _, b in etat._backlog(mem, borne=True) for l in b if "besoins à placer" in l]


class TestLeSignal(unittest.TestCase):
    """T-0221 : un besoin en réserve sans tri depuis quinze lots clos remonte
    à placer, dans l'état et la feuille de route ; le compte repart à chaque
    tri."""

    def test_quinze_lots_clos_depuis_son_tri_le_signalent_quatorze_non(self):
        self.assertEqual(memoire.LOTS_SANS_TRI, 15)
        quinze = backlog_trie(15)
        self.assertEqual([e.id for e in memoire.a_placer(memoire.Graphe(quinze))], ["B-0002"])
        self.assertEqual(ligne_a_placer(quinze), [
            "  besoins à placer (en réserve, sans raison ou sans tri depuis 15 lots clos) : B-0002 ; à la clôture "
            "du lot, chacun dans un jalon, ou `réserve : <raison> · trié : L-0017`"])
        self.assertEqual(suite.texte(suite.calculer(quinze)).splitlines()[-1], "En réserve : 1 besoin, 1 à placer")
        quatorze = backlog_trie(14)
        self.assertEqual(memoire.a_placer(memoire.Graphe(quatorze)), [])
        self.assertEqual(ligne_a_placer(quatorze), [])
        self.assertEqual(suite.texte(suite.calculer(quatorze)).splitlines()[-1], "En réserve : 1 besoin")

    def test_le_compte_repart_au_tri(self):
        self.assertEqual(memoire.a_placer(memoire.Graphe(backlog_trie(15, "trié : L-0016"))), [])
        # Sans `trié`, tous les lots clos comptent : seize ici.
        self.assertEqual([e.id for e in memoire.a_placer(memoire.Graphe(backlog_trie(15, "priorité : haute")))],
                         ["B-0002"])

    def test_sans_raison_un_besoin_est_a_placer_aussitot(self):
        mem = memoire_de(entree("B-0001"), entree("B-0002"), entree("B-0003", meta="pour : humain"),
                         entree("JA-0001", meta="après : B-0001"))
        self.assertEqual([e.id for e in memoire.a_placer(memoire.Graphe(mem))], ["B-0002"])
        self.assertEqual(ligne_a_placer(mem), [
            "  besoins à placer (en réserve, sans raison ou sans tri depuis 15 lots clos) : B-0002 ; à la clôture "
            "du lot, chacun dans un jalon, ou `réserve : <raison>`"])

    def test_sans_jalon_ouvert_rien_n_est_a_placer(self):
        mem = backlog_trie(20, jalon="fait")
        self.assertEqual(memoire.a_placer(memoire.Graphe(mem)), [])
        self.assertEqual(ligne_a_placer(mem), [])
        self.assertEqual(suite.texte(suite.calculer(mem)).splitlines()[-1], "En réserve : 2 besoins")

    def test_la_ligne_est_bornee_et_parle_anglais(self):
        mem = memoire_de(*(entree(f"B-{n:04d}") for n in range(2, 14)), entree("JA-0001"))
        ligne = ligne_a_placer(mem)[0]
        self.assertIn(": B-0002, B-0003, B-0004, B-0005, B-0006, B-0007, B-0008, B-0009, B-0010, B-0011 … et 2 "
                      "autre(s) ;", ligne)
        with messages.dans("en"):
            self.assertIn("In reserve: 12 needs, 12 to place", suite.texte(suite.calculer(mem)).splitlines())
            lignes = [l for _, b in etat._backlog(mem) for l in b if "needs to place" in l]
        self.assertIn("needs to place (in reserve, without a reason or unsorted for 15 closed batches): B-0002, ",
                      lignes[0])

    def test_la_ligne_passe_avant_ce_qui_se_relit_a_la_borne_du_demarrage(self):
        """Le signal ne se lit nulle part ailleurs : la borne du démarrage, qui
        coupe d'abord ce qui se relit (les listes du backlog), le garde."""
        mem = memoire_de(entree("B-0002"), entree("JA-0001"))
        rangs = [rang for rang, b in etat._backlog(mem, borne=True) for l in b if "besoins à placer" in l]
        self.assertEqual(rangs, [etat.INFO])

    def test_un_jalon_dont_les_besoins_sont_clos_annonce_le_tri_de_la_reserve(self):
        """Sa clôture exige la réserve retriée : l'état le dit avant, sans
        attendre le refus ; rien tant qu'un besoin du jalon reste ouvert, ni
        sans réserve."""
        def lignes(mem):
            return [l for _, b in etat._backlog(mem) for l in b if "jalons à clore" in l]

        clos = entree("B-0001", statut="fait", meta="ref : fichier:calc.py")
        reserve = entree("B-0002", meta="réserve : plus tard · trié : L-0001")
        self.assertEqual(lignes(memoire_de(clos, reserve, entree("L-0001"), entree("JA-0001", meta="après : B-0001"))),
                         ["  jalons à clore, leurs besoins clos : JA-0001 ; avant, la réserve se retrie (1 besoin(s)) : "
                          "chacun dans un jalon à venir, ou `réserve : <raison> · trié : L-0001`, ou son abandon "
                          "proposé à l'humain par une demande"])
        self.assertEqual(lignes(memoire_de(entree("B-0001"), reserve, entree("JA-0001", meta="après : B-0001"))), [])
        self.assertEqual(lignes(memoire_de(clos, entree("JA-0001", meta="après : B-0001"))), [])


class TestLaClotureDUnJalon(Projet):
    """T-0221 : un jalon ouvert à la base et clos à la tête exige la réserve
    triée, chaque besoin avec sa raison et un `trié` au moins égal au plus
    haut lot de la base ; `socle close` le refuse avec le contrôle."""

    def setUp(self):
        super().setUp()
        self.poser("B-0001", "ref : fichier:calc.py", "fait")
        self.poser("B-0002")
        self.poser("B-0003", "pour : humain")
        self.poser("JA-0001", "après : B-0001")
        self.poser("L-0001", "ref : fichier:calc.py", "fait")
        self.poser("L-0002")
        self.base = self.commiter("la base")
        self.ouvert = self.racine / "memory/backlog/JA-0001-essai.md"

    def test_refusee_sur_une_reserve_non_triee_puis_passant_une_fois_triee(self):
        avant = self.ouvert.read_text()
        code, sortie = self.socle("close", "JA-0001")
        self.assertEqual(code, 1, sortie)
        self.assertIn("`JA-0001` ne se clôt pas, rien n'est changé", sortie)
        self.assertIn("`JA-0001` se clôt sur une réserve non triée : B-0002 ; avant de clore un jalon, chaque "
                      "besoin de la réserve rejoint un jalon à venir, reste en réserve, sa raison et son tri récrits "
                      "(`réserve : <raison> · trié : L-0002`), ou se propose à l'humain pour abandon, par une "
                      "demande que sa raison nomme", sortie)
        self.assertEqual(self.ouvert.read_text(), avant)
        # Une raison et un tri d'avant le plus haut lot de la base : encore refusé.
        self.poser("B-0002", "réserve : après la mesure · trié : L-0001")
        self.assertEqual(self.socle("close", "JA-0001")[0], 1)
        self.poser("B-0002", "réserve : après la mesure · trié : L-0002")
        code, sortie = self.socle("close", "JA-0001")
        self.assertEqual(code, 0, sortie)
        self.assertFalse(self.ouvert.exists())

    def erreurs(self) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="git", base=self.base)
        return [c.message for c in contexte.executer(ctx, ["memoire.reserve"]).erreurs()]

    def test_le_controle_juge_le_jalon_clos_contre_la_base(self):
        self.poser("B-0002", "réserve : après la mesure · trié : L-0002")
        self.assertEqual(self.socle("close", "JA-0001")[0], 0)
        self.assertEqual(self.erreurs(), [])
        # Un lot clos ensuite sur la branche ne fait rien refuser.
        self.poser("L-0002", "ref : fichier:calc.py", "fait")
        (self.racine / "memory/backlog/L-0002-essai.md").unlink()
        self.poser("L-0003")
        self.assertEqual(self.erreurs(), [])
        # Sans raison, un besoin d'avant fait refuser la clôture.
        self.poser("B-0002")
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertTrue(erreurs[0].startswith("`JA-0001` se clôt sur une réserve non triée : B-0002 ;"), erreurs)


if __name__ == "__main__":
    unittest.main()
