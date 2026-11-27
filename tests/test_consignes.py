"""B-0161 : la couche des consignes de l'humain. Chaque consigne a son
identifiant (`C-`), sa ligne de résumé, sa source et son texte exact ; le
démarrage donne la ligne de résumé de celles qui sont en vigueur ; une
consigne citée dans la mémoire porte son empreinte ; son texte exact ne
change jamais, et seule une demande validée la lève."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import (archive as archivage, checks_docs as controles_docs, cli, config, context as contexte,
                   checks_memory as controles_memoire,
                   installer as installeur, language as langue, memory as memoire, private as prive,
                   state as etat)
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
# Un identifiant privé ne s'écrit pas en clair dans un fichier public.
PC = "P" + "C"


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


ENTETE = "<!-- socle: couche=consignes zone=publique -->\n# Consignes\n"
JOURNAL = """<!-- socle: couche=journal zone=publique -->
# Journal — 2026-11

## J-2026-11-12-A — Théo donne ses consignes

Il écrit : « Pas de dépendance externe. » et « La roadmap au format court. »
"""


def consigne(n: int, titre: str = "", statut: str = "en vigueur", source: str = "J-2026-11-12-A",
             texte: str = "", ident: str = "C") -> str:
    titre = titre or f"La consigne numéro {n}"
    texte = texte if texte else f"> « Le texte exact de la consigne {n}. »"
    return f"\n## {ident}-{n:04d} — {titre}\n\n> statut : {statut} · source : {source} · date : 2026-11-12\n\n{texte}\n"


class Depot(unittest.TestCase):
    """Un dépôt minimal : un journal, des consignes, commités en base ; la
    suite du test change l'arbre de travail, que les contrôles jugent
    contre la base."""

    consignes = consigne(1) + consigne(2, "La roadmap demandée se donne au format court")

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-consignes-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "memory/journal").mkdir(parents=True)
        self.journal = self.racine / "memory/journal/2026-11.md"
        self.journal.write_text(JOURNAL)
        self.directives = self.racine / "memory/directives.md"
        self.directives.write_text(ENTETE + self.consignes)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def ecrire(self, chemin: Path, avant: str, apres: str):
        texte = chemin.read_text()
        self.assertIn(avant, texte)
        chemin.write_text(texte.replace(avant, apres, 1))

    def constats(self, *controles, base: bool = True) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base if base else None,
                                tete=None)
        r = Rapport()
        for f in controles:
            f(ctx, r)
        return [c.message for c in r.erreurs()]

    def empreinte(self, ident: str) -> str:
        return memoire.empreinte_entree(memoire.Memoire.charger(self.racine).entree(ident))

    def demande(self, n: int, reponse: str | None):
        """Une demande, avec la réponse de l'humain si elle est donnée."""
        d = self.racine / "memory/requests"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"D-{n:04d}-lever.md").write_text(
            f"<!-- socle: couche=demandes zone=publique -->\n# D-{n:04d} — Lever une consigne\n\n> date : "
            "2026-11-20\n\n## Décision donnée\n\nElle ne vaut plus.\n")
        if reponse:
            (d / f"D-{n:04d}-lever.answer.toml").write_text(f'reponse = "{reponse}"\npar = "Théo"\n')


