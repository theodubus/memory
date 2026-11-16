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


def demande(ident: str) -> str:
    return (f"<!-- socle: couche=demandes zone=publique -->\n# {ident} — La demande {ident}\n\n"
            "> date : 2026-11-01\n\n## Décision demandée\n\nTrancher.\n")


def avec_demande(mem: memoire.Memoire, ident: str, repondue: bool = False) -> str:
    chemin = f"memory/requests/{ident}-essai.md"
    mem.fichiers[chemin] = memoire.analyser(chemin, demande(ident))
    if repondue:
        mem.repondues.add(chemin)
    return chemin


def avec_meta(texte: str, meta: str) -> str:
    """Le sujet, une métadonnée de plus sur sa ligne."""
    return texte.replace("\n\nPour l'essai.", f" · {meta}\n\nPour l'essai.")


class TestPriorite(unittest.TestCase):
    """D-0062 : une priorité, haute ou basse, que l'humain ou l'agent pose ;
    la normale ne s'écrit pas."""

    def test_la_priorite_se_lit_dans_les_deux_langues(self):
        fr = memoire_de(avec_meta(sujet("B-0001"), "priorité : basse")).entree("B-0001")
        en = memoire_de(avec_meta(sujet("B-0001", "open", en=True), "priority: low")).entree("B-0001")
        self.assertEqual([memoire.priorite(fr), memoire.priorite(en)], ["basse", "basse"])
        self.assertIsNone(memoire.priorite(memoire_de(sujet("B-0001")).entree("B-0001")))

    def test_les_prets_se_rangent_par_priorite_et_les_basses_restent_a_part(self):
        mem = memoire_de(sujet("B-0001"), avec_meta(sujet("B-0002"), "priorité : haute"),
                         avec_meta(sujet("B-0003"), "priorité : basse"))
        o = memoire.ordre(mem)
        self.assertEqual([e.id for e in o.prets], ["B-0002", "B-0001"])
        self.assertEqual([e.id for e in o.basses], ["B-0003"])
        self.assertEqual(o.en_attente, 0)
        self.assertEqual(memoire.lignes_ordre(mem), [
            "prêt : B-0002 — Le sujet B-0002 (priorité haute)",
            "prêt : B-0001 — Le sujet B-0001",
            "prêts aussi, de priorité basse : B-0003",
        ])

    def test_une_priorite_autre_que_haute_ou_basse_est_refusee(self):
        for valeur in ("urgente", "normale"):
            with self.subTest(valeur=valeur):
                mem = memoire_de(avec_meta(sujet("B-0001"), f"priorité : {valeur}"))
                self.assertEqual(len(erreurs(mem)), 1, erreurs(mem))
        self.assertEqual(erreurs(memoire_de(avec_meta(sujet("B-0001"), "priorité : haute"))), [])


