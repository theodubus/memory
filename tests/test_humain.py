import json
import os
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from socle import config, human as humain


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestBranchesASupprimer(unittest.TestCase):
    """Un cas réel, généralisé : une ligne qui se tait
    presque toujours s'éprouve sur des dépôts fabriqués."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-humain-"))
        source = self.dossier / "source"
        source.mkdir()
        git(source, "init", "-q", "-b", "main")
        (source / "f").write_text("un")
        git(source, "add", "f")
        git(source, "commit", "-qm", "un")
        for b in ("fusionnee", "codex/ui", "travail"):
            git(source, "branch", b)
        (source / "f").write_text("deux")
        git(source, "commit", "-qam", "deux")
        git(source, "switch", "-q", "-c", "en-cours")
        (source / "f").write_text("trois")
        git(source, "commit", "-qam", "trois")
        git(source, "switch", "-q", "main")
        self.clone = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(source), str(self.clone))
        git(self.clone, "switch", "-q", "travail")
        self.projet = config.Projet(racine=self.clone)

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)

    def test_seules_les_branches_contenues_sont_proposees(self):
        self.assertEqual(humain.branches_a_supprimer(self.projet), ["codex/ui", "fusionnee"])

    def test_la_politique_garde_certaines_branches(self):
        self.projet.politique = {"human": {"keep_branches": ["codex/*"]}}
        self.assertEqual(humain.branches_a_supprimer(self.projet), ["fusionnee"])

    def test_une_branche_contenue_dans_la_branche_de_travail_poussee_est_proposee(self):
        """B-0145 : une branche fusionnée dans la branche de travail, poussée,
        n'était proposée qu'une fois la pull request de celle-ci fusionnée."""
        import time

        source = self.dossier / "source"
        git(source, "branch", "morceau", "en-cours")
        git(source, "switch", "-q", "en-cours")
        (source / "f").write_text("quatre")
        git(source, "commit", "-qam", "quatre")
        git(source, "switch", "-q", "main")
        git(self.clone, "fetch", "-q", "origin")
        self.assertEqual(humain.branches_contenues_dans_le_travail(self.projet), [])
        git(self.clone, "switch", "-q", "en-cours")
        self.assertEqual(humain.branches_contenues_dans_le_travail(self.projet), [("morceau", "origin/en-cours")])
        # Celles que la branche par défaut contient restent à part, et la
        # politique en garde.
        self.assertEqual(humain.branches_a_supprimer(self.projet), ["codex/ui", "fusionnee", "travail"])
        self.projet.politique = {"human": {"keep_branches": ["morc*"]}}
        self.assertEqual(humain.branches_contenues_dans_le_travail(self.projet), [])
        self.projet.politique = {}
        (self.clone / "memory").mkdir()
        quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertTrue(any("`morceau`" in q and "`origin/en-cours`" in q for q in quoi), quoi)
        # Inactive, elle n'est pas dite deux fois.
        with unittest.mock.patch.object(time, "time", return_value=time.time() + 30 * 86400):
            quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertEqual(sum("`morceau`" in q for q in quoi), 1, quoi)
        # Une branche de travail qui n'est pas poussée ne contient rien.
        git(self.clone, "switch", "-q", "-c", "locale")
        self.assertEqual(humain.branches_contenues_dans_le_travail(self.projet), [])

    def test_ni_un_prototype_ni_une_branche_au_meme_sommet(self):
        """La revue de B-0145 : une branche de travail jetable ne se fusionne
        pas, son contenu n'est gardé nulle part ailleurs ; deux branches au
        même sommet se désigneraient l'une l'autre."""
        source = self.dossier / "source"
        git(source, "branch", "morceau", "en-cours")
        git(source, "branch", "jumelle", "en-cours")
        git(source, "switch", "-q", "en-cours")
        (source / "f").write_text("plus")
        git(source, "commit", "-qam", "plus")
        git(source, "switch", "-q", "-c", "proto/essai")
        (source / "f").write_text("essai")
        git(source, "commit", "-qam", "essai")
        git(source, "switch", "-q", "main")
        git(self.clone, "fetch", "-q", "origin")
        git(self.clone, "switch", "-q", "jumelle")
        # `jumelle` au sommet de `morceau` : ni l'une ni l'autre n'est dite.
        self.assertEqual(humain.branches_contenues_dans_le_travail(self.projet), [])
        git(self.clone, "switch", "-q", "proto/essai")
        self.assertEqual(humain.branches_contenues_dans_le_travail(self.projet), [])
        git(self.clone, "switch", "-q", "en-cours")
        self.assertEqual(humain.branches_contenues_dans_le_travail(self.projet),
                         [("jumelle", "origin/en-cours"), ("morceau", "origin/en-cours")])

    def test_elles_apparaissent_dans_ce_qui_revient_a_l_humain(self):
        (self.clone / "memory").mkdir()
        quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertTrue(any("`fusionnee`" in q for q in quoi), quoi)

    def test_une_branche_que_l_origine_n_a_plus_n_est_plus_donnee_a_supprimer(self):
        """B-0193 : le clone garde la référence d'une branche supprimée sur
        l'origine tant qu'un fetch ne l'élague pas ; l'état la donnait à
        supprimer à l'humain, qui l'avait déjà supprimée."""
        (self.clone / "memory").mkdir()
        git(self.dossier / "source", "branch", "-D", "fusionnee")
        # Le dernier fetch la garde : la liste calculée sur lui la contient.
        self.assertIn("fusionnee", humain.branches_a_supprimer(self.projet))
        self.assertNotIn("fusionnee", humain.branches_de_l_origine(self.projet))
        quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertFalse(any("`fusionnee`" in q for q in quoi), quoi)
        self.assertTrue(any("`codex/ui`" in q for q in quoi), quoi)
        self.assertFalse(any("dernier fetch" in q for q in quoi), quoi)

    def test_de_meme_une_branche_contenue_dans_le_travail_ou_inactive(self):
        import time

        source = self.dossier / "source"
        git(source, "branch", "morceau", "en-cours")
        git(source, "switch", "-q", "en-cours")
        (source / "f").write_text("quatre")
        git(source, "commit", "-qam", "quatre")
        git(source, "switch", "-q", "main")
        git(self.clone, "fetch", "-q", "origin")
        git(self.clone, "switch", "-q", "en-cours")
        (self.clone / "memory").mkdir()
        git(source, "branch", "-D", "morceau")
        self.assertEqual(humain.branches_contenues_dans_le_travail(self.projet), [("morceau", "origin/en-cours")])
        # Dans trente jours aussi : elle ne se dit pas (le filtre des inactives a son propre test, plus bas).
        with unittest.mock.patch.object(time, "time", return_value=time.time() + 30 * 86400):
            quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertFalse(any("`morceau`" in q for q in quoi), quoi)

    def test_une_branche_de_travail_que_l_origine_n_a_plus_ne_garde_rien(self):
        """B-0292 : supprimée sur l'origine, la branche de travail poussée ne
        garde plus le contenu d'une autre ; l'état le disait encore, et
        supprimer l'autre en aurait perdu les commits."""
        import time

        source = self.dossier / "source"
        git(source, "branch", "morceau", "en-cours")
        git(source, "switch", "-q", "en-cours")
        (source / "f").write_text("quatre")
        git(source, "commit", "-qam", "quatre")
        git(source, "switch", "-q", "main")
        git(self.clone, "fetch", "-q", "origin")
        git(self.clone, "switch", "-q", "en-cours")
        (self.clone / "memory").mkdir()
        quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertTrue(any("`morceau`" in q and "`origin/en-cours`" in q for q in quoi), quoi)
        git(source, "branch", "-D", "en-cours")
        # Le dernier fetch garde sa référence : le calcul sur lui la dit encore.
        self.assertEqual(humain.branches_contenues_dans_le_travail(self.projet), [("morceau", "origin/en-cours")])
        quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertFalse(any("`origin/en-cours`" in q for q in quoi), quoi)
        # Inactive, elle se signale comme une branche que rien ne garde.
        with unittest.mock.patch.object(time, "time", return_value=time.time() + 30 * 86400):
            quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertTrue(any(q.startswith("examiner la branche distante `morceau`") for q in quoi), quoi)

    def test_sans_reponse_de_l_origine_la_liste_dit_qu_elle_vient_du_dernier_fetch(self):
        (self.clone / "memory").mkdir()
        git(self.clone, "remote", "set-url", "origin", str(self.dossier / "absente"))
        self.assertIsNone(humain.branches_de_l_origine(self.projet))
        quoi = [e.quoi for e in humain.a_faire(self.projet)]
        ligne = next(q for q in quoi if "`fusionnee`" in q)
        self.assertIn("dernier fetch", ligne)
        self.assertIn("`git fetch --prune origin`", ligne)
        # Une origine qui ne répond pas dans le délai : de même.
        with unittest.mock.patch.object(humain.subprocess, "run",
                                        side_effect=subprocess.TimeoutExpired("git", humain.DELAI_ORIGINE)):
            self.assertIsNone(humain.branches_de_l_origine(self.projet))

    def test_rien_a_proposer_rien_a_demander_a_l_origine(self):
        """L'origine n'est interrogée que s'il y a une branche à dire."""
        (self.clone / "memory").mkdir()
        self.projet.politique = {"human": {"keep_branches": ["*", "*/*"]}}
        with unittest.mock.patch.object(humain, "branches_de_l_origine") as origine:
            humain.a_faire(self.projet)
        self.assertEqual(origine.call_count, 0)

    def test_une_branche_non_fusionnee_et_inactive_se_signale(self):
        """B-0112 : les branches de session du pilote, jamais livrées,
        restaient sans que personne ne les signale."""
        import time

        source = self.dossier / "source"
        git(source, "switch", "-q", "-c", "ancienne", "main")
        (source / "g").write_text("vieux")
        git(source, "add", "g")
        vieux = "2026-01-01T12:00:00"
        subprocess.run(["git", "commit", "-qm", "vieux"], cwd=source, check=True, capture_output=True,
                       env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                            "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(source),
                            "GIT_COMMITTER_DATE": vieux, "GIT_AUTHOR_DATE": vieux})
        git(source, "switch", "-q", "main")
        git(self.clone, "fetch", "-q", "origin")
        inactives = humain.branches_inactives(self.projet)
        # `en-cours` a un commit absent de main, mais récent : elle ne se signale pas.
        self.assertEqual([b for b, _, _ in inactives], ["ancienne"])
        self.assertEqual(inactives[0][1], 1)
        self.assertGreater(inactives[0][2], 7)
        self.assertEqual(humain.branches_inactives(self.projet, maintenant=time.time() + 30 * 86400)[0][0], "ancienne")
        (self.clone / "memory").mkdir()
        quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertTrue(any(q.startswith("examiner la branche distante `ancienne`") for q in quoi), quoi)

    def test_une_branche_qui_seule_garde_un_commit_cite_dit_de_l_etiqueter(self):
        """B-0116 : supprimer une telle branche avait fait échouer
        `memoire.references` en CI, dont le clone ne récupère que les
        branches et les étiquettes."""
        from socle import utils as outils

        source = self.dossier / "source"
        git(source, "switch", "-q", "-c", "ancienne", "main")
        (source / "g").write_text("vieux")
        git(source, "add", "g")
        vieux = "2026-01-01T12:00:00"
        subprocess.run(["git", "commit", "-qm", "vieux"], cwd=source, check=True, capture_output=True,
                       env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                            "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(source),
                            "GIT_COMMITTER_DATE": vieux, "GIT_AUTHOR_DATE": vieux})
        sha = git(source, "rev-parse", "--short=7", "HEAD").strip()
        git(source, "switch", "-q", "main")
        git(self.clone, "fetch", "-q", "origin")
        deux = git(self.clone, "rev-parse", "--short=7", "origin/main").strip()
        journal = self.clone / "memory/journal/2026-01.md"
        journal.parent.mkdir(parents=True)
        journal.write_text("<!-- socle: couche=journal zone=publique -->\n# Journal\n\n"
                           f"## J-2026-01-01-A — Essai\n\n> ref : commit:{sha}, commit:{deux}\n\nTexte.\n")
        self.assertEqual(humain.commits_cites(self.projet), {sha, deux})
        outils._PULL_REQUESTS_RECUPEREES.clear()
        self.assertEqual(humain.commits_cites_seuls(self.projet, "ancienne"), [sha])
        quoi = [e.quoi for e in humain.a_faire(self.projet) if "`ancienne`" in e.quoi]
        self.assertEqual(len(quoi), 1, quoi)
        self.assertIn(f"dont {sha}, que la mémoire cite et qu'elle seule garde", quoi[0])
        self.assertIn(outils.etiqueter([sha]), quoi[0])
        self.assertEqual(outils.etiqueter(["a1b2c3d", "e4f5a6b"]),
                         "git tag cite/a1b2c3d a1b2c3d && git tag cite/e4f5a6b e4f5a6b"
                         " && git push origin cite/a1b2c3d cite/e4f5a6b")
        # Une pull request le garde : la CI le retrouve (B-0117), rien à étiqueter.
        git(source, "update-ref", "refs/pull/3/head", "ancienne")
        outils._PULL_REQUESTS_RECUPEREES.clear()
        self.assertEqual(humain.commits_cites_seuls(self.projet, "ancienne"), [])
        # Une étiquette aussi.
        git(self.clone, "update-ref", "-d", "refs/socle/pull/3")
        git(self.clone, "tag", f"cite/{sha}", sha)
        outils._PULL_REQUESTS_RECUPEREES.add(str(self.clone.resolve()))
        self.assertEqual(humain.commits_cites_seuls(self.projet, "ancienne"), [])

    def test_une_branche_inactive_que_l_origine_n_a_plus_ne_se_dit_que_pour_un_commit_cite_qu_elle_seule_garde(self):
        """La revue de L-0017 : une branche inactive supprimée sur l'origine ne
        se propose plus à examiner ; mais si sa référence, dans ce clone, garde
        seule un commit que la mémoire cite, l'état dit encore de l'étiqueter,
        sans quoi un `git fetch --prune` le perdrait (B-0116)."""
        from socle import utils as outils

        source = self.dossier / "source"
        git(source, "switch", "-q", "-c", "abandon", "main")
        (source / "g").write_text("vieux")
        git(source, "add", "g")
        vieux = "2026-01-01T12:00:00"
        subprocess.run(["git", "commit", "-qm", "vieux"], cwd=source, check=True, capture_output=True,
                       env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                            "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(source),
                            "GIT_COMMITTER_DATE": vieux, "GIT_AUTHOR_DATE": vieux})
        sha = git(source, "rev-parse", "--short=7", "HEAD").strip()
        git(source, "switch", "-q", "main")
        git(self.clone, "fetch", "-q", "origin")
        (self.clone / "memory").mkdir()
        self.assertTrue(any("`abandon`" in e.quoi for e in humain.a_faire(self.projet)))
        git(source, "branch", "-D", "abandon")
        # Ni la mémoire ne cite son commit : elle ne se dit plus du tout.
        self.assertEqual([b for b, _, _ in humain.branches_inactives(self.projet)], ["abandon"])
        self.assertFalse(any("`abandon`" in e.quoi for e in humain.a_faire(self.projet)))
        # La mémoire le cite : l'étiqueter d'abord, depuis ce clone.
        journal = self.clone / "memory/journal/2026-01.md"
        journal.parent.mkdir(parents=True)
        journal.write_text("<!-- socle: couche=journal zone=publique -->\n# Journal\n\n"
                           f"## J-2026-01-01-A — Essai\n\n> ref : commit:{sha}\n\nTexte.\n")
        outils._PULL_REQUESTS_RECUPEREES.clear()
        quoi = [e.quoi for e in humain.a_faire(self.projet) if "`abandon`" in e.quoi]
        self.assertEqual(len(quoi), 1, quoi)
        self.assertTrue(quoi[0].startswith(f"étiqueter {sha}, que la mémoire cite"), quoi[0])
        self.assertIn("que l'origine n'a plus", quoi[0])
        self.assertIn(outils.etiqueter([sha]), quoi[0])

    def test_une_action_humaine_vient_avec_le_lien_de_son_sujet(self):
        # ADR-0025 : le mode d'emploi d'une action humaine (commandes,
        # résultats attendus) vit dans son sujet, que l'état donne par son lien.
        sujet = self.clone / "memory/backlog/B-0001-entrainer-le-reseau.md"
        sujet.parent.mkdir(parents=True)
        sujet.write_text("<!-- socle: couche=backlog zone=publique -->\n# B-0001 — Entraîner le réseau\n\n"
                         "> statut : ouvert · origine : fichier:f · pour : humain\n")
        git(self.clone, "add", "-A")
        git(self.clone, "commit", "-qm", "sujet")
        git(self.clone, "push", "-q", "-u", "origin", "travail")
        self.projet.politique = {"human": {"repo_url": "https://github.com/essai/calc"}}
        actions = [e for e in humain.a_faire(self.projet) if e.quoi.startswith("B-0001")]
        self.assertEqual([e.quoi for e in actions], ["B-0001 — Entraîner le réseau"])
        self.assertTrue(actions[0].lien.startswith("https://github.com/essai/calc/blob/"), actions[0].lien)
        self.assertIn("/memory/backlog/B-0001-entrainer-le-reseau.md", actions[0].lien)


