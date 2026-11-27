"""ADR-0117 (T-0214) : `socle close` clôt une entrée du backlog en un
geste, son statut, sa référence et son rangement, sans rien cocher ; la
valeur `ce commit` du champ `ref` désigne le commit qui la clôt, que
l'historique de son fichier retrouve."""

import contextlib
import io
import unittest
from argparse import Namespace

from socle import archive as archivage, cli, config, context as contexte, memory as memoire
from socle import selftest as autotest
from tests.test_format_3 import Format3, git

TACHE = """
## T-0001 — Écrire triple et son test

> statut : en cours · origine : fichier:calc.py · besoin : B-0001{champs}

Pour l'essai.

## Fait quand

{criteres}
"""


class Cloture(Format3):
    """Le projet du format 3 : B-0001 ouvert, B-0002 clos et rangé ; plus
    T-0001, la tâche de B-0001, commitée."""

    criteres = "- [x] triple existe\n- [x] son test passe"
    champs = ""

    def setUp(self):
        super().setUp()
        autotest.ajouter_sujet(self.racine, TACHE.format(criteres=self.criteres, champs=self.champs))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "la tâche", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        self.ouverte = self.racine / "memory/backlog/T-0001-ecrire-triple-et-son-test.md"
        self.close = self.racine / "memory/backlog/closed/T-0001-ecrire-triple-et-son-test.md"

    def constats_de_cloture(self) -> list[str]:
        """Les erreurs des contrôles qui jugent une entrée close."""
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="git", base=self.base)
        return [c.message for c in contexte.executer(ctx, archivage.CONTROLES_DE_CLOTURE).erreurs()]


class TestUneTacheCochee(Cloture):
    def test_se_clot_reference_et_rangee_en_une_commande(self):
        code, sortie = self.socle("close", "T-0001")
        self.assertEqual(code, 0, sortie)
        self.assertIn("`T-0001` clos « fait », ref : ce commit", sortie)
        self.assertFalse(self.ouverte.exists())
        texte = self.close.read_text()
        self.assertIn("> statut : fait · origine : fichier:calc.py · besoin : B-0001 · ref : ce commit\n", texte)
        # Les cases restent comme l'agent les a cochées.
        self.assertIn("- [x] triple existe\n- [x] son test passe", texte)
        # Le déplacement est dans l'index, comme celui de `socle archive`.
        self.assertIn("memory/backlog/closed/T-0001-ecrire-triple-et-son-test.md",
                      git(self.racine, "diff", "--cached", "--name-only"))
        self.assertEqual(self.constats_de_cloture(), [])
        self.assertEqual(self.erreurs(), [])

    def test_show_resout_ce_commit_par_l_historique_du_fichier(self):
        self.assertEqual(self.socle("close", "T-0001")[0], 0)
        code, sortie = self.socle("show", "T-0001")
        self.assertIn("--- ref « ce commit » : pas encore commité, le commit à venir ---", sortie)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "triple, et sa tâche close", "--no-verify")
        # Un commit d'après qui touche la ligne ne change pas le commit qui clôt.
        self.close.write_text(self.close.read_text().replace("> statut : fait", "> statut : fait · pour : humain"))
        git(self.racine, "commit", "-qam", "plus tard", "--no-verify")
        court = git(self.racine, "rev-parse", "--short", "HEAD~1").strip()
        code, sortie = self.socle("show", "T-0001")
        self.assertEqual(code, 0, sortie)
        self.assertIn(f"--- ref « ce commit » : {court} triple, et sa tâche close ---", sortie)

    def test_commit_qui_clot_rien_avant_le_commit_puis_lui(self):
        self.assertIsNone(archivage.commit_qui_clot(self.racine, memoire.Memoire.charger(self.racine).entree("T-0001")))
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            self.assertEqual(archivage.cloturer(config.Projet.charger(self.racine), "T-0001"), 0)
        self.assertIn("Ensuite : le commiter avec le travail qui le fait", sortie.getvalue())
        e = memoire.Memoire.charger(self.racine).entree("T-0001")
        self.assertIsNone(archivage.commit_qui_clot(self.racine, e))
        git(self.racine, "commit", "-qm", "T-0001 close", "--no-verify")
        self.assertEqual(archivage.commit_qui_clot(self.racine, e),
                         git(self.racine, "rev-parse", "--short", "HEAD").strip() + " T-0001 close")

    def test_la_commande_est_celle_de_l_agent(self):
        """`cli.cmd_close`, rangée parmi les commandes de l'agent, `--ref` facultatif."""
        args = cli.analyseur()[0].parse_args(["close", "T-0001"])
        self.assertIs(args.f, cli.cmd_close)
        self.assertIsNone(args.ref)
        self.assertIn("close", cli.GROUPES["pour l'agent"])
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.cmd_close(Namespace(root=str(self.racine), id="T-0099", ref=None)), 1)

    def test_une_ref_donnee_remplace_ce_commit(self):
        code, sortie = self.socle("close", "T-0001", "--ref", "fichier:calc.py")
        self.assertEqual(code, 0, sortie)
        self.assertIn("· besoin : B-0001 · ref : fichier:calc.py\n", self.close.read_text())
        self.assertEqual(self.constats_de_cloture(), [])

    def test_puis_son_besoin_se_clot_de_meme(self):
        self.assertEqual(self.socle("close", "T-0001")[0], 0)
        code, sortie = self.socle("close", "B-0001")
        self.assertEqual(code, 0, sortie)
        self.assertTrue(next((self.racine / "memory/backlog/closed").glob("B-0001-*.md")).is_file())
        self.assertEqual(self.constats_de_cloture(), [])