class TestDemandeAttendue(unittest.TestCase):
    """D-0064 : un sujet peut attendre une demande ; il est prêt une fois
    qu'elle a sa réponse."""

    def test_un_sujet_qui_attend_une_demande_est_pret_a_sa_reponse(self):
        mem = memoire_de(sujet("B-0001", apres="D-0001"))
        chemin = avec_demande(mem, "D-0001")
        o = memoire.ordre(mem)
        self.assertEqual((o.prets, o.en_attente), ([], 1))
        self.assertEqual(erreurs(mem), [])
        mem.repondues.add(chemin)
        self.assertEqual([e.id for e in memoire.ordre(mem).prets], ["B-0001"])

    def test_un_jalon_qui_attend_un_sujet_qui_attend_une_demande(self):
        """B-0146 : sur le pilote, l'état disait la mémoire illisible
        (`KeyError`), le prochain jalon lisant comme un sujet chaque attendu,
        demandes comprises."""
        mem = memoire_de(sujet("B-0001", apres="D-0001"), sujet("B-0002", forme="jalon", apres="B-0001"))
        avec_demande(mem, "D-0001")
        o = memoire.ordre(mem)
        self.assertEqual(o.jalon.id, "B-0002")
        self.assertEqual(o.restants, ["B-0001", "D-0001"])
        self.assertEqual((o.prets, o.en_attente), ([], 1))
        self.assertEqual(memoire.lignes_ordre(mem)[0],
                         "prochain jalon : B-0002 — Le sujet B-0002 ; reste : B-0001, D-0001")
        self.assertEqual(erreurs(mem), [])

    def test_l_etat_dit_ce_qu_attendent_ses_sujets_un_sujet_ou_une_demande(self):
        """B-0153 : l'état disait « attendent un sujet ouvert » d'un sujet qui
        attend une demande sans réponse ; il dit maintenant ce qu'attend
        chacun, et un sujet qui attend les deux compte dans les deux."""
        mem = memoire_de(sujet("B-0001"), sujet("B-0002", apres="D-0001"), sujet("B-0003", apres="B-0001"),
                         sujet("B-0004", apres="B-0001, D-0001"))
        avec_demande(mem, "D-0001")
        o = memoire.ordre(mem)
        self.assertEqual((o.en_attente, o.attendent_un_sujet, o.attendent_une_demande), (3, 2, 2))
        self.assertEqual(memoire.lignes_ordre(mem)[-2:], ["2 sujet(s) attendent un sujet ouvert",
                                                          "2 sujet(s) attendent une demande sans réponse"])
        seule = memoire_de(sujet("B-0001", apres="D-0001"))
        avec_demande(seule, "D-0001")
        self.assertEqual(memoire.lignes_ordre(seule), ["1 sujet(s) attendent une demande sans réponse"])
        from socle import messages
        with messages.dans("en"):
            self.assertEqual(memoire.lignes_ordre(seule), ["1 topic(s) wait on an unanswered request"])

    def test_un_sujet_fait_avant_la_reponse_qu_il_attend_est_refuse(self):
        mem = memoire_de(sujet("B-0001", "fait", apres="D-0001"))
        avec_demande(mem, "D-0001")
        self.assertEqual(erreurs(mem), ["`B-0001` est fait avant `D-0001`, qu'il attend, encore sans réponse"])
        avec_demande(mem, "D-0001", repondue=True)
        self.assertEqual(erreurs(mem), [])

    def test_une_demande_repondue_se_lit_a_cote_de_sa_reponse(self):
        import shutil
        import subprocess
        import tempfile

        racine = Path(tempfile.mkdtemp(prefix="socle-repondues-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        (racine / "memory/requests").mkdir(parents=True)
        (racine / "memory/requests/D-0001-essai.md").write_text(demande("D-0001"))
        (racine / "memory/requests/D-0001-essai.answer.toml").write_text('reponse = "valider"\n')
        subprocess.run(["git", "init", "-q"], cwd=racine, check=True)
        subprocess.run(["git", "add", "-A"], cwd=racine, check=True)
        mem = memoire.Memoire.charger(racine)
        self.assertTrue(memoire.demande_close(mem, mem.entree("D-0001")))


class TestFaitQuand(unittest.TestCase):
    """D-0064 : la section « Fait quand », en cases à cocher, toutes cochées
    avant de clore un sujet « fait »."""

    TEXTE = "\n\n## Fait quand\n\n- [x] le test passe\n- [ ] le guide le dit\n\n## Notes\n\n- [ ] hors section\n"

    def fautes(self, texte: str) -> list[str]:
        r = Rapport()
        controles_memoire.backlog(types.SimpleNamespace(memoire=memoire_de(texte)), r)
        return [c.message for c in r.erreurs("memoire.backlog") if "Fait quand" in c.message]

    def test_les_criteres_se_lisent_dans_leur_section(self):
        e = memoire_de(sujet("B-0001") + self.TEXTE).entree("B-0001")
        self.assertEqual(memoire.criteres(e), [(True, "le test passe"), (False, "le guide le dit")])
        self.assertEqual(memoire.criteres(memoire_de(sujet("B-0001")).entree("B-0001")), [])

    def test_un_sujet_fait_avec_un_critere_non_coche_est_refuse(self):
        self.assertEqual(self.fautes(sujet("B-0001", "fait") + self.TEXTE),
                         ["`B-0001` est clos « fait » avec un critère de « Fait quand » non coché : le guide le dit"])
        self.assertEqual(self.fautes(sujet("B-0001", "fait") + self.TEXTE.replace("[ ] le guide", "[x] le guide")), [])
        # Ouvert, ou abandonné, il peut garder des critères non cochés.
        self.assertEqual(self.fautes(sujet("B-0001") + self.TEXTE), [])
        self.assertEqual(self.fautes(sujet("B-0001", "abandonné") + self.TEXTE), [])


class TestLot(unittest.TestCase):
    """ADR-0079 : un lot est un sujet `forme : lot` qui attend les sujets
    qu'on mène ensemble ; l'état montre le prochain et où en sont ses
    sujets, et il se clôt quand ils le sont."""

    def memoire(self, lot_fait: bool = False) -> memoire.Memoire:
        mem = memoire_de(
            sujet("B-0001", "fait"),
            sujet("B-0002", "en cours"),
            sujet("B-0003", apres="B-0005"),           # attend B-0005, hors du lot
            sujet("B-0004"),
            sujet("B-0005"),
            sujet("B-0010", "fait" if lot_fait else "ouvert", forme="lot", apres="B-0001, B-0002, B-0003, D-0001"),
            sujet("B-0011", forme="lot", apres="B-0010, B-0004"),
        )
        avec_demande(mem, "D-0001")
        return mem

    def test_est_lot_se_lit_dans_les_deux_langues(self):
        fr = memoire_de(sujet("B-0003", apres="B-0001", forme="lot")).entree("B-0003")
        en = memoire_de(sujet("B-0003", "open", apres="B-0001", forme="batch", en=True)).entree("B-0003")
        self.assertTrue(memoire.est_lot(fr) and memoire.est_lot(en))
        self.assertFalse(memoire.est_jalon(fr))
        self.assertFalse(memoire.est_lot(memoire_de(sujet("B-0003", forme="jalon")).entree("B-0003")))

    def test_la_memoire_relie_le_lot_a_ses_sujets_et_l_etat_montre_le_prochain(self):
        from socle import state as etat

        mem = self.memoire()
        o = memoire.ordre(mem)
        # B-0011 attend le lot B-0010 : il n'est pas le prochain.
        self.assertEqual(o.lot.id, "B-0010")
        self.assertEqual(o.avancement, [("B-0001", "fait"), ("B-0002", "en-cours"), ("B-0003", "attend"),
                                        ("D-0001", "sans-reponse")])
        # Un lot n'est jamais un sujet à prendre, ni un sujet en attente.
        self.assertEqual([e.id for e in o.prets], ["B-0004", "B-0005"])
        self.assertEqual(o.en_attente, 1)
        ligne = ("prochain lot : B-0010 — Le sujet B-0010 ; 1 clos sur 4 ; "
                 "reste : B-0002 (en cours), B-0003 (attend), D-0001 (sans réponse)")
        self.assertEqual(memoire.lignes_ordre(mem)[0], ligne)
        self.assertIn(f"  {ligne}", [l for _, bloc in etat._backlog(mem) for l in bloc])

    def test_un_lot_dont_tout_est_clos_se_dit_a_clore(self):
        mem = memoire_de(sujet("B-0001", "fait"), sujet("B-0002", "abandonné"),
                         sujet("B-0003", forme="lot", apres="B-0001, B-0002, D-0001"))
        avec_demande(mem, "D-0001", repondue=True)
        self.assertEqual(memoire.lignes_ordre(mem),
                         ["prochain lot : B-0003 — Le sujet B-0003 ; 3 clos sur 3 ; reste : rien, il se clôt"])
        self.assertEqual(erreurs(mem), [])

    def test_le_lot_en_cours_passe_devant_et_un_lot_fait_avant_ses_sujets_est_refuse(self):
        mem = memoire_de(sujet("B-0001"), sujet("B-0002"), sujet("B-0003", forme="lot", apres="B-0001"),
                         sujet("B-0004", "en cours", forme="lot", apres="B-0002"))
        self.assertEqual(memoire.ordre(mem).lot.id, "B-0004")
        self.assertEqual(memoire.lignes_ordre(self.memoire(lot_fait=True))[0],
                         "prochain lot : B-0011 — Le sujet B-0011 ; 0 clos sur 1 ; reste : B-0004 (prêt)")
        self.assertEqual(erreurs(self.memoire(lot_fait=True)),
                         ["`B-0010` est fait avant `B-0002`, qu'il attend, encore « en-cours »",
                          "`B-0010` est fait avant `B-0003`, qu'il attend, encore « ouvert »",
                          "`B-0010` est fait avant `D-0001`, qu'il attend, encore sans réponse"])