class TestLecture(unittest.TestCase):
    def test_une_consigne_se_lit_comme_une_entree_de_sa_couche(self):
        f = memoire.analyser("memory/directives.md", ENTETE + consigne(3) + consigne(4, statut="levée"))
        self.assertEqual((f.couche, f.zone), ("consignes", "publique"))
        self.assertEqual([(e.id, e.type) for e in f.entrees], [("C-0003", "C"), ("C-0004", "C")])
        self.assertEqual([e.statut for e in f.entrees], ["en-vigueur", "levee"])
        self.assertEqual(f.entrees[0].refs("source"), [("id", "J-2026-11-12-A")])
        self.assertEqual(memoire.couche_attendue("memory/directives.md"), "consignes")
        self.assertEqual(memoire.couche_attendue("memory/private/directives.md"), "consignes")
        self.assertEqual(config.FORMAT_ACTUEL.consignes, "memory/directives.md")
        self.assertEqual(memoire.TYPES["C"], "consignes")
        self.assertIn("consignes", memoire.COUCHES)

    def test_les_mots_anglais_se_lisent_aussi(self):
        f = memoire.analyser("memory/directives.md", "<!-- socle: layer=directives zone=public -->\n"
                             "\n## C-0001 — Short roadmap\n\n> status : lifted · lifted-by : D-0002\n\n> “Short.”\n")
        e = f.entrees[0]
        self.assertEqual((f.couche, e.statut), ("consignes", "levee"))
        self.assertEqual(e.refs("levee-par"), [("id", "D-0002")])
        self.assertEqual(langue.mot(langue.STATUTS["C"], "en-vigueur", "en"), "in force")

    def test_une_mention_nue_se_distingue_d_une_citation(self):
        texte = "Selon C-0003 et C-0004@0123abcd, voir aussi F-0001.\n```\nC-0009 en exemple\n```\n"
        self.assertEqual(memoire.mentions_nues(texte, ("C",)), [("C-0003", 1)])
        self.assertIn(("C-0004", 1), memoire.mentions(texte))
        self.assertEqual(memoire.mentions_nues(f"{PC}-0002 seule", ("C",)), [(f"{PC}-0002", 1)])

    def test_une_consigne_levee_peut_s_archiver_dans_le_journal(self):
        texte = JOURNAL + "\n## J-2026-11-20-A — Rangement\n\nRangées.\n" + consigne(1, statut="levée").replace(
            "## C-0001", "### C-0001")
        e = memoire.analyser("memory/journal/2026-11.md", texte).entrees[-1]
        self.assertEqual((e.id, e.parent), ("C-0001", "J-2026-11-20-A"))


class TestFormat(Depot):
    def format(self) -> list[str]:
        return self.constats(controles_memoire.format_memoire, base=False)

    def test_une_consigne_bien_formee_passe(self):
        self.assertEqual([m for m in self.format() if "C-" in m], [])

    def test_une_ligne_de_resume_de_plus_de_120_octets_est_refusee(self):
        titre = "Le module reste sans dépendance, ni bibliothèque externe, ni outil de construction, ni rien que la " \
                "bibliothèque standard"
        self.assertGreater(len(titre.encode("utf-8")), 120)
        self.directives.write_text(ENTETE + consigne(1, titre))
        self.assertTrue(any("`C-0001` : sa ligne de résumé fait" in m and "120 au plus" in m for m in self.format()))
        self.directives.write_text(ENTETE + consigne(1, "é" * 60))  # 120 octets : dans la borne
        self.assertFalse(any("ligne de résumé" in m for m in self.format()))

    def test_une_consigne_sans_source_du_journal_ou_d_une_demande_est_refusee(self):
        for source in ("", "fichier:memory/journal/2026-11.md", "F-0001"):
            with self.subTest(source=source):
                self.directives.write_text(ENTETE + consigne(1, source=source).replace(" · source : ·", " ·"))
                self.assertTrue(any("`C-0001` sans `source`" in m for m in self.format()), source)

    def test_une_consigne_sans_son_texte_exact_cite_est_refusee(self):
        self.directives.write_text(ENTETE + consigne(1, texte="Pas de dépendance."))
        self.assertTrue(any("`C-0001` sans le texte exact de l'humain" in m for m in self.format()))
        # Collée à la ligne de métadonnées, la citation en ferait partie.
        self.directives.write_text(ENTETE + consigne(1).replace("2026-11-12\n\n>", "2026-11-12\n>"))
        self.assertTrue(any("`C-0001` sans le texte exact de l'humain" in m for m in self.format()))

    def test_un_statut_inconnu_est_refuse(self):
        self.directives.write_text(ENTETE + consigne(1, statut="suspendue"))
        self.assertTrue(any("`C-0001` : statut « suspendue » inconnu" in m for m in self.format()))

    def test_une_consigne_hors_de_sa_couche_est_refusee(self):
        (self.racine / "memory/canonical.md").write_text("<!-- socle: couche=canonique zone=publique -->\n"
                                                         + consigne(5))
        self.assertTrue(any("`C-0005` n'a pas sa place dans la couche « canonique »" in m for m in self.format()))


