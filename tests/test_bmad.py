"""Le mariage avec BMAD Method (ADR-0032) : ce que le socle lit de BMAD
(ses dossiers, ses specs, ses travaux reportés, l'état de son sprint), et
les reports qu'il fait entrer dans son backlog."""

import contextlib
import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import bmad, checks_bmad as controles_bmad, config, context as contexte, hooks, installer as installeur, \
    memory as memoire, requests as demandes, state as etat

MOTEUR = Path(__file__).resolve().parent.parent / "engine"

SPEC = """---
title: 'Ajouter triple'
type: 'feature' # feature | bugfix
status: 'ready-for-dev'
route: 'dispatch'
---

<frozen-after-approval reason="human-owned intent">

## Intent

**Problem:** Il manque triple.

</frozen-after-approval>

## Code Map
"""

REPORTS = """- source_spec: `_bmad-output/implementation-artifacts/spec-triple.md`
  summary: Décrire le projet dans AGENTS.md.
  evidence: AGENTS.md, ligne 3 ; antérieur au changement.

- source_spec: none
  summary: Valider l'entrée de double.
  evidence: double("a") rend "aa".
"""

SPRINT = """# STATUS DEFINITIONS:
generated: 05-06-2025 21:30
development_status:
  epic-1: in-progress
  1-1-authentification: done
  1-2-comptes: in-progress
  1-3-donnees: review
  epic-1-retrospective: optional

action_items: []
"""


def depot(fichiers: dict[str, str]) -> Path:
    racine = Path(tempfile.mkdtemp(prefix="socle-bmad-"))
    env = {**os.environ, "HOME": str(racine), "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True, env=env)
    for chemin, texte in fichiers.items():
        p = racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=racine, check=True, env=env)
    return racine


def projet_avec_bmad(reports: str = REPORTS) -> Path:
    racine = depot({"calc.py": "X = 1\n",
                    "_bmad/config.toml": '[modules.bmm]\nimplementation_artifacts = '
                                         '"{project-root}/_bmad-output/implementation-artifacts"\n',
                    "_bmad-output/implementation-artifacts/spec-triple.md": SPEC,
                    "_bmad-output/implementation-artifacts/deferred-work.md": reports})
    with contextlib.redirect_stdout(io.StringIO()):
        installeur.installer(racine, "python", "@essai", source=MOTEUR)
    return racine


class TestLecture(unittest.TestCase):
    def test_en_tete_lit_les_cles_sans_guillemets_ni_commentaires(self):
        self.assertEqual(bmad.en_tete(SPEC)["type"], "feature")
        self.assertEqual(bmad.en_tete(SPEC)["status"], "ready-for-dev")
        self.assertEqual(bmad.en_tete("# Pas d'en-tête\n"), {})
        self.assertEqual(bmad.en_tete("---\nstatus: x\n"), {})

    def test_spec_reconnait_une_spec_et_son_intention_figee(self):
        s = bmad.spec("x.md", SPEC)
        self.assertEqual((s.statut, s.route), ("ready-for-dev", "dispatch"))
        self.assertIn("Il manque triple.", s.intention)
        self.assertTrue(s.approuvee)
        self.assertIsNone(bmad.spec("y.md", "---\ntitle: 'brief'\n---\n"))

    def test_l_empreinte_de_l_intention_ignore_les_espaces_pas_le_texte(self):
        a = bmad.spec("x.md", SPEC).empreinte_intention
        self.assertEqual(bmad.spec("x.md", SPEC.replace("Il manque", "Il  manque")).empreinte_intention, a)
        self.assertNotEqual(bmad.spec("x.md", SPEC.replace("triple.", "quadruple.")).empreinte_intention, a)

    def test_une_spec_courte_ou_en_brouillon_n_est_pas_approuvee(self):
        self.assertFalse(bmad.spec("x.md", SPEC.replace("'dispatch'", "'oneshot'")).approuvee)
        self.assertFalse(bmad.spec("x.md", SPEC.replace("'ready-for-dev'", "'draft'")).approuvee)

    def test_reports_lit_chaque_entree(self):
        r = bmad.reports(REPORTS)
        self.assertEqual([x.resume for x in r], ["Décrire le projet dans AGENTS.md.", "Valider l'entrée de double."])
        self.assertEqual(r[0].source, "_bmad-output/implementation-artifacts/spec-triple.md")
        self.assertEqual(r[1].source, "none")
        self.assertNotEqual(r[0].empreinte, r[1].empreinte)
        self.assertEqual(bmad.reports("# rien\n"), [])

    def test_sprint_lit_les_statuts(self):
        self.assertEqual(bmad.sprint(SPRINT), {"epic-1": "in-progress", "1-1-authentification": "done",
                                               "1-2-comptes": "in-progress", "1-3-donnees": "review",
                                               "epic-1-retrospective": "optional"})

    def test_dossiers_suit_la_configuration_de_bmad(self):
        racine = depot({"_bmad/config.toml": '[modules.bmm]\nplanning_artifacts = "{project-root}/plan"\n'
                                              'implementation_artifacts = "{project-root}/out/impl"\n'})
        self.assertTrue(bmad.present(racine))
        self.assertEqual(bmad.dossiers(racine), ("plan", "out/impl"))
        self.assertEqual(bmad.fichier_des_reports(racine), "out/impl/deferred-work.md")
        self.assertFalse(bmad.present(depot({"calc.py": ""})))

    def test_specs_trouve_les_specs_du_dossier_d_implementation(self):
        racine = projet_avec_bmad()
        specs = bmad.specs(racine, ["_bmad-output/implementation-artifacts/spec-triple.md", "calc.py"])
        self.assertEqual([s.chemin for s in specs], ["_bmad-output/implementation-artifacts/spec-triple.md"])


