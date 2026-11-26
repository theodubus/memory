"""B-0351, ADR-0114 : l'agent supprime lui-même ses branches de travail
distantes déjà contenues dans la branche par défaut, ou dans sa branche de
travail poussée (`socle prune-branches`) ; une branche de l'humain, une
branche qui n'est contenue nulle part, ou qui a bougé depuis la
vérification, reste. L'état ne donne plus à l'humain que les siennes."""

import contextlib
import io
import json
import shutil
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from socle import branches, cli, config, hooks, human as humain, state as etat
from tests.test_humain import git

MARQUE = "\n\nCo-Authored-By: Claude <noreply@anthropic.com>"


class TestBranchesDeLAgent(unittest.TestCase):
    """Une origine nue ; dans le clone, `main` et des branches poussées."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-branches-agent-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        self.origine = self.dossier / "origine.git"
        git(self.dossier, "init", "-q", "--bare", "-b", "main", str(self.origine))
        self.clone = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(self.origine), str(self.clone))
        git(self.clone, "switch", "-q", "-c", "main")
        self.commit("un")
        git(self.clone, "push", "-q", "origin", "main")
        (self.clone / "memory").mkdir()

    def commit(self, message: str, fichier: str = "f"):
        p = self.clone / fichier
        p.write_text((p.read_text() if p.exists() else "") + message + "\n")
        git(self.clone, "add", "-A")
        git(self.clone, "commit", "-qm", message)

    def branche(self, nom: str, agent: bool, fusionner: bool = True):
        """Une branche poussée d'un commit, de l'agent ou de l'humain ;
        fusionnée dans `main`, poussée elle aussi, si `fusionner`."""
        git(self.clone, "switch", "-q", "-c", nom, "main")
        self.commit(f"travail de {nom}" + (MARQUE if agent else ""), fichier=nom.replace("/", "-"))
        git(self.clone, "push", "-q", "origin", nom)
        git(self.clone, "switch", "-q", "main")
        if fusionner:
            git(self.clone, "merge", "-q", "--no-ff", "-m", f"fusion de {nom}", nom)
            git(self.clone, "push", "-q", "origin", "main")

    def projet(self, politique: dict | None = None) -> config.Projet:
        p = config.Projet(racine=self.clone)
        p.politique = politique or {}
        return p

    def sur_l_origine(self) -> set[str]:
        return {l.split("\trefs/heads/")[1] for l in git(self.clone, "ls-remote", "--heads", "origin").splitlines()}

    def test_une_branche_de_l_agent_contenue_dans_la_branche_par_defaut_se_supprime(self):
        self.branche("agent/fait", agent=True)
        tete = git(self.clone, "rev-parse", "origin/agent/fait").strip()
        bilan = branches.elaguer(self.projet())
        self.assertEqual(bilan.supprimees, [("agent/fait", tete)])
        self.assertNotIn("agent/fait", self.sur_l_origine())
        # La commande donne de quoi la recréer.
        sortie = "\n".join(branches.lignes(bilan))
        self.assertIn(f"`git push origin {tete}:refs/heads/agent/fait`", sortie)
        git(self.clone, "push", "-q", "origin", f"{tete}:refs/heads/agent/fait")
        self.assertIn("agent/fait", self.sur_l_origine())

    def test_une_branche_de_l_humain_reste(self):
        self.branche("humain/fait", agent=False)
        bilan = branches.elaguer(self.projet())
        self.assertEqual(bilan.supprimees, [])
        self.assertIn("humain/fait", self.sur_l_origine())
        self.assertEqual([n for n, _ in bilan.laissees], ["humain/fait"])
        self.assertIn("marque d'un agent", bilan.laissees[0][1])
        # L'état la donne toujours à l'humain, et rien à l'agent.
        agent: list[str] = []
        quoi = [e.quoi for e in humain.a_faire(self.projet(), agent)]
        self.assertTrue(any("`humain/fait`" in q for q in quoi), quoi)
        self.assertEqual(agent, [])

    def test_un_commit_de_l_humain_en_tete_rend_la_branche_a_l_humain(self):
        """Une marque d'agent plus bas ne compte pas : seul le dernier commit
        dit à qui est la branche."""
        git(self.clone, "switch", "-q", "-c", "melee", "main")
        self.commit("de l'agent" + MARQUE, fichier="melee")
        self.commit("puis de l'humain", fichier="melee")
        git(self.clone, "push", "-q", "origin", "melee")
        git(self.clone, "switch", "-q", "main")
        git(self.clone, "merge", "-q", "--ff-only", "melee")
        git(self.clone, "push", "-q", "origin", "main")
        self.assertEqual(branches.elaguer(self.projet()).supprimees, [])
        self.assertIn("melee", self.sur_l_origine())

    def test_une_branche_de_l_agent_non_contenue_reste(self):
        self.branche("agent/en-cours", agent=True, fusionner=False)
        bilan = branches.elaguer(self.projet())
        self.assertEqual(bilan.supprimees, [])
        self.assertIn("agent/en-cours", self.sur_l_origine())
        self.assertEqual(branches.pour_l_agent(self.projet(), humain.branches_a_supprimer(self.projet())), [])

    def test_une_branche_qui_a_bouge_depuis_la_verification_reste(self):
        """Entre la vérification et le push, quelqu'un pousse sur la branche :
        le bail refuse la suppression, et le commit nouveau reste."""
        self.branche("agent/fait", agent=True)
        verifiee = git(self.clone, "rev-parse", "origin/agent/fait").strip()
        tetes = branches.tetes_de_l_origine(self.projet())
        autre = self.dossier / "autre"
        git(self.dossier, "clone", "-q", str(self.origine), str(autre))
        git(autre, "switch", "-q", "agent/fait")
        (autre / "g").write_text("nouveau\n")
        git(autre, "add", "g")
        git(autre, "commit", "-qm", "un commit de plus")
        git(autre, "push", "-q", "origin", "agent/fait")
        nouvelle = git(autre, "rev-parse", "HEAD").strip()
        # La vérification a vu l'origine avant ce push : le fetch et la
        # question à l'origine rendent ce qu'ils rendaient alors.
        with unittest.mock.patch.object(branches, "_fetch"), \
                unittest.mock.patch.object(branches, "tetes_de_l_origine", return_value=tetes):
            bilan = branches.elaguer(self.projet())
        self.assertEqual(bilan.supprimees, [])
        self.assertEqual(bilan.refusees, [])
        self.assertEqual([n for n, _ in bilan.laissees], ["agent/fait"])
        self.assertIn("bougé", bilan.laissees[0][1])
        self.assertNotEqual(verifiee, nouvelle)
        self.assertEqual(git(self.clone, "ls-remote", "origin", "refs/heads/agent/fait").split()[0], nouvelle)
        # Ce n'est pas un refus de l'origine : rien n'est gardé.
        self.assertEqual(branches.refus(self.clone), {})

    def test_une_branche_contenue_dans_la_branche_de_travail_poussee_se_supprime(self):
        """La passation : la branche de la session d'avant est contenue dans
        celle de la session qui reprend, poussée."""
        git(self.clone, "switch", "-q", "-c", "session-1", "main")
        self.commit("passation" + MARQUE, fichier="s")
        git(self.clone, "push", "-q", "origin", "session-1")
        git(self.clone, "switch", "-q", "-c", "session-2")
        self.commit("reprise" + MARQUE, fichier="s")
        git(self.clone, "push", "-q", "origin", "session-2")
        agent: list[str] = []
        humain.a_faire(self.projet(), agent)
        self.assertEqual(agent, ["session-1"])
        bilan = branches.elaguer(self.projet())
        self.assertEqual([n for n, _ in bilan.supprimees], ["session-1"])
        self.assertEqual(self.sur_l_origine(), {"main", "session-2"})

    def test_ni_la_branche_courante_ni_une_branche_gardee(self):
        self.branche("agent/gardee", agent=True)
        self.branche("agent/courante", agent=True)
        git(self.clone, "switch", "-q", "agent/courante")
        bilan = branches.elaguer(self.projet({"human": {"keep_branches": ["agent/gardee"]}}))
        self.assertEqual(bilan.supprimees, [])
        self.assertTrue({"agent/gardee", "agent/courante"} <= self.sur_l_origine())

    def test_la_commande_ne_perd_pas_la_reference_d_une_branche_que_l_origine_n_a_plus(self):
        """La revue de L-0043 : un `git fetch --prune`, même en `--dry-run`,
        élaguait la référence d'une branche supprimée sur l'origine sans
        fusion, qui seule gardait un commit ; l'état disait de l'étiqueter
        d'abord, et la ligne disparaissait avec le commit."""
        self.branche("agent/fait", agent=True)
        self.branche("abandonnee", agent=False, fusionner=False)
        seule = git(self.clone, "rev-parse", "origin/abandonnee").strip()
        autre = self.dossier / "autre"
        git(self.dossier, "clone", "-q", str(self.origine), str(autre))
        git(autre, "push", "-q", "origin", "--delete", "abandonnee")
        git(self.clone, "branch", "-q", "-D", "abandonnee")
        for essai in (True, False):
            bilan = branches.elaguer(self.projet(), essai=essai)
            self.assertEqual(git(self.clone, "rev-parse", "refs/remotes/origin/abandonnee").strip(), seule, essai)
            self.assertNotIn("abandonnee", [n for n, _ in bilan.laissees], essai)
        self.assertEqual([n for n, _ in bilan.supprimees], ["agent/fait"])
        self.assertIn("origin/abandonnee", git(self.clone, "branch", "-a", "--contains", seule))

    def test_les_pieces_de_la_commande(self):
        """La marque d'un agent, la tête connue, les candidates, le refus
        gardé et son chemin, et la commande elle-même."""
        import argparse

        self.branche("agent/fait", agent=True)
        self.branche("humain/fait", agent=False)
        self.branche("agent/en-cours", agent=True, fusionner=False)
        projet = self.projet()
        tete = branches.tete_connue(projet, "agent/fait")
        self.assertEqual(tete, git(self.clone, "rev-parse", "origin/agent/fait").strip())
        self.assertTrue(branches.de_l_agent(projet, tete))
        self.assertFalse(branches.de_l_agent(projet, branches.tete_connue(projet, "humain/fait")))
        self.assertEqual(branches.tete_connue(projet, "absente"), "")
        # Contenues dans la branche par défaut, chacune avec elle ; pas la
        # branche qui ne l'est pas.
        self.assertEqual(branches.candidates(projet), [("agent/fait", "origin/main"), ("humain/fait", "origin/main")])
        chemin = branches.chemin_des_refus(self.clone)
        self.assertEqual(chemin.name, "prune-refused.json")
        self.assertIsNone(branches.refus_actuel(projet, "agent/fait"))
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(json.dumps({"agent/fait": {"sha": tete, "raison": "non"}}), encoding="utf-8")
        self.assertEqual(branches.refus_actuel(projet, "agent/fait")["raison"], "non")
        self.assertIsNone(branches.refus_actuel(projet, "agent/fait", "0" * 40))
        chemin.write_text("illisible", encoding="utf-8")
        self.assertEqual(branches.refus(self.clone), {})
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            code = cli.cmd_prune_branches(argparse.Namespace(root=str(self.clone), dry_run=True))
        self.assertEqual(code, 0)
        self.assertIn("à supprimer : `agent/fait`", sortie.getvalue())

    def test_dry_run_ne_supprime_rien(self):
        self.branche("agent/fait", agent=True)
        bilan = branches.elaguer(self.projet(), essai=True)
        self.assertEqual([n for n, _ in bilan.a_supprimer], ["agent/fait"])
        self.assertIn("agent/fait", self.sur_l_origine())
        self.assertIn("--dry-run", "\n".join(branches.lignes(bilan, essai=True)))

    def test_la_politique_coupe_la_suppression(self):
        """`prune_branches = false` : toutes les branches reviennent à
        l'humain, et la commande refuse en le disant."""
        self.branche("agent/fait", agent=True)
        coupee = self.projet({"irreversible": {"prune_branches": False}})
        agent: list[str] = []
        quoi = [e.quoi for e in humain.a_faire(coupee, agent)]
        self.assertEqual(agent, [])
        self.assertTrue(any("`agent/fait`" in q for q in quoi), quoi)
        with self.assertRaises(branches.SuppressionRefusee) as refus:
            branches.elaguer(coupee)
        self.assertIn("prune_branches = false", str(refus.exception))
        self.assertIn("agent/fait", self.sur_l_origine())
        # Une valeur qui n'est pas un booléen vrai la coupe aussi.
        self.assertFalse(branches.active(self.projet({"irreversible": {"prune_branches": "false"}})))
        self.assertTrue(branches.active(self.projet()))

    def test_un_refus_de_l_origine_redonne_la_branche_a_l_humain(self):
        self.branche("agent/fait", agent=True)
        git(self.origine, "config", "receive.denyDeletes", "true")
        projet = self.projet()
        bilan = branches.elaguer(projet)
        self.assertEqual([n for n, _ in bilan.refusees], ["agent/fait"])
        self.assertIn("agent/fait", self.sur_l_origine())
        tete = git(self.clone, "rev-parse", "origin/agent/fait").strip()
        self.assertEqual(branches.refus(self.clone)["agent/fait"]["sha"], tete)
        agent: list[str] = []
        quoi = [e.quoi for e in humain.a_faire(projet, agent)]
        self.assertEqual(agent, [])
        ligne = next(q for q in quoi if "`agent/fait`" in q)
        self.assertIn("l'origine a refusé à l'agent de la supprimer", ligne)
        # La commande ne la retente pas tant qu'elle n'a pas changé.
        git(self.origine, "config", "receive.denyDeletes", "false")
        bilan = branches.elaguer(projet)
        self.assertEqual(bilan.supprimees, [])
        self.assertIn("agent/fait", self.sur_l_origine())
        # Changée, elle se retente, et le refus s'efface.
        git(self.clone, "switch", "-q", "agent/fait")
        self.commit("encore" + MARQUE, fichier="agent-fait")
        git(self.clone, "push", "-q", "origin", "agent/fait")
        git(self.clone, "switch", "-q", "main")
        git(self.clone, "merge", "-q", "--no-ff", "-m", "fusion", "agent/fait")
        git(self.clone, "push", "-q", "origin", "main")
        bilan = branches.elaguer(projet)
        self.assertEqual([n for n, _ in bilan.supprimees], ["agent/fait"])
        self.assertEqual(branches.refus(self.clone), {})

    def test_l_etat_donne_a_l_agent_ses_branches_et_la_commande(self):
        self.branche("agent/fait", agent=True)
        self.branche("humain/fait", agent=False)
        sortie = etat.calculer(self.projet(), contenus=False)
        self.assertIn("branches de l'agent à supprimer : `agent/fait`", sortie)
        self.assertIn("`python3 .socle/socle prune-branches`", sortie)
        humaines = sortie.split("ce qui revient à l'humain", 1)[1].split("branches de l'agent", 1)[0]
        self.assertIn("`humain/fait`", humaines)
        self.assertNotIn("`agent/fait`", humaines)

    def test_la_commande_rend_un_code_et_ecrit_son_bilan(self):
        self.branche("agent/fait", agent=True)
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            code = cli.main(["--root", str(self.clone), "prune-branches", "--dry-run"])
        self.assertEqual(code, 0)
        self.assertIn("à supprimer : `agent/fait`", sortie.getvalue())
        self.assertIn("agent/fait", self.sur_l_origine())
        git(self.origine, "config", "receive.denyDeletes", "true")
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            code = cli.main(["--root", str(self.clone), "prune-branches"])
        self.assertEqual(code, 1)
        self.assertIn("refusée par l'origine : `agent/fait`", sortie.getvalue())
        (self.clone / ".socle").mkdir()
        (self.clone / ".socle/policy.toml").write_text("[irreversible]\nprune_branches = false\n")
        with contextlib.redirect_stderr(io.StringIO()) as erreur:
            code = cli.main(["--root", str(self.clone), "prune-branches"])
        self.assertEqual(code, 1)
        self.assertIn("prune_branches = false", erreur.getvalue())


