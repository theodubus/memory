"""T-0081 (B-0259, D-0174) : la passation programmée, côté moteur. `socle
handoff prompt` écrit le prompt de la session neuve, précédé de sa garde :
refusé tant que la tête locale n'est pas poussée et, pour une session
programmée, aux bornes d'une chaîne sans l'humain. `socle handoff check` juge
la garde dans la session neuve, sur de vrais dépôts git dont l'origine est
nue, comme sur GitHub."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from socle import cli, config, handoff as passation, messages
from tests.test_structure import entree

# L'heure de la passation, et celle d'un commit qui la suit ou la précède.
HEURE = datetime(2026, 11, 24, 10, 5, tzinfo=timezone.utc)
APRES = HEURE + timedelta(minutes=10)
AVANT = HEURE - timedelta(minutes=10)


def git(cwd: Path, *args: str, date: datetime | None = None) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    if date:
        env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"] = date.strftime("%Y-%m-%dT%H:%M:%S+0000")
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


def ecrire(racine: Path, chemin: str, texte: str):
    p = racine / chemin
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texte, encoding="utf-8")


def commiter(racine: Path, message: str, fichiers: dict[str, str], date: datetime | None = None) -> str:
    for chemin, texte in fichiers.items():
        ecrire(racine, chemin, texte)
    git(racine, "add", "-A")
    git(racine, "commit", "-q", "-m", message, date=date)
    return git(racine, "rev-parse", "HEAD").strip()


# Un lot en cours, une tâche faite et une prête ; et un lot dont la seule
# tâche attend une demande sans réponse.
BACKLOG = dict([
    entree("B-0001"),
    entree("T-0001", "fait", meta="besoin : B-0001"),
    entree("T-0002", meta="besoin : B-0001"),
    entree("L-0001", "en cours", meta="après : T-0001, T-0002"),
])
SANS_TACHE_PRETE = dict([
    entree("B-0001"),
    entree("T-0003", meta="besoin : B-0001 · après : D-0001"),
    entree("L-0002", meta="après : T-0003"),
    ("memory/requests/D-0001-essai.md", "<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Une demande\n\n"
                                        "> date : 2026-11-24\n"),
])


class Depots(unittest.TestCase):
    """Une origine nue, la session qui part (`partante`), qui pousse sa
    branche `travail`, puis la session neuve (`neuve`), clonée après."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-passation-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        self.origine = self.dossier / "memory.git"
        git(self.dossier, "init", "-q", "--bare", "-b", "main", str(self.origine))
        self.partante = self.clone("partante")
        commiter(self.partante, "le projet", {"app.py": "print('ok')\n", **BACKLOG}, date=AVANT)
        git(self.partante, "push", "-q", "origin", "main")
        git(self.partante, "checkout", "-q", "-b", "travail")
        self.tete = commiter(self.partante, "le lot", {"memory/active.md": "# Chantier actif\n\nLe lot.\n"},
                             date=AVANT)
        git(self.partante, "push", "-q", "-u", "origin", "travail")

    def clone(self, nom: str) -> Path:
        git(self.dossier, "clone", "-q", str(self.origine), nom)
        return self.dossier / nom

    def projet(self, racine: Path) -> config.Projet:
        return config.Projet.charger(racine)

    def neuve(self, ref: str = "origin/travail", tete: str | None = None, depuis: datetime | None = HEURE):
        """La session neuve : clonée maintenant, `git fetch`, puis la garde."""
        neuve = self.dossier / "neuve"
        if not neuve.is_dir():
            neuve = self.clone("neuve")
        git(neuve, "fetch", "-q", "--prune", "origin")
        return passation.juger(self.projet(neuve), ref, tete or self.tete, depuis)

    def fusionner(self, squash: bool = False, supprimer: bool = False):
        """La pull request du lot fusionnée sur GitHub : par un commit de
        fusion, ou par squash ; sa branche supprimée ensuite, ou non."""
        github = self.clone("github")
        if squash:
            git(github, "merge", "-q", "--squash", "origin/travail")
            git(github, "commit", "-q", "-m", "Le lot (#1)", date=APRES)
        else:
            git(github, "merge", "-q", "--no-ff", "-m", "Merge pull request #1", "origin/travail", date=APRES)
        git(github, "push", "-q", "origin", "main")
        if supprimer:
            git(github, "push", "-q", "origin", "--delete", "travail")