class TestReports(unittest.TestCase):
    def test_un_report_hors_du_backlog_fait_echouer_le_controle(self):
        racine = projet_avec_bmad()
        p = config.Projet.charger(racine)
        rapport = contexte.executer(contexte.Contexte(p, etage="ci", base=None), ids=["bmad.reports"])
        self.assertIn("bmad.reports", rapport.controles_en_echec())
        self.assertIn("bmad-import", "\n".join(c.message for c in rapport.constats))

    def test_importer_fait_entrer_chaque_report_une_fois(self):
        racine = projet_avec_bmad()
        p = config.Projet.charger(racine)
        poses = controles_bmad.importer(p)
        self.assertEqual(len(poses), 2)
        self.assertEqual(controles_bmad.importer(p), [])
        mem = memoire.Memoire.charger(racine)
        self.assertEqual(controles_bmad.reports_entres(mem), {r.empreinte for r in bmad.reports(REPORTS)})
        sujet = (racine / poses[0][1]).read_text(encoding="utf-8")
        self.assertIn("Décrire le projet dans AGENTS.md", sujet)
        self.assertIn("deferred-work.md", sujet)
        rapport = contexte.executer(contexte.Contexte(config.Projet.charger(racine), etage="ci", base=None))
        self.assertNotIn("bmad.reports", rapport.controles_en_echec())
        self.assertNotIn("memoire.format", rapport.controles_en_echec())
        self.assertNotIn("memoire.lectures", rapport.controles_en_echec())

    def test_la_commande_dit_ce_qu_elle_pose(self):
        from socle import cli

        import argparse

        racine = projet_avec_bmad()
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            self.assertEqual(cli.cmd_bmad_import(argparse.Namespace(root=str(racine))), 0)
        self.assertEqual(len([l for l in sortie.getvalue().splitlines() if l.startswith("B-")]), 2)
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            cli.main(["--root", str(racine), "bmad-import"])
        self.assertIn("aucun travail reporté", sortie.getvalue())

    def test_reports_a_entrer_ignore_un_doublon_et_un_projet_sans_bmad(self):
        racine = projet_avec_bmad(REPORTS + "\n" + REPORTS.split("\n\n")[0] + "\n")
        p = config.Projet.charger(racine)
        self.assertEqual(len(controles_bmad.reports_a_entrer(p, memoire.Memoire.charger(racine))), 2)
        sans = depot({"calc.py": ""})
        self.assertEqual(controles_bmad.reports_a_entrer(config.Projet(racine=sans), memoire.Memoire.charger(sans)), [])


