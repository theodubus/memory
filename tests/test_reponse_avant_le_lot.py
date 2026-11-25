"""D-0189, la piste B : une réponse donnée avant le lot de son changement le
couvre. Une validation ajoutée sur la branche depuis son point de départ
compte comme une de la plage ; déjà dans la branche par défaut, elle compte
tant qu'une tâche ouverte la cite et que ce qu'elle nomme n'a pas bougé
depuis le parent du commit de sa demande. Un test par cas du tableau de
« La règle » de la spécification
(`docs/fabrication/reponse-avant-le-lot-specification.md`), puis chaque
chose qu'une validation nomme, et la règle qui ne s'applique pas."""

import contextlib
import io
import shutil
import tempfile
import types
import unittest
from pathlib import Path

from socle import (checks_ratchet, cli, config, context as contexte, installer as installeur, requests as demandes,
                   utils as outils)
from socle.report import AVERTISSEMENT
from tests.test_attendus import MOTEUR, TEST, git

DEMANDE = """<!-- socle: couche=demandes zone=publique -->
# D-0001 — Le facteur passe à 3 ?

> date : 2026-11-25

## Décision demandée

{objet}

## Réponses possibles

- `valider` — je fais le changement.
- `refuser` — je garde tout tel quel.
"""
TACHE = """<!-- socle: couche=backlog zone=publique -->
# T-0001 — Changer ce que la demande nomme

> statut : {statut} · origine : {cite}

Le changement que {cite} autorise.
"""
WORKFLOW = ".github/workflows/socle.yml"
CONTROLES = ["tests.attendus", "cliquet.garde-fous", "protege.fichiers"]
TEST_DOUBLE = "Valider que `test_double` attende 6."


