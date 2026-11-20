"""ADR-0100 (D-0144) : le recul n'est plus exigé. `socle review` écrit les
passes d'un lot au-delà de la première sans recul de la précédente, ni
marque de cause, ni arrêt sur une demande ; le contrôle du backlog laisse se
clore « fait » un lot relu sans recul ; la section « Revues » garde ses
passes, leurs commits et leurs bloquants, lisibles d'une session neuve ; ni
les skills de revue et de lot, ni le guide, ni le format ne disent le
recul."""

import shutil
import tempfile
import types
import unittest
from pathlib import Path

from socle import checks_memory as controles_memoire, config, language as langue, memory as memoire, \
    review as revue
from socle.report import Rapport
from tests.test_revue import commande, git

MOTEUR = Path(__file__).resolve().parent.parent / "engine" / "socle"
JOUR = "2026-11-20"
ENTETE = "<!-- socle: couche=backlog zone=publique -->\n"
BESOIN = (ENTETE + "# B-0001 — Doubler\n\n> statut : ouvert · origine : J-2026-11-20-A\n\nPour l'essai.\n\n"
          "## Satisfait quand\n\n- [ ] le module double\n")
TACHE = (ENTETE + "# T-0001 — Écrire double et son test\n\n> statut : ouvert · origine : J-2026-11-20-A · "
         "besoin : B-0001\n\nPour l'essai.\n\n## Fait quand\n\n- [x] le test passe\n")
LOT = (ENTETE + "# L-0001 — Le lot du doublement\n\n> statut : en cours · origine : J-2026-11-20-A · "
       "après : T-0001\n\nCe qui réunit ses tâches : le module de calcul.\n")
# Une demande du lot qui attend sa réponse : avant ADR-0100, un « Recul :
# … s'arrêter » qui la nommait arrêtait le lot.
DEMANDE = ("<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Borner la règle qui fait tourner le lot "
           "L-0001\n\n> date : 2026-11-20\n\nLa règle tourne ; une proposition la borne.\n")


def bloquants(*causes: str) -> str:
    return "".join(f"- Bloquant : {c}\n" for c in causes) + "- Ouvre : rien\n"


class _Depot(unittest.TestCase):
    """Un dépôt cloné, sa branche de travail, un besoin, sa tâche et le lot
    en cours qui l'attend."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-sans-recul-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        self.source = self.dossier / "source"
        (self.source / "memory/backlog").mkdir(parents=True)
        (self.source / "memory/requests").mkdir(parents=True)
        git(self.source, "init", "-q", "-b", "main")
        (self.source / "calc.py").write_text("def double(x):\n    return x + x\n")
        (self.source / "memory/backlog/B-0001-doubler.md").write_text(BESOIN)
        (self.source / "memory/backlog/T-0001-ecrire-double.md").write_text(TACHE)
        (self.source / "memory/backlog/L-0001-le-lot-du-doublement.md").write_text(LOT)
        (self.source / "memory/requests/D-0001-borner-la-regle.md").write_text(DEMANDE)
        git(self.source, "add", "-A")
        git(self.source, "commit", "-qm", "un")
        self.racine = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(self.source), str(self.racine))
        git(self.racine, "switch", "-q", "-c", "travail")
        self.projet = config.Projet(racine=self.racine)

    @property
    def fichier_du_lot(self) -> Path:
        return self.racine / "memory/backlog/L-0001-le-lot-du-doublement.md"

    def lot(self) -> memoire.Entree:
        return memoire.Memoire.charger(self.racine).entree("L-0001")

    def code(self, corps: str, message: str):
        (self.racine / "calc.py").write_text(f"def double(x):\n    return {corps}\n")
        git(self.racine, "commit", "-qam", message)

    def consigner(self, texte: str):
        """Ce que l'agent écrit au bout de la dernière passe du lot."""
        p = self.fichier_du_lot
        p.write_text(p.read_text().rstrip("\n") + "\n\n" + texte.strip("\n") + "\n")


class TestUnePasseAuDelaDeLaPremiere(_Depot):
    def test_les_passes_suivantes_s_ecrivent_sans_recul_ni_regard_ni_arret(self):
        self.code("x * 2", "le lot")
        _, note = revue.relire(self.projet, jour=JOUR)
        self.assertIn("passe 1 du lot L-0001 écrite", note)
        self.consigner(bloquants("la correction change la lecture des commandes"))
        # Ni recul, ni regard du relecteur : la passe 2 s'écrit.
        self.code("2 * x", "la correction")
        texte, note = revue.relire(self.projet, jour=JOUR)
        self.assertIn("passe 2 du lot L-0001 écrite", note)
        self.assertNotIn("Recul", note)
        self.assertNotIn("même cause", note)
        # Son dossier est celui de toute passe : ni second regard, ni les
        # causes d'avant.
        self.assertEqual(texte, revue.dossier(self.projet))
        self.assertNotIn("second regard", texte)
        self.assertNotIn("la correction change la lecture des commandes", texte)
        # Un bloquant sans marque de cause, puis un ancien recul qui
        # s'arrêtait sur une demande du lot encore sans réponse : la passe 3
        # s'écrit aussi, par la commande.
        self.consigner(bloquants("un test qui ne prouve rien") + "\nRecul : la cause revient, s'arrêter sur "
                       "D-0001 : s'arrêter.\n")
        self.code("x + x + 0", "la seconde correction")
        code, _, err = commande(self.racine)
        self.assertEqual(code, 0, err)
        self.assertIn("passe 3 du lot L-0001 écrite", err)
        self.assertEqual([p.numero for p in memoire.passes(self.lot())], [1, 2, 3])


