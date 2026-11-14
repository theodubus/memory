"""B-0142, ADR-0074 : une réponse `valider` poussée avant le changement
qu'elle autorise ne le couvre plus au push suivant, que la CI d'un push et
le hook avant push jugent sur leur seule plage. `demandes.reponse-seule` le
dit avant qu'elle parte seule, sans rien refuser ; et une réponse consignée
aussitôt, pas encore commitée, n'est plus « en attente » dans l'état (la
gêne 6 de chess)."""

import contextlib
import io
import shutil
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from socle import (cli, config, context as contexte, checks_memory as controles_memoire, hooks,
                   installer as installeur, state as etat, utils as outils)
from socle.report import Rapport
from tests.test_attendus import MOTEUR, TEST, git

DEMANDE = """<!-- socle: couche=demandes zone=publique -->
# D-0001 — Le facteur passe à 3 ?

> date : 2026-11-14

## Décision demandée

{objet}

## Réponses possibles

- `valider` — je fais le changement.
- `refuser` — je garde tout tel quel.
"""
WORKFLOW = ".github/workflows/socle.yml"


class TestReponsePousseeSeule(unittest.TestCase):
    """Un projet installé, poussé sur une origine locale, et une branche de
    travail qui y a poussé sa demande ; l'humain y répond `valider`."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-reponse-seule-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        origine = self.racine.parent / (self.racine.name + "-origine.git")
        self.addCleanup(shutil.rmtree, origine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        (self.racine / "tests").mkdir()
        (self.racine / "tests/test_calc.py").write_text(TEST.format(attendu=4))
        (self.racine / "docs").mkdir()
        (self.racine / "docs/double.cas.json").write_text('[\n  {"entree": 2, "attendu": 4}\n]\n')
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(gf.read_text().replace("spec_paths =", 'case_paths = ["docs/*.cas.json"]\nspec_paths =', 1))
        pol = self.racine / ".socle/policy.toml"
        pol.write_text(pol.read_text().replace("[human]\n", '[human]\nrepo_url = "https://github.com/x/y"\n', 1))
        self.commit("base")
        git(self.racine.parent, "init", "-q", "--bare", str(origine))
        git(self.racine, "remote", "add", "origin", str(origine))
        git(self.racine, "push", "-q", "--no-verify", "origin", "main")
        git(self.racine, "checkout", "-qb", "travail")

    def commit(self, message):
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", message, "--no-verify")

    def tete(self) -> str:
        return git(self.racine, "rev-parse", "HEAD").strip()

    def demander(self, objet: str):
        """La demande, commitée et poussée telle quelle : l'humain l'a lue."""
        (self.racine / "memory/requests").mkdir(parents=True, exist_ok=True)
        (self.racine / "memory/requests/D-0001-facteur.md").write_text(DEMANDE.format(objet=objet))
        self.commit("La demande")
        git(self.racine, "push", "-q", "--no-verify", "-u", "origin", "travail")

    def repondre(self):
        """La réponse donnée dans la conversation, consignée aussitôt par
        l'agent, dans l'arbre, pas encore commitée."""
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as erreurs:
            code = cli.main(["--root", str(self.racine), "answer", "D-0001", "valider", "--relayed", "--by", "Théo",
                             "--quote", "oui, valide"])
        self.assertEqual(code, 0, erreurs.getvalue())

    def avertissements(self, etage="agent", tete=None, branches=None) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage=etage,
                                base=outils.base_de_travail(self.racine), tete=tete, branches=branches)
        r = Rapport()
        controles_memoire.reponse_seule(ctx, r)
        self.assertEqual(r.erreurs(), [])
        return [c.message for c in r.constats if c.controle == "demandes.reponse-seule"]

    def avant_push(self) -> tuple[int, str]:
        """Le hook avant push, sur le push de la branche vers son homonyme."""
        distant = git(self.racine, "rev-parse", "origin/travail").strip()
        ligne = f"refs/heads/travail {self.tete()} refs/heads/travail {distant}\n"
        with unittest.mock.patch("sys.stdin", io.StringIO(ligne)), contextlib.redirect_stderr(io.StringIO()) as flux:
            code = hooks.git_pre_push(config.Projet.charger(self.racine))
        return code, flux.getvalue()

    def test_la_reponse_seule_avertit_dans_l_arbre_au_commit_et_avant_le_push(self):
        self.demander("Valider que `test_double` attende 6.")
        self.repondre()
        dans_l_arbre = self.avertissements()
        self.assertEqual(len(dans_l_arbre), 1, dans_l_arbre)
        self.assertIn("réponse `valider` de D-0001", dans_l_arbre[0])
        self.assertIn("`test_double`", dans_l_arbre[0])
        self.assertIn("Poussée seule, elle ne couvrira pas ce changement", dans_l_arbre[0])
        self.commit("La réponse de Théo")
        self.assertEqual(len(self.avertissements("git", self.tete())), 1)
        # Le hook avant push laisse partir, et le dit : c'est un
        # avertissement, pas un refus.
        code, sortie = self.avant_push()
        self.assertEqual(code, 0, sortie)
        self.assertIn("socle — avertissement (demandes.reponse-seule) : ", sortie)
        self.assertIn("Poussée seule, elle ne couvrira pas ce changement", sortie)

    def test_avec_le_changement_qu_elle_autorise_rien_a_dire(self):
        self.demander("Valider que `test_double` attende 6.")
        self.repondre()
        (self.racine / "tests/test_calc.py").write_text(TEST.format(attendu=6))
        self.assertEqual(self.avertissements(), [])
        self.commit("La réponse et le test qu'elle autorise")
        self.assertEqual(self.avertissements("git", self.tete()), [])
        code, sortie = self.avant_push()
        self.assertEqual(code, 0, sortie)
        self.assertNotIn("Poussée seule", sortie)

    def test_une_reponse_deja_poussee_est_hors_de_la_plage(self):
        self.demander("Valider que `test_double` attende 6.")
        self.repondre()
        self.commit("La réponse de Théo")
        git(self.racine, "push", "-q", "--no-verify", "origin", "travail")
        self.assertEqual(self.avertissements(), [])

    def test_une_demande_qui_ne_nomme_ni_test_ni_fichier_ne_dit_rien(self):
        self.demander("Valider que le module de calcul se refonde d'abord.")
        self.repondre()
        self.assertEqual(self.avertissements(), [])

    def test_un_fichier_protege_cite_avec_son_empreinte(self):
        self.demander(f"Valider le workflow mis à jour :\n\n- `{WORKFLOW}` — `sha256:0123456789abcdef`")
        self.repondre()
        avertis = self.avertissements()
        self.assertEqual(len(avertis), 1, avertis)
        self.assertIn(f"`{WORKFLOW}`", avertis[0])
        p = self.racine / WORKFLOW
        p.write_text(p.read_text() + "\n# changé\n")
        self.assertEqual(self.avertissements(), [])

    def test_un_fichier_protege_cite_sans_empreinte_ne_compte_pas(self):
        self.demander(f"Valider que `{WORKFLOW}` reste tel quel.")
        self.repondre()
        self.assertEqual(self.avertissements(), [])

    def test_un_fichier_deja_pousse_sous_la_demande_en_attente_precede_sa_reponse(self):
        """D-0071 : le fichier protégé part avant la réponse, sous la demande
        en attente ; la réponse qui le suit seule ne l'oublie pas."""
        self.demander(f"Valider le workflow mis à jour :\n\n- `{WORKFLOW}` — `sha256:0123456789abcdef`")
        p = self.racine / WORKFLOW
        p.write_text(p.read_text() + "\n# changé\n")
        self.commit("Le workflow, en attente de D-0001")
        git(self.racine, "push", "-q", "--no-verify", "origin", "travail")
        self.repondre()
        self.assertEqual(self.avertissements(), [])

    def test_un_fichier_de_cas_cite(self):
        self.demander("Valider que `docs/double.cas.json` attende 6 pour 3.")
        self.repondre()
        avertis = self.avertissements()
        self.assertEqual(len(avertis), 1, avertis)
        self.assertIn("`docs/double.cas.json`", avertis[0])
        (self.racine / "docs/double.cas.json").write_text('[\n  {"entree": 2, "attendu": 6}\n]\n')
        self.assertEqual(self.avertissements(), [])

    def test_la_base_non_poussee(self):
        self.demander("Valider que `test_double` attende 6.")
        poussee = self.tete()
        git(self.racine, "commit", "-q", "--allow-empty", "-m", "Un commit de plus", "--no-verify")
        # La branche suivie, puis son homonyme distante sans suivi.
        self.assertEqual(outils.base_non_poussee(self.racine), poussee)
        git(self.racine, "branch", "-q", "--unset-upstream")
        self.assertEqual(outils.base_non_poussee(self.racine), poussee)
        # Au hook avant push, la branche où part le push ; une branche neuve
        # se juge depuis la branche par défaut.
        self.assertEqual(outils.base_non_poussee(self.racine, ["travail"]), poussee)
        self.assertEqual(outils.base_non_poussee(self.racine, ["neuve"]), outils.base_de_travail(self.racine))
        git(self.racine, "checkout", "-qb", "autre")
        self.assertEqual(outils.base_non_poussee(self.racine), outils.base_de_travail(self.racine))

    def test_une_reponse_consignee_mais_pas_commitee_n_est_plus_en_attente(self):
        """La gêne 6 de chess : l'état lit l'arbre, fichiers non suivis
        compris ; la réponse consignée aussitôt y est répondue."""
        self.demander("Valider que `test_double` attende 6.")
        projet = config.Projet.charger(self.racine)
        avant = etat.calculer(projet, contenus=False)
        self.assertIn("demandes humaines en attente : 1", avant)
        self.repondre()
        self.assertEqual(git(self.racine, "status", "--porcelain", "--", "memory/requests").count("??"), 1)
        apres = etat.calculer(config.Projet.charger(self.racine), contenus=False)
        self.assertIn("demandes humaines en attente : 0", apres)
        self.assertNotIn("D-0001 — Le facteur passe à 3", apres)


class TestSansCommit(unittest.TestCase):
    def test_un_depot_sans_commit_n_a_pas_de_base(self):
        vide = Path(tempfile.mkdtemp(prefix="socle-vide-"))
        self.addCleanup(shutil.rmtree, vide, ignore_errors=True)
        git(vide, "init", "-q", "-b", "main")
        self.assertIsNone(outils.base_non_poussee(vide))


if __name__ == "__main__":
    unittest.main()