FAUX_GH = """#!/usr/bin/env python3
import os, sys
if sys.argv[1] != "api":
    print("[]")  # `gh run list` : aucune exécution
else:
    print(os.environ["FAUX_REGLES" if "/rules/branches/" in sys.argv[2] else "FAUX_BRANCHE"])
"""
CI = "Socle — verify, contrôles, auto-test"


class TestCiExigee(unittest.TestCase):
    """B-0044, L2 (R1) : la garantie « seule la CI est incontournable » tient
    à une règle de GitHub que rien ne vérifiait. Ce dépôt l'a montré : sa
    branche se dit protégée (`protected`) alors que la protection classique
    n'exige rien ; c'est un ensemble de règles qui exige la CI."""

    def setUp(self):
        from socle import state as etat

        self.etat = etat
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-protection-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        self.racine = self.dossier / "projet"
        (self.racine / ".github/workflows").mkdir(parents=True)
        (self.racine / ".github/workflows/socle.yml").write_text(f"jobs:\n  socle:\n    name: {CI}\n")
        (self.racine / "memory").mkdir()
        git(self.racine, "init", "-q", "-b", "main")
        git(self.racine, "commit", "-q", "--allow-empty", "-m", "un")
        self.projet = config.Projet(racine=self.racine)
        self.projet.politique = {"human": {"repo_url": "https://github.com/o/r"}}
        outils_gh = self.dossier / "bin"
        outils_gh.mkdir()
        (outils_gh / "gh").write_text(FAUX_GH)
        (outils_gh / "gh").chmod(0o755)
        self.enterContext(unittest.mock.patch.dict(os.environ, {"PATH": f"{outils_gh}{os.pathsep}{os.environ['PATH']}"}))

    def repondre(self, regles, protection=None):
        os.environ["FAUX_REGLES"] = json.dumps(regles)
        os.environ["FAUX_BRANCHE"] = json.dumps({"protected": True, "protection": protection or {
            "enabled": False, "required_status_checks": {"enforcement_level": "off", "contexts": [], "checks": []}}})

    def test_un_ensemble_de_regles_qui_exige_la_ci(self):
        self.repondre([{"type": "required_status_checks",
                        "parameters": {"required_status_checks": [{"context": CI}]}}])
        exigee, detail = self.etat.ci_exigee(self.projet)
        self.assertTrue(exigee)
        self.assertEqual(detail, "main ; revue des propriétaires du code non exigée")

    def test_marquee_protegee_sans_ci_exigee(self):
        self.repondre([{"type": "deletion"}])
        self.assertEqual(self.etat.ci_exigee(self.projet)[0], False)
        texte = self.etat.calculer(self.projet, contenus=False)
        self.assertIn("branche  : main — CI du socle NON exigée", texte)
        self.assertIn("action : protéger la branche `main`", texte)
        self.assertIn("https://github.com/o/r/settings/rules", texte)

    def test_une_protection_classique_qui_exige_la_ci(self):
        self.repondre([], {"enabled": True, "required_status_checks": {
            "enforcement_level": "non_admins", "contexts": [CI], "checks": []}})
        self.assertTrue(self.etat.ci_exigee(self.projet)[0])

    def test_sans_github_on_ne_sait_pas(self):
        self.projet.politique = {}
        self.assertEqual(self.etat.ci_exigee(self.projet), (None, "dépôt hors de GitHub"))
        self.assertIsNone(self.etat.page_protection(self.projet))
        self.assertEqual(self.etat.nom_de_la_ci(self.projet), CI)


