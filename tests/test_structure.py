"""ADR-0083 (D-0123) : le backlog en quatre formes, chacune son préfixe — un
besoin `B-`, une tâche `T-`, un lot `L-`, un jalon `JA-` ; ce que chaque
forme attend, la clôture, les contrôles qui empêchent de les remélanger,
l'état, les commandes, l'ancien numéro, et la migration d'un backlog
d'avant."""

import contextlib
import io
import re
import shutil
import tempfile
import types
import unittest
from pathlib import Path

from socle import (checks_memory as controles_memoire, cli, config, context as contexte, hooks,
                   installer as installeur, memory as memoire, messages, migration, readings as lectures,
                   selftest as autotest)
from socle.report import Rapport
from tests.test_bascule import MOTEUR, git

JOURNAL = "J-2026-11-16-A"


def entree(ident: str, statut: str = "ouvert", meta: str = "", corps: str = "Pour l'essai.") -> tuple[str, str]:
    """(chemin, texte) d'une entrée du backlog, dans son fichier."""
    ligne = f"> statut : {statut} · origine : {JOURNAL}" + (f" · {meta}" if meta else "")
    if statut in ("fait", "abandonné") and "ref :" not in meta:
        ligne += " · ref : J-2026-11-16-B"
    clos = "closed/" if statut in ("fait", "abandonné") else ""
    texte = f"<!-- socle: couche=backlog zone=publique -->\n# {ident} — L'entrée {ident}\n\n{ligne}\n\n{corps}\n"
    return f"memory/backlog/{clos}{ident}-essai.md", texte


def memoire_de(*entrees: tuple[str, str]) -> memoire.Memoire:
    mem = memoire.Memoire(Path("."), None)
    for chemin, texte in entrees:
        mem.fichiers[chemin] = memoire.analyser(chemin, texte)
    return mem


SATISFAIT = "Pour l'essai.\n\n## Satisfait quand\n\n- [ ] le module le fait"
FAIT = "Pour l'essai.\n\n## Fait quand\n\n- [x] le test passe"


def formes(mem: memoire.Memoire, base: memoire.Memoire | None = None) -> list[str]:
    r = Rapport()
    controles_memoire.formes(types.SimpleNamespace(memoire=mem, memoire_base=base), r)
    return [c.message for c in r.erreurs("memoire.formes")]


class TestLecture(unittest.TestCase):
    def test_la_forme_se_lit_sur_le_prefixe(self):
        mem = memoire_de(entree("B-0001"), entree("T-0001", meta="besoin : B-0001"), entree("L-0001"),
                         entree("JA-0001"))
        e = {i: mem.entree(i) for i in ("B-0001", "T-0001", "L-0001", "JA-0001")}
        self.assertEqual([x.forme for x in e.values()], ["besoin", "tache", "lot", "jalon"])
        self.assertTrue(memoire.est_besoin(e["B-0001"]) and memoire.est_tache(e["T-0001"]))
        self.assertTrue(memoire.est_lot(e["L-0001"]) and memoire.est_jalon(e["JA-0001"]))
        self.assertEqual(memoire.besoin_de(e["T-0001"]), "B-0001")
        self.assertEqual([memoire.type_d_id(i) for i in ("JA-0005", "J-2026-11-16-A", "T-0012", "X-1")],
                         ["JA", "J", "T", None])
        # Un champ `forme` ne fait plus rien : un B- reste un besoin.
        self.assertFalse(memoire.est_jalon(memoire_de(entree("B-0002", meta="forme : jalon")).entree("B-0002")))

    def test_l_ancien_numero_se_resout_et_ne_se_reattribue_jamais(self):
        mem = memoire_de(entree("B-0001"), entree("L-0001", meta="ancien : B-0009"))
        self.assertEqual(mem.entree("L-0001").anciens, ["B-0009"])
        self.assertEqual(set(mem.anciens()), {"B-0009"})
        self.assertIsNone(mem.entree("B-0009"))
        self.assertEqual(mem.resoudre("B-0009").id, "L-0001")
        self.assertEqual(mem.prochain_id("B"), "B-0010")

    def test_une_tache_prend_sa_section_et_un_besoin_la_sienne(self):
        mem = memoire_de(entree("B-0001", corps=SATISFAIT), entree("T-0001", meta="besoin : B-0001", corps=FAIT))
        self.assertIs(memoire.section_de(mem.entree("B-0001")), memoire.SECTION_SATISFAIT_QUAND)
        self.assertEqual(memoire.criteres(mem.entree("B-0001")), [(False, "le module le fait")])
        self.assertEqual(memoire.criteres(mem.entree("T-0001")), [(True, "le test passe")])