class TestEtat(unittest.TestCase):
    def test_l_etat_montre_les_specs_le_sprint_et_les_reports(self):
        racine = projet_avec_bmad()
        (racine / "_bmad-output/implementation-artifacts/sprint-status.yaml").write_text(SPRINT, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=racine, check=True)
        texte = etat.calculer(config.Projet.charger(racine), contenus=False)
        self.assertIn("1 spec(s) non finie(s)", texte)
        self.assertIn("spec-triple.md (ready-for-dev, dispatch)", texte)
        self.assertIn("in-progress : 1-2-comptes", texte)
        self.assertIn("review : 1-3-donnees", texte)
        self.assertIn("2 travail(aux) reporté(s) par BMAD hors du backlog", texte)

    def test_sans_bmad_l_etat_n_en_dit_rien(self):
        racine = depot({"calc.py": "X = 1\n"})
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(racine, "python", "@essai", source=MOTEUR)
        self.assertNotIn("BMAD", etat.calculer(config.Projet.charger(racine), contenus=False))


class TestSeance(unittest.TestCase):
    def setUp(self):
        self.racine = projet_avec_bmad(reports="")
        self.projet = config.Projet.charger(self.racine)
        self.spec = "_bmad-output/implementation-artifacts/spec-triple.md"

    def approuver(self, sujet=None):
        return demandes.ecrire_seance(self.projet, "Approuver la spec de triple", "Tu approuves la spec ?",
                                      "valider", "Théo", "2026-10-19", "conversation", "Oui, approuvé.",
                                      sujet or f"{self.spec}@{bmad.spec(self.spec, SPEC).empreinte_intention}")

    def echecs(self):
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        rapport = contexte.executer(contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=None),
                                    ids=["bmad.approbation", "demandes.contrat", "demandes.reponses"])
        return rapport.controles_en_echec(), "\n".join(c.message for c in rapport.constats)

    def test_ecrire_seance_pose_la_question_et_sa_reponse(self):
        chemin, reponse = self.approuver()
        d = next(x for x in demandes.toutes(self.racine) if x.chemin == chemin)
        self.assertTrue(d.seance)
        self.assertTrue(d.validee)
        self.assertEqual(d.sujet[0], self.spec)
        self.assertIn("Tu approuves la spec ?", d.texte)
        self.assertTrue((self.racine / reponse).is_file())
        self.assertEqual(demandes.verifier_reponse(d), [])
        self.assertIsNone(demandes.illisible(self.projet, d))
        self.assertTrue(d.accepte("approuver et continuer"))

    def test_une_seance_relayee_sans_citation_est_refusee(self):
        with self.assertRaises(ValueError):
            demandes.ecrire_seance(self.projet, "Approuver la spec de triple", "", "valider", "Théo", "2026-10-19",
                                   "conversation", "")
        self.assertEqual(list((self.racine / "memory/requests").glob("D-*.md")), [])

    def test_une_seance_sans_reponse_est_hors_contrat(self):
        chemin, reponse = self.approuver()
        (self.racine / reponse).unlink()
        d = next(x for x in demandes.toutes(self.racine) if x.chemin == chemin)
        self.assertTrue(any("séance" in f for f in demandes.linter(d, self.projet)))

    def test_une_spec_approuvee_sans_trace_est_refusee(self):
        echecs, texte = self.echecs()
        self.assertIn("bmad.approbation", echecs)
        self.assertIn("socle decision", texte)

    def test_une_spec_approuvee_et_consignee_passe(self):
        self.approuver()
        echecs, texte = self.echecs()
        self.assertEqual(echecs, [], texte)

    def test_une_intention_changee_apres_l_approbation_est_refusee(self):
        self.approuver()
        p = self.racine / self.spec
        p.write_text(p.read_text(encoding="utf-8").replace("Il manque triple.", "Il manque quadruple."),
                     encoding="utf-8")
        echecs, texte = self.echecs()
        self.assertIn("bmad.approbation", echecs)
        self.assertIn("changée après son approbation", texte)

    def test_une_spec_courte_n_a_pas_besoin_d_approbation(self):
        p = self.racine / self.spec
        p.write_text(SPEC.replace("'dispatch'", "'oneshot'"), encoding="utf-8")
        self.assertNotIn("bmad.approbation", self.echecs()[0])

    def test_la_commande_cmd_decision_cite_l_intention_de_la_spec(self):
        import argparse
        from socle import cli

        citation = self.racine.parent / f"{self.racine.name}-citation.txt"
        citation.write_text("Oui, approuvé.", encoding="utf-8")
        args = argparse.Namespace(root=str(self.racine), question="Approuver la spec de triple", answer="valider",
                                  question_file=None, about=self.spec, by="Théo", relayed=True, quote=None,
                                  quote_file=str(citation))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.cmd_decision(args), 0)
        d = next(x for x in demandes.toutes(self.racine) if x.seance)
        self.assertEqual(d.sujet, (self.spec, bmad.spec(self.spec, SPEC).empreinte_intention))

    def test_le_hook_refuse_une_decision_que_l_agent_ne_relaie_pas(self):
        h = hooks.COMMANDES_HUMAINES.search("python3 .socle/socle decision 'Approuver la spec x' valider")
        self.assertIsNotNone(h)
        self.assertEqual(h.group(0), "decision")


