"""ADR-0084 (D-0124) : un lot garde l'historique de ses passes de revue dans
sa section « Revues » ; `socle review` y écrit chaque passe, refuse la
suivante tant que la précédente n'a pas son recul, refuse « continuer »
après deux passes de suite où le relecteur voit une même cause revenir, et
toute passe tant que la demande d'un arrêt attend sa réponse ; le contrôle
du backlog refuse un lot relu clos « fait » sans le recul de sa dernière
passe ; l'historique se lit d'un clone neuf."""

import contextlib
import io
import re
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
DEMANDE = ("<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Borner la règle qui fait tourner le lot\n\n"
           "> date : 2026-11-16\n\nLa règle tourne ; une proposition la borne.\n")
REPONSE = 'reponse = "valider"\npar = "Théo"\ndate = "2026-11-16"\n'
# La demande d'un arrêt cite le lot qu'elle arrête : seule sa réponse le lève
# (ADR-0084, point 6).
DEMANDE_DU_LOT = DEMANDE.replace("fait tourner le lot", "fait tourner le lot L-0001")
RETIREE = "> date : 2026-11-16 · retirée : posée trop tôt"


def recul(decision: str, *, mots: int = 64, demande: str = "") -> str:
    """Un paragraphe de recul de `mots` mots (vingt-cinq au moins), qui
    finit par `decision`."""
    texte = ("Recul : la cause ne revient pas" + (f", et {demande} le pose" if demande else "") +
             " ; les entrées ouvertes sont d'une autre nature que les closes, la passe suivante ne relit que la "
             "correction")
    while len(memoire.mots_du_recul(texte)) < mots - 1:
        texte += " encore"
    return texte + f" : {decision}."


# Sept mots : trop court.
COURT = "Recul : la cause ne revient pas, continuer."


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

    def test_les_passes_leurs_commits_leurs_bloquants_et_leur_recul(self):
        texte = self.LOT.format(recul1=recul("continuer").replace(" la correction", "\nla correction", 3))
        passes = memoire.passes(self.entree(texte))
        self.assertEqual([(p.numero, p.date, p.debut, p.tete) for p in passes],
                         [(1, "2026-11-15", "1a2b3c4", "5d6e7f8"), (2, "2026-11-16", "5d6e7f8", "9a8b7c6")])
        self.assertEqual(passes[0].bloquants, [("la correction change la lecture des commandes", None)])
        self.assertEqual(passes[1].bloquants, [("la lecture des commandes encore", "meme"),
                                               ("un test qui ne prouve rien", "nouvelle"), ("un oubli", None)])
        # Un paragraphe sur plusieurs lignes se lit entier.
        self.assertEqual(passes[0].recul, " ".join(recul("continuer").split()))
        self.assertIsNone(passes[1].recul)
        self.assertTrue(passes[1].voit_revenir and not passes[0].voit_revenir)

    def test_une_section_anglaise_se_lit_de_meme(self):
        texte = (ENTETE + "# L-0001 — A batch\n\n> status : in progress · origin : J-2026-11-16-A\n\n## Reviews\n\n"
                 "### Pass 1 — 2026-11-16\n\nCommits: 1a2b3c4..5d6e7f8\n\n- Blocker: a cause · same cause\n\n"
                 "Step back: " + " ".join(["word"] * 60) + " stop.\n")
        p, = memoire.passes(self.entree(texte))
        self.assertEqual((p.debut, p.bloquants), ("1a2b3c4", [("a cause", "meme")]))
        self.assertEqual(memoire.decision_du_recul(p.recul), "s-arreter")
        self.assertIsNone(memoire.refus_du_recul(p))

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

    def test_une_section_qui_n_est_pas_la_derniere_finit_au_titre_suivant(self):
        texte = self.LOT.format(recul1=recul("continuer")) + "\n## Notes\n\n### Passe 9 — hors section\n"
        self.assertEqual([p.numero for p in memoire.passes(self.entree(texte))], [1, 2])
        self.assertEqual(memoire.passes(self.entree(texte.split("## Revues")[0])), [])

    def test_le_recul_commence_par_recul_a_soixante_mots_et_finit_par_sa_decision(self):
        def refus(texte):
            return memoire.refus_du_recul(memoire.Passe(1, JOUR, recul=texte))

        self.assertIn("n'a pas son recul", memoire.refus_du_recul(memoire.Passe(1, JOUR)))
        self.assertIn("a 7 mot(s) : il en faut 60 au moins", refus(COURT))
        self.assertIn("a 59 mot(s)", refus(recul("continuer", mots=59)))
        self.assertIn("ne finit ni par « continuer » ni par « s'arrêter »", refus(recul("continuer") + " Ensuite."))
        self.assertIsNone(refus(recul("continuer")))
        # La décision se lit sans sa ponctuation, ses accents ni la forme de
        # son apostrophe.
        for fin in ("s'arrêter", "s’arrêter", "« s'arreter »", "Continuer", "continuer…"):
            with self.subTest(fin=fin):
                self.assertIsNone(refus(recul(fin)))
        self.assertEqual(memoire.decision_du_recul(recul("« s’arrêter »")), "s-arreter")
        self.assertEqual(memoire.decision_du_recul(recul("Continuer")), "continuer")

    def test_un_arret_nomme_sa_demande(self):
        p = memoire.Passe(3, JOUR, recul=recul("s'arrêter", demande="D-0007") + " Voir D-0120 et B-0001.")
        self.assertEqual(memoire.demandes_du_recul(p), ["D-0007", "D-0120"])

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
        self.assertEqual((p.numero, p.date, p.debut, p.tete, p.recul), (1, JOUR, debut, tete, None))
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
        # nouvelle, refusée sans recul, et la ligne `Commits` disait `X..X`.
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
        # Un arbre qui change encore : une autre passe, que l'historique juge.
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        self.assertFalse(revue.meme_passe(self.projet, memoire.passes(self.lot())[-1]))
        with self.assertRaises(revue.PasseRefusee):
            self.relire()

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