class TestLePrompt(Depots):
    def test_il_refuse_tant_que_la_tete_locale_n_est_pas_poussee(self):
        commiter(self.partante, "pas poussé", {"memory/active.md": "# Chantier actif\n\nPlus loin.\n"}, date=AVANT)
        with self.assertRaises(passation.PassationRefusee) as refus:
            passation.tete_poussee(self.partante)
        self.assertIn("n'est pas poussée : pousser d'abord", str(refus.exception))
        git(self.partante, "push", "-q", "origin", "travail")
        self.assertEqual(passation.tete_poussee(self.partante)[0], "origin/travail")
        # Un fichier suivi changé sans commit ne passe pas non plus.
        ecrire(self.partante, "app.py", "print('changé')\n")
        with self.assertRaises(passation.PassationRefusee) as refus:
            passation.prompt(self.projet(self.partante))
        self.assertIn("ne sont pas commités", str(refus.exception))

    def test_il_nomme_la_tete_distante_et_l_heure_puis_le_prompt_d_une_session_neuve(self):
        texte = passation.prompt(self.projet(self.partante), attente="la CI du commit de tête.", maintenant=HEURE)
        lignes = texte.splitlines()
        self.assertEqual(lignes[0], "Passation — partante, à 2026-11-24T10:05:00Z.")
        self.assertEqual(lignes[1:3], [
            "Avant tout : git fetch origin, puis",
            f"python3 .socle/socle handoff check --ref origin/travail --head {self.tete} --since 2026-11-24T10:05:00Z"])
        self.assertIn("S'il refuse, ne fais rien d'autre que le dire", lignes[3])
        self.assertIn("la pull request ouverte de cette branche devient la tienne", lignes[3])
        self.assertEqual(lignes[4:], [
            "Chaîne : 0 lot(s) mené(s) sans message de l'humain.",
            "Reprends le travail de ce dépôt, en session neuve.",
            "Puis : lis l'état que le démarrage injecte, et ce qu'une ligne « !! coupé » y dit manquer ; puis le "
            "chantier actif, et applique-les.",
            "Le lot : L-0001 (T-0002), selon le skill socle-batch.",
            "Ce qui attend : la CI du commit de tête."])
        # Sans le lien de la session, ni ce qui attend.
        lignes = passation.prompt(self.projet(self.partante), maintenant=HEURE).splitlines()
        self.assertEqual(lignes[0], "Passation — partante, à 2026-11-24T10:05:00Z.")
        self.assertEqual(lignes[-1], "Ce qui attend : rien.")

    def test_apres_une_fusion_la_garde_nomme_la_branche_par_defaut(self):
        """La pull request fusionnée avant la passation, la branche locale
        repartie de la branche par défaut et pas encore poussée."""
        self.fusionner()
        git(self.partante, "fetch", "-q", "origin")
        git(self.partante, "reset", "-q", "--hard", "origin/main")
        ref, tete = passation.tete_poussee(self.partante)
        self.assertEqual((ref, tete), ("origin/main", git(self.partante, "rev-parse", "origin/main").strip()))

    def test_les_bornes_d_une_session_programmee(self):
        projet = self.projet(self.partante)
        texte = passation.prompt(projet, chaine=1, programmee=True, maintenant=HEURE)
        self.assertIn("Chaîne : 1 lot(s) mené(s) sans message de l'humain.", texte)
        # Deux lots menés sans message de l'humain : rien ne se programme.
        with self.assertRaises(passation.PassationRefusee) as refus:
            passation.prompt(projet, chaine=2, programmee=True)
        self.assertIn("sa borne est 2 : ne rien programmer, donner le prompt à copier", str(refus.exception))
        # Le prompt à copier porte la chaîne 0.
        with self.assertRaises(passation.PassationRefusee) as refus:
            passation.prompt(projet, chaine=1)
        self.assertIn("le prompt à copier porte la chaîne 0", str(refus.exception))
        # Un prochain lot sans tâche prête : le prompt se donne à copier.
        for chemin in BACKLOG:
            (self.partante / chemin).unlink()
        commiter(self.partante, "un lot qui attend une demande", SANS_TACHE_PRETE, date=AVANT)
        git(self.partante, "push", "-q", "origin", "travail")
        self.assertEqual(passation.lot_de_l_etat(self.partante), ("L-0002", ["T-0003"], False))
        with self.assertRaises(passation.PassationRefusee) as refus:
            passation.prompt(projet, programmee=True)
        self.assertIn("le prochain lot n'a aucune tâche prête", str(refus.exception))
        self.assertIn("Le lot : L-0002 (T-0003), selon le skill socle-batch.", passation.prompt(projet))

    def test_le_lot_de_l_etat(self):
        self.assertEqual(passation.lot_de_l_etat(self.partante), ("L-0001", ["T-0002"], True))
        self.assertEqual(passation.nom_du_depot(self.projet(self.partante)), "partante")