class TestDernierMessage(unittest.TestCase):
    def ecrire(self, objets):
        p = Path(tempfile.mkdtemp()) / "t.jsonl"
        p.write_text("\n".join(json.dumps(o) for o in objets) + "\n")
        return p

    def test_dernier_texte_de_l_agent(self):
        p = self.ecrire([
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "ancien"}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}},
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash"}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "Fait.\n\nPour toi : rien.\nEnsuite : B-0001."}]}},
        ])
        message = humain.dernier_message(p)
        self.assertEqual(message, "Fait.\n\nPour toi : rien.\nEnsuite : B-0001.")
        self.assertEqual(humain.recap_manquant(config.Projet(racine=Path(".")), message), [])

    def test_sans_recap(self):
        manque = humain.recap_manquant(config.Projet(racine=Path(".")), "Fait. Rien à signaler pour toi.")
        self.assertEqual(manque, ["Pour toi :", "Ensuite :"])

    def test_recap_en_gras(self):
        # Relevé de la passe de recul, E : « **Pour toi** : » n'était pas reconnu.
        message = "Fait.\n\n**Pour toi** : rien.\n__Ensuite__ : B-0001."
        self.assertEqual(humain.recap_manquant(config.Projet(racine=Path(".")), message), [])

    # Le compact de `socle roadmap`, que le récap de la clôture d'un lot
    # colle dans un bloc de code, finit par sa propre ligne « Ensuite : ».
    COMPACT = ("JA-0005  Fini avant les nouvelles fonctions        1/11 besoins clos\n"
               " ▶ L-0013  Structure du backlog, chantier en rond  2/3   en cours\n"
               "Hors lot : 4 besoins sans tâche · 1 bloqué (B-0179)\n"
               "Ensuite : JA-0002 Le pilote équipé (B-0126) · puis B-0055, B-0101")

    def test_une_ligne_du_recap_dans_un_bloc_de_code_ne_compte_pas(self):
        """ADR-0089 (L-0016, passe 1 de la revue) : la ligne « Ensuite : »
        d'une sortie collée dans un bloc de code remplissait le contrôle,
        et un récap sans la sienne passait."""
        projet = config.Projet(racine=Path("."))
        for cloture, fin in (("```", "```"), ("```text", "```"), ("~~~", "~~~"), ("````markdown", "`````")):
            message = f"Lot clos.\n\n{cloture}\n{self.COMPACT}\n{fin}\n\nPour toi : rien."
            with self.subTest(cloture=cloture):
                self.assertEqual(humain.recap_manquant(projet, message), ["Ensuite :"])
        # Les deux lignes, toutes deux dans un bloc : aucune ne compte.
        self.assertEqual(humain.recap_manquant(projet, "Fait.\n\n```\nPour toi : rien.\nEnsuite : rien.\n```"),
                         ["Pour toi :", "Ensuite :"])

    def test_un_bloc_jamais_ferme_court_jusqu_a_la_fin_du_message(self):
        projet = config.Projet(racine=Path("."))
        ouvert = f"Lot clos.\n\nPour toi : rien.\n\n```text\n{self.COMPACT}\n\nEnsuite : L-0017."
        self.assertEqual(humain.recap_manquant(projet, ouvert), ["Ensuite :"])
        # Une clôture d'un autre caractère, ou plus courte, ne le ferme pas.
        for interieur, cloture in (("```", "~~~"), ("~~~", "```"), ("``", "```"), ("```", "````")):
            message = f"Fait.\n\n{cloture}\n{interieur}\nPour toi : rien.\nEnsuite : rien.\n"
            with self.subTest(interieur=interieur, cloture=cloture):
                self.assertEqual(humain.recap_manquant(projet, message), ["Pour toi :", "Ensuite :"])
        # Une clôture d'accents graves ne porte pas d'autre accent grave : ```a``` est du code en ligne.
        self.assertEqual(humain.recap_manquant(projet, "Fait.\n```a```\nPour toi : rien.\nEnsuite : rien."), [])

    def test_les_deux_lignes_en_texte_avec_un_compact_colle_dans_un_bloc(self):
        projet = config.Projet(racine=Path("."))
        message = (f"Lot clos.\n\n```text\n{self.COMPACT}\n```\n\n  ~~~~\n  sortie\n  ~~~~~\n\n"
                   "Pour toi : rien.\n> Ensuite : L-0017.")
        self.assertEqual(humain.recap_manquant(projet, message), [])

    def test_les_motifs_de_la_politique_ne_se_cherchent_pas_dans_un_bloc_non_plus(self):
        projet = config.Projet(racine=Path("."), politique={"human": {"recap_markers": {
            "Bilan :": r"(?im)^\s*bilan\s*:", "Après :": r"(?im)^\s*après\s*:"}}})
        message = "Fait.\n\nBilan : rien.\n\n~~~\nAprès : la suite.\n~~~"
        self.assertEqual(humain.recap_manquant(projet, message), ["Après :"])
        self.assertEqual(humain.recap_manquant(projet, message.replace("~~~\n", "")), [])

    def test_transcript_illisible(self):
        self.assertIsNone(humain.dernier_message(Path("/inexistant/t.jsonl")))


