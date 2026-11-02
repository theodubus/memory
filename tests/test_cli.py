"""Les commandes de lecture et d'écriture de la mémoire, et ce qu'elles
calculent, sur un projet fabriqué dont une branche est poussée."""

import argparse
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from socle import cli, config, hooks, human as humain, links as liens, memory as memoire, report as rapport

DEPOT = "https://github.com/essai/memoire"

SUJET = "memory/backlog/B-0001-ajouter-une-fonction-triple.md"
BACKLOG = """<!-- socle: couche=backlog zone=publique -->
# B-0001 — Ajouter une fonction triple

> statut : ouvert · origine : fichier:calc.py

Pour l'essai.
"""

ADR = """<!-- socle: couche=decisions zone=publique -->
# ADR-0001 — Une seule constante de multiplication

> statut : acceptée · date : 2026-10-10

## Décision

Une seule constante.
"""

ACTIF = """<!-- socle: couche=actif zone=publique -->
# Chantier actif

## En cours

L'essai.

## Prochaines étapes

1. Ajouter triple (B-0001).
"""


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


def sortie(commande, **args) -> tuple[int, str]:
    flux = io.StringIO()
    with contextlib.redirect_stdout(flux), contextlib.redirect_stderr(io.StringIO()):
        code = commande(argparse.Namespace(**args))
    return code, flux.getvalue()


