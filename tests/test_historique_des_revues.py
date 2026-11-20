"""ADR-0084, ADR-0100 : un lot garde l'historique de ses passes de revue
dans sa section « Revues » ; `socle review` y écrit chaque passe, sans
exiger de recul ; le contrôle du backlog refuse une ligne de bloquant que
l'historique ne lit pas ; l'historique se lit d'un clone neuf."""

import contextlib
import io
import shutil
import tempfile
import types
import unittest
from pathlib import Path

from socle import checks_memory as controles_memoire, cli, config, language as langue, memory as memoire, \
    review as revue
from socle.report import Rapport
from tests.test_revue import commande, git

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
JOUR = "2026-11-16"
ENTETE = "<!-- socle: couche=backlog zone=publique -->\n"
BESOIN = (ENTETE + "# B-0001 — Doubler\n\n> statut : ouvert · origine : J-2026-11-16-A\n\nPour l'essai.\n\n"
          "## Satisfait quand\n\n- [ ] le module double\n")
TACHE = (ENTETE + "# T-0001 — Écrire double et son test\n\n> statut : {statut} · origine : J-2026-11-16-A · "
         "besoin : B-0001{ref}\n\nPour l'essai.\n\n## Fait quand\n\n- [x] le test passe\n")
LOT = (ENTETE + "# {id} — Le lot du doublement\n\n> statut : {statut} · origine : J-2026-11-16-A · "
       "après : {apres}{ref}\n\nCe qui réunit ses tâches : le module de calcul.\n")


def recul(decision: str, *, mots: int = 64) -> str:
    """Un paragraphe de recul de `mots` mots, qui finit par `decision`, tel
    qu'un lot l'écrivait avant ADR-0100 : du texte, que rien ne juge."""
    texte = ("Recul : la cause ne revient pas ; les entrées ouvertes sont d'une autre nature que les closes, la "
             "passe suivante ne relit que la correction")
    while len(texte.split()) < mots - 1:
        texte += " encore"
    return texte + f" : {decision}."


def bloquants(*causes: str) -> str:
    return "".join(f"- Bloquant : {c}\n" for c in causes) + "- Ouvre : rien\n"


class _Depot(unittest.TestCase):
    """Un dépôt cloné, sa branche de travail, un besoin, sa tâche et le lot
    en cours qui l'attend."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-revues-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        self.source = self.dossier / "source"
        (self.source / "memory/backlog").mkdir(parents=True)
        (self.source / "memory/requests").mkdir(parents=True)
        git(self.source, "init", "-q", "-b", "main")
        (self.source / "calc.py").write_text("def double(x):\n    return x + x\n")
        self.ecrire_source("memory/backlog/B-0001-doubler.md", BESOIN)
        self.ecrire_source("memory/backlog/T-0001-ecrire-double.md", TACHE.format(statut="ouvert", ref=""))
        self.ecrire_source("memory/backlog/L-0001-le-lot-du-doublement.md",
                           LOT.format(id="L-0001", statut="en cours", apres="T-0001", ref=""))
        git(self.source, "add", "-A")
        git(self.source, "commit", "-qm", "un")
        self.racine = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(self.source), str(self.racine))
        git(self.racine, "switch", "-q", "-c", "travail")
        self.projet = config.Projet(racine=self.racine)

    def ecrire_source(self, rel: str, texte: str):
        (self.source / rel).write_text(texte)

    @property
    def fichier_du_lot(self) -> Path:
        return self.racine / "memory/backlog/L-0001-le-lot-du-doublement.md"

    def code(self, corps: str, message: str = "le lot"):
        (self.racine / "calc.py").write_text(f"def double(x):\n    return {corps}\n")
        git(self.racine, "commit", "-qam", message)

    def relire(self, **options):
        return revue.relire(self.projet, jour=JOUR, **options)

    def lot(self) -> memoire.Entree:
        return memoire.Memoire.charger(self.racine).entree("L-0001")

    def consigner(self, texte: str):
        """Ce que l'agent écrit au bout de la dernière passe du lot."""
        p = self.fichier_du_lot
        p.write_text(p.read_text().rstrip("\n") + "\n\n" + texte.strip("\n") + "\n")

    def passe(self, corps: str, consigne: str, message: str):
        """Une correction commitée, puis la passe suivante produite, et ce
        que l'agent y consigne au retour du relecteur."""
        self.code(corps, message)
        texte, note = self.relire()
        self.consigner(consigne)
        return texte, note