class TestOrdre(unittest.TestCase):
    def test_seule_une_tache_se_prend_et_elle_herite_de_son_besoin(self):
        """Une tâche prend la priorité de son besoin, et attend ce qu'il
        attend ; un lot attend ses tâches, un jalon ses besoins."""
        mem = memoire_de(
            entree("B-0001", meta="priorité : haute"),
            entree("B-0002", meta="après : B-0001"),
            entree("B-0003"),
            entree("T-0001", meta="besoin : B-0001"),
            entree("T-0002", meta="besoin : B-0002"),
            entree("L-0001", meta="après : T-0001, T-0002"),
            entree("JA-0001", meta="après : B-0001, B-0002"),
        )
        o = memoire.ordre(mem)
        self.assertEqual(o.jalon.id, "JA-0001")
        self.assertEqual(o.restants, ["B-0001", "B-0002"])
        self.assertEqual(o.lot.id, "L-0001")
        self.assertEqual(o.avancement, [("T-0001", "pret"), ("T-0002", "attend")])
        self.assertEqual([e.id for e in o.prets], ["T-0001"])
        self.assertEqual(memoire.priorite_effective(mem.entree("T-0001"), {e.id: e for e in mem.entrees("B")}),
                         "haute")
        self.assertEqual([e.id for e in o.a_decouper], ["B-0003"])
        self.assertEqual((o.en_attente, o.attendent_une_entree), (1, 1))

    def test_un_besoin_dont_les_taches_sont_closes_est_a_fermer(self):
        mem = memoire_de(entree("B-0001"), entree("T-0001", "fait", meta="besoin : B-0001"),
                         entree("B-0002"), entree("T-0002", "abandonné", meta="besoin : B-0002"))
        o = memoire.ordre(mem)
        self.assertEqual([e.id for e in o.a_fermer], ["B-0001"])
        self.assertEqual([e.id for e in o.a_decouper], ["B-0002"])

    def test_les_messages_de_l_etat_disent_besoin_tache_lot_et_jalon_jamais_sujet(self):
        """B-0265 : l'état n'appelle plus « sujet » un lot ni un jalon, ni
        « tâche » un sujet, en français comme en anglais."""
        mem = memoire_de(
            entree("B-0001"), entree("B-0002", meta="priorité : basse"), entree("B-0003"),
            entree("B-0004", meta="après : D-0001"), entree("B-0005"),
            entree("T-0001", meta="besoin : B-0001 · priorité : haute"), entree("T-0002", meta="besoin : B-0002"),
            entree("T-0003", meta="besoin : B-0001 · après : T-0001"), entree("T-0004", "fait", meta="besoin : B-0005"),
            entree("L-0001", meta="après : T-0001, T-0003"), entree("JA-0001", meta="après : B-0001"),
        )
        chemin = "memory/requests/D-0001-essai.md"
        mem.fichiers[chemin] = memoire.analyser(chemin, "<!-- socle: couche=demandes zone=publique -->\n"
                                                        "# D-0001 — Une demande\n\n> date : 2026-11-16\n")
        fr = memoire.lignes_ordre(mem)
        self.assertEqual(fr, [
            "prochain jalon : JA-0001 — L'entrée JA-0001 ; besoins ouverts : B-0001",
            "prochain lot : L-0001 — L'entrée L-0001 ; 0 close(s) sur 2 ; reste : T-0001 (prête), T-0003 (attend)",
            "tâche prête : T-0001 — L'entrée T-0001 (priorité haute)",
            "prêtes aussi, de priorité basse : T-0002",
            "besoins à fermer, leurs tâches closes : B-0005",
            "besoins à découper en tâches : B-0003",
            "1 entrée(s) attendent une entrée ouverte du backlog",
            "1 entrée(s) attendent une demande sans réponse",
        ])
        with messages.dans("en"):
            en = memoire.lignes_ordre(mem)
        self.assertEqual(en[0], "next milestone: JA-0001 — L'entrée JA-0001; open needs: B-0001")
        self.assertIn("ready task: T-0001 — L'entrée T-0001 (high priority)", en)
        for ligne in fr + en:
            self.assertNotRegex(ligne.lower(), r"\bsujets?\b|\btopics?\b")