if __name__ == "__main__":
    unittest.main()


class TestSpecificationsNonSoumises(unittest.TestCase):
    """D-0066 : le pilote avait écrit le code de deux spécifications que
    l'humain n'avait jamais vues. Une spécification déclarée qu'aucune
    demande ne soumet, ni en attente ni approuvée, revient à l'humain."""

    def test_une_specification_qu_aucune_demande_ne_soumet_se_signale(self):
        import types

        dossier = Path(tempfile.mkdtemp(prefix="socle-specs-"))
        self.addCleanup(shutil.rmtree, dossier, ignore_errors=True)
        git(dossier, "init", "-q", "-b", "main")
        (dossier / "docs/specs").mkdir(parents=True)
        for nom in ("approuvee", "en-attente", "refusee", "jamais"):
            (dossier / f"docs/specs/{nom}.md").write_text("# Spécification\n")
        git(dossier, "add", "-A")

        def projet(motifs):
            return types.SimpleNamespace(racine=dossier, gf=lambda *cles, defaut=None:
                                         motifs if cles == ("specs", "paths") else defaut)

        demandes = [
            types.SimpleNamespace(texte="Approuver `docs/specs/approuvee.md`.", reponse={"reponse": "valider"}),
            types.SimpleNamespace(texte="Approuver `docs/specs/en-attente.md`.", reponse=None),
            types.SimpleNamespace(texte="Approuver `docs/specs/refusee.md`.", reponse={"reponse": "reject"}),
        ]
        self.assertEqual(sorted(humain.specifications_non_soumises(projet(["docs/specs/*.md"]), demandes)),
                         ["docs/specs/jamais.md", "docs/specs/refusee.md"])
        # Sans spécification déclarée, rien ne se signale.
        self.assertEqual(humain.specifications_non_soumises(projet(None), demandes), [])