class TestCopie(Depot):
    """Le texte exact d'une consigne recopie la parole de l'humain
    consignée au journal : ce n'est pas une copie qui divergera."""

    PAROLE = ("Je veux que chaque session parte de la branche par défaut, que rien ne se pousse ailleurs que sur "
              "la branche de son environnement, et que la pull request ouverte soit fusionnée avant qu'une autre "
              "ne s'ouvre, sans exception.")

    def copies(self) -> list[str]:
        return self.constats(controles_docs.copie)

    def test_la_citation_d_une_consigne_reprend_sa_source_sans_refus(self):
        self.assertGreaterEqual(len(self.PAROLE), 200)
        self.journal.write_text(JOURNAL + f"\n## J-2026-11-20-A — Théo donne une consigne\n\n> {self.PAROLE}\n")
        self.directives.write_text(ENTETE + consigne(3, source="J-2026-11-20-A", texte=f"> {self.PAROLE}"))
        self.assertEqual(self.copies(), [])
        # Ailleurs, la même copie reste refusée.
        (self.racine / "docs").mkdir()
        (self.racine / "docs/notes.md").write_text(f"# Notes\n\n> {self.PAROLE}\n")
        self.assertTrue(any("paragraphe identique aussi présent" in m for m in self.copies()))

    def test_le_contexte_d_une_consigne_se_juge_comme_tout_fichier(self):
        """Hors de ses lignes citées, une consigne qui recopie une doc
        vivante est une copie qui divergera : refusée."""
        (self.racine / "docs").mkdir()
        (self.racine / "docs/notes.md").write_text(f"# Notes\n\n{self.PAROLE}\n")
        self.directives.write_text(ENTETE + consigne(3) + f"\n{self.PAROLE}\n")
        erreurs = self.copies()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("paragraphe identique aussi présent", erreurs[0])

    def test_la_consigne_privee_aussi(self):
        prive = self.racine / "memory/private"
        prive.mkdir()
        (prive / "directives.md").write_text(ENTETE.replace("publique", "privée")
                                             + consigne(1, ident=PC, texte=f"> {self.PAROLE}"))
        self.journal.write_text(JOURNAL + f"\n## J-2026-11-20-A — Théo donne une consigne\n\n> {self.PAROLE}\n")
        self.assertEqual(self.copies(), [])


class TestLevee(Depot):
    def preuves(self) -> list[str]:
        return self.constats(controles_memoire.preuves, base=False)

    def test_une_consigne_levee_sans_levee_par_est_refusee(self):
        self.ecrire(self.directives, "> statut : en vigueur", "> statut : levée")
        self.assertTrue(any("`C-0001` levée sans `levée-par : D-NNNN`" in m for m in self.preuves()))

    def test_une_consigne_levee_par_une_demande_sans_valider_est_refusee(self):
        for reponse in (None, "refuser"):
            with self.subTest(reponse=reponse):
                self.demande(7, reponse)
                self.directives.write_text(ENTETE + consigne(1, statut="levée · levée-par : D-0007"))
                self.assertIn("`C-0001` cite `D-0007`, qui n'a pas de réponse « valider »", self.preuves())

    def test_une_consigne_levee_par_une_demande_validee_passe(self):
        self.demande(7, "valider")
        self.directives.write_text(ENTETE + consigne(1, statut="levée · levée-par : D-0007"))
        self.assertEqual(self.preuves(), [])