class TestFormes(unittest.TestCase):
    """Les refus de `memoire.formes`, chacun avec un témoin sain."""

    def test_une_structure_saine_passe(self):
        mem = memoire_de(entree("B-0001", corps=SATISFAIT), entree("T-0001", meta="besoin : B-0001", corps=FAIT),
                         entree("L-0001", meta="après : T-0001"), entree("L-0002", meta="après : L-0001"),
                         entree("JA-0001", meta="après : B-0001"))
        self.assertEqual(formes(mem, memoire_de()), [])

    def test_chaque_melange_est_refuse(self):
        cas = {
            "forme": [entree("B-0001", meta="forme : lot")],
            "besoin hors tâche": [entree("B-0001", meta="besoin : B-0001")],
            "priorité d'un lot": [entree("L-0001", meta="priorité : haute")],
            "tâche sans besoin": [entree("T-0001")],
            "tâche dans deux lots": [entree("B-0001"), entree("T-0001", meta="besoin : B-0001"),
                                     entree("L-0001", meta="après : T-0001"), entree("L-0002", meta="après : T-0001")],
            "lot qui attend un besoin": [entree("B-0001"), entree("L-0001", meta="après : B-0001")],
            "jalon qui attend une tâche": [entree("B-0001"), entree("T-0001", meta="besoin : B-0001"),
                                           entree("JA-0001", meta="après : T-0001")],
            "besoin qui attend un lot": [entree("L-0001"), entree("B-0001", meta="après : L-0001")],
            "après par l'ancien numéro": [entree("L-0001", meta="ancien : B-0009"),
                                          entree("B-0001", meta="après : B-0009")],
            "Fait quand d'un besoin": [entree("B-0001", corps=FAIT)],
            "Satisfait quand d'une tâche": [entree("B-0001"), entree("T-0001", meta="besoin : B-0001", corps=SATISFAIT)],
        }
        for nom, entrees in cas.items():
            with self.subTest(nom):
                self.assertEqual(len(formes(memoire_de(*entrees))), 1, formes(memoire_de(*entrees)))

    def test_le_besoin_d_une_tache_est_un_besoin(self):
        """Revue du lot L-0013 : ce refus n'avait ni test ni défaut injecté."""
        mem = memoire_de(entree("T-0001", meta="besoin : L-0001"), entree("L-0001", meta="après : T-0001"))
        self.assertEqual(formes(mem), ["`T-0001` : `besoin : L-0001` ne nomme pas un besoin du backlog"])

    def test_une_entree_nouvelle_porte_sa_section(self):
        base = memoire_de(entree("B-0001"))
        mem = memoire_de(entree("B-0001"), entree("B-0002"), entree("T-0001", meta="besoin : B-0001"))
        self.assertEqual(formes(mem, base), ["`B-0002` : entrée nouvelle (besoin) sans sa section « Satisfait quand »",
                                             "`T-0001` : entrée nouvelle (tâche) sans sa section « Fait quand »"])
        # Une entrée d'avant, ou renumérotée, n'en a pas à porter.
        self.assertEqual(formes(memoire_de(entree("B-0001")), base), [])

    def test_un_besoin_se_ferme_apres_ses_taches_l_une_faite(self):
        base = memoire_de(entree("B-0001"), entree("T-0001", meta="besoin : B-0001", corps=FAIT))
        ouverte = memoire_de(entree("B-0001", "fait"), entree("T-0001", meta="besoin : B-0001", corps=FAIT))
        self.assertEqual(formes(ouverte, base), ["`B-0001` est clos (« fait ») avec une tâche ouverte : T-0001"])
        sans = memoire_de(entree("B-0001", "fait"), entree("T-0001", "abandonné", meta="besoin : B-0001", corps=FAIT))
        self.assertEqual(len(formes(sans, base)), 1)
        faite = memoire_de(entree("B-0001", "fait"), entree("T-0001", "fait", meta="besoin : B-0001", corps=FAIT))
        self.assertEqual(formes(faite, base), [])
        # Clos avant : ce qui est clos reste tel quel.
        self.assertEqual(formes(memoire_de(entree("B-0001", "fait")), memoire_de(entree("B-0001", "fait"))), [])

    def test_un_besoin_fait_coche_son_satisfait_quand(self):
        r = Rapport()
        mem = memoire_de(entree("B-0001", "fait", corps=SATISFAIT))
        controles_memoire.backlog(types.SimpleNamespace(memoire=mem), r)
        self.assertEqual([c.message for c in r.erreurs("memoire.backlog")],
                         ["`B-0001` est clos « fait » avec un critère de « Satisfait quand » non coché : le module "
                          "le fait"])

    def test_un_ancien_numero_reattribue_est_refuse(self):
        r = Rapport()
        mem = memoire_de(entree("B-0001"), entree("L-0001", meta="ancien : B-0001"))
        controles_memoire.format_memoire(types.SimpleNamespace(
            memoire=mem, fichiers=[*mem.fichiers, "memory/canonical.md", "memory/active.md"],
            projet=types.SimpleNamespace(chemins=config.FORMAT_ACTUEL)), r)
        self.assertIn("`B-0001` est l'ancien numéro de `L-0001` : il ne se réattribue jamais, `socle renumber "
                      "B-0001` donne à l'entrée qui le prend le prochain libre", [c.message for c in r.erreurs()])


class TestLecturesDeFormesDiverses(unittest.TestCase):
    def test_un_besoin_sa_tache_et_leur_lot_ecrits_ensemble_prouvent_leur_lecture(self):
        """L'index lu par chacun, dans l'ordre de leur écriture : le besoin
        avant tout, la tâche après lui, le lot après elle."""
        base = memoire_de(entree("B-0001"))
        b, t, lot = (entree("B-0002", corps=SATISFAIT), entree("T-0001", meta="besoin : B-0002", corps=FAIT),
                     entree("L-0001", meta="après : T-0001"))
        lu = {"B-0002": memoire.empreinte_index(base, "backlog"),
              "T-0001": memoire.empreinte_index(memoire_de(entree("B-0001"), b), "backlog"),
              "L-0001": memoire.empreinte_index(memoire_de(entree("B-0001"), b, t), "backlog")}
        mem = memoire_de(entree("B-0001"), b, t, lot)
        plage = lectures.Plage(Path("."), base, mem, [])
        for ident, h in lu.items():
            with self.subTest(ident):
                self.assertTrue(lectures.index_lu(plage, mem.entree(ident).fichier, mem.entree(ident), "backlog", h))
        self.assertFalse(lectures.index_lu(plage, mem.entree("T-0001").fichier, mem.entree("T-0001"), "backlog",
                                           "0badc0de"))