class TestLeRecul(_Depot):
    """D-0124, points 2 à 6 : le recul avant chaque passe au-delà de la
    première, le second regard, l'arrêt."""

    def premiere(self):
        self.code("x * 2")
        self.relire()
        self.consigner(bloquants("la correction change la lecture des commandes"))

    def test_une_deuxieme_passe_sans_recul_est_refusee_et_montre_l_historique(self):
        self.premiere()
        self.code("2 * x", "la correction")
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire()
        texte = str(refus.exception)
        self.assertIn("la passe 2 du lot L-0001 est refusée — la passe 1 n'a pas son recul", texte)
        self.assertIn("## L'historique du lot (memory/backlog/L-0001-le-lot-du-doublement.md)", texte)
        self.assertIn("- Bloquant : la correction change la lecture des commandes", texte)
        self.assertIn("1. Les bloquants de cette passe ont-ils la même cause que ceux de la précédente ?", texte)
        self.assertIn("2. Les entrées que le lot ouvre sont-elles de même nature que celles qu'il ferme ?", texte)
        self.assertIn("3. Les lots clos qui ont touché les mêmes fichiers ont-ils déjà ouvert ce genre d'entrées ?",
                      texte)
        self.assertIn("d'un paragraphe qui commence par « Recul : », de soixante mots au moins", texte)
        # Rien ne s'écrit d'une passe refusée.
        self.assertEqual(len(memoire.passes(self.lot())), 1)

    def test_un_recul_trop_court_est_refuse_comme_un_recul_absent(self):
        self.premiere()
        self.consigner(recul("continuer", mots=30))
        self.code("2 * x", "la correction")
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire()
        self.assertIn("le recul de la passe 1 a ", str(refus.exception))

    def test_avec_son_recul_la_deuxieme_passe_donne_au_relecteur_les_causes_d_avant(self):
        self.premiere()
        self.consigner(recul("continuer"))
        self.code("2 * x", "la correction")
        texte, note = self.relire()
        self.assertIn("## Le second regard : les causes des passes d'avant", texte)
        self.assertIn("dis s'il a la même cause que l'un d'eux, « même cause : » suivi de celle-ci, ou une cause "
                      "nouvelle, « cause nouvelle »", texte)
        self.assertIn("- passe 1 : la correction change la lecture des commandes", texte)
        self.assertIn("passe 2 du lot L-0001 écrite", note)
        self.assertEqual([p.numero for p in memoire.passes(self.lot())], [1, 2])
        # Le reste du dossier est celui d'avant.
        self.assertEqual(re.sub(r"## Le second regard.*?\n\n(?=## )", "", texte, flags=re.S),
                         revue.dossier(self.projet))

    def test_a_partir_de_la_deuxieme_passe_chaque_bloquant_porte_le_regard_du_relecteur(self):
        self.premiere()
        self.consigner(recul("continuer"))
        self.passe("2 * x", bloquants("un test qui ne prouve rien"), "la correction")
        self.consigner(recul("continuer"))
        self.code("x + x + 0", "la seconde correction")
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire()
        self.assertIn("la passe 2 ne consigne pas le regard du relecteur sur 1 bloquant(s)", str(refus.exception))

    def deux_passes_ou_une_cause_revient(self, decision: str, demande: str = ""):
        self.premiere()
        self.consigner(recul("continuer"))
        self.passe("2 * x", bloquants("la lecture des commandes encore · même cause"), "la correction")
        self.consigner(recul("continuer"))
        self.passe("x + x + 0", bloquants("la lecture des commandes, toujours · même cause : passe 2"),
                   "la seconde correction")
        self.consigner(recul(decision, demande=demande))
        self.code("x * 2 + 0", "la troisième correction")

    def test_continuer_apres_deux_passes_ou_une_meme_cause_revient_est_refuse(self):
        self.deux_passes_ou_une_cause_revient("continuer")
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire()
        texte = str(refus.exception)
        self.assertIn("la passe 4 du lot L-0001 est refusée — le relecteur a vu une même cause revenir deux passes de "
                      "suite, aux passes 2 et 3 : « continuer » est refusé, le lot s'arrête", texte)
        self.assertIn("finit donc par « s'arrêter » : une demande à l'humain", texte)

    def test_une_seule_passe_ou_la_cause_revient_laisse_continuer(self):
        self.premiere()
        self.consigner(recul("continuer"))
        self.passe("2 * x", bloquants("la lecture des commandes encore · même cause"), "la correction")
        self.consigner(recul("continuer"))
        self.passe("x + x + 0", bloquants("un cas limite · cause nouvelle"), "la seconde correction")
        self.consigner(recul("continuer"))
        self.code("x * 2 + 0", "la troisième correction")
        texte, note = self.relire()
        self.assertIn("passe 4 du lot L-0001 écrite", note)

    def test_un_arret_attend_la_reponse_a_sa_demande(self):
        (self.racine / "memory/requests").mkdir()
        (self.racine / "memory/requests/D-0001-borner-la-regle.md").write_text(DEMANDE_DU_LOT)
        self.deux_passes_ou_une_cause_revient("s'arrêter", demande="D-0001")
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire()
        texte = str(refus.exception)
        self.assertIn("le lot s'est arrêté à la passe 3, et attend la réponse à D-0001 : il avance ailleurs "
                      "jusque-là", texte)
        self.assertNotIn("Trois questions", texte)
        # Sa réponse donnée, la passe suivante se produit.
        (self.racine / "memory/requests/D-0001-borner-la-regle.answer.toml").write_text(REPONSE)
        texte, note = self.relire()
        self.assertIn("passe 4 du lot L-0001 écrite", note)

    def ecrire_demande(self, ident: str, texte: str, repondue: bool = False):
        dossier = self.racine / "memory/requests"
        dossier.mkdir(exist_ok=True)
        (dossier / f"{ident}-une-demande.md").write_text(texte.replace("D-0001", ident))
        if repondue:
            (dossier / f"{ident}-une-demande.answer.toml").write_text(REPONSE)

    def test_une_demande_ancienne_repondue_qui_ne_cite_pas_le_lot_ne_leve_pas_l_arret(self):
        self.ecrire_demande("D-0001", DEMANDE, repondue=True)
        self.deux_passes_ou_une_cause_revient("s'arrêter", demande="D-0001")
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire()
        texte = str(refus.exception)
        self.assertIn("la passe 4 du lot L-0001 est refusée — l'arrêt de la passe 3 n'est levé par aucune des "
                      "demandes que nomme son recul (D-0001) : seule le lève la réponse de l'humain à une demande qui "
                      "cite le lot (L-0001) ; une demande retirée, ou qui ne le cite pas, ne le lève pas", texte)
        self.assertIn("finit donc par « s'arrêter » : une demande à l'humain, qui cite le lot (L-0001), que le "
                      "paragraphe nomme", texte)
        self.assertEqual(len(memoire.passes(self.lot())), 3)
        # La même, avec la demande du lot répondue : la passe se produit.
        self.ecrire_demande("D-0001", DEMANDE_DU_LOT, repondue=True)
        texte, note = self.relire()
        self.assertIn("passe 4 du lot L-0001 écrite", note)

    def test_une_demande_du_lot_retiree_ne_leve_pas_l_arret_meme_repondue(self):
        self.ecrire_demande("D-0001", DEMANDE_DU_LOT.replace("> date : 2026-11-16", RETIREE))
        self.deux_passes_ou_une_cause_revient("s'arrêter", demande="D-0001")
        for _ in range(2):
            with self.assertRaises(revue.PasseRefusee) as refus:
                self.relire()
            self.assertIn("l'arrêt de la passe 3 n'est levé par aucune des demandes que nomme son recul (D-0001)",
                          str(refus.exception))
            self.ecrire_demande("D-0001", DEMANDE_DU_LOT.replace("> date : 2026-11-16", RETIREE), repondue=True)

    def test_parmi_les_demandes_du_recul_une_du_lot_repondue_suffit(self):
        self.ecrire_demande("D-0001", DEMANDE, repondue=True)
        self.ecrire_demande("D-0002", DEMANDE_DU_LOT)
        self.deux_passes_ou_une_cause_revient("s'arrêter", demande="D-0001 et D-0002")
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire()
        self.assertIn("le lot s'est arrêté à la passe 3, et attend la réponse à D-0002 : il avance ailleurs "
                      "jusque-là", str(refus.exception))
        self.ecrire_demande("D-0002", DEMANDE_DU_LOT, repondue=True)
        texte, note = self.relire()
        self.assertIn("passe 4 du lot L-0001 écrite", note)

    def test_un_arret_sans_sa_demande_est_refuse(self):
        self.deux_passes_ou_une_cause_revient("s'arrêter")
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire()
        self.assertIn("le recul de la passe 3 s'arrête sans nommer sa demande", str(refus.exception))

    def test_la_commande_refuse_la_passe_sur_sa_sortie_d_erreur(self):
        self.premiere()
        self.code("2 * x", "la correction")
        code, out, err = commande(self.racine)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("la passe 2 du lot L-0001 est refusée", err)
        self.assertIn("- Bloquant : la correction change la lecture des commandes", err)

    def test_la_commande_ecrit_la_passe_et_le_dit_sur_sa_sortie_d_erreur(self):
        self.code("x * 2")
        code, out, err = commande(self.racine)
        self.assertEqual(code, 0)
        self.assertIn("## Le diff du lot (1 fichier(s), depuis origin/main)", out)
        self.assertIn("passe 1 du lot L-0001 écrite", err)
        self.assertIn("### Passe 1 — ", self.fichier_du_lot.read_text())