class TestLaSectionRevues(_Depot):
    def test_la_section_garde_ses_passes_et_leurs_bloquants(self):
        self.code("x * 2", "le lot")
        revue.relire(self.projet, jour=JOUR)
        self.consigner(bloquants("la correction change la lecture des commandes", "un cas limite oublié"))
        self.code("2 * x", "la correction")
        revue.relire(self.projet, jour="2026-11-21")
        self.consigner(bloquants("un test qui ne prouve rien"))
        self.code("x + x + 0", "la seconde correction")
        revue.relire(self.projet, jour="2026-11-22")
        passes = memoire.passes(self.lot())
        self.assertEqual([(p.numero, p.date) for p in passes],
                         [(1, JOUR), (2, "2026-11-21"), (3, "2026-11-22")])
        self.assertEqual([p.bloquants for p in passes],
                         [["la correction change la lecture des commandes", "un cas limite oublié"],
                          ["un test qui ne prouve rien"], []])
        # Chaque passe garde ses commits, depuis le début du lot jusqu'à la
        # tête qu'elle a relue.
        debut = git(self.racine, "rev-parse", "--short", "origin/main").strip()
        self.assertEqual({p.debut for p in passes}, {debut})
        self.assertEqual(len({p.tete for p in passes}), 3)
        # La section garde, dans le fichier, les lignes « Bloquant » et
        # « Ouvre » de chaque passe, sous son titre.
        section = memoire.section_des_revues(self.lot())
        for ligne in ("### Passe 1 — " + JOUR, "- Bloquant : la correction change la lecture des commandes",
                      "- Bloquant : un cas limite oublié", "### Passe 2 — 2026-11-21",
                      "- Bloquant : un test qui ne prouve rien", "- Ouvre : rien", "### Passe 3 — 2026-11-22"):
            self.assertIn(ligne, section)
        self.assertLess(section.index("un cas limite oublié"), section.index("### Passe 2"))
        # Une session neuve la lit de même, d'un clone de la branche poussée.
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "les passes consignées")
        git(self.racine, "push", "-q", "origin", "travail")
        neuf = self.dossier / "neuf"
        git(self.dossier, "clone", "-q", "-b", "travail", str(self.source), str(neuf))
        relues = memoire.passes(memoire.Memoire.charger(neuf).entree("L-0001"))
        self.assertEqual([(p.numero, p.bloquants) for p in relues], [(p.numero, p.bloquants) for p in passes])

    def test_une_section_ecrite_avant_adr_0099_se_lit_encore(self):
        # Un ancien recul et d'anciennes marques de cause restent du texte : la
        # passe garde ses bloquants, la marque comprise.
        texte = (LOT + "\n## Revues\n\n### Passe 1 — 2026-11-15\n\nCommits : 1a2b3c4..5d6e7f8\n\n"
                 "- Bloquant : une cause\n- Ouvre : T-0002\n\nRecul : la cause ne revient pas, continuer.\n\n"
                 "### Passe 2 — 2026-11-16\n\nCommits : 5d6e7f8..9a8b7c6\n\n"
                 "- Bloquant : la même encore · même cause : passe 1\n- Ouvre : rien\n")
        lot = memoire.analyser("memory/backlog/L-0001-un-lot.md", texte).entrees[0]
        self.assertEqual([(p.numero, p.debut, p.tete, p.bloquants) for p in memoire.passes(lot)],
                         [(1, "1a2b3c4", "5d6e7f8", ["une cause"]),
                          (2, "5d6e7f8", "9a8b7c6", ["la même encore · même cause : passe 1"])])
        # De même en anglais.
        anglais = (ENTETE + "# L-0001 — A batch\n\n> status : in progress · origin : J-2026-11-20-A\n\n"
                   "## Reviews\n\n### Pass 1 — 2026-11-16\n\nCommits: 1a2b3c4..5d6e7f8\n\n- Blocker: a cause\n"
                   "- Opens: none\n")
        p, = memoire.passes(memoire.analyser("memory/backlog/L-0001-a-batch.md", anglais).entrees[0])
        self.assertEqual((p.debut, p.bloquants), ("1a2b3c4", ["a cause"]))