class TestCommandes(unittest.TestCase):
    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-cli-"))
        source = self.dossier / "source"
        source.mkdir()
        git(source, "init", "-q", "-b", "main")
        (source / ".socle").mkdir()
        (source / ".socle/policy.toml").write_text(f'[human]\nrepo_url = "{DEPOT}"\n')
        (source / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        for chemin, texte in ((SUJET, BACKLOG), ("memory/active.md", ACTIF),
                              ("memory/decisions/ADR-0001-une-seule-constante.md", ADR)):
            (source / chemin).parent.mkdir(parents=True, exist_ok=True)
            (source / chemin).write_text(texte)
        git(source, "add", "-A")
        git(source, "commit", "-qm", "base")
        self.racine = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(source), str(self.racine))
        self.projet = config.Projet.charger(self.racine)
        self.pousse = git(self.racine, "rev-parse", "origin/main").strip()

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)

    def test_show_donne_l_empreinte(self):
        mem = memoire.Memoire.charger(self.racine)
        attendue = memoire.empreinte_entree(mem.entree("B-0001"))
        code, texte = sortie(cli.cmd_show, root=str(self.racine), ids=["B-0001"], index=None)
        self.assertEqual(code, 0)
        self.assertIn(f"--- B-0001@{attendue} ({SUJET}:2) ---", texte)
        code, texte = sortie(cli.cmd_show, root=str(self.racine), ids=["B-0099"], index="backlog")
        self.assertEqual(code, 1)
        self.assertIn(f"index backlog@{memoire.empreinte_index(mem, 'backlog')}", texte)

    def test_index_du_backlog_ouvert(self):
        mem = memoire.Memoire.charger(self.racine)
        self.assertEqual(memoire.lignes_index(mem, "backlog"), ["B-0001 — Ajouter une fonction triple (ouvert)"])
        avant = memoire.empreinte_index(mem, "backlog")
        p = self.racine / SUJET
        p.write_text(p.read_text().replace("statut : ouvert", "statut : fait · ref : fichier:calc.py"))
        mem = memoire.Memoire.charger(self.racine)
        self.assertEqual(memoire.lignes_index(mem, "backlog"), [])
        self.assertNotEqual(memoire.empreinte_index(mem, "backlog"), avant)

    def test_url_donne_le_permalien(self):
        code, texte = sortie(cli.cmd_url, root=str(self.racine), cibles=["B-0001", "ADR-0001", "absent.md"])
        self.assertEqual(code, 1)
        self.assertIn(f"[B-0001]({DEPOT}/blob/{self.pousse}/{SUJET})", texte)
        self.assertIn(f"[ADR-0001]({DEPOT}/blob/{self.pousse}/memory/decisions/ADR-0001-une-seule-constante.md)", texte)
        self.assertNotIn("absent.md", texte)

    def test_new_adr_prouve_la_lecture_de_l_index(self):
        mem = memoire.Memoire.charger(self.racine)
        code, texte = sortie(cli.cmd_new, root=str(self.racine), type="adr", title="Garder la constante")
        self.assertEqual(code, 0)
        adr = (self.racine / "memory/decisions/ADR-0002-garder-la-constante.md").read_text()
        self.assertIn(f"lu : decisions@{memoire.empreinte_index(mem, 'decisions')}", adr)

    def test_new_ecrit_le_sujet_meme_si_sa_sortie_est_coupee(self):
        """B-0092 : `socle new backlog … | head -1` ne créait rien, la sortie
        coupée l'arrêtant avant l'écriture."""
        class TubeCoupe(io.StringIO):
            def write(self, s):
                if "\n" in self.getvalue():
                    raise BrokenPipeError
                return super().write(s)

        with contextlib.redirect_stdout(TubeCoupe()), self.assertRaises(BrokenPipeError):
            cli.cmd_new(argparse.Namespace(root=str(self.racine), type="backlog", title="Un sujet coupé"))
        self.assertTrue((self.racine / "memory/backlog/B-0002-un-sujet-coupe.md").is_file())

    def test_new_request_questions_pose_des_questions_de_cadrage(self):
        """D-0067 : en cours de projet, des questions ouvertes sur un sujet,
        auxquelles l'humain répond librement, sur le modèle des questions
        de départ."""
        from socle import requests as demandes

        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.cmd_new(argparse.Namespace(root=str(self.racine), type="request", questions=True,
                                                            title="Cadrer le mode multi-agent")), 0)
        chemin = next((self.racine / "memory/requests").glob("D-*-cadrer-le-mode-multi-agent.md"))
        texte = chemin.read_text()
        self.assertIn("## Questions", texte)
        self.assertIn("Hypothèse de l'agent", texte)
        d = demandes.charger(self.racine, None, str(chemin.relative_to(self.racine)), texte)
        self.assertEqual(d.reponses_possibles(), ["valider", "reponses", "refuser", "contexte-insuffisant"])
        # Ce que le gabarit écrit seul passe le contrat (B-0125) : son
        # « Options » dit l'effort, le risque et la réversibilité de chaque
        # option, ses « Conséquences » ce qui se passe sans réponse.
        fautes = demandes.linter(d, config.Projet.charger(self.racine))
        self.assertFalse([f for f in fautes if "« Options »" in f or "« Conséquences »" in f], fautes)
        # Réservé aux demandes.
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.cmd_new(argparse.Namespace(root=str(self.racine), type="backlog", questions=True,
                                                            title="Un sujet")), 2)

    def test_prochaines_etapes_du_chantier_actif(self):
        self.assertEqual(humain.prochaines_etapes(self.projet), "1. Ajouter triple (B-0001).")

    def test_adresse_et_commit_pousse(self):
        self.assertEqual(liens.url_depot(self.projet), DEPOT)
        self.assertEqual(liens.commit_pousse(self.racine), self.pousse)
        self.assertIsNone(liens.url_morte(self.racine, DEPOT, f"{DEPOT}/blob/main/calc.py"))
        self.assertIn("n'existe pas", liens.url_morte(self.racine, DEPOT, f"{DEPOT}/blob/main/triple.py"))
        self.assertIn("inconnue", liens.url_morte(self.racine, DEPOT, f"{DEPOT}/blob/travail/calc.py"))

    def test_un_lien_vers_une_etiquette(self):
        # Relevé de la passe de recul, E : un lien vers une étiquette était mort.
        git(self.racine, "tag", "v1", "origin/main")
        self.assertIsNone(liens.url_morte(self.racine, DEPOT, f"{DEPOT}/blob/v1/calc.py"))
        self.assertIn("n'existe pas", liens.url_morte(self.racine, DEPOT, f"{DEPOT}/blob/v1/triple.py"))

    def test_trace_commune_aux_worktrees(self):
        autre = self.dossier / "autre"
        git(self.racine, "worktree", "add", "-q", "-b", "autre", str(autre))
        trace = config.chemin_trace(self.racine)
        self.assertEqual(trace, config.chemin_trace(autre))
        self.assertEqual(trace, (self.racine / ".git/socle/hooks.log").resolve())
        trace.parent.mkdir(parents=True, exist_ok=True)
        trace.write_text("nouvelle\n")
        self.assertEqual(config.lire_trace(self.racine), ["nouvelle"])
        self.assertEqual(config.lire_trace(autre), ["nouvelle"])
        hooks.tracer(autre, "Stop", "session")
        self.assertRegex(config.lire_trace(self.racine)[-1], r"^\S+\tStop\tsession\t$")