class TestCeQueGitDonne(_Depot):
    """D-0124, point 2 : les entrées ouvertes et closes depuis le début du
    lot, et les lots clos qui ont touché les mêmes fichiers."""

    def test_le_refus_donne_les_entrees_ouvertes_et_closes_et_les_lots_voisins(self):
        # Un lot d'avant, clos, dont un commit qui changeait calc.py cite la
        # tâche, et un lot clos qui n'a rien touché de ce lot.
        self.ecrire_source("memory/backlog/T-0009-un-ancien-travail.md",
                           TACHE.replace("T-0001 — Écrire double", "T-0009 — Un ancien travail").format(
                               statut="fait", ref=" · ref : J-2026-11-16-A"))
        self.ecrire_source("memory/backlog/L-0007-le-lot-d-avant.md",
                           LOT.format(id="L-0007", statut="fait", apres="T-0009", ref=" · ref : J-2026-11-16-A")
                           .replace("Le lot du doublement", "Le lot d'avant"))
        self.ecrire_source("memory/backlog/L-0008-un-lot-ailleurs.md",
                           LOT.format(id="L-0008", statut="fait", apres="T-0001", ref=" · ref : J-2026-11-16-A")
                           .replace("Le lot du doublement", "Un lot ailleurs"))
        (self.source / "calc.py").write_text("def double(x):\n    return x + x  # T-0009\n")
        git(self.source, "add", "-A")
        git(self.source, "commit", "-qm", "T-0009 : un ancien travail sur calc.py")
        git(self.racine, "pull", "-q", "--rebase", "origin", "main")
        self.code("x * 2")
        self.relire()
        (self.racine / "memory/backlog/T-0002-une-tache-ouverte.md").write_text(
            TACHE.replace("T-0001 — Écrire double", "T-0002 — Une tâche ouverte").format(statut="ouvert", ref=""))
        p = self.racine / "memory/backlog/T-0001-ecrire-double.md"
        p.write_text(TACHE.format(statut="fait", ref=" · ref : J-2026-11-16-A"))
        self.code("2 * x", "la correction")
        with self.assertRaises(revue.PasseRefusee) as refus:
            self.relire()
        texte = str(refus.exception)
        ouvertes = texte.split("Les entrées que le lot a ouvertes :\n")[1].split("\n\n")[0]
        closes = texte.split("Les entrées qu'il a closes :\n")[1].split("\n\n")[0]
        voisins = texte.split("Les lots clos qui ont touché les mêmes fichiers :\n")[1].split("\n\n")[0]
        self.assertEqual(ouvertes, "- T-0002 — Une tâche ouverte et son test")
        self.assertEqual(closes, "- T-0001 — Écrire double et son test")
        self.assertEqual(voisins, "- L-0007 — Le lot d'avant")
        # Les mêmes, par les fonctions qui les calculent.
        debut = git(self.racine, "merge-base", "origin/main", "HEAD").strip()
        ouvertes, closes = revue.entrees_depuis(self.projet, debut)
        self.assertEqual(([e.id for e in ouvertes], [e.id for e in closes]), (["T-0002"], ["T-0001"]))
        self.assertEqual([e.id for e in revue.lots_voisins(self.projet, debut, self.lot())], ["L-0007"])
        self.assertIn("la passe 1 n'a pas son recul",
                      revue.refus_de_la_passe(self.projet, self.lot(), memoire.passes(self.lot()), debut))


