"""B-0029 : ce qui est privé se choisit couche par couche, et entrée par
entrée ; une entrée publique existante se bascule dans la mémoire privée
sans casser un renvoi, et sans rien effacer."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import cli, config, contexte, controles_memoire, etat, installeur, memoire, prive
from socle.rapport import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "moteur"
# Un identifiant privé ne s'écrit pas en clair dans un fichier public.
P = "P"
SUJET = """
## B-0001 — Démarcher le client Orion

> statut : ouvert · origine : {journal} · lu : backlog@00000000

Le contrat se signe en novembre.
"""
DECISION = """<!-- socle: couche=decisions zone=publique -->
# ADR-0001 — Viser le client Orion

> statut : acceptée · date : 2026-10-11

## Décision

Le premier client sera Orion.
"""
DOC = ("Voir [le sujet](../memory/backlog.md#b-0001--démarcher-le-client-orion) et "
       "[la décision](../memory/decisions/ADR-0001-viser-le-client-orion.md).\n")


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class Projet(unittest.TestCase):
    """Un projet installé, une mémoire privée en mode chiffré (sans filtre :
    l'arbre de travail se lit en clair), un sujet et une décision publics
    que des documents citent."""

    prive_ = 'mode = "chiffre"\n'

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-bascule-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        with contextlib.redirect_stdout(io.StringIO()):
            # Le backlog en un fichier ; le format 3 a ses tests (`test_format_3`).
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR, format_memoire=2)
        pol = self.racine / ".socle/policy.toml"
        pol.write_text(pol.read_text() + "\n[private]\n" + self.prive_)
        journal = next((self.racine / "memory/journal").glob("*.md"))
        ident = journal.read_text().split("## ", 2)[1].split(" ", 1)[0]
        backlog = self.racine / "memory/backlog.md"
        backlog.write_text(backlog.read_text().rstrip("\n") + "\n" + SUJET.format(journal=ident))
        (self.racine / "memory/decisions").mkdir(exist_ok=True)
        (self.racine / "memory/decisions/ADR-0001-viser-le-client-orion.md").write_text(DECISION)
        (self.racine / "docs").mkdir(exist_ok=True)
        (self.racine / "docs/notes.md").write_text(DOC)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        config.oublier_formats()
        self.projet = config.Projet.charger(self.racine)

    def socle(self, *args) -> tuple[int, str]:
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            code = cli.main(["--root", str(self.racine), *args])
        return code, sortie.getvalue()

    def erreurs(self) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.base)
        r = Rapport()
        for f in (controles_memoire.format_memoire, controles_memoire.references, controles_memoire.backlog,
                  controles_memoire.ajout_seul, controles_memoire.lectures, controles_memoire.prive):
            f(ctx, r)
        return [c.message for c in r.erreurs()]


class TestCouches(Projet):
    def regler(self, texte: str):
        pol = self.racine / ".socle/policy.toml"
        pol.write_text(pol.read_text().split("\n[private]\n")[0] + "\n[private]\n" + texte)
        self.projet = config.Projet.charger(self.racine)

    def test_par_defaut_tout_est_prive_sauf_les_demandes(self):
        self.assertEqual(prive.couches_privees(self.projet), {"canonique", "backlog", "decisions", "journal"})
        self.regler('mode = "chiffre"\nrequests = true\n')
        self.assertIn("demandes", prive.couches_privees(self.projet))

    def test_la_politique_choisit_les_couches(self):
        self.regler('mode = "chiffre"\nlayers = ["decisions", "journal", "inconnue"]\n')
        self.assertEqual(prive.couches_privees(self.projet), {"decisions", "journal"})
        self.assertEqual(prive.couches_inconnues(self.projet), ["inconnue"])

    def test_sans_memoire_privee_rien_n_est_prive(self):
        self.regler("")
        self.assertEqual(prive.couches_privees(self.projet), set())

    def test_new_suit_les_couches_et_la_consigne_de_l_humain(self):
        self.regler('mode = "chiffre"\nlayers = ["decisions"]\n')
        self.assertIn("memory/canonical.md", self.socle("new", "fact", "Un fait public")[1])
        self.assertIn(f"memory/private/decisions/{P}ADR-0001", self.socle("new", "adr", "Une décision privée")[1])
        self.assertIn("memory/decisions/ADR-0002", self.socle("new", "adr", "Celle-ci publique", "--public")[1])
        self.assertIn("memory/private/canonical.md", self.socle("new", "fact", "Celui-ci privé", "--private")[1])


class TestBascule(Projet):
    def test_un_sujet_basculé_garde_son_identifiant_et_perd_son_texte(self):
        code, sortie = self.socle("prive", "basculer", "B-0001")
        self.assertEqual(code, 0, sortie)
        self.assertIn("l'historique public garde l'ancien texte", sortie)
        public = (self.racine / "memory/backlog.md").read_text()
        self.assertIn(f"## B-0001 — {memoire.TITRE_BASCULEE}", public)
        self.assertNotIn("Orion", public)
        copie = (self.racine / "memory/private/backlog.md").read_text()
        self.assertIn(f"## {P}B-0001 — Démarcher le client Orion", copie)
        self.assertIn("depuis : B-0001", copie)
        self.assertIn("Le contrat se signe en novembre.", copie)
        self.assertEqual(self.erreurs(), [])

    def test_une_decision_basculee_change_de_fichier_et_ses_liens_restent_valides(self):
        code, sortie = self.socle("prive", "basculer", "ADR-0001")
        self.assertEqual(code, 0, sortie)
        self.assertFalse((self.racine / "memory/decisions/ADR-0001-viser-le-client-orion.md").exists())
        self.assertNotIn("Orion", (self.racine / "memory/decisions/ADR-0001-basculee.md").read_text())
        self.assertIn("Le premier client sera Orion.",
                      (self.racine / f"memory/private/decisions/{P}ADR-0001-viser-le-client-orion.md").read_text())
        self.assertEqual(self.erreurs(), [])

    def test_en_ci_la_copie_privee_se_lit_a_la_revision(self):
        self.socle("prive", "basculer", "B-0001")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "bascule", "--no-verify")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete="HEAD")
        r = Rapport()
        controles_memoire.ajout_seul(ctx, r)
        self.assertEqual([c.message for c in r.constats if c.gravite != "ok"], [])
        self.assertIsNotNone(prive.memoire_privee(ctx))

    def test_l_index_ne_montre_plus_l_entree_basculee(self):
        self.socle("prive", "basculer", "B-0001")
        lignes = memoire.lignes_index(memoire.Memoire.charger(self.racine), "backlog")
        self.assertFalse(any(l.startswith("B-0001") for l in lignes), lignes)
        self.assertTrue(any(l.startswith(P + "B-0001") for l in lignes), lignes)

    def test_une_pierre_sans_copie_privee_est_un_effacement(self):
        backlog = self.racine / "memory/backlog.md"
        texte = backlog.read_text()
        debut = texte.index("## B-0001")
        backlog.write_text(texte[:debut] + f"## B-0001 — {memoire.TITRE_BASCULEE}\n\n> basculée : 2026-10-11\n")
        self.assertTrue(any("sans copie privée" in e for e in self.erreurs()), self.erreurs())

    def test_une_copie_qui_ne_reprend_pas_le_texte_est_refusee(self):
        self.socle("prive", "basculer", "B-0001")
        copie = self.racine / "memory/private/backlog.md"
        copie.write_text(copie.read_text().replace("Le contrat se signe en novembre.", "Rien."))
        self.assertTrue(any("n'en reprend ni le titre ni le texte" in e for e in self.erreurs()), self.erreurs())

    def test_une_pierre_garde_ni_titre_ni_texte(self):
        self.socle("prive", "basculer", "B-0001")
        backlog = self.racine / "memory/backlog.md"
        backlog.write_text(backlog.read_text().replace(memoire.TEXTE_BASCULEE, "Le client Orion."))
        self.assertTrue(any("garde un titre ou un texte" in e for e in self.erreurs()), self.erreurs())

    def test_une_entree_basculee_ne_change_plus(self):
        self.socle("prive", "basculer", "B-0001")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "bascule", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        backlog = self.racine / "memory/backlog.md"
        backlog.write_text(backlog.read_text().replace("> basculée : ", "> basculée : hier, "))
        self.assertTrue(any("elle reste telle quelle" in e for e in self.erreurs()), self.erreurs())

    def test_ce_qui_ne_se_bascule_pas(self):
        self.socle("new", "request", "Une question", "--public")
        for ident, motif in (("D-0001", "se lit là où l'humain lit"), ("B-0099", "aucune entrée"),
                             ("ADR-0001", None)):
            code, sortie = self.socle("prive", "basculer", ident)
            if motif:
                self.assertEqual(code, 1, sortie)
                self.assertIn(motif, sortie)
        code, sortie = self.socle("prive", "basculer", P + "ADR-0001")
        self.assertIn("déjà privée", sortie)

    def test_l_etat_du_demarrage_injecte_les_faits_prives(self):
        self.socle("new", "fact", "Un fait privé")
        self.assertIn("Un fait privé", etat.calculer(config.Projet.charger(self.racine)))


class TestSansMemoirePrivee(Projet):
    prive_ = ""

    def test_rien_ou_basculer(self):
        code, sortie = self.socle("prive", "basculer", "B-0001")
        self.assertEqual(code, 1)
        self.assertIn("aucune mémoire privée", sortie)


if __name__ == "__main__":
    unittest.main()