if __name__ == "__main__":
    unittest.main()


class TestRapportCourt(unittest.TestCase):
    """B-0034, P2 : le rapport court, pour l'humain, ne montre que ce qui
    échoue, avertit ou n'a pas pu s'exécuter."""

    def test_seul_ce_qui_signale_quelque_chose(self):
        r = rapport.Rapport()
        for nom in ("a.sain", "b.sain", "c.avertit", "d.echoue", "e.indisponible"):
            r.execute(nom)
        r.avertir("c.avertit", "à surveiller")
        r.erreur("d.echoue", "cassé")
        r.indisponible("e.indisponible", "outil absent")
        court = r.texte(court=True)
        for nom in ("c.avertit", "d.echoue", "e.indisponible"):
            self.assertIn(nom, court)
        self.assertNotIn("a.sain", court)
        self.assertIn("… et 2 autre(s) contrôle(s) sans rien à signaler", court)
        self.assertIn("ECHEC — 1 contrôle(s) : d.echoue", court)
        self.assertIn("a.sain", r.texte())

    def rapport(self):
        r = rapport.Rapport()
        for nom in ("a.sain", "b.sain", "d.echoue"):
            r.execute(nom)
        r.erreur("d.echoue", "cassé")
        return r

    def test_afficher_court_sur_un_flux(self):
        flux = io.StringIO()
        self.rapport().afficher("titre", flux=flux, court=True)
        self.assertIn("… et 2 autre(s) contrôle(s) sans rien à signaler", flux.getvalue())

    def test_cmd_check_court(self):
        from unittest import mock

        from socle import context as contexte

        ns = argparse.Namespace(stage="ci", base=None, rev=None, fast=False, only=None, court=True)
        with mock.patch.object(cli, "_projet"), mock.patch.object(cli, "_base", return_value=None), \
                mock.patch.object(contexte, "executer", return_value=self.rapport()), \
                contextlib.redirect_stdout(io.StringIO()) as flux:
            self.assertEqual(cli.cmd_check(ns), 1)
        self.assertIn("… et 2 autre(s) contrôle(s)", flux.getvalue())
        self.assertNotIn("a.sain", flux.getvalue())


class TestAide(unittest.TestCase):
    """B-0034, P6 : l'humain trouve son chemin sans lire `AGENTS.md`."""

    def test_sans_commande_l_aide_de_l_humain(self):
        with contextlib.redirect_stdout(io.StringIO()) as flux:
            self.assertEqual(cli.main(["--root", "."]), 0)
        self.assertIn("pour l'humain :", flux.getvalue())
        self.assertIn("approve", flux.getvalue())
        self.assertNotIn("pour l'agent", flux.getvalue())

    def test_chaque_commande_dans_un_seul_groupe(self):
        p, aides = cli.analyseur()
        ranges = [n for noms in cli.GROUPES.values() for n in noms if n not in cli.SOUS_COMMANDES]
        self.assertEqual(sorted(ranges), sorted(aides))
        self.assertIn("pour l'agent :", cli.aide_groupee(aides))

    def test_cmd_aide_et_ses_commandes_existent(self):
        import re

        with contextlib.redirect_stdout(io.StringIO()) as flux:
            self.assertEqual(cli.cmd_aide(argparse.Namespace()), 0)
        guide = flux.getvalue()
        self.assertIn("Le socle, côté humain", guide)
        _, aides = cli.analyseur()
        citees = set(re.findall(r"(?:\.socle/socle|-m socle) ([a-z-]+)", guide))
        self.assertTrue(citees)
        self.assertEqual(citees - set(aides), set())