class TestLaCloture(unittest.TestCase):
    """D-0124, point 3 : un lot relu ne se clôt « fait » que si sa dernière
    passe a son recul ; un lot sans passe n'en a pas."""

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

    PASSES = ("\n## Revues\n\n### Passe 1 — 2026-11-15\n\nCommits : 1a2b3c4..5d6e7f8\n\n- Bloquant : une cause\n\n"
              "{recul1}\n\n### Passe 2 — 2026-11-16\n\nCommits : 5d6e7f8..9a8b7c6\n\n{recul2}\n")

    def test_un_lot_clos_sans_le_recul_de_sa_derniere_passe_est_refuse(self):
        erreurs = self.erreurs(self.PASSES.format(recul1=recul("continuer"), recul2=""))
        self.assertEqual(erreurs, ["`L-0001` est clos « fait » sans le recul de sa dernière passe de revue : la "
                                   "passe 2 n'a pas son recul : un paragraphe qui commence par « Recul : »"])
        self.assertIn("a 7 mot(s)", self.erreurs(self.PASSES.format(recul1=recul("continuer"), recul2=COURT))[0])

    def test_avec_son_recul_ou_sans_passe_il_se_clot(self):
        self.assertEqual(self.erreurs(self.PASSES.format(recul1="", recul2=recul("continuer"))), [])
        self.assertEqual(self.erreurs(""), [])
        # Ouvert, il n'a pas encore à l'avoir.
        self.assertEqual(self.erreurs(self.PASSES.format(recul1="", recul2=""), statut="en cours"), [])


    def test_une_ligne_de_bloquant_mal_ecrite_est_refusee_a_tout_statut(self):
        # T-0054 : ignorée, elle n'exigeait ni le regard du relecteur ni la règle de la même cause.
        revues = ("\n## Revues\n\n### Passe 1 — 2026-11-15\n\nCommits : 1a2b3c4..5d6e7f8\n\n{ligne}\n"
                  "- Bloquant : une cause lue\n\n" + recul("continuer") + "\n")
        for ligne in ("- **Bloquant** : une cause", "- Bloquant 1 : une cause", "1. Bloquant : une cause"):
            for statut in ("en cours", "fait"):
                with self.subTest(ligne=ligne, statut=statut):
                    self.assertEqual(self.erreurs(revues.format(ligne=ligne), statut), [
                        f"`L-0001` : « {ligne} », dans sa section « Revues », se donne pour un bloquant sans la "
                        "forme que lit `socle review`, une ligne `- Bloquant : <sa cause>` par bloquant, ni gras, ni "
                        "numéro, ni pluriel ; ignorée, elle n'exigerait ni le regard du relecteur ni la règle de la "
                        "même cause"])
        self.assertEqual(self.erreurs(revues.format(ligne="- Bloquant : une autre cause")), [])