class TestAjoutSeul(Depot):
    def ajout_seul(self) -> list[str]:
        return self.constats(controles_memoire.ajout_seul)

    def test_le_texte_exact_ne_change_jamais(self):
        self.ecrire(self.directives, "Le texte exact de la consigne 1.", "Un texte exact réécrit.")
        self.assertTrue(any("consigne `C-0001` : son texte exact a changé" in m for m in self.ajout_seul()))

    def test_la_ligne_de_resume_et_les_metadonnees_peuvent_changer(self):
        self.ecrire(self.directives, "La consigne numéro 1", "La consigne numéro 1, mieux résumée")
        self.ecrire(self.directives, "> statut : en vigueur · source : J-2026-11-12-A · date : 2026-11-12\n\n"
                    "> « Le texte exact de la consigne 1",
                    "> statut : levée · levée-par : D-0007 · source : J-2026-11-12-A · date : 2026-11-12\n\n"
                    "> « Le texte exact de la consigne 1")
        self.assertEqual(self.ajout_seul(), [])

    def test_une_consigne_ne_s_efface_pas(self):
        self.directives.write_text(ENTETE + consigne(2, "La roadmap demandée se donne au format court"))
        self.assertTrue(any("consigne `C-0001` effacée" in m for m in self.ajout_seul()))

    def test_seule_une_consigne_levee_se_range_dans_le_journal(self):
        self.directives.write_text(ENTETE + consigne(2, "La roadmap demandée se donne au format court"))
        rangement = "\n## J-2026-11-20-A — Rangement\n\nRangée.\n"
        self.journal.write_text(JOURNAL + rangement + consigne(1).replace("## C-0001", "### C-0001"))
        self.assertTrue(any("consigne `C-0001` rangée dans le journal sans être levée" in m
                            for m in self.ajout_seul()))
        self.journal.write_text(JOURNAL + rangement + consigne(1, statut="levée · levée-par : D-0007").replace(
            "## C-0001", "### C-0001"))
        self.assertEqual(self.ajout_seul(), [])


class TestLecturesProuvees(Depot):
    def lectures(self) -> list[str]:
        return self.constats(controles_memoire.lectures)

    def entree_de_journal(self, texte: str):
        self.journal.write_text(JOURNAL + f"\n## J-2026-11-20-A — Constat\n\n{texte}\n")

    def test_une_consigne_citee_sans_empreinte_dans_le_journal_est_refusee(self):
        self.entree_de_journal("Selon C-0002, la roadmap est courte.")
        erreurs = self.lectures()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("`C-0002`, une consigne de l'humain, cité sans son empreinte", erreurs[0])
        self.assertIn("`python3 .socle/socle show C-0002`", erreurs[0])

    def test_une_consigne_citee_avec_son_empreinte_actuelle_passe(self):
        self.entree_de_journal(f"Selon C-0002@{self.empreinte('C-0002')}, la roadmap est courte.")
        self.assertEqual(self.lectures(), [])

    def test_une_empreinte_perimee_ou_inventee_est_refusee(self):
        perimee = self.empreinte("C-0002")
        self.ecrire(self.directives, "au format court", "au format court, sans détail")
        for h in (perimee, "0badc0de"):
            with self.subTest(h=h):
                self.entree_de_journal(f"Selon C-0002@{h}, la roadmap est courte.")
                erreurs = self.lectures()
                self.assertEqual(len(erreurs), 1, erreurs)
                self.assertIn(f"`C-0002@{h}` ne correspond pas à la version actuelle", erreurs[0])

    def test_le_chantier_actif_aussi(self):
        actif = self.racine / "memory/active.md"
        actif.write_text("<!-- socle: couche=actif zone=publique -->\n# Chantier actif\n\nSuivre C-0001.\n")
        self.assertTrue(any("`C-0001`, une consigne de l'humain, cité sans son empreinte" in m
                            for m in self.lectures()))

    def test_une_mention_deja_la_a_la_base_ne_se_rejuge_pas(self):
        actif = self.racine / "memory/active.md"
        actif.write_text("<!-- socle: couche=actif zone=publique -->\n# Chantier actif\n\nSuivre C-0001.\n")
        self.entree_de_journal("Selon C-0002, la roadmap est courte.")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "mentions nues d'avant la règle")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        actif.write_text(actif.read_text() + "\nPuis la suite.\n")
        self.journal.write_text(self.journal.read_text() + "\nUne ligne de plus.\n")
        self.assertEqual(self.lectures(), [])

    def test_sa_definition_et_une_consigne_inexistante_ne_se_jugent_pas_ici(self):
        self.directives.write_text(self.directives.read_text() + consigne(3))
        self.entree_de_journal("Une consigne C-0099 qui n'existe pas.")
        self.assertEqual(self.lectures(), [])

    def test_la_question_d_une_decision_en_seance_recopie_la_conversation(self):
        d = self.racine / "memory/requests"
        d.mkdir()
        (d / "D-0007-lever-la-consigne-c-0002.md").write_text(
            "<!-- socle: couche=demandes zone=publique -->\n# D-0007 — Lever la consigne C-0002\n\n"
            "> date : 2026-11-20 · forme : séance\n\n## Décision donnée\n\nC-0002 ne vaut plus.\n")
        self.assertEqual(self.lectures(), [])
        self.entree_de_journal("Théo lève C-0002 (D-0007).")
        self.assertEqual(len(self.lectures()), 1)