class TestLaClotureSansRecul(unittest.TestCase):
    def erreurs(self, revues: str) -> list[str]:
        """Les erreurs de `memoire.backlog` sur le lot L-0001 clos « fait »
        avec la section `revues`, et la demande D-0001 du lot, sans
        réponse."""
        mem = memoire.Memoire(Path("."), None)
        chemin = "memory/backlog/closed/L-0001-un-lot.md"
        mem.fichiers[chemin] = memoire.analyser(chemin, ENTETE + "# L-0001 — Un lot\n\n> statut : fait · origine : "
                                                "J-2026-11-20-A · ref : J-2026-11-20-A\n\nSon corps.\n" + revues)
        demande = "memory/requests/D-0001-borner-la-regle.md"
        mem.fichiers[demande] = memoire.analyser(demande, DEMANDE)
        r = Rapport()
        controles_memoire.backlog(types.SimpleNamespace(memoire=mem), r)
        return [c.message for c in r.erreurs("memoire.backlog")]

    def test_un_lot_relu_se_clot_sans_recul(self):
        passe = "\n### Passe {n} — 2026-11-20\n\nCommits : 1a2b3c4..5d6e7f8\n\n{corps}"
        revues = "\n## Revues\n" + "".join(passe.format(n=n, corps=bloquants(f"la cause {n}")) for n in (1, 2, 3))
        self.assertEqual(self.erreurs(revues), [])
        # Deux passes de suite où une même cause revient, et un « continuer »
        # trop court : il se clôt aussi.
        meme = bloquants("la lecture encore · même cause") + "\nRecul : continuer.\n"
        self.assertEqual(self.erreurs("\n## Revues\n" + passe.format(n=1, corps=bloquants("la lecture")) +
                                      passe.format(n=2, corps=meme) + passe.format(n=3, corps=meme)), [])
        # Un ancien arrêt sur la demande du lot, qui attend encore sa réponse :
        # il se clôt.
        arret = bloquants("la lecture encore") + "\nRecul : la règle tourne, D-0001 la borne : s'arrêter.\n"
        self.assertEqual(self.erreurs("\n## Revues\n" + passe.format(n=1, corps=arret)), [])
        # Sans passe, de même.
        self.assertEqual(self.erreurs(""), [])

    def test_une_ligne_de_bloquant_mal_ecrite_reste_refusee(self):
        # Le format de l'historique reste jugé : une ligne qu'il ne lirait pas.
        revues = "\n## Revues\n\n### Passe 1 — 2026-11-20\n\nCommits : 1a2b3c4..5d6e7f8\n\n- **Bloquant** : une cause\n"
        erreurs = self.erreurs(revues)
        self.assertEqual(len(erreurs), 1)
        self.assertIn("« - **Bloquant** : une cause », dans sa section « Revues », se donne pour un bloquant", erreurs[0])
        self.assertNotIn("recul", erreurs[0])
        self.assertNotIn("regard", erreurs[0])


class TestLeRetraitDuRecul(unittest.TestCase):
    def test_ni_les_skills_ni_le_guide_ni_le_format_ne_disent_le_recul(self):
        fichiers = ["templates/skills/socle-review/SKILL.md", "templates/skills/socle-review/SKILL.en.md",
                    "templates/skills/socle-batch/SKILL.md", "templates/skills/socle-batch/SKILL.en.md",
                    "HELP.md", "HELP.en.md", "FORMAT.md"]
        for rel in fichiers:
            texte = " ".join((MOTEUR / rel).read_text(encoding="utf-8").split())
            with self.subTest(fichier=rel):
                for mot in ("« Recul : »", "Recul : <", "“Step back:”", "step back", "son recul",
                            "· même cause", "· same cause", "« s'arrêter »", "“stop”", "tourne en rond",
                            "round in circles", "refuserait la suivante", "would refuse the next one"):
                    self.assertNotIn(mot, texte)
        # Le vocabulaire de la section ne garde que ses passes et leurs lignes.
        self.assertEqual(sorted(langue.REVUES), ["arbre", "bloquant", "commits", "ouvre", "passe", "revues"])
        # Les deux skills disent encore la section « Revues » et ses bloquants.
        for rel, mots in (("templates/skills/socle-review/SKILL.md", ("## Revues", "- Bloquant :", "- Ouvre :")),
                          ("templates/skills/socle-review/SKILL.en.md", ("## Reviews", "- Blocker:", "- Opens:"))):
            texte = " ".join((MOTEUR / rel).read_text(encoding="utf-8").split())
            for mot in mots:
                self.assertIn(mot, texte, rel)


if __name__ == "__main__":
    unittest.main()