class TestLaGarde(Depots):
    def test_une_passation_que_rien_n_a_suivie_est_acceptee(self):
        verdict = self.neuve()
        self.assertEqual((verdict.refus, verdict.place, verdict.sha), ([], "origin/travail", self.tete))

    def test_un_push_sur_la_branche_depuis_la_passation_est_refuse(self):
        """Le 23 novembre : la session qui part avait poussé après avoir
        programmé."""
        commiter(self.partante, "après la passation", {"memory/active.md": "# Chantier actif\n\nAprès.\n"},
                 date=APRES)
        git(self.partante, "push", "-q", "origin", "travail")
        verdict = self.neuve()
        self.assertEqual(len(verdict.refus), 1, verdict.refus)
        self.assertIn("quelqu'un a poussé sur origin/travail depuis la passation", verdict.refus[0])
        self.assertIsNone(verdict.place)

    def test_la_memoire_ecrite_sur_une_autre_branche_depuis_la_passation_est_refusee(self):
        autre = self.clone("autre")
        git(autre, "checkout", "-q", "-b", "autre-session", "origin/main")
        commiter(autre, "une autre session", {"memory/journal/2026-11-24.md": "# Journal\n"}, date=APRES)
        git(autre, "push", "-q", "origin", "autre-session")
        verdict = self.neuve()
        self.assertEqual(len(verdict.refus), 1, verdict.refus)
        self.assertIn("origin/autre-session porte 1 commit(s) daté(s) d'après 2026-11-24T10:05:00Z", verdict.refus[0])
        self.assertIn("une autre session travaille sur le projet", verdict.refus[0])

    def test_un_robot_qui_ne_touche_pas_la_memoire_et_un_commit_d_avant_sont_ignores(self):
        robot = self.clone("robot")
        git(robot, "checkout", "-q", "-b", "dependabot/pip", "origin/main")
        commiter(robot, "Bump", {"requirements.txt": "x==2\n"}, date=APRES)
        git(robot, "push", "-q", "origin", "dependabot/pip")
        vieille = self.clone("vieille")
        git(vieille, "checkout", "-q", "-b", "vieille", "origin/main")
        commiter(vieille, "une session d'avant", {"memory/journal/2026-11-23.md": "# Journal\n"}, date=AVANT)
        git(vieille, "push", "-q", "origin", "vieille")
        self.assertEqual(self.neuve().refus, [])
        # Sans `--since`, l'heure est la date de la tête passée : le commit
        # d'avant, daté comme elle, ne compte pas davantage.
        self.assertEqual(self.neuve(depuis=None).refus, [])

    def test_la_pull_request_fusionnee_par_un_commit_de_fusion_est_acceptee(self):
        """La session repart de la branche par défaut, où la tête passée est
        entrée."""
        self.fusionner()
        verdict = self.neuve()
        self.assertEqual((verdict.refus, verdict.place), ([], "origin/main"))
        self.assertEqual(verdict.sha, git(self.dossier / "github", "rev-parse", "HEAD").strip())

    def test_fusionnee_par_un_commit_de_fusion_puis_sa_branche_supprimee_aussi(self):
        self.fusionner(supprimer=True)
        verdict = self.neuve()
        self.assertEqual((verdict.refus, verdict.place), ([], "origin/main"))

    def test_la_pull_request_fusionnee_par_squash_est_refusee(self):
        self.fusionner(squash=True)
        verdict = self.neuve()
        self.assertEqual(len(verdict.refus), 1, verdict.refus)
        self.assertIn("origin/main porte 1 commit(s)", verdict.refus[0])
        # Sa branche supprimée, la garde le dit aussi.
        shutil.rmtree(self.dossier / "neuve")
        git(self.dossier / "github", "push", "-q", "origin", "--delete", "travail")
        verdict = self.neuve()
        self.assertEqual(len(verdict.refus), 2, verdict.refus)
        self.assertIn("origin/travail n'existe plus, et", verdict.refus[0])
        self.assertIn("fusionnée par squash, ou la branche supprimée", verdict.refus[0])

    def test_une_tete_introuvable_est_refusee(self):
        verdict = self.neuve(tete="0123456789abcdef0123456789abcdef01234567")
        self.assertIn("est introuvable dans ce clone", verdict.refus[0])