class TestArchive(Depot):
    consignes = consigne(1, statut="levée · levée-par : D-0007") + consigne(2, "La roadmap au format court")

    def test_socle_archive_range_les_levees_dans_le_journal(self):
        projet = config.Projet.charger(self.racine)
        ranges = archivage.ranger_consignes(projet, "2026-11-25")
        self.assertEqual(ranges, [("C-0001", "memory/journal/2026-11.md")])
        mem = memoire.Memoire.charger(self.racine)
        e = mem.entree("C-0001")
        self.assertEqual((e.fichier, e.parent, e.statut), ("memory/journal/2026-11.md", "J-2026-11-25-A", "levee"))
        self.assertEqual(self.directives.read_text(), ENTETE + consigne(2, "La roadmap au format court"))
        self.assertIn("### C-0001 — La consigne numéro 1", self.journal.read_text())
        self.demande(7, "valider")
        (self.racine / "memory/canonical.md").write_text("<!-- socle: couche=canonique zone=publique -->\n")
        (self.racine / "memory/active.md").write_text("<!-- socle: couche=actif zone=publique -->\n")
        self.assertEqual(self.constats(controles_memoire.format_memoire, controles_memoire.ajout_seul,
                                       controles_memoire.lectures, controles_memoire.preuves), [])
        self.assertEqual(archivage.ranger_consignes(projet, "2026-11-25"), [])