class TestChecks(unittest.TestCase):
    def test_cmd_checks_liste_tous_les_controles_executes(self):
        """`socle checks` oubliait les contrôles de la mémoire privée, que
        l'exécution charge : la liste n'était pas celle qui tourne. Dans un
        interpréteur neuf, où aucun autre module ne les a déjà chargés."""
        import sys

        from socle import context as contexte

        moteur = Path(cli.__file__).resolve().parent.parent
        sortie = subprocess.run([sys.executable, "-c", "from socle.cli import cmd_checks; cmd_checks(None)"],
                                env={**os.environ, "PYTHONPATH": str(moteur)}, capture_output=True, text=True).stdout
        listes = {l.split()[0] for l in sortie.splitlines() if l.strip()}
        self.assertIn("prive.verrou", listes)
        self.assertEqual(listes, set(contexte.charger_controles()))


class TestTubeFerme(unittest.TestCase):
    """B-0070 : une sortie coupée (`| head -1`) n'est pas une panne."""

    def test_main_rend_la_main_sans_trace_quand_le_lecteur_ferme_le_tube(self):
        racine = Path(__file__).resolve().parent.parent
        p = subprocess.Popen([sys.executable, str(racine / ".socle/socle"), "checks"], cwd=racine,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        p.stdout.close()  # le lecteur s'en va avant que la commande n'écrive
        erreurs = p.stderr.read()
        p.wait(timeout=60)
        self.assertNotIn("Traceback", erreurs)
        self.assertNotIn("BrokenPipeError", erreurs)
        self.assertEqual(p.returncode, 0)

    def test_une_sortie_tamponnee_jusqu_au_bout_constate_aussi_le_tube_ferme(self):
        """Python 3.14 tamponne 128 Kio, 8 Kio avant : la sortie de `checks`
        ne partait plus qu'à l'arrêt de l'interpréteur, hors de `main`, qui
        disait « Exception ignored while flushing sys.stdout » et rendait 120.
        Le push de Théo s'y est arrêté."""
        import contextlib
        import io

        racine = Path(__file__).resolve().parent.parent
        lecture, ecriture = os.pipe()
        os.close(lecture)  # le lecteur s'en va avant que la commande n'écrive
        flux = io.TextIOWrapper(io.BufferedWriter(io.FileIO(ecriture, "w"), buffer_size=1 << 20), encoding="utf-8")
        avant, sys.stdout = sys.stdout, flux
        try:
            code = cli.main(["--root", str(racine), "checks"])
            flux.flush()  # ce que fait l'arrêt de l'interpréteur
        finally:
            sys.stdout = avant
            with contextlib.suppress(BrokenPipeError):
                flux.close()
        self.assertEqual(code, 0)


class TestSignataire(unittest.TestCase):
    """B-0073 : le nom de l'humain, dans la politique, signe ses réponses
    relayées ; l'agent ne le devine pas."""

    def projet(self, nom: str = "") -> config.Projet:
        politique = {"human": {"name": nom}} if nom else {}
        return config.Projet(racine=Path(tempfile.mkdtemp()), politique=politique)

    def args(self, by=None, relayed=True):
        return argparse.Namespace(by=by, relayed=relayed)

    def test_politique_nom_ecrit_le_nom_de_l_humain(self):
        from socle import installer as installeur
        from socle.templates import gabarit

        texte = installeur.politique_nom(gabarit("policy.toml", "fr"), "Théo")
        self.assertIn('\nname = "Théo"\n', texte)
        self.assertEqual(installeur.politique_nom(gabarit("policy.toml", "fr"), ""), gabarit("policy.toml", "fr"))

    def test_le_nom_de_la_politique_signe_par_defaut(self):
        self.assertEqual(cli._signataire(self.projet("Théo"), self.args()), "Théo")
        self.assertEqual(cli._auteur(self.projet("Théo")), "Théo")

    def test_sans_nom_ni_by_une_reponse_relayee_n_est_signee_par_personne(self):
        self.assertIsNone(cli._signataire(self.projet(), self.args()))

    def test_un_by_qui_differe_de_la_politique_est_dit(self):
        erreurs = io.StringIO()
        with contextlib.redirect_stderr(erreurs):
            self.assertEqual(cli._signataire(self.projet("Théo"), self.args(by="Marie")), "Marie")
        self.assertIn("Marie", erreurs.getvalue())
        self.assertIn("Théo", erreurs.getvalue())

    def test_l_installeur_pose_le_nom_git_de_l_humain(self):
        from socle import installer as installeur

        racine = Path(tempfile.mkdtemp(prefix="socle-nom-"))
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True)
        subprocess.run(["git", "config", "user.name", "Théo Essai"], cwd=racine, check=True)
        (racine / "calc.py").write_text("X = 1\n", encoding="utf-8")
        # Hors session cloud : l'identité git est alors celle de l'humain.
        with contextlib.redirect_stdout(io.StringIO()), mock.patch.dict(os.environ, {hooks.SESSION_CLOUD: ""}):
            installeur.installer(racine, "python", "@essai", source=Path(__file__).resolve().parent.parent / "engine")
        self.assertEqual(config.Projet.charger(racine).pol("human", "name"), "Théo Essai")
        self.assertEqual(installeur.diff_politique(racine), [])

    def installer_en_session_cloud(self, **options) -> tuple[Path, str]:
        from socle import installer as installeur

        racine = Path(tempfile.mkdtemp(prefix="socle-nom-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True)
        subprocess.run(["git", "config", "user.name", "Claude"], cwd=racine, check=True)
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), mock.patch.dict(os.environ, {hooks.SESSION_CLOUD: "true"}):
            installeur.installer(racine, "python", "@essai", source=Path(__file__).resolve().parent.parent / "engine",
                                 **options)
        return racine, sortie.getvalue()

    def test_en_session_cloud_le_nom_git_de_l_agent_ne_signe_pas(self):
        """B-0094 : le pilote, installé par l'agent en session cloud, nommait
        l'humain « Claude », l'identité git du conteneur."""
        racine, sortie = self.installer_en_session_cloud()
        self.assertEqual(config.Projet.charger(racine).pol("human", "name", defaut=""), "")
        self.assertIn("écrire ton nom dans `.socle/policy.toml` (`[human] name`) avant de fusionner "
                      "l'installation", sortie)

    def test_nom_de_l_humain_ne_prend_pas_l_identite_git_de_l_agent(self):
        from socle import installer as installeur

        racine = Path(tempfile.mkdtemp(prefix="socle-nom-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True)
        subprocess.run(["git", "config", "user.name", "Claude"], cwd=racine, check=True)
        with mock.patch.dict(os.environ, {hooks.SESSION_CLOUD: "true"}):
            self.assertEqual(installeur.nom_de_l_humain(racine), "")
            self.assertEqual(installeur.nom_de_l_humain(racine, " Théo "), "Théo")
        with mock.patch.dict(os.environ, {hooks.SESSION_CLOUD: ""}):
            self.assertEqual(installeur.nom_de_l_humain(racine), "Claude")

    def test_human_donne_le_nom_meme_en_session_cloud(self):
        racine, sortie = self.installer_en_session_cloud(humain="Théo")
        self.assertEqual(config.Projet.charger(racine).pol("human", "name"), "Théo")
        self.assertNotIn("écrire ton nom", sortie)
        args = cli.analyseur()[0].parse_args(["install", "--target", ".", "--human", "Théo"])
        self.assertEqual(args.human, "Théo")