class TestLaCommande(Depots):
    def lancer(self, racine: Path, *args: str) -> tuple[int, str, str]:
        sortie, erreur = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreur):
            code = cli.main(["--root", str(racine), "handoff", *args])
        return code, sortie.getvalue(), erreur.getvalue()

    def test_la_commande_ecrit_le_prompt_puis_juge_sa_garde(self):
        """`cli.cmd_handoff`, rangée parmi les commandes de l'agent."""
        self.assertIs(cli.analyseur()[0].parse_args(["handoff", "prompt"]).f, cli.cmd_handoff)
        self.assertIn("handoff", cli.GROUPES["pour l'agent"])
        code, sortie, _ = self.lancer(self.partante, "prompt", "--waiting", "rien de plus")
        self.assertEqual(code, 0)
        garde = next(l for l in sortie.splitlines() if l.startswith("python3 .socle/socle handoff check "))
        neuve = self.clone("neuve")
        code, sortie, erreur = self.lancer(neuve, *garde.split()[3:])
        self.assertEqual((code, erreur), (0, ""))
        self.assertEqual(sortie.strip(), f"passation acceptée : se placer sur origin/travail ({self.tete[:10]})")
        # Poussé depuis : refusée, en disant pourquoi.
        commiter(self.partante, "après", {"memory/active.md": "# Chantier actif\n\nAprès.\n"})
        git(self.partante, "push", "-q", "origin", "travail")
        git(neuve, "fetch", "-q", "origin")
        code, sortie, erreur = self.lancer(neuve, *garde.split()[3:])
        self.assertEqual((code, sortie), (1, ""))
        self.assertTrue(erreur.startswith("passation refusée — la tête de origin/travail est "), erreur)

    def test_ses_refus_d_usage(self):
        code, _, erreur = self.lancer(self.partante, "check", "--ref", "origin/travail")
        self.assertEqual(code, 2)
        self.assertIn("--ref et --head", erreur)
        code, _, erreur = self.lancer(self.partante, "check", "--ref", "origin/travail", "--head", self.tete,
                                      "--since", "hier")
        self.assertEqual(code, 2)
        self.assertIn("une heure ISO 8601", erreur)
        code, _, erreur = self.lancer(self.partante, "prompt", "--scheduled", "--chain", "2")
        self.assertEqual(code, 1)
        self.assertTrue(erreur.startswith("pas de passation : chaîne : 2 lots menés"), erreur)

    def test_le_prompt_ne_prend_plus_le_lien_de_la_session_qui_part(self):
        """B-0345 (D-0176) : la session neuve ne se sert pas du lien de la
        session qui part ; ni la commande, ni le skill ne le nomment."""
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            cli.analyseur()[0].parse_args(["handoff", "prompt", "--session", "https://claude.ai/code/session_x"])
        moteur = Path(__file__).resolve().parent.parent / "engine" / "socle"
        for rel in ("templates/skills/socle-handoff/SKILL.md", "templates/skills/socle-handoff/SKILL.en.md"):
            texte = (moteur / rel).read_text(encoding="utf-8")
            with self.subTest(gabarit=rel):
                self.assertNotIn("--session", texte)
                self.assertIn("handoff prompt --waiting", texte)
                self.assertIn("handoff prompt --scheduled --chain <n> --waiting", texte)

    def test_l_heure_en_utc(self):
        self.assertEqual(passation.heure("2026-11-24T10:05:00Z"), HEURE)
        self.assertEqual(passation.heure("2026-11-24T11:05:00+01:00"), HEURE)
        self.assertEqual(passation.heure("2026-11-24T10:05:00"), HEURE)
        with self.assertRaises(ValueError):
            passation.heure("hier")

    def test_le_prompt_dans_la_langue_de_la_memoire(self):
        with messages.dans("en"):
            texte = passation.prompt(self.projet(self.partante), maintenant=HEURE)
        self.assertIn("Handoff — partante, at 2026-11-24T10:05:00Z.", texte)
        self.assertIn("If it refuses, do nothing else but say so", texte)
        self.assertIn("The batch: L-0001 (T-0002), following the socle-batch skill.", texte)
        self.assertIn("What is waiting: nothing.", texte)


if __name__ == "__main__":
    unittest.main()