class TestDemarrage(Depot):
    consignes = (consigne(1, "Opus partout depuis le 12 novembre") + consigne(2, "Une consigne levée", "levée")
                 + consigne(3, "La roadmap demandée se donne au format court"))

    def test_l_etat_donne_la_ligne_de_resume_des_consignes_en_vigueur_et_pas_les_levees(self):
        prive_ = self.racine / "memory/private"
        prive_.mkdir()
        (prive_ / "directives.md").write_text("<!-- socle: couche=consignes zone=privee -->\n"
                                              + consigne(1, "Une consigne privée", ident=PC))
        projet = config.Projet.charger(self.racine)
        parties = etat.parties_injectees(projet, memoire.Memoire.charger(self.racine))
        consignes = [p for p in parties if p.groupe == "consignes"]
        self.assertEqual([p.lignes for p in consignes],
                         [["C-0001 — Opus partout depuis le 12 novembre",
                           "C-0003 — La roadmap demandée se donne au format court"],
                          [f"{PC}-0001 — Une consigne privée"]])
        self.assertEqual(consignes[0].entete(2, 2), ["", (
            "--- memory/directives.md : 2 consigne(s) en vigueur, par leur ligne de résumé ; avant de s'appuyer sur "
            "une, de l'appliquer à un cas que sa ligne ne tranche pas ou de la citer, son texte exact : `python3 "
            ".socle/socle show C-NNNN` ---")])
        self.assertIn("1 consigne(s) en vigueur sur 2", consignes[0].entete(1, 2)[1])
        self.assertEqual(consignes[0].manque(1, 2), "1 consigne(s) sur 2 : lire memory/directives.md")
        sortie = etat.borner(parties, 9500)
        self.assertEqual(sortie, ["", *consignes[0].entete(2, 2)[1:], *consignes[0].lignes,
                                  "", *consignes[1].entete(1, 1)[1:], *consignes[1].lignes])
        self.assertNotIn("C-0002 — Une consigne levée", sortie)

    def test_les_consignes_viennent_juste_apres_le_chantier_actif_dans_leur_part(self):
        (self.racine / "memory/active.md").write_text("<!-- socle: couche=actif zone=publique -->\n# Chantier actif\n")
        (self.racine / "memory/canonical.md").write_text(
            "<!-- socle: couche=canonique zone=publique -->\n\n## F-0001 — Un fait\n\n> statut : mesuré · "
            "preuve : fichier:memory/journal/2026-11.md\n")
        projet = config.Projet.charger(self.racine)
        groupes = [p.groupe for p in etat.parties_injectees(projet, memoire.Memoire.charger(self.racine))]
        self.assertEqual(groupes, ["actif", "consignes", "faits"])
        self.assertEqual(etat.PARTS, {"etat": 0.25, "actif": 0.18, "consignes": 0.25, "faits": 0.20,
                                      "decisions": 0.12})
        self.assertEqual(etat.GROUPES["consignes"], "les consignes")
        self.assertEqual(etat.budget_actif_permis(projet), int(9500 * 0.18) - 60)
        self.assertEqual([e.id for e in etat.consignes_en_vigueur(memoire.Memoire.charger(self.racine),
                                                                  "memory/directives.md")], ["C-0001", "C-0003"])

    def test_des_consignes_au_dela_de_leur_part_se_coupent_et_disent_ou_lire_le_reste(self):
        self.directives.write_text(ENTETE + "".join(consigne(n, f"La consigne numéro {n}, " + "x" * 90)
                                                    for n in range(1, 41)))
        # Les autres groupes débordent aussi de leur part : peu à partager.
        (self.racine / "memory/canonical.md").write_text("<!-- socle: couche=canonique zone=publique -->\n" + "".join(
            f"\n## F-{n:04d} — Le fait numéro {n}, " + "y" * 50 + "\n\n> statut : supposé\n" for n in range(1, 81)))
        (self.racine / "memory/active.md").write_text("<!-- socle: couche=actif zone=publique -->\n" + "z\n" * 3000)
        projet = config.Projet.charger(self.racine)
        sortie = etat.borner(etat.parties_injectees(projet, memoire.Memoire.charger(self.racine)), 9500)
        montrees = [l for l in sortie if l.startswith("C-")]
        self.assertTrue(0 < len(montrees) < 40, len(montrees))
        self.assertEqual(montrees, [f"C-{n:04d} — La consigne numéro {n}, " + "x" * 90
                                    for n in range(1, len(montrees) + 1)])
        self.assertRegex(sortie[-1], r"^!! coupé à la borne du démarrage .* ; les consignes, \d+ octets pour une "
                                     rf"part de 2375 — {40 - len(montrees)} consigne\(s\) sur 40 : lire "
                                     r"memory/directives\.md ; les faits, ")