class TestReponseAvantLeLot(unittest.TestCase):
    """Un projet installé, poussé sur une origine locale, et une branche de
    travail ; une branche fusionnée l'est dans `main`, poussée."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-avant-le-lot-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        self.origine = self.racine.parent / (self.racine.name + "-origine.git")
        self.addCleanup(shutil.rmtree, self.origine, ignore_errors=True)
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
        git(self.racine.parent, "init", "-q", "--bare", str(self.origine))
        git(self.racine, "remote", "add", "origin", str(self.origine))
        git(self.racine, "push", "-q", "--no-verify", "origin", "main")
        git(self.racine, "checkout", "-qb", "travail")

    # -- les gestes ---------------------------------------------------------

    def commit(self, message) -> str:
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", message, "--no-verify")
        return self.sha("HEAD")

    def sha(self, rev: str) -> str:
        return git(self.racine, "rev-parse", rev).strip()

    def pousser(self):
        branche = git(self.racine, "branch", "--show-current").strip()
        git(self.racine, "push", "-q", "--no-verify", "-u", "origin", branche)

    def demander(self, objet: str, ident: str = "D-0001"):
        """La demande, commitée et poussée telle quelle : l'humain l'a lue."""
        (self.racine / "memory/requests").mkdir(parents=True, exist_ok=True)
        (self.racine / f"memory/requests/{ident}-facteur.md").write_text(
            DEMANDE.format(objet=objet).replace("D-0001", ident))
        self.commit("La demande")
        self.pousser()

    def repondre(self, ident: str = "D-0001"):
        """La réponse de l'humain, consignée par l'agent."""
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as erreurs:
            code = cli.main(["--root", str(self.racine), "answer", ident, "valider", "--relayed", "--by", "Théo",
                             "--quote", "oui, valide"])
        self.assertEqual(code, 0, erreurs.getvalue())

    def tache(self, statut: str = "ouvert"):
        """La tâche qui fera le changement, et cite la demande (D-0141)."""
        (self.racine / "memory/backlog").mkdir(parents=True, exist_ok=True)
        (self.racine / "memory/backlog/T-0001-changer.md").write_text(TACHE.format(statut=statut, cite="D-0001"))

    def changer_le_test(self, attendu):
        (self.racine / "tests/test_calc.py").write_text(TEST.format(attendu=attendu))

    def fusionner(self, suite: str, squash: bool = False) -> str:
        """La branche courante fusionnée dans `main`, poussée ; le travail
        repart d'elle sur la branche `suite`. Rend la tête de `main`
        d'avant la fusion."""
        branche = git(self.racine, "branch", "--show-current").strip()
        git(self.racine, "checkout", "-q", "main")
        avant = self.sha("HEAD")
        if squash:
            git(self.racine, "merge", "-q", "--squash", branche)
            self.commit("La pull request, fusionnée par squash")
        else:
            git(self.racine, "merge", "-q", "--no-ff", "--no-verify", "-m", "La pull request, fusionnée", branche)
        git(self.racine, "push", "-q", "--no-verify", "origin", "main")
        git(self.racine, "checkout", "-qb", suite)
        return avant

    def juger(self, base: str, tete: str | None = "HEAD", etage: str = "ci",
              racine: Path | None = None) -> tuple[list[str], list[str]]:
        """Les erreurs et les avertissements des contrôles qui comptent les
        validations, sur la plage `base..tete`."""
        ctx = contexte.Contexte(config.Projet.charger(racine or self.racine), etage=etage, base=base, tete=tete)
        r = contexte.executer(ctx, CONTROLES)
        return ([c.message for c in r.erreurs() if c.controle in CONTROLES],
                [c.message for c in r.constats if c.controle in CONTROLES and c.gravite == AVERTISSEMENT])

    # -- le tableau de « La règle » ------------------------------------------

    def test_une_reponse_poussee_seule_couvre_le_test_change_au_push_suivant(self):
        """Cas 1 : la réponse poussée seule, le test au push suivant de la
        même pull request. Aucune tâche n'est requise : la validation est
        sur la branche depuis son point de départ."""
        self.demander(TEST_DOUBLE)
        self.repondre()
        poussee = self.commit("La réponse de Théo")
        self.pousser()
        self.changer_le_test(6)
        self.commit("Le test qu'elle autorise")
        # La CI du push, et le hook avant push qui la reproduit.
        erreurs, avertis = self.juger(poussee)
        self.assertEqual(erreurs, [])
        self.assertIn("assertion changée dans `test_double` (validé par D-0001)", avertis)

    def test_une_reponse_fusionnee_couvre_le_test_de_sa_tache_ouverte(self):
        """Cas 2 : la réponse fusionnée avec une pull request, le test changé
        dans une suivante, sa tâche ouverte au point de départ ; le lot la
        clôt avec le test."""
        self.demander(TEST_DOUBLE)
        self.tache()
        self.repondre()
        self.commit("La réponse de Théo, et la tâche qui la cite")
        self.pousser()
        self.fusionner("lot")
        depart = self.sha("origin/main")
        self.changer_le_test(6)
        erreurs, _ = self.juger(depart, tete=None, etage="agent")
        self.assertEqual(erreurs, [])
        self.tache("fait")
        self.commit("Le test, et sa tâche close")
        erreurs, avertis = self.juger(depart)
        self.assertEqual(erreurs, [])
        self.assertIn("assertion changée dans `test_double` (validé par D-0001)", avertis)

    def test_la_ci_de_la_fusion_juge_depuis_la_base_de_sa_plage(self):
        """La CI du push sur la branche par défaut, après la fusion du cas 2 :
        sa tête est dans la branche par défaut, elle part de la base de sa
        plage, où la tâche était encore ouverte."""
        self.demander(TEST_DOUBLE)
        self.tache()
        self.repondre()
        self.commit("La réponse de Théo, et la tâche qui la cite")
        self.pousser()
        self.fusionner("lot")
        self.changer_le_test(6)
        self.tache("fait")
        self.commit("Le test, et sa tâche close")
        self.pousser()
        avant = self.fusionner("suite")
        erreurs, avertis = self.juger(avant, tete=self.sha("main"))
        self.assertEqual(erreurs, [])
        self.assertIn("assertion changée dans `test_double` (validé par D-0001)", avertis)

    def test_un_test_corrige_apres_la_revue_au_push_suivant_reste_couvert(self):
        """Cas 3 : le test changé avec sa réponse, poussé, puis corrigé après
        la revue, au push suivant."""
        self.demander(TEST_DOUBLE)
        self.repondre()
        self.changer_le_test(6)
        poussee = self.commit("La réponse et son test")
        self.pousser()
        self.changer_le_test(8)
        self.commit("Le test corrigé après la revue")
        erreurs, avertis = self.juger(poussee)
        self.assertEqual(erreurs, [])
        self.assertIn("assertion changée dans `test_double` (validé par D-0001)", avertis)

    def test_une_validation_epuisee_ne_couvre_pas_un_second_changement(self):
        """Cas 4 : réponse et test dans le même commit, fusionnés avec la
        tâche close ; le test changé de nouveau ensuite."""
        self.demander(TEST_DOUBLE)
        self.repondre()
        self.changer_le_test(6)
        self.tache("fait")
        self.commit("La réponse, son test, sa tâche close")
        self.pousser()
        self.fusionner("suite")
        self.changer_le_test(8)
        self.commit("Le test, changé de nouveau")
        erreurs, _ = self.juger(self.sha("origin/main"))
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("assertion changée ou retirée dans `test_double`", erreurs[0])
        self.assertIn("déjà dans la branche par défaut, une validation qui le nomme ne le couvre pas : D-0001, "
                      "qu'aucune tâche ouverte ne cite", erreurs[0])

    def test_un_test_pousse_sous_sa_demande_puis_fusionne_par_squash_ne_reste_pas_couvert(self):
        """Cas 5 : le test poussé sous sa demande en attente (D-0147), puis
        la réponse, fusionnés par squash ; le test changé de nouveau. La
        tâche reste ouverte : seul le test qui a bougé le refuse, lu au
        parent du commit de squash, qui ajoute la demande."""
        self.demander(TEST_DOUBLE)
        self.tache()
        self.changer_le_test(6)
        self.commit("Le test, en attente de D-0001")
        self.pousser()
        self.repondre()
        self.commit("La réponse de Théo")
        self.pousser()
        self.fusionner("suite", squash=True)
        self.changer_le_test(8)
        self.commit("Le test, changé de nouveau")
        erreurs, _ = self.juger(self.sha("origin/main"))
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("D-0001, dont ce qu'elle nomme a changé depuis sa demande", erreurs[0])

    def test_une_demande_ancienne_qu_aucune_tache_ouverte_ne_cite_ne_couvre_pas(self):
        """Cas 6 : une demande ancienne nomme le test, aucune tâche ouverte ne
        la cite. Une tâche écrite sur la branche ne la rend pas : la tâche se
        lit au point de départ."""
        self.demander(TEST_DOUBLE)
        self.repondre()
        self.commit("La réponse de Théo")
        self.pousser()
        self.fusionner("suite")
        self.changer_le_test(6)
        self.commit("Le test")
        depart = self.sha("origin/main")
        erreurs, _ = self.juger(depart)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("D-0001, qu'aucune tâche ouverte ne cite", erreurs[0])
        self.tache()
        self.commit("Une tâche qui la cite, sur la branche")
        erreurs, _ = self.juger(depart)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("D-0001, qu'aucune tâche ouverte ne cite", erreurs[0])

    # -- ce qu'une validation fusionnée nomme --------------------------------

    def test_un_test_qui_a_bouge_dans_la_branche_par_defaut_n_est_plus_couvert(self):
        """Changé dans la branche par défaut par un autre chemin, le test
        n'est plus celui que l'humain avait sous les yeux."""
        self.demander(TEST_DOUBLE)
        self.tache()
        self.repondre()
        self.commit("La réponse de Théo, et la tâche qui la cite")
        self.pousser()
        self.fusionner("autre")
        self.changer_le_test("4  # deux fois deux")
        self.commit("Une autre pull request touche le test")
        self.pousser()
        self.fusionner("suite")
        self.changer_le_test(6)
        self.commit("Le test")
        erreurs, _ = self.juger(self.sha("origin/main"))
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("D-0001, dont ce qu'elle nomme a changé depuis sa demande", erreurs[0])

    def test_un_fichier_de_cas_cite_par_une_validation_fusionnee(self):
        self.demander("Valider que `docs/double.cas.json` attende 6 pour 2.")
        self.tache()
        self.repondre()
        self.commit("La réponse de Théo, et la tâche qui la cite")
        self.pousser()
        self.fusionner("suite")
        (self.racine / "docs/double.cas.json").write_text('[\n  {"entree": 2, "attendu": 6}\n]\n')
        self.commit("Le cas")
        erreurs, avertis = self.juger(self.sha("origin/main"))
        self.assertEqual(erreurs, [])
        self.assertTrue(any("docs/double.cas.json" in a and "(validé par D-0001)" in a for a in avertis), avertis)

    def test_une_cle_des_seuils_citee_par_une_validation_fusionnee(self):
        """La clé citée se relâche sous la validation fusionnée ; une clé
        qu'elle ne nomme pas, non."""
        self.demander("Valider que `staleness.active_days` passe de 7 à 14 jours.")
        self.tache()
        self.repondre()
        self.commit("La réponse de Théo, et la tâche qui la cite")
        self.pousser()
        self.fusionner("suite")
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(gf.read_text().replace("active_days = 7", "active_days = 14", 1)
                      .replace("max_tasks = 9", "max_tasks = 12", 1))
        self.commit("Les seuils")
        erreurs, avertis = self.juger(self.sha("origin/main"))
        self.assertTrue(any(a.startswith("assouplissement validé par D-0001 : staleness.active_days")
                            for a in avertis), avertis)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("batches.max_tasks", erreurs[0])
        self.assertNotIn("D-0001", erreurs[0])

    def test_un_fichier_protege_cite_avec_son_empreinte_par_une_validation_fusionnee(self):
        p = self.racine / WORKFLOW
        nouveau = p.read_text() + "\n# changé\n"
        cite = "sha256:" + outils.sha256(nouveau)[:16]
        self.demander(f"Valider le workflow mis à jour :\n\n- `{WORKFLOW}` — `{cite}`")
        self.tache()
        self.repondre()
        self.commit("La réponse de Théo, et la tâche qui la cite")
        self.pousser()
        self.fusionner("suite")
        p.write_text(nouveau)
        self.commit("Le workflow")
        erreurs, avertis = self.juger(self.sha("origin/main"))
        self.assertEqual(erreurs, [])
        self.assertIn("modification validée par D-0001", avertis)

    # -- les pièces de la règle ---------------------------------------------

    def test_le_point_de_depart_distingue_les_validations_de_la_branche_et_les_fusionnees(self):
        """`depart`, `validations_de_branche`, `validations_fusionnees` et
        `hors_plage` sur un même travail : D-0001 fusionnée, que T-0001
        cite ; D-0002 poussée sur la branche, hors de la plage jugée."""
        avant_la_demande = self.sha("HEAD")
        self.demander(TEST_DOUBLE)
        self.tache()
        self.repondre()
        self.commit("La réponse de Théo, et la tâche qui la cite")
        self.pousser()
        self.fusionner("suite")
        depart = self.sha("origin/main")
        self.demander("Valider que `docs/double.cas.json` attende 6 pour 2.", "D-0002")
        self.repondre("D-0002")
        poussee = self.commit("La réponse de D-0002")
        self.pousser()
        (self.racine / "notes.txt").write_text("un commit de plus\n")
        self.commit("Un commit de plus")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=poussee, tete="HEAD")
        self.assertEqual(ctx.depart, depart)
        self.assertEqual([d.id for d in ctx.validations], [])
        self.assertEqual([d.id for d in ctx.validations_de_branche], ["D-0002"])
        self.assertEqual([demandes.identite(d) for d in ctx.validations_de_branche], ["D-0002"])
        fusionnees = ctx.validations_fusionnees
        self.assertEqual([(f.demande.id, f.citee) for f in fusionnees], [("D-0001", True)])
        self.assertEqual(fusionnees[0].parent, avant_la_demande)

        def nomme(nom):
            return lambda texte: nom in texte

        self.assertEqual(ctx.hors_plage(nomme("double.cas.json"), lambda p: False)[0].id, "D-0002")
        self.assertEqual(ctx.hors_plage(nomme("test_double"), lambda p: True)[0].id, "D-0001")
        d, note = ctx.hors_plage(nomme("test_double"), lambda p: False)
        self.assertIsNone(d)
        self.assertIn("D-0001, dont ce qu'elle nomme a changé depuis sa demande", note)
        self.assertEqual(ctx.hors_plage(nomme("test_triple"), lambda p: True), (None, ""))

    def test_le_parent_de_l_ajout_suit_un_renommage(self):
        """Le parent du commit qui a ajouté un fichier, même renommé depuis ;
        rien pour un fichier du commit racine."""
        racine = self.sha("HEAD")
        self.demander(TEST_DOUBLE)
        git(self.racine, "mv", "memory/requests/D-0001-facteur.md", "memory/requests/D-0001-le-facteur.md")
        self.commit("La demande renommée")
        self.assertEqual(outils.parent_de_l_ajout(self.racine, "HEAD", "memory/requests/D-0001-le-facteur.md"),
                         racine)
        self.assertIsNone(outils.parent_de_l_ajout(self.racine, "HEAD", "calc.py"))
        self.assertIsNone(outils.parent_de_l_ajout(self.racine, "HEAD", "absent.py"))

    def test_une_cle_intacte_se_compare_par_sa_valeur_citable(self):
        """`valeurs_citables` nomme les clés comme le cliquet ; `cle_intacte`
        les compare entre le parent d'une demande et le point de départ, un
        constat toléré par la liste de sa clé."""
        gf = {"staleness": {"active_days": 7}, "docmap": [{"code": ["calc.py"], "docs": ["docs/calc.md"]}],
              "values": [{"name": "facteur", "file": "calc.py"}]}
        valeurs = checks_ratchet.valeurs_citables(gf)
        self.assertEqual(valeurs["staleness.active_days"], 7)
        self.assertIn("batches.max_tasks", valeurs)
        self.assertEqual(valeurs['docmap "calc.py"'], [["docs/calc.md"]])
        self.assertEqual(valeurs['values "facteur"'], {"name": "facteur", "file": "calc.py"})
        avant = self.sha("HEAD")
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(gf.read_text().replace("active_days = 7", "active_days = 5", 1))
        apres = self.commit("Un seuil durci")
        ctx = types.SimpleNamespace(racine=self.racine, projet=config.Projet.charger(self.racine), depart=apres)
        self.assertFalse(checks_ratchet.cle_intacte(ctx, avant, "staleness.active_days"))
        self.assertFalse(checks_ratchet.cle_intacte(ctx, avant, 'staleness.active_days "un constat"'))
        self.assertTrue(checks_ratchet.cle_intacte(ctx, avant, "batches.max_tasks"))
        self.assertTrue(checks_ratchet.cle_intacte(ctx, avant, 'batches.max_tasks "un constat"'))

    # -- là où la règle ne s'applique pas ------------------------------------

    def test_sans_branche_par_defaut_seules_les_validations_de_la_plage_comptent(self):
        self.demander(TEST_DOUBLE)
        self.repondre()
        poussee = self.commit("La réponse de Théo")
        self.changer_le_test(6)
        self.commit("Le test")
        git(self.racine, "remote", "remove", "origin")
        git(self.racine, "branch", "-q", "-D", "main")
        erreurs, _ = self.juger(poussee)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("hors de la plage, une validation qui le nomme ne compte pas ici, faute de branche par "
                      "défaut lisible : D-0001", erreurs[0])

    def test_dans_un_clone_partiel_une_demande_sans_historique_ne_compte_pas(self):
        """Un clone superficiel n'a pas le commit de la demande : la
        validation fusionnée ne compte pas, et le refus le dit. La CI tire
        tout l'historique."""
        self.demander(TEST_DOUBLE)
        self.tache()
        self.repondre()
        self.commit("La réponse de Théo, et la tâche qui la cite")
        self.pousser()
        self.fusionner("suite")
        partiel = self.racine.parent / (self.racine.name + "-partiel")
        self.addCleanup(shutil.rmtree, partiel, ignore_errors=True)
        git(self.racine.parent, "clone", "-q", "--depth", "1", "-b", "main", f"file://{self.origine}", str(partiel))
        git(partiel, "checkout", "-qb", "suite")
        (partiel / "tests/test_calc.py").write_text(TEST.format(attendu=6))
        git(partiel, "add", "-A")
        git(partiel, "commit", "-qm", "Le test", "--no-verify")
        base = git(partiel, "rev-parse", "origin/main").strip()
        erreurs, _ = self.juger(base, racine=partiel)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("D-0001, dont la demande n'a pas son historique dans ce clone", erreurs[0])


if __name__ == "__main__":
    unittest.main()