class TestLaSection(unittest.TestCase):
    """La forme de la section « Revues », telle que le moteur la relit."""

    LOT = (ENTETE + "# L-0001 — Un lot\n\n> statut : en cours · origine : J-2026-11-16-A · après : T-0001\n\n"
           "Son corps.\n\n## Revues\n\n### Passe 1 — 2026-11-15\n\nCommits : 1a2b3c4..5d6e7f8\n\n"
           "- Bloquant : la correction change la lecture des commandes\n- Ouvre : T-0002\n\n"
           "{recul1}\n\n### Passe 2 — 2026-11-16\n\nCommits : 5d6e7f8..9a8b7c6\n\n"
           "- Bloquant : la lecture des commandes encore · même cause : passe 1\n"
           "- Bloquant : un test qui ne prouve rien · cause nouvelle\n"
           "- Bloquant : un oubli\n")

    def entree(self, texte: str) -> memoire.Entree:
        return memoire.analyser("memory/backlog/L-0001-un-lot.md", texte).entrees[0]

    def test_une_section_anglaise_se_lit_de_meme(self):
        texte = (ENTETE + "# L-0001 — A batch\n\n> status : in progress · origin : J-2026-11-16-A\n\n## Reviews\n\n"
                 "### Pass 1 — 2026-11-16\n\nCommits: 1a2b3c4..5d6e7f8\n\n- Blocker: a cause\n- Opens: none\n")
        p, = memoire.passes(self.entree(texte))
        self.assertEqual((p.debut, p.bloquants), ("1a2b3c4", ["a cause"]))

    def test_une_passe_garde_l_empreinte_de_l_arbre_de_travail_qu_elle_a_relu(self):
        texte = self.LOT.format(recul1=recul("continuer")).replace(
            "Commits : 5d6e7f8..9a8b7c6", "Commits : 5d6e7f8..5d6e7f8 + arbre de travail 0a1b2c3d4e5f")
        self.assertEqual([(p.tete, p.arbre) for p in memoire.passes(self.entree(texte))],
                         [("5d6e7f8", None), ("5d6e7f8", "0a1b2c3d4e5f")])
        self.assertEqual(memoire.LIGNE_COMMITS.match("Commits: 1a2b3c4..1a2b3c4 + working tree 0a1b2c3d4e5f")["arbre"],
                         "0a1b2c3d4e5f")

    def test_une_ligne_de_bloquant_ecrite_autrement_se_releve_avec_sa_ligne(self):
        # T-0054 : `LIGNE_BLOQUANT` ne lit que `- Bloquant : …` ; les autres formes étaient ignorées en silence.
        mal = ["- **Bloquant** : une cause", "- Bloquant 1 : une cause", "1. Bloquant : une cause",
               "- Bloquants : deux causes", "- Bloquant :"]
        bien = ["- Bloquant : une cause", "* bloquant: une cause · même cause", "- Ouvre : rien",
                "- Bloquante, la passe ? non", "bloquants de la passe, un recul replié"]
        texte = self.LOT.format(recul1=recul("continuer")) + "\n".join(mal + bien) + "\n"
        lignes = texte.split("\n")
        self.assertEqual(memoire.bloquants_mal_ecrits(self.entree(texte)),
                         [(lignes.index(ligne) + 1, ligne) for ligne in mal])
        # Hors de la section « Revues », rien ne se relève.
        self.assertEqual(memoire.bloquants_mal_ecrits(self.entree(texte.replace("## Revues", "## Notes"))), [])

    def test_une_ligne_de_bloquant_sans_puce_se_releve_aussi(self):
        # Revue de L-0015, bloquant 1 : sans puce, une ligne de bloquant n'était ni lue ni relevée.
        mal = ["Bloquant : une cause", "**Bloquant** : une cause", "Bloquant 2 — une cause", "-Bloquant : une cause",
               "• Bloquant : une cause", "- [ ] Bloquant : une cause", "> - Bloquant 1 : une cause",
               "Blocker: a cause", "Bloquants – deux causes"]
        bien = ["- Bloquant : une cause", "bloquants de la passe, un recul replié", "Bloquants, corrigés plus haut",
                "Bloquante, la passe ? non", "- Ouvre : rien"]
        texte = self.LOT.format(recul1=recul("continuer")) + "\n".join(mal + bien) + "\n"
        lignes = texte.split("\n")
        self.assertEqual(memoire.bloquants_mal_ecrits(self.entree(texte)),
                         [(lignes.index(ligne) + 1, ligne) for ligne in mal])

    def test_une_section_qui_n_est_pas_la_derniere_finit_au_titre_suivant(self):
        texte = self.LOT.format(recul1=recul("continuer")) + "\n## Notes\n\n### Passe 9 — hors section\n"
        self.assertEqual([p.numero for p in memoire.passes(self.entree(texte))], [1, 2])
        self.assertEqual(memoire.passes(self.entree(texte.split("## Revues")[0])), [])

    def test_le_format_documente_chaque_mot_de_la_section(self):
        format_ = (MOTEUR / "socle/FORMAT.md").read_text()
        for cle, mots in langue.REVUES.items():
            with self.subTest(cle=cle):
                self.assertIn(f"`{cle}` | {mots['fr']} | {mots['en']} |", format_)


