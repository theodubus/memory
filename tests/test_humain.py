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

    def test_elles_apparaissent_dans_ce_qui_revient_a_l_humain(self):
        (self.clone / "memory").mkdir()
        quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertTrue(any("`fusionnee`" in q for q in quoi), quoi)

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