CUSTOMIZE_WORKFLOW = "[workflow]\nactivation_steps_append = []\non_complete = \"\"\n"
CUSTOMIZE_AGENT = "[agent]\nactivation_steps_append = []\n"


class TestPersonnalisation(unittest.TestCase):
    def projet(self, propre: str | None = None) -> Path:
        fichiers = {"calc.py": "X = 1\n", "_bmad/config.toml": "",
                    ".claude/skills/bmad-build/customize.toml": CUSTOMIZE_WORKFLOW,
                    ".claude/skills/bmad-agent-dev/customize.toml": CUSTOMIZE_AGENT,
                    ".claude/skills/bmad-help/SKILL.md": "# aide\n"}
        if propre:
            fichiers["_bmad/custom/bmad-build.toml"] = propre
        return depot(fichiers)

    def test_personnalisations_bmad_lit_la_table_de_chaque_skill(self):
        self.assertEqual(installeur.personnalisations_bmad(self.projet()),
                         {"bmad-agent-dev": "agent", "bmad-build": "workflow"})

    def test_l_installeur_pose_la_personnalisation_dans_la_langue_du_projet(self):
        import tomllib

        racine = self.projet()
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            installeur.installer(racine, "python", "@essai", source=MOTEUR)
        self.assertIn("personnalisation posée pour 2 skill(s)", sortie.getvalue())
        build = tomllib.loads((racine / "_bmad/custom/bmad-build.toml").read_text(encoding="utf-8"))["workflow"]
        self.assertEqual(build["persistent_facts"], ["file:memory/active.md", "file:memory/canonical.md"])
        self.assertIn("socle decision", " ".join(build["activation_steps_append"]))
        self.assertIn("bmad-import", build["on_complete"])
        agent = tomllib.loads((racine / "_bmad/custom/bmad-agent-dev.toml").read_text(encoding="utf-8"))["agent"]
        self.assertNotIn("on_complete", agent)
        self.assertNotIn("sans la personnalisation du socle",
                         etat.calculer(config.Projet.charger(racine), contenus=False))

    def test_poser_bmad_garde_une_personnalisation_du_projet(self):
        racine = self.projet(propre="[workflow]\non_complete = \"Ouvrir la spec.\"\n")
        journal = installeur.poser_bmad(racine, "fr")
        self.assertIn("bmad-build", " ".join(journal))
        self.assertEqual((racine / "_bmad/custom/bmad-build.toml").read_text(encoding="utf-8"),
                         "[workflow]\non_complete = \"Ouvrir la spec.\"\n")
        self.assertTrue((racine / "_bmad/custom/bmad-agent-dev.toml").is_file())

    def test_poser_bmad_regenere_ce_qu_il_a_pose_et_parle_anglais(self):
        racine = self.projet()
        installeur.poser_bmad(racine, "en")
        p = racine / "_bmad/custom/bmad-build.toml"
        self.assertIn("Before handing back", p.read_text(encoding="utf-8"))
        installeur.poser_bmad(racine, "fr")
        self.assertIn("Avant de rendre la main", p.read_text(encoding="utf-8"))

    def test_l_etat_signale_un_skill_sans_personnalisation(self):
        racine = projet_avec_bmad(reports="")
        (racine / ".claude/skills/bmad-spec").mkdir(parents=True)
        (racine / ".claude/skills/bmad-spec/customize.toml").write_text(CUSTOMIZE_WORKFLOW, encoding="utf-8")
        self.assertIn("sans la personnalisation du socle (bmad-spec)",
                      etat.calculer(config.Projet.charger(racine), contenus=False))