class TestLaPremierePasse(_Depot):
    def test_sans_lot_en_cours_le_dossier_d_avant_et_rien_d_ecrit(self):
        self.fichier_du_lot.write_text(LOT.format(id="L-0001", statut="ouvert", apres="T-0001", ref=""))
        self.code("x * 2")
        texte, note = self.relire()
        self.assertEqual(texte, revue.dossier(self.projet))
        self.assertIn("aucun lot en cours au backlog", note)
        self.assertNotIn("## Revues", self.fichier_du_lot.read_text())

    def test_la_premiere_passe_garde_le_dossier_d_avant_et_s_ecrit_a_la_fin_du_lot(self):
        self.code("x * 2")
        attendu = revue.dossier(self.projet)
        tete = git(self.racine, "rev-parse", "--short", "HEAD").strip()
        debut = git(self.racine, "rev-parse", "--short", "origin/main").strip()
        texte, note = self.relire()
        self.assertEqual(texte, attendu)
        self.assertNotIn("second regard", texte)
        self.assertIn("passe 1 du lot L-0001 écrite dans memory/backlog/L-0001-le-lot-du-doublement.md", note)
        self.assertTrue(self.fichier_du_lot.read_text().endswith(
            "Ce qui réunit ses tâches : le module de calcul.\n\n## Revues\n\n"
            f"### Passe 1 — {JOUR}\n\nCommits : {debut}..{tete}\n"))
        p, = memoire.passes(self.lot())
        self.assertEqual((p.numero, p.date, p.debut, p.tete), (1, JOUR, debut, tete))
        self.assertEqual(memoire.section_des_revues(self.lot()),
                         f"## Revues\n\n### Passe 1 — {JOUR}\n\nCommits : {debut}..{tete}")
        self.assertTrue(revue.meme_passe(self.projet, p))
        # Une passe de plus, écrite par la fonction elle-même, à la fin de la
        # section.
        self.assertEqual(revue.ecrire_passe(self.projet, self.lot(), 2, tete, tete, "2026-11-17"),
                         "memory/backlog/L-0001-le-lot-du-doublement.md")
        self.assertEqual([x.numero for x in memoire.passes(self.lot())], [1, 2])
        self.code("2 * x", "la correction")
        self.assertFalse(revue.meme_passe(self.projet, memoire.passes(self.lot())[-1]))

    def test_la_meme_passe_se_redonne_sans_s_ecrire_deux_fois(self):
        self.code("x * 2")
        premier, _ = self.relire()
        git(self.racine, "commit", "-qam", "la passe écrite")
        second, note = self.relire()
        self.assertEqual(second, premier)
        self.assertIn("la passe 1 du lot L-0001 : rien n'a changé hors de la mémoire", note)
        self.assertEqual(len(memoire.passes(self.lot())), 1)

    def test_la_meme_passe_se_reconnait_sur_un_arbre_sale(self):
        # T-0054 : comparée au seul commit de tête, une relance sur un arbre sale inchangé faisait une passe
        # nouvelle, et la ligne `Commits` disait `X..X`.
        (self.racine / "calc.py").write_text("def double(x):\n    return x * 2\n")
        tete = git(self.racine, "rev-parse", "--short", "HEAD").strip()
        premier, note = self.relire()
        self.assertIn("passe 1 du lot L-0001 écrite", note)
        self.assertIn("+    return x * 2", premier)
        self.assertRegex(memoire.section_des_revues(self.lot()),
                         rf"\nCommits : {tete}\.\.{tete} \+ arbre de travail [0-9a-f]{{12}}$")
        p, = memoire.passes(self.lot())
        self.assertEqual((p.debut, p.tete, p.arbre), (tete, tete, revue.empreinte_de_l_arbre(self.projet, tete)))
        # Relancée sur le même arbre, toujours sale : la même passe, rien d'écrit.
        second, note = self.relire()
        self.assertEqual(second, premier)
        self.assertIn("la passe 1 du lot L-0001 : rien n'a changé hors de la mémoire", note)
        # Le même état, commité : encore la même passe.
        git(self.racine, "commit", "-qam", "le lot et sa passe")
        _, note = self.relire()
        self.assertIn("la passe 1 du lot L-0001 : rien n'a changé hors de la mémoire", note)
        self.assertEqual(len(memoire.passes(self.lot())), 1)
        # Un arbre qui change encore : une autre passe, qui s'écrit.
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        self.assertFalse(revue.meme_passe(self.projet, memoire.passes(self.lot())[-1]))
        _, note = self.relire()
        self.assertIn("passe 2 du lot L-0001 écrite", note)

    def test_un_lot_qui_ne_change_rien_hors_de_la_memoire_n_a_pas_de_passe(self):
        texte, note = self.relire()
        self.assertIn("(aucun changement hors de la mémoire : rien à relire)", texte)
        self.assertIsNone(note)
        self.assertEqual(memoire.passes(self.lot()), [])

    def test_une_section_qui_existe_recoit_la_passe_a_sa_fin_avant_la_section_suivante(self):
        p = self.fichier_du_lot
        p.write_text(p.read_text() + "\n## Revues\n\n### Passe 1 — 2026-11-15\n\nCommits : 0000000..1111111\n\n"
                     f"- Bloquant : une cause\n\n{recul('continuer')}\n\n## Notes\n\nUne note.\n")
        self.code("x * 2")
        self.relire()
        texte = p.read_text()
        self.assertIn(f"{recul('continuer')}\n\n### Passe 2 — {JOUR}\n\nCommits : ", texte)
        self.assertTrue(texte.endswith("\n\n## Notes\n\nUne note.\n"))
        self.assertEqual([x.numero for x in memoire.passes(self.lot())], [1, 2])

    def test_un_projet_anglais_ecrit_la_section_dans_sa_langue(self):
        (self.racine / ".socle").mkdir()
        (self.racine / ".socle/policy.toml").write_text('[memory]\nlanguage = "en"\n')
        projet = config.Projet.charger(self.racine)
        self.code("x * 2")
        revue.relire(projet, jour=JOUR)
        self.assertIn(f"\n## Reviews\n\n### Pass 1 — {JOUR}\n\nCommits: ", self.fichier_du_lot.read_text())
        self.assertEqual(len(memoire.passes(self.lot())), 1)

    def test_la_commande_ecrit_la_passe_et_le_dit_sur_sa_sortie_d_erreur(self):
        self.code("x * 2")
        code, out, err = commande(self.racine)
        self.assertEqual(code, 0)
        self.assertIn("## Le diff du lot (1 fichier(s), depuis origin/main)", out)
        self.assertIn("passe 1 du lot L-0001 écrite", err)
        self.assertIn("### Passe 1 — ", self.fichier_du_lot.read_text())