class TestTexte(unittest.TestCase):
    """T-0192 : les gabarits de la politique portent la ligne qui coupe la
    suppression, en commentaire ; décommentée, elle la coupe. Le point 4
    du gabarit d'`AGENTS.md` nomme l'exception, dans les deux langues."""

    def test_la_ligne_des_gabarits_de_la_politique_coupe_la_suppression(self):
        import tomllib

        modeles = Path(branches.__file__).resolve().parent / "templates"
        for nom in ("policy.toml", "policy.en.toml"):
            texte = (modeles / nom).read_text(encoding="utf-8")
            self.assertIn("\n# prune_branches = false\n", texte, nom)
            projet = config.Projet(racine=Path("."))
            projet.politique = tomllib.loads(texte)
            self.assertTrue(branches.active(projet), nom)
            projet.politique = tomllib.loads(texte.replace("\n# prune_branches = false\n", "\nprune_branches = false\n"))
            self.assertFalse(branches.active(projet), nom)

    def test_le_point_4_d_agents_md_nomme_l_exception(self):
        modeles = Path(branches.__file__).resolve().parent / "templates"
        for nom, phrase in (("AGENTS.md", "suppression distante hors `socle prune-branches`, dépense"),
                            ("AGENTS.en.md", "remote deletion except `socle prune-branches`, spending")):
            self.assertIn(phrase, (modeles / nom).read_text(encoding="utf-8"), nom)