# Un npx factice : il note ses arguments, et pose ce que BMAD poserait.
NPX_FACTICE = """#!/usr/bin/env python3
import json, sys
from pathlib import Path
args = sys.argv[1:]
cible = Path(args[args.index("--directory") + 1])
(cible / "appel-npx.json").write_text(json.dumps(args))
(cible / "_bmad").mkdir()
(cible / "_bmad/config.toml").write_text("")
skill = cible / ".claude/skills/bmad-build"
skill.mkdir(parents=True)
(skill / "customize.toml").write_text("[workflow]\\non_complete = ''\\n")
"""


class TestEnUneCommande(unittest.TestCase):
    def avec_npx(self, echec: bool = False) -> Path:
        dossier = Path(tempfile.mkdtemp(prefix="socle-npx-"))
        npx = dossier / "npx"
        npx.write_text("#!/bin/sh\nexit 3\n" if echec else NPX_FACTICE, encoding="utf-8")
        npx.chmod(0o755)
        return dossier

    def installer(self, racine: Path, dossier_npx: Path | None, **options) -> tuple[int, str]:
        from unittest import mock

        chemin = os.environ.get("PATH", "")
        chemin = f"{dossier_npx}:{chemin}" if dossier_npx else ":".join(
            d for d in chemin.split(":") if not (Path(d) / "npx").exists())
        sortie = io.StringIO()
        with mock.patch.dict(os.environ, {"PATH": chemin}), contextlib.redirect_stdout(sortie), \
                contextlib.redirect_stderr(sortie):
            code = installeur.installer(racine, "python", "@essai", source=MOTEUR, avec_bmad=True, **options)
        return code, sortie.getvalue()

    def test_commande_bmad_suit_la_langue_et_la_version(self):
        c = installeur.commande_bmad(Path("/p"), "en", "6.12.4")
        self.assertEqual(c[:3], ["npx", "-y", "bmad-method@6.12.4"])
        self.assertEqual(c[c.index("--communication-language") + 1], "English")
        self.assertEqual(installeur.commande_bmad(Path("/p"), "fr")[2], f"bmad-method@{installeur.VERSION_BMAD}")

    def test_une_commande_installe_bmad_puis_le_socle_qui_le_reconnait(self):
        import json

        racine = depot({"calc.py": "X = 1\n"})
        code, sortie = self.installer(racine, self.avec_npx())
        self.assertEqual(code, 0, sortie)
        appel = json.loads((racine / "appel-npx.json").read_text())
        self.assertIn("--yes", appel)
        self.assertEqual(appel[appel.index("--document-output-language") + 1], "French")
        self.assertIn("BMAD Method 6.12.4 installé", sortie)
        self.assertEqual(config.Projet.charger(racine).chemins_tiers(), ["_bmad/**", "**/skills/bmad-*/**"])
        self.assertTrue((racine / "_bmad/custom/bmad-build.toml").is_file())

    def test_installer_bmad_garde_un_bmad_deja_la(self):
        racine = depot({"calc.py": "X = 1\n", "_bmad/config.toml": ""})
        present, dits = installeur.installer_bmad(racine, "fr")
        self.assertTrue(present)
        self.assertIn("déjà présent", dits[0])
        self.assertFalse((racine / "appel-npx.json").exists())

    def test_sans_npx_l_installation_s_arrete_avec_le_remede(self):
        racine = depot({"calc.py": "X = 1\n"})
        code, sortie = self.installer(racine, None)
        self.assertEqual(code, 2)
        self.assertIn("Node.js", sortie)
        self.assertFalse((racine / ".socle").exists())

    def test_un_echec_de_bmad_arrete_l_installation(self):
        racine = depot({"calc.py": "X = 1\n"})
        code, sortie = self.installer(racine, self.avec_npx(echec=True), version_bmad="9.9.9")
        self.assertEqual(code, 2)
        self.assertIn("BMAD Method 9.9.9 a échoué", sortie)
        self.assertFalse((racine / ".socle").exists())


if __name__ == "__main__":
    unittest.main()