class TestLaCloture(unittest.TestCase):
    """Le contrôle du backlog juge la section « Revues » d'un lot, à tout
    statut : une ligne de bloquant que l'historique ne lit pas."""

    def erreurs(self, revues: str, statut: str = "fait") -> list[str]:
        ref = " · ref : J-2026-11-16-A" if statut == "fait" else ""
        dossier = "closed/" if statut == "fait" else ""
        texte = (ENTETE + f"# L-0001 — Un lot\n\n> statut : {statut} · origine : J-2026-11-16-A{ref}\n\n"
                 f"Son corps.\n{revues}")
        mem = memoire.Memoire(Path("."), None)
        chemin = f"memory/backlog/{dossier}L-0001-un-lot.md"
        mem.fichiers[chemin] = memoire.analyser(chemin, texte)
        r = Rapport()
        controles_memoire.backlog(types.SimpleNamespace(memoire=mem), r)
        return [c.message for c in r.erreurs("memoire.backlog")]

    def test_une_ligne_de_bloquant_mal_ecrite_est_refusee_a_tout_statut(self):
        # T-0054 : ignorée, l'historique ne la comptait pas parmi les bloquants de la passe.
        revues = ("\n## Revues\n\n### Passe 1 — 2026-11-15\n\nCommits : 1a2b3c4..5d6e7f8\n\n{ligne}\n"
                  "- Bloquant : une cause lue\n\n" + recul("continuer") + "\n")
        for ligne in ("- **Bloquant** : une cause", "- Bloquant 1 : une cause", "1. Bloquant : une cause"):
            for statut in ("en cours", "fait"):
                with self.subTest(ligne=ligne, statut=statut):
                    self.assertEqual(self.erreurs(revues.format(ligne=ligne), statut), [
                        f"`L-0001` : « {ligne} », dans sa section « Revues », se donne pour un bloquant sans la "
                        "forme que lit l'historique du lot, une ligne `- Bloquant : <sa cause>` par bloquant, ni "
                        "gras, ni numéro, ni pluriel"])
        self.assertEqual(self.erreurs(revues.format(ligne="- Bloquant : une autre cause")), [])