class Installe(unittest.TestCase):
    """Un projet installé, sur un dépôt neuf."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-consignes-installe-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        self.installer()

    def installer(self) -> str:
        with contextlib.redirect_stdout(io.StringIO()) as flux:
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        return flux.getvalue()

    def socle(self, *args) -> tuple[int, str]:
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            code = cli.main(["--root", str(self.racine), *args])
        return code, sortie.getvalue()


class TestInstallation(Installe):
    def test_l_installeur_pose_les_consignes_vides_et_les_repose_a_la_mise_a_jour(self):
        directives = self.racine / "memory/directives.md"
        modele = (MOTEUR / "socle/templates/memory/directives.md").read_text()
        self.assertEqual(directives.read_text(), modele)
        self.assertEqual(memoire.analyser("memory/directives.md", modele).couche, "consignes")
        self.assertEqual(memoire.analyser("memory/directives.md", (
            MOTEUR / "socle/templates/memory/directives.en.md").read_text()).couche, "consignes")
        gf = (self.racine / ".socle/guardrails.toml").read_text()
        self.assertIn('"memory/directives.md" = { max_bytes = 24000 }', gf)
        self.assertIn('"memory/active.md" = { max_bytes = 1600 }', gf)
        directives.unlink()
        self.installer()
        self.assertEqual(directives.read_text(), modele)

    def test_une_mise_a_jour_garde_les_consignes_ecrites(self):
        directives = self.racine / "memory/directives.md"
        directives.write_text(directives.read_text() + consigne(1))
        self.installer()
        self.assertIn("## C-0001 — La consigne numéro 1", directives.read_text())


class TestCommandes(Installe):
    def test_socle_new_directive_pose_le_squelette_et_socle_show_son_empreinte(self):
        code, sortie = self.socle("new", "directive", "La roadmap demandée se donne au format court")
        self.assertEqual(code, 0, sortie)
        self.assertIn("C-0001\tmemory/directives.md", sortie)
        texte = (self.racine / "memory/directives.md").read_text()
        self.assertIn("\n## C-0001 — La roadmap demandée se donne au format court\n\n> statut : en vigueur · "
                      "source : <J-… ou D-… où la parole de l'humain est consignée> · date : ", texte)
        self.assertIn("> « <le texte exact de l'humain, mot pour mot> »", texte)
        code, sortie = self.socle("show", "C-0001")
        self.assertEqual(code, 0, sortie)
        e = memoire.Memoire.charger(self.racine).entree("C-0001")
        self.assertIn(f"--- C-0001@{memoire.empreinte_entree(e)} (memory/directives.md:", sortie)
        code, sortie = self.socle("new", "directive", "Une seconde")
        self.assertIn("C-0002\tmemory/directives.md", sortie)

    def test_socle_archive_dit_les_consignes_rangees(self):
        directives = self.racine / "memory/directives.md"
        directives.write_text(directives.read_text() + consigne(1, statut="levée · levée-par : D-0001"))
        code, sortie = self.socle("archive")
        self.assertEqual(code, 0, sortie)
        self.assertIn("C-0001 → memory/journal/", sortie)
        self.assertIn("1 consigne(s) levée(s) rangée(s) dans le journal", sortie)
        code, sortie = self.socle("show", "C-0001")
        self.assertIn(", archivée dans J-", sortie)


class TestMemoirePrivee(Installe):
    def regler(self, texte: str) -> config.Projet:
        pol = self.racine / ".socle/policy.toml"
        pol.write_text(pol.read_text() + "\n[private]\n" + texte)
        return config.Projet.charger(self.racine)

    def test_les_consignes_ne_sont_privees_que_si_la_politique_les_nomme(self):
        self.assertNotIn("consignes", prive.couches_privees(self.regler('mode = "chiffre"\n')))
        self.assertIn("consignes", prive.COUCHES_PRIVABLES)

    def test_nommees_par_la_politique_elles_s_ecrivent_dans_la_zone_privee(self):
        projet = self.regler('mode = "chiffre"\nlayers = ["consignes"]\n')
        self.assertEqual(prive.couches_privees(projet), {"consignes"})
        code, sortie = self.socle("new", "directive", "Une consigne privée")
        self.assertEqual(code, 0, sortie)
        self.assertIn(f"{PC}-0001\tmemory/private/directives.md", sortie)
        self.assertTrue((self.racine / "memory/private/directives.md").read_text().startswith(
            "<!-- socle: couche=consignes zone=privee -->\n"))


class TestCeQueRecoitUnProjet(unittest.TestCase):
    """T-0189 : le gabarit d'`AGENTS.md`, le guide, les skills et la note de
    version disent la couche des consignes, dans les deux langues."""

    REGLES = {
        "fr": ("Une consigne de l'humain donnée dans la conversation, qui vaut au-delà du tour (une règle, une "
               "préférence, une interdiction), s'écrit dans la mémoire avant de continuer, dans les consignes "
               "(`socle new directive`), avec son texte exact, et au journal",
               "Avant de s'appuyer sur une consigne, son texte exact se lit.",
               "| Consignes | `memory/directives.md` |", "(`F-`, `C-`, `B-`,",
               "le chantier actif, les consignes en vigueur, les titres des faits"),
        "en": ("An instruction from the human given in the conversation, that holds beyond the turn (a rule, a "
               "preference, a prohibition), is written into the memory before going on, in the directives "
               "(`socle new directive`), with its exact text, and in the journal",
               "Before relying on a directive, its exact text is read.",
               "| Directives | `memory/directives.md` |", "(`F-`, `C-`, `B-`,",
               "the active work, the directives in force, the titles of the facts"),
    }
    ANCIENNES = {"fr": "au chantier actif si elle touche le travail en cours",
                 "en": "in the active work if it concerns the work in progress"}

    def test_le_gabarit_d_agents_md_envoie_une_consigne_dans_les_consignes_sans_grossir(self):
        from socle.templates import gabarit

        for lg, phrases in self.REGLES.items():
            texte = gabarit("AGENTS.md", lg)
            agents = " ".join(texte.split())
            for phrase in phrases:
                self.assertIn(phrase, agents, (lg, phrase))
            self.assertNotIn(self.ANCIENNES[lg], agents, lg)
            # Le gabarit ne grossit pas : la section se recopie dans des
            # instructions déjà près de leur budget.
            self.assertLessEqual(len(texte.encode("utf-8")), {"fr": 14625, "en": 13865}[lg], lg)

    def test_le_guide_et_les_skills_disent_ou_va_une_consigne_et_comment_elle_se_leve(self):
        from socle.templates import gabarit

        for nom, phrases in (("HELP.md", ("**Une consigne durable.**", "`socle new directive`", "(`levée-par`)")),
                             ("HELP.en.md", ("**A lasting directive.**", "`socle new directive`", "(`lifted-by`)"))):
            texte = " ".join((MOTEUR / "socle" / nom).read_text(encoding="utf-8").split())
            for phrase in phrases:
                self.assertIn(phrase, texte, (nom, phrase))
        for lg, phrase in (("fr", "Une consigne de l'humain ne se lève que par sa parole : elle se consigne ainsi, "
                                  "en séance, puis la consigne passe `levée`, avec `levée-par : D-NNNN`"),
                           ("en", "A directive of the human is only lifted by their word: it is recorded this way, "
                                  "in session, then the directive becomes `lifted`, with `lifted-by : D-NNNN`")):
            texte = gabarit("skills/socle-request/SKILL.md", lg)
            self.assertIn(phrase, " ".join(texte.split()), lg)
            self.assertLessEqual(len(texte.encode("utf-8")), 10000, lg)

    def test_la_note_de_version_dit_le_changement_et_la_migration_dans_les_deux_langues(self):
        for nom, titre, migration in (
                ("CHANGES.md", "Les consignes durables de l'humain ont leur couche",
                 "À faire : migrer les consignes du chantier actif dans la couche, une par une"),
                ("CHANGES.en.md", "The human's lasting directives have their layer",
                 "To do: migrate the directives of the active work into the layer, one by one")):
            entrees = dict(installeur.entrees_des_notes((MOTEUR / "socle" / nom).read_text(encoding="utf-8")))
            note = entrees["2026-11-25-e"]
            self.assertIn(titre, note)
            texte = " ".join(note.split())
            self.assertIn(migration, texte)
            self.assertIn('`"memory/directives.md" = { max_bytes = 16000 }`', texte)
            self.assertIn("`socle new directive", texte)
            self.assertFalse(installeur.ne_demande_rien(note))


if __name__ == "__main__":
    unittest.main()