class TestLaClotureSuitLesReglesDeLaPasse(unittest.TestCase):
    """La clôture « fait » d'un lot relu applique à sa dernière passe les
    règles qui refuseraient une passe de plus (`memoire.refus_de_la_suite`),
    sans ce que git donne : le regard du relecteur à partir de la deuxième
    passe, « continuer » après deux passes où une même cause revient, et
    l'arrêt, que seule lève la réponse à une demande qui cite le lot."""

    def memoire_du_lot(self, *suivantes: str, demandes: dict | None = None,
                       repondues: tuple = ()) -> memoire.Memoire:
        """Le lot L-0001 clos « fait », sa passe 1 avec son recul, puis une
        passe par texte de `suivantes` ; les demandes `demandes`, celles de
        `repondues` avec leur réponse."""
        revues = (f"\n## Revues\n\n### Passe 1 — 2026-11-14\n\nCommits : 1a2b3c4..5d6e7f8\n\n"
                  f"{bloquants('une cause')}\n{recul('continuer')}\n")
        for i, texte in enumerate(suivantes, start=2):
            revues += f"\n### Passe {i} — 2026-11-14\n\nCommits : 5d6e7f8..9a8b7c6\n\n{texte}\n"
        mem = memoire.Memoire(Path("."), None)
        chemin = "memory/backlog/closed/L-0001-un-lot.md"
        mem.fichiers[chemin] = memoire.analyser(chemin, ENTETE + "# L-0001 — Un lot\n\n> statut : fait · origine : "
                                                "J-2026-11-16-A · ref : J-2026-11-16-A\n\nSon corps.\n" + revues)
        for ident, texte in (demandes or {}).items():
            c = f"memory/requests/{ident}-une-demande.md"
            mem.fichiers[c] = memoire.analyser(c, texte.replace("D-0001", ident))
            if ident in repondues:
                mem.repondues.add(c)
        return mem

    def erreurs(self, *suivantes: str, **demandes) -> list[str]:
        r = Rapport()
        controles_memoire.backlog(types.SimpleNamespace(memoire=self.memoire_du_lot(*suivantes, **demandes)), r)
        return [c.message for c in r.erreurs("memoire.backlog")]

    def test_continuer_apres_deux_passes_ou_une_meme_cause_revient_ne_clot_pas(self):
        meme = bloquants("la lecture encore · même cause") + "\n" + recul("continuer")
        self.assertEqual(self.erreurs(meme, meme), [
            "`L-0001` est clos « fait » avant ce que sa dernière passe de revue exige : le relecteur a vu une même "
            "cause revenir deux passes de suite, aux passes 2 et 3 : « continuer » est refusé, le lot s'arrête"])
        # Une seule passe où la cause revient : il se clôt.
        self.assertEqual(self.erreurs(meme, bloquants("un oubli · cause nouvelle") + "\n" + recul("continuer")), [])

    def test_un_bloquant_sans_le_regard_du_relecteur_ne_clot_pas(self):
        erreurs = self.erreurs(bloquants("un oubli") + "\n" + recul("continuer"))
        self.assertEqual(erreurs, ["`L-0001` est clos « fait » avant ce que sa dernière passe de revue exige : la "
                                   "passe 2 ne consigne pas le regard du relecteur sur 1 bloquant(s), « · même cause » "
                                   "ou « · cause nouvelle » au bout de sa ligne : un oubli"])
        self.assertEqual(self.erreurs(bloquants("un oubli · cause nouvelle") + "\n" + recul("continuer")), [])

    def test_un_arret_ne_clot_qu_apres_la_reponse_a_la_demande_du_lot(self):
        arret = bloquants("la lecture encore · même cause") + "\n" + recul("s'arrêter", demande="D-0001")
        self.assertEqual(self.erreurs(arret, demandes={"D-0001": DEMANDE_DU_LOT}), [
            "`L-0001` est clos « fait » avant ce que sa dernière passe de revue exige : le lot s'est arrêté à la "
            "passe 2, et attend la réponse à D-0001 : il avance ailleurs jusque-là"])
        self.assertEqual(self.erreurs(arret, demandes={"D-0001": DEMANDE_DU_LOT}, repondues=("D-0001",)), [])
        # Une demande ancienne répondue qui ne cite pas le lot, ou une demande
        # du lot retirée, ne le lève pas ; un arrêt sans demande non plus.
        for demande in (DEMANDE, DEMANDE_DU_LOT.replace("> date : 2026-11-16", RETIREE)):
            with self.subTest(demande=demande[:90]):
                erreurs = self.erreurs(arret, demandes={"D-0001": demande}, repondues=("D-0001",))
                self.assertEqual(len(erreurs), 1)
                self.assertIn("n'est levé par aucune des demandes que nomme son recul (D-0001)", erreurs[0])
        self.assertIn("s'arrête sans nommer sa demande", self.erreurs(recul("s'arrêter"))[0])

    def test_une_fonction_pour_la_passe_et_la_cloture(self):
        mem = self.memoire_du_lot(bloquants("la lecture encore · même cause") + "\n" +
                                  recul("s'arrêter", demande="D-0001 et D-0002"),
                                  demandes={"D-0001": DEMANDE, "D-0002": DEMANDE_DU_LOT}, repondues=("D-0001",))
        lot = mem.entree("L-0001")
        self.assertTrue(memoire.cite_le_lot(mem.entree("D-0002"), lot))
        self.assertFalse(memoire.cite_le_lot(mem.entree("D-0001"), lot))
        self.assertEqual([memoire.leve_l_arret(mem, lot, d) for d in ("D-0001", "D-0002", "D-0099")],
                         [False, False, False])
        self.assertEqual(memoire.refus_de_la_suite(mem, lot, memoire.passes(lot)),
                         ("attente", "le lot s'est arrêté à la passe 2, et attend la réponse à D-0002 : il avance "
                                     "ailleurs jusque-là"))
        mem.repondues.add(mem.entree("D-0002").fichier)
        self.assertTrue(memoire.leve_l_arret(mem, lot, "D-0002"))
        self.assertIsNone(memoire.refus_de_la_suite(mem, lot, memoire.passes(lot)))
        # Un ancien numéro du lot le cite aussi.
        ancien = memoire.analyser("memory/backlog/L-0001-un-lot.md", ENTETE + "# L-0001 — Un lot\n\n> statut : fait "
                                  "· origine : J-2026-11-16-A · ancien : B-0269\n").entrees[0]
        self.assertTrue(memoire.cite_le_lot(memoire.analyser("memory/requests/D-0003-x.md", DEMANDE.replace(
            "fait tourner le lot", "fait tourner le lot B-0269")).entrees[0], ancien))


class TestUnCloneNeuf(_Depot):
    """D-0124, point 8 : l'historique d'un lot se lit depuis un clone neuf,
    et `socle review` y produit la passe suivante avec ses causes."""

    def test_l_historique_se_lit_d_une_session_neuve(self):
        self.code("x * 2")
        self.relire()
        self.consigner(bloquants("la correction change la lecture des commandes") + "\n" + recul("continuer"))
        git(self.racine, "commit", "-qam", "la passe 1 consignée")
        git(self.racine, "push", "-q", "origin", "travail")
        neuf = self.dossier / "neuf"
        git(self.dossier, "clone", "-q", "-b", "travail", str(self.source), str(neuf))
        lot = memoire.Memoire.charger(neuf).entree("L-0001")
        p, = memoire.passes(lot)
        self.assertEqual((p.numero, p.date, p.bloquants), (1, JOUR, [("la correction change la lecture des "
                                                                       "commandes", None)]))
        self.assertIsNone(memoire.refus_du_recul(p))
        (neuf / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        git(neuf, "commit", "-qam", "la correction")
        texte, note = revue.relire(config.Projet(racine=neuf), "origin/main", jour=JOUR)
        self.assertIn("- passe 1 : la correction change la lecture des commandes", texte)
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