class TestUnCloneNeuf(_Depot):
    """D-0124, point 8 : l'historique d'un lot se lit depuis un clone neuf,
    et `socle review` y produit la passe suivante."""

    def test_l_historique_se_lit_d_une_session_neuve(self):
        self.code("x * 2")
        self.relire()
        self.consigner(bloquants("la correction change la lecture des commandes"))
        git(self.racine, "commit", "-qam", "la passe 1 consignée")
        git(self.racine, "push", "-q", "origin", "travail")
        neuf = self.dossier / "neuf"
        git(self.dossier, "clone", "-q", "-b", "travail", str(self.source), str(neuf))
        lot = memoire.Memoire.charger(neuf).entree("L-0001")
        p, = memoire.passes(lot)
        self.assertEqual((p.numero, p.date, p.bloquants), (1, JOUR, ["la correction change la lecture des "
                                                                       "commandes"]))
        (neuf / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        git(neuf, "commit", "-qam", "la correction")
        texte, note = revue.relire(config.Projet(racine=neuf), "origin/main", jour=JOUR)
        self.assertNotIn("la correction change la lecture des commandes", texte)
        self.assertIn("passe 2 du lot L-0001 écrite", note)


class TestLeLotDeLaRevue(_Depot):
    def test_plusieurs_lots_en_cours_se_nomment(self):
        (self.racine / "memory/backlog/L-0002-un-autre-lot.md").write_text(
            LOT.format(id="L-0002", statut="en cours", apres="L-0001", ref=""))
        self.code("x * 2")
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire()
        self.assertIn("2 lots sont en cours (L-0001, L-0002) : `socle review --batch L-NNNN`", str(refus.exception))
        self.assertEqual(revue.lot_de_la_revue(self.projet, "L-0002").id, "L-0002")
        self.relire(nom_du_lot="L-0002")
        self.assertEqual(len(memoire.passes(memoire.Memoire.charger(self.racine).entree("L-0002"))), 1)
        self.assertEqual(memoire.passes(self.lot()), [])

    def test_un_lot_nomme_inconnu_ou_clos_est_refuse(self):
        self.code("x * 2")
        for nom, raison in (("L-0042", "aucun lot de ce nom"), ("T-0001", "aucun lot de ce nom")):
            with self.subTest(nom=nom), self.assertRaises(revue.PasseRefusee) as refus:
                self.relire(nom_du_lot=nom)
            self.assertIn(raison, str(refus.exception))
        self.fichier_du_lot.write_text(LOT.format(id="L-0001", statut="fait", apres="T-0001",
                                                  ref=" · ref : J-2026-11-16-A"))
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire(nom_du_lot="L-0001")
        self.assertIn("le lot est clos (« fait »)", str(refus.exception))

    def test_l_option_batch_de_la_commande(self):
        self.code("x * 2")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = cli.main(["--root", str(self.racine), "review", "--batch", "L-0001"])
        self.assertEqual(code, 0)
        self.assertEqual(len(memoire.passes(self.lot())), 1)


if __name__ == "__main__":
    unittest.main()