class TestUneRefDejaPortee(Cloture):
    champs = " · ref : fichier:calc.py"

    def test_la_reference_s_ajoute_a_celle_qu_elle_porte(self):
        self.assertEqual(self.socle("close", "T-0001")[0], 0)
        self.assertIn("· besoin : B-0001 · ref : fichier:calc.py, ce commit\n", self.close.read_text())

    def test_une_reference_deja_portee_ne_se_double_pas(self):
        self.assertEqual(self.socle("close", "T-0001", "--ref", "fichier:calc.py")[0], 0)
        self.assertIn("· besoin : B-0001 · ref : fichier:calc.py\n", self.close.read_text())


class TestUneCaseVide(Cloture):
    criteres = "- [x] triple existe\n- [ ] le guide le dit"

    def test_refuse_et_ne_change_rien(self):
        avant = self.ouverte.read_text()
        code, sortie = self.socle("close", "T-0001")
        self.assertEqual(code, 1)
        self.assertIn("`T-0001` ne se clôt pas, rien n'est changé ; les contrôles du backlog le refuseraient clos :",
                      sortie)
        self.assertIn("non coché : le guide le dit", sortie)
        self.assertEqual(self.ouverte.read_text(), avant)
        self.assertFalse(self.close.exists())
        self.assertEqual(git(self.racine, "status", "--porcelain"), "")


class TestUnFichierDejaALaPlace(Cloture):
    criteres = "- [x] triple existe\n- [ ] le guide le dit"

    def test_ni_ecrase_ni_perdu(self):
        """La revue de L-0053 : un fichier non suivi déjà à la place où
        l'entrée se range (une copie, une fusion) n'est ni écrasé, ni
        effacé par la remise d'un refus."""
        self.close.parent.mkdir(parents=True, exist_ok=True)
        self.close.write_text("une copie que git ne suit pas\n")
        avant = self.ouverte.read_text()
        code, sortie = self.socle("close", "T-0001")
        self.assertEqual(code, 1)
        self.assertIn("`T-0001` ne se clôt pas : `memory/backlog/closed/T-0001-ecrire-triple-et-son-test.md` existe "
                      "déjà, à la place où elle se range", sortie)
        self.assertEqual(self.close.read_text(), "une copie que git ne suit pas\n")
        self.assertEqual(self.ouverte.read_text(), avant)


class TestLeSkillDuLot(unittest.TestCase):
    def test_la_cloture_du_lot_range_encore_les_consignes_levees(self):
        """La revue de L-0053 : `socle close` ne range pas les consignes
        levées ; la clôture du lot garde `socle archive`, qui les range."""
        from socle.templates import DOSSIER

        for lg, attendu in (("SKILL.md", "`python3 .socle/socle archive` range les consignes levées"),
                            ("SKILL.en.md", "`python3 .socle/socle archive` files the lifted directives")):
            texte = (DOSSIER / "skills/socle-batch" / lg).read_text(encoding="utf-8")
            self.assertIn(attendu, " ".join(texte.split()), lg)


class TestLesRefus(Cloture):
    def test_un_besoin_dont_une_tache_reste_ouverte(self):
        code, sortie = self.socle("close", "B-0001")
        self.assertEqual(code, 1)
        self.assertIn("`B-0001` est clos (« fait ») avec une tâche ouverte : T-0001", sortie)
        self.assertEqual(git(self.racine, "status", "--porcelain"), "")

    def test_une_entree_deja_close_hors_du_backlog_ou_inconnue(self):
        for ident, attendu in (("B-0002", "`B-0002` est déjà clos (« fait »)"),
                               ("ADR-0001", "`ADR-0001` n'est pas une entrée du backlog"),
                               ("T-0099", "T-0099 : aucune entrée de ce nom dans la mémoire")):
            code, sortie = self.socle("close", ident)
            self.assertEqual(code, 1, ident)
            self.assertIn(attendu, sortie)


class TestCeCommit(unittest.TestCase):
    def entree(self, ref: str) -> memoire.Entree:
        texte = f"<!-- socle: couche=backlog zone=publique -->\n# T-0001 — Essai\n\n> statut : fait · ref : {ref}\n"
        return memoire.analyser("memory/backlog/closed/T-0001-essai.md", texte).entrees[0]

    def test_seule_parmi_d_autres_dans_les_deux_langues(self):
        self.assertEqual(memoire.ref_ce_commit(self.entree("ce commit")), "ce commit")
        self.assertEqual(memoire.ref_ce_commit(self.entree("D-0001, Ce commit")), "Ce commit")
        self.assertEqual(memoire.ref_ce_commit(self.entree("this commit")), "this commit")

    def test_une_autre_reference_n_est_pas_ce_commit(self):
        self.assertIsNone(memoire.ref_ce_commit(self.entree("commit:abc1234")))
        self.assertIsNone(memoire.ref_ce_commit(self.entree("le prochain commit")))


if __name__ == "__main__":
    unittest.main()