class Projet(unittest.TestCase):
    """Un projet installé, commité, dont le backlog est d'avant ADR-0083."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-structure-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        journal = next((self.racine / "memory/journal").glob("*.md"))
        self.journal = journal.read_text().split("## ", 2)[1].split(" ", 1)[0]

    def poser(self, ident: str, meta: str = "", statut: str = "ouvert", corps: str = "Pour l'essai.",
              titre: str = ""):
        clos = "closed/" if statut == "fait" else ""
        ligne = f"> statut : {statut} · origine : {self.journal}" + (f" · {meta}" if meta else "")
        (self.racine / f"memory/backlog/{clos}").mkdir(parents=True, exist_ok=True)
        (self.racine / f"memory/backlog/{clos}{ident}-essai.md").write_text(
            f"<!-- socle: couche=backlog zone=publique -->\n# {ident} — {titre or 'Entrée ' + ident}\n\n{ligne}\n\n"
            f"{corps}\n")

    def commiter(self, message: str) -> str:
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", message, "--no-verify")
        return git(self.racine, "rev-parse", "HEAD").strip()

    def socle(self, *args) -> tuple[int, str]:
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            code = cli.main(["--root", str(self.racine), *args])
        return code, sortie.getvalue()

    def erreurs(self, base: str) -> list[str]:
        """Les contrôles de la mémoire et de la documentation, en CI contre
        `base`."""
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=base, tete="HEAD")
        ids = [i for i in contexte.charger_controles() if i.startswith(("memoire.", "docs.", "demandes."))]
        r = contexte.executer(ctx, ids)
        return [f"{c.controle} : {c.message}" for c in r.erreurs()]


CRITERES = ("## Fait quand\n\n- [ ] la fonction triple existe, rend le triple de son argument pour les entiers et "
            "les flottants, et refuse une chaîne par une erreur de type que le test vérifie mot pour mot\n"
            "- [x] le guide la décrit")


class TestMigration(Projet):
    def avant(self):
        self.poser("B-0001", "ref : fichier:calc.py", "fait", CRITERES.replace("[ ]", "[x]"))
        self.poser("B-0002", corps=CRITERES)
        self.poser("B-0003", "forme : lot · après : B-0001 · ref : fichier:calc.py", "fait")
        self.poser("B-0004")
        self.poser("B-0005", "forme : lot · après : B-0003, B-0002, B-0004")
        self.poser("B-0006", "forme : jalon · après : B-0003, B-0005", corps="Un but.\n\n## Fait quand\n\n- [ ] x")
        self.poser("B-0007", "après : B-0006")
        actif = self.racine / "memory/active.md"
        actif.write_text(actif.read_text() + "\nLe lot B-0005 d'abord.\n")
        journal = next((self.racine / "memory/journal").glob("*.md"))
        journal.write_text(journal.read_text() + "\nLe lot B-0005 se forme.\n")
        return self.commiter("le backlog d'avant")

    def test_la_migration_renumerote_pose_les_taches_et_recrit_les_citations(self):
        self.avant()
        bilan = migration.migrer_backlog(self.racine)
        self.assertEqual(bilan.renumerotees, [("B-0003", "L-0001"), ("B-0005", "L-0002"), ("B-0006", "JA-0001")])
        self.assertEqual(bilan.taches, ["T-0001", "T-0002"])
        mem = memoire.Memoire.charger(self.racine)
        self.assertIsNone(mem.entree("B-0005"))
        self.assertEqual(mem.resoudre("B-0005").id, "L-0002")
        self.assertEqual(memoire.dependances(mem.entree("L-0002")), ["L-0001", "T-0001", "T-0002"])
        self.assertEqual(memoire.dependances(mem.entree("L-0001")), ["B-0001"])
        self.assertEqual(memoire.dependances(mem.entree("JA-0001")), ["B-0001", "B-0002", "B-0004"])
        self.assertEqual(memoire.dependances(mem.entree("B-0007")), ["B-0002", "B-0004"])
        self.assertNotIn("forme", mem.entree("L-0002").meta)
        t1, t2 = mem.entree("T-0001"), mem.entree("T-0002")
        self.assertEqual((memoire.besoin_de(t1), t1.statut, t1.titre), ("B-0002", "ouvert", "Entrée B-0002"))
        self.assertEqual(memoire.criteres(t1)[1], (True, "le guide la décrit"))
        self.assertEqual(memoire.criteres(t2), [(False, "ce que demande B-0004 est livré, et un test le montre")])
        # Le besoin renvoie à sa tâche : une copie divergerait.
        self.assertEqual(memoire.criteres(mem.entree("B-0002")), [(False, "le « Fait quand » de T-0001 est tenu")])
        # Le jalon garde sa section ; un besoin clos a la sienne renommée.
        self.assertTrue(memoire.SECTION_FAIT_QUAND.search(mem.entree("JA-0001").corps))
        self.assertTrue(memoire.SECTION_SATISFAIT_QUAND.search(mem.entree("B-0001").corps))
        self.assertIn("Le lot L-0002 d'abord.", (self.racine / "memory/active.md").read_text())
        self.assertIn("Le lot B-0005 se forme.", next((self.racine / "memory/journal").glob("*.md")).read_text())
        code, sortie = self.socle("show", "B-0005")
        self.assertEqual(code, 0)
        self.assertIn("B-0005 est l'ancien numéro de L-0002", sortie)
        # La seconde fois, rien.
        self.assertFalse(migration.migrer_backlog(self.racine))

    def test_apres_la_migration_aucun_controle_n_echoue(self):
        base = self.avant()
        migration.migrer_backlog(self.racine)
        from socle import archive as archivage

        archivage.ranger_backlog(self.racine)
        self.commiter("la migration")
        self.assertEqual(self.erreurs(base), [])

    def migrer_et_ranger(self) -> memoire.Memoire:
        migration.migrer_backlog(self.racine)
        from socle import archive as archivage

        archivage.ranger_backlog(self.racine)
        return memoire.Memoire.charger(self.racine)

    def test_une_entree_close_n_attend_rien_d_ouvert_apres_la_migration(self):
        """T-0052 : un besoin fait et un jalon fait qui attendaient un lot
        abandonné se mettaient à attendre ses besoins encore ouverts, et
        `memoire.ordre` les refusait. Ouverte, une entrée n'attend toujours
        que ce qui reste ouvert."""
        clos = "ref : fichier:calc.py"
        self.poser("B-0001", clos, "fait", CRITERES.replace("[ ]", "[x]"))
        self.poser("B-0002", corps=CRITERES)
        self.poser("B-0003", f"forme : lot · après : B-0001, B-0002 · {clos}", "abandonné")
        self.poser("B-0004", f"après : B-0003 · {clos}", "fait")
        self.poser("B-0005", f"forme : jalon · après : B-0003 · {clos}", "fait")
        self.poser("B-0006", "après : B-0003")
        base = self.commiter("le backlog d'avant")
        mem = self.migrer_et_ranger()
        self.assertEqual([memoire.dependances(mem.entree(i)) for i in ("B-0004", "JA-0001", "B-0006")],
                         [["B-0001"], ["B-0001"], ["B-0002"]])
        self.commiter("la migration")
        self.assertEqual(self.erreurs(base), [])

    def test_un_critere_sur_plusieurs_lignes_passe_entier_dans_la_tache(self):
        """T-0052 : la tâche ne recevait que la première ligne d'un critère,
        et la suite restait dans le besoin, sous sa case de renvoi."""
        criteres = ("## Fait quand\n\n- [ ] la fonction triple existe, rend le triple de son argument\n"
                    "  pour les entiers et les flottants,\net refuse une chaîne par une erreur de type\n"
                    "- [x] le guide la décrit\n\nUn mot après la liste.")
        self.poser("B-0001", corps=criteres)
        self.poser("B-0002", "forme : lot · après : B-0001")
        base = self.commiter("le backlog d'avant")
        mem = self.migrer_et_ranger()
        tache = mem.entree("T-0001").texte
        self.assertIn("- [ ] la fonction triple existe, rend le triple de son argument\n  pour les entiers et les "
                      "flottants,\net refuse une chaîne par une erreur de type\n- [x] le guide la décrit", tache)
        besoin = mem.entree("B-0001").corps
        self.assertNotIn("flottants", besoin)
        self.assertNotIn("erreur de type", besoin)
        self.assertIn("- [ ] le « Fait quand » de T-0001 est tenu\n\nUn mot après la liste.", besoin)
        self.assertEqual(migration.criteres_entiers(memoire_de(entree("B-0009", corps=criteres)).entree("B-0009")),
                         [(False, "la fonction triple existe, rend le triple de son argument\n  pour les entiers "
                                  "et les flottants,\net refuse une chaîne par une erreur de type"),
                          (True, "le guide la décrit")])
        self.commiter("la migration")
        self.assertEqual(self.erreurs(base), [])

    def test_la_tache_posee_cite_les_identifiants_actuels(self):
        """T-0052 : la tâche lisait son besoin avant la réécriture des
        mentions ; son titre et ses critères gardaient l'ancien numéro d'un
        lot (dans l'atelier, T-0012 disait B-0224 de JA-0005)."""
        self.poser("B-0001", "forme : lot")
        self.poser("B-0002", titre="B-0001 a réuni trop de besoins",
                   corps="## Fait quand\n\n- [ ] l'état signale un lot comme B-0001\n  ou B-0001@abcdef12")
        self.poser("B-0003", "forme : lot · après : B-0002")
        base = self.commiter("le backlog d'avant")
        mem = self.migrer_et_ranger()
        tache = mem.entree("T-0001")
        self.assertEqual(tache.titre, "L-0001 a réuni trop de besoins")
        self.assertEqual(mem.entree("B-0002").titre, tache.titre)
        self.assertIn("- [ ] l'état signale un lot comme L-0001\n  ou L-0001", tache.texte)
        self.assertNotRegex(tache.texte, r"B-0001\b")
        self.assertTrue(tache.fichier.endswith("/T-0001-l-0001-a-reuni-trop-de-besoins.md"), tache.fichier)
        self.commiter("la migration")
        self.assertEqual(self.erreurs(base), [])

    def test_la_mise_a_jour_migre_le_backlog(self):
        self.avant()
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        self.assertIn("backlog : 3 lot(s) et jalon(s) renumérotés (B-0003 → L-0001, B-0005 → L-0002, B-0006 → "
                      "JA-0001)", sortie.getvalue())
        self.assertIn("backlog : 2 tâche(s) posée(s)", sortie.getvalue())
        self.assertTrue(list((self.racine / "memory/backlog/closed").glob("L-0001-*.md")))

    def test_la_migration_et_le_rangement_sans_index_laissent_l_index_inchange(self):
        """T-0200 (B-0357) : la migration mettait ses renommages dans
        l'index (`git add`). Elle n'écrit plus que l'arbre de travail, comme
        le rangement appelé sans `indexer` ; `socle archive` indexe encore
        les siens (`test_format_3`)."""
        self.avant()
        from socle import archive as archivage

        self.assertTrue(migration.migrer_backlog(self.racine).renumerotees)
        archivage.ranger_backlog(self.racine, indexer=False)
        self.assertEqual(git(self.racine, "diff", "--cached", "--name-only"), "")
        self.assertFalse((self.racine / "memory/backlog/B-0005-essai.md").exists())
        self.assertTrue(list((self.racine / "memory/backlog").glob("L-0002-*.md")))

    def test_la_mise_a_jour_laisse_l_index_inchange_et_git_add_prend_ses_renommages(self):
        """T-0200 (B-0357) : chez chess, le 26 novembre, le commit de la
        demande seule qui suit la mise à jour emportait les renommages de
        la migration et du rangement, que l'installeur avait indexés.
        L'index reste celui du dernier commit ; `git add -A`, au commit des
        fichiers de la mise à jour, prend chaque renommage, l'ancien
        fichier et le neuf."""
        self.avant()
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        self.assertEqual(git(self.racine, "diff", "--cached", "--name-only"), "")
        git(self.racine, "add", "-A")
        etats = git(self.racine, "diff", "--cached", "--name-status", "--no-renames", "--",
                    "memory/backlog").splitlines()
        for attendu in ("D\tmemory/backlog/B-0005-essai.md", "A\tmemory/backlog/L-0002-essai.md",
                        "D\tmemory/backlog/closed/B-0003-essai.md", "A\tmemory/backlog/closed/L-0001-essai.md"):
            self.assertIn(attendu, etats)

    def test_la_priorite_d_un_lot_et_d_un_jalon_se_retire_et_le_bilan_les_nomme(self):
        """Revue du lot L-0013 : l'ancien format permettait une priorité sur
        un jalon, que `memoire.formes` refusait après la migration."""
        self.poser("B-0001", corps=CRITERES)
        self.poser("B-0002", "forme : lot · après : B-0001 · priorité : haute")
        self.poser("B-0003", "forme : jalon · après : B-0002 · priorité : basse")
        base = self.commiter("le backlog d'avant")
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        self.assertIn("backlog : priorité retirée de 2 lot(s) et jalon(s) (L-0001, JA-0001)", sortie.getvalue())
        mem = memoire.Memoire.charger(self.racine)
        self.assertEqual([memoire.priorite(mem.entree(i)) for i in ("L-0001", "JA-0001")], [None, None])
        self.commiter("la mise à jour")
        self.assertEqual(self.erreurs(base), [])
        # Le bilan, en anglais aussi.
        with messages.dans("en"):
            self.assertIn("priority removed from 2 batch(es) and milestone(s) (L-0001, JA-0001)",
                          messages.trad("backlog : priorité retirée de {n} lot(s) et jalon(s) ({liste}) : ils "
                                        "n'étaient déjà jamais prêts, elle ne changeait aucun ordre ; elle se donne "
                                        "à un besoin ou à une tâche", n=2, liste="L-0001, JA-0001"))

    def migre(self) -> tuple[str, str]:
        """Le backlog d'avant migré et commité : (le commit, le journal)."""
        self.avant()
        migration.migrer_backlog(self.racine)
        from socle import archive as archivage

        archivage.ranger_backlog(self.racine)
        return self.commiter("la migration"), str(next((self.racine / "memory/journal").glob("*.md")))

    def test_une_citation_par_l_ancien_numero_se_juge_contre_l_entree_actuelle(self):
        """Revue du lot L-0013 : `B-0005@<inventée>`, ancien numéro de L-0002,
        passait le contrôle et le hook ; seul `L-0002@<inventée>` tombait."""
        base, journal = self.migre()
        juste = memoire.empreinte_entree(memoire.Memoire.charger(self.racine).entree("L-0002"))
        rel = str(Path(journal).relative_to(self.racine))
        avant = Path(journal).read_text()
        projet = config.Projet.charger(self.racine)
        for h, refus in (("deadbeef", True), (juste, False)):
            with self.subTest(h):
                apres = avant + f"\n## {self.journal[:-1]}Z — Constat\n\nVoir B-0005@{h}.\n"
                fautes = hooks.references_inventees(projet, rel, avant, apres)
                self.assertEqual(any(f"`B-0005@{h}`" in f and "empreinte" in f for f in fautes), refus, fautes)
                Path(journal).write_text(apres)
                self.commiter(f"le constat {h}")
                erreurs = [e for e in self.erreurs(base) if e.startswith("memoire.lectures")]
                self.assertEqual(len(erreurs), int(refus), erreurs)
                self.assertTrue(not refus or "`B-0005@deadbeef`" in erreurs[0], erreurs)
                git(self.racine, "reset", "-q", "--hard", base)

    def test_l_ancien_numero_dans_un_texte_neuf_fait_nommer_l_identifiant_actuel(self):
        """T-0051 : le hook refusait l'ancien numéro d'une entrée renumérotée
        en le disant inventé, quand les contrôles le résolvent ; il nomme
        l'identifiant actuel, que le texte neuf cite alors."""
        _, journal = self.migre()
        projet = config.Projet.charger(self.racine)

        def ecrire(chemin: Path, texte: str) -> str:
            entree = {"session_id": "s", "tool_name": "Write",
                      "tool_input": {"file_path": str(chemin), "content": texte}}
            with contextlib.redirect_stdout(io.StringIO()) as sortie:
                hooks.pre_tool_use(projet, entree)
            return sortie.getvalue()

        note = self.racine / "docs/note.md"
        refus = ecrire(note, "Le lot B-0005 avance.\n")
        self.assertIn('"deny"', refus)
        self.assertIn("ancien numéro — `B-0005` (ligne 1) est l'ancien numéro de L-0002 : un texte neuf cite "
                      "l'entrée par son identifiant actuel, L-0002", refus)
        self.assertNotIn("ne désigne aucune entrée", refus)
        self.assertEqual(ecrire(note, "Le lot L-0002 avance.\n"), "")
        # Sur la ligne qui nomme aussi l'identifiant actuel, l'ancien passe :
        # le bilan de la mise à jour se recopie au journal.
        self.assertEqual(ecrire(note, "Renumérotés : B-0005 → L-0002.\n"), "")
        self.assertIn("`B-0005` (ligne 2)", ecrire(note, "Le lot L-0002 avance.\nB-0005 aussi.\n"))
        # T-0083 : l'ancien numéro se juge sur les lignes que l'écriture
        # ajoute, même dans un fichier qui le cite déjà.
        self.assertIn("ancien numéro — `B-0005`",
                      ecrire(Path(journal), Path(journal).read_text() + "\nLe lot B-0005 avance.\n"))
        # Une référence inventée reste dite inventée, avant l'ancien numéro.
        self.assertIn("référence inventée — `B-0099`", ecrire(note, "B-0005 et B-0099.\n"))
        self.assertEqual(hooks.references_refusees(projet, "docs/note.md", None, "B-0005.\n")[0], [])

    def test_l_ancien_numero_se_juge_sur_les_lignes_ajoutees(self):
        """T-0083 : le hook sautait toute mention que le fichier portait déjà ;
        dans un fichier qui cite B-0005, une ligne neuve qui le reprenait
        passait. Il juge les lignes que l'écriture ajoute ou change ; une
        ligne gardée telle quelle passe, même si l'écriture change ce qui
        l'entoure, et la ligne qui nomme aussi L-0002 passe."""
        self.migre()
        projet = config.Projet.charger(self.racine)
        avant = "# Notes\n\nLe lot B-0005 avance.\n\nFin.\n"

        def vieux(apres: str) -> list[str]:
            return hooks.references_refusees(projet, "docs/note.md", avant, apres)[1]

        self.assertIn("`B-0005` (ligne 7)", " ".join(vieux(avant + "\nVoir B-0005.\n")))
        self.assertIn("`B-0005` (ligne 3)", " ".join(vieux(avant.replace("avance.", "avance vite."))))
        self.assertEqual(vieux(avant + "\nVoir L-0002.\n"), [])
        self.assertEqual(vieux("# Notes revues\n\nLe lot B-0005 avance.\n\nFin, enfin.\n"), [])
        self.assertEqual(vieux(avant + "\nRenumérotés : B-0005 → L-0002.\n"), [])

    def test_l_ancien_numero_que_portait_une_ligne_de_metadonnees_y_reste(self):
        """Passe 1 de la revue de L-0005 : le hook refusait toute retouche de
        la ligne de métadonnées d'une entrée renumérotée, qui porte son
        ancien numéro (`ancien : B-0005`) ; clore le lot l'était, comme
        changer le statut d'une décision dont la source cite un ancien
        numéro. Sur une ligne de métadonnées, l'ancien numéro que portait le
        bloc remplacé reste ; un ancien numéro neuf s'y refuse, et une ligne
        de texte retouchée se juge comme avant (ADR-0093)."""
        self.migre()
        projet = config.Projet.charger(self.racine)
        rel = next((self.racine / "memory/backlog").glob("L-0002-*.md")).relative_to(self.racine).as_posix()
        avant = (self.racine / rel).read_text()
        self.assertIn("ancien : B-0005", avant)

        def vieux(apres: str) -> list[str]:
            return hooks.references_refusees(projet, rel, avant, apres)[1]

        close = re.sub(r"^> statut : [^·]*·", "> statut : fait · ref : J-2026-01-01-A ·", avant, count=1, flags=re.M)
        self.assertNotEqual(close, avant)
        self.assertEqual(vieux(close), [])
        self.assertIn("`B-0006`", " ".join(vieux(close.replace("ref : J-2026-01-01-A", "ref : B-0006"))))
        self.assertIn("`B-0005`", " ".join(vieux(avant + "\nLe lot B-0005 avance.\n")))

    def test_lignes_remplacees(self):
        self.assertEqual(hooks.lignes_remplacees("a\nb\nc\n", "a\nx\nc\nd\n"), {2: "b", 4: ""})
        self.assertEqual(hooks.lignes_remplacees("a\nb\nc\n", "a\nx\ny\n"), {2: "b\nc", 3: "b\nc"})
        self.assertEqual(hooks.lignes_remplacees("a\n", "a\n"), {})

    def test_lignes_ajoutees(self):
        self.assertEqual(hooks.lignes_ajoutees("a\nb\nc\n", "a\nb\nc\nd\n"), {4})
        self.assertEqual(hooks.lignes_ajoutees("a\nb\nc\n", "x\nb\ny\n"), {1, 3})
        self.assertEqual(hooks.lignes_ajoutees("a\nb\n", "a\nb\nb\n"), {3})
        self.assertEqual(hooks.lignes_ajoutees("", "a\n"), {1})
        self.assertEqual(hooks.lignes_ajoutees("a\nb\n", "b\n"), set())

    def test_poser_lectures_cite_l_index_sans_les_taches(self):
        self.avant()
        bilan = migration.migrer_backlog(self.racine)
        mem = memoire.Memoire.charger(self.racine)
        h = memoire.empreinte_index(mem, "backlog", set(bilan.taches))
        self.assertEqual(migration.poser_lectures(self.racine, bilan.taches), h)
        self.assertIn(f"lu : backlog@{h}", (self.racine / mem.entree("T-0002").fichier).read_text())

    def test_forme_ecrite_lit_l_ancien_champ_dans_les_deux_langues(self):
        mem = memoire_de(entree("B-0001", meta="forme : lot"), entree("B-0002", meta="form : milestone"))
        self.assertEqual([migration.forme_ecrite(mem.entree(i)) for i in ("B-0001", "B-0002")], ["lot", "jalon"])


class TestCommandes(Projet):
    def test_new_need_task_batch_milestone_et_new_backlog_retire(self):
        self.commiter("base")
        code, sortie = self.socle("new", "need", "Ajouter triple", "--task", "Écrire triple et son test")
        self.assertEqual(code, 0, sortie)
        self.assertIn("B-0001\tmemory/backlog/B-0001-ajouter-triple.md\nT-0001\tmemory/backlog/T-0001-ecrire-triple-"
                      "et-son-test.md", sortie)
        tache = (self.racine / "memory/backlog/T-0001-ecrire-triple-et-son-test.md").read_text()
        self.assertIn("besoin : B-0001", tache)
        self.assertIn("## Fait quand", tache)
        self.assertIn("## Satisfait quand", (self.racine / "memory/backlog/B-0001-ajouter-triple.md").read_text())
        for type_, ident in (("task", "T-0002"), ("batch", "L-0001"), ("milestone", "JA-0001")):
            args = ["new", type_, f"Une entrée {type_}"] + (["--need", "B-0001"] if type_ == "task" else [])
            code, sortie = self.socle(*args)
            self.assertEqual(code, 0, sortie)
            self.assertIn(f"{ident}\t", sortie)
        self.assertEqual(self.socle("new", "task", "Sans besoin")[0], 2)
        self.assertEqual(self.socle("new", "task", "Un besoin absent", "--need", "B-0009")[0], 2)
        self.assertEqual(self.socle("new", "batch", "Un lot", "--need", "B-0001")[0], 2)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cli.main(["--root", str(self.racine), "new", "backlog", "Un sujet"])


class TestGuideProtection(unittest.TestCase):
    """B-0317 (T-0119) : hors du hook de l'agent, seul l'ensemble de règles
    de GitHub refuse un push forcé sur la branche par défaut, ou sa
    suppression ; l'étape 4 du guide ne faisait exiger que la CI."""

    def test_l_etape_4_fait_refuser_le_push_force_et_la_suppression(self):
        for nom, debut in (("HELP.md", "4. Protéger la branche par défaut"),
                           ("HELP.en.md", "4. Protect the default branch")):
            with self.subTest(nom):
                texte = (Path(MOTEUR) / "socle" / nom).read_text(encoding="utf-8")
                etape = texte[texte.index(debut):]
                etape = " ".join(etape[:etape.index("\n5. ")].split())
                for case in ("Block force pushes", "Restrict deletions"):
                    self.assertIn(case, etape)


class TestVocabulaire(unittest.TestCase):
    """B-0265 (T-0053) : un mot pour une chose. Une entrée du backlog n'est
    pas un « sujet », et « tâche » ne dit que la tâche `T-`."""

    def test_le_guide_ne_dit_tache_qu_a_partir_de_sa_definition(self):
        """Le guide disait « tâche » du travail confié à l'agent, quinze
        lignes avant de définir la tâche `T-` (J-2026-11-16-AA)."""
        for nom, mot, definition, avant in (("HELP.md", "tâches?", "une **tâche** (`T-`)", "une **"),
                                            ("HELP.en.md", "tasks?", "a **task** (`T-`)", "a **")):
            with self.subTest(nom):
                plat = " ".join((Path(MOTEUR) / "socle" / nom).read_text(encoding="utf-8").split())
                premier = re.search(rf"(?i)\b{mot}\b", plat)
                self.assertEqual(premier.start(), plat.index(definition) + len(avant), plat[premier.start() - 80:
                                                                                          premier.end() + 80])

    def test_les_textes_du_produit_ne_disent_plus_sujet_d_une_entree_du_backlog(self):
        """T-0053 : la docstring de `memoire.lectures`, que `socle checks`
        affiche, l'aide de `socle review` et les libellés de l'auto-test
        disaient « sujet » d'une entrée du backlog, et l'un d'eux « tâche »
        d'une commande en arrière-plan."""
        aide = io.StringIO()
        with contextlib.redirect_stdout(aide), self.assertRaises(SystemExit):
            cli.main(["review", "--help"])
        textes = {"memoire.lectures": controles_memoire.lectures.__doc__, "socle review": aide.getvalue()}
        textes |= {c.id: c.defaut for c in autotest._cas()}
        textes |= {nom: nom for nom, _ in autotest._temoins()}
        for ou, texte in textes.items():
            with self.subTest(ou):
                plat = " ".join(texte.split())
                self.assertNotRegex(plat, r"(?i)\bsujets?\b")
                self.assertNotIn("tâche de fond", plat)
        self.assertIn("une entrée du backlog nouvelles prouvent", " ".join(textes["memoire.lectures"].split()))
        self.assertIn("les tâches du lot entier", " ".join(textes["socle review"].split()))


class TestAtelier(unittest.TestCase):
    def test_les_entrees_d_essai_de_l_autotest_ont_leur_forme(self):
        a = types.SimpleNamespace(journal=JOURNAL)
        empreinte = autotest.empreinte
        autotest.empreinte = lambda *_: "00000000"
        self.addCleanup(setattr, autotest, "empreinte", empreinte)
        # Comme `ajouter_sujet` la pose : son titre remonté d'un niveau.
        t = memoire.analyser("memory/backlog/T-0001-x.md", autotest.tache_essai(a, None).replace("## ", "# ", 1)
                             ).entrees[0]
        lot = memoire.analyser("memory/backlog/L-0001-x.md", autotest.lot_essai(a, None, "L-0001", "T-0001")).entrees[0]
        self.assertEqual((t.id, memoire.besoin_de(t), memoire.criteres(t)), ("T-0001", "B-0001", [(True, "le test passe")]))
        self.assertEqual((lot.id, memoire.dependances(lot)), ("L-0001", ["T-0001"]))


if __name__ == "__main__":
    unittest.main()