class TestHooks(unittest.TestCase):
    def test_le_hook_avant_push_laisse_passer_une_suppression_seule_sans_rien_lancer(self):
        nul = "0" * 40
        lignes = f"(delete) {nul} refs/heads/agent/fait {'a' * 40}\n"
        self.assertTrue(hooks.suppressions_seules(lignes.splitlines()))
        self.assertFalse(hooks.suppressions_seules([]))
        self.assertFalse(hooks.suppressions_seules([f"refs/heads/t {'b' * 40} refs/heads/t {nul}",
                                                    lignes.strip()]))
        projet = unittest.mock.Mock()
        with unittest.mock.patch("sys.stdin", io.StringIO(lignes)), \
                unittest.mock.patch.object(hooks, "tracer"), \
                unittest.mock.patch.object(hooks.outils, "base_de_travail") as base:
            self.assertEqual(hooks.git_pre_push(projet), 0)
        base.assert_not_called()

    def test_le_hook_de_l_agent_refuse_toujours_une_suppression_et_nomme_la_commande(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-branches-hook-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        git(racine, "init", "-q", "-b", "travail")
        projet = config.Projet(racine=racine)
        for cmd in ("git push origin --delete agent/fait", "git push origin :agent/fait",
                    "git push origin :refs/heads/agent/fait"):
            raison = hooks.refus_bash(projet, cmd)
            self.assertIsNotNone(raison, cmd)
            self.assertIn("suppression d'une branche distante", raison)
            self.assertIn("`python3 .socle/socle prune-branches`", raison)
        # La commande elle-même, l'agent la lance.
        self.assertIsNone(hooks.refus_bash(projet, "python3 .socle/socle prune-branches"))


if __name__ == "__main__":
    unittest.main()
