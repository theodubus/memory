"""T-0081 (B-0259, D-0174), puis T-0182 (B-0346, D-0190) : la passation
programmée, côté moteur. `socle handoff write` écrit la passation dans la
mémoire (`memory/handoff.md`) : son estampille, l'heure `écrite` et la
branche, et sa chaîne ; refusée, pour une session programmée, aux bornes
d'une chaîne sans l'humain. `socle handoff check`, sans argument, la trouve
sur les branches distantes, la plus récente, reprise ou non, et juge sa
garde ; avec `--ref` et `--head`, il juge la garde seule, comme avant. Sur de
vrais dépôts git dont l'origine est nue, comme sur GitHub."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import types
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from socle import checks_memory as controles_memoire, cli, config, handoff as passation, memory as memoire, messages
from socle import state as etat
from socle.report import Rapport
from tests.test_structure import entree, memoire_de

# L'heure de la passation, et celle d'un commit qui la suit ou la précède.
HEURE = datetime(2026, 11, 24, 10, 5, tzinfo=timezone.utc)
APRES = HEURE + timedelta(minutes=10)
AVANT = HEURE - timedelta(minutes=10)
# Le commit de la passation suit de peu son heure `écrite`.
PASSEE = HEURE + timedelta(seconds=30)


def git(cwd: Path, *args: str, date: datetime | None = None, commite: datetime | None = None) -> str:
    """`date` : celle de l'auteur et du commit ; `commite`, celle du commit
    seul, comme un rebase la donne."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    if date:
        env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"] = date.strftime("%Y-%m-%dT%H:%M:%S+0000")
    if commite:
        env["GIT_COMMITTER_DATE"] = commite.strftime("%Y-%m-%dT%H:%M:%S+0000")
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
# La passation qu'écrit `socle handoff write`, à HEURE, sur `travail`.
PASSATION = ("<!-- socle: couche=passation zone=publique -->\n# Passation\n\n"
             "> écrite : 2026-11-24T10:05:00Z · branche : travail · chaîne : 0\n\n"
             "Ce qui attend : la CI du commit de tête.\n")


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

    def passer(self, attente: str | None = "la CI du commit de tête", pousser: bool = True) -> memoire.Passation:
        """La session qui part écrit sa passation à HEURE, la commite en
        dernier et la pousse : `self.tete` devient le commit de la passation."""
        p = passation.ecrire(self.projet(self.partante), attente=attente, maintenant=HEURE)
        self.tete = commiter(self.partante, "la passation", {}, date=PASSEE)
        if pousser:
            git(self.partante, "push", "-q", "origin", "travail")
        return p

    def trouver(self, racine: Path | None = None) -> passation.Trouvee:
        """`socle handoff check` sans argument, après `git fetch` : dans la
        session neuve, clonée la première fois, ou dans `racine`."""
        if racine is None:
            racine = self.dossier / "neuve"
            if not racine.is_dir():
                racine = self.clone("neuve")
        git(racine, "fetch", "-q", "--prune", "origin")
        return passation.trouver(self.projet(racine))

    def reprendre(self, branche: str = "travail", date: datetime = APRES) -> str:
        """Une session neuve reprend la passation : son premier commit la
        retire, poussé aussitôt sur `branche`, partie de `origin/travail`."""
        reprise = self.clone(f"reprise-{branche}")
        git(reprise, "checkout", "-q", "-B", branche, "origin/travail")
        git(reprise, "rm", "-q", "memory/handoff.md")
        git(reprise, "commit", "-q", "-m", "reprise : la passation retirée", date=date)
        git(reprise, "push", "-q", "origin", f"HEAD:refs/heads/{branche}")
        return git(reprise, "rev-parse", "HEAD").strip()


class TestEcrire(Depots):
    def test_write_ecrit_la_passation_son_estampille_et_ce_qui_attend(self):
        p = passation.ecrire(self.projet(self.partante), attente="la CI du commit de tête.", maintenant=HEURE)
        self.assertEqual((self.partante / "memory/handoff.md").read_text(encoding="utf-8"), PASSATION)
        self.assertEqual((p.ecrite, p.branche, p.chaine, p.heure), (HEURE, "travail", 0, "2026-11-24T10:05:00Z"))
        self.assertEqual(p.attente, "Ce qui attend : la CI du commit de tête.")
        # Sans rien qui attende, « rien » ; réécrite, une heure nouvelle :
        # le fichier change toujours.
        p = passation.ecrire(self.projet(self.partante), maintenant=HEURE)
        self.assertEqual(p.heure, "2026-11-24T10:05:01Z")
        self.assertIn("Ce qui attend : rien.", (self.partante / "memory/handoff.md").read_text(encoding="utf-8"))

    def test_sa_branche_est_celle_que_suit_la_branche_courante(self):
        git(self.partante, "checkout", "-q", "-b", "locale", "--track", "origin/travail")
        self.assertEqual(passation.branche_de_travail(self.partante), "travail")
        # Partie de la branche par défaut, qu'elle suit, elle ne s'y pousse
        # pas : son nom.
        git(self.partante, "checkout", "-q", "-b", "seule", "origin/main")
        self.assertEqual(git(self.partante, "rev-parse", "--abbrev-ref", "@{upstream}").strip(), "origin/main")
        self.assertEqual(passation.branche_de_travail(self.partante), "seule")
        git(self.partante, "checkout", "-q", "--detach")
        with self.assertRaises(passation.PassationRefusee) as refus:
            passation.ecrire(self.projet(self.partante))
        self.assertIn("la tête est détachée, sur aucune branche", str(refus.exception))

    def test_les_bornes_d_une_session_programmee(self):
        projet = self.projet(self.partante)
        p = passation.ecrire(projet, chaine=1, programmee=True, maintenant=HEURE)
        self.assertEqual(p.chaine, 1)
        self.assertIn("chaîne : 1\n", (self.partante / "memory/handoff.md").read_text(encoding="utf-8"))
        # Deux lots menés sans message de l'humain : rien ne se programme.
        with self.assertRaises(passation.PassationRefusee) as refus:
            passation.ecrire(projet, chaine=2, programmee=True)
        self.assertIn("sa borne est 2 : ne rien programmer ; écrire la passation sans `--scheduled`",
                      str(refus.exception))
        # La passation que l'humain fait reprendre porte la chaîne 0.
        with self.assertRaises(passation.PassationRefusee) as refus:
            passation.ecrire(projet, chaine=1)
        self.assertIn("porte la chaîne 0, que sa demande remet à zéro", str(refus.exception))
        with self.assertRaises(passation.PassationRefusee) as refus:
            passation.ecrire(projet, chaine=-1, programmee=True)
        self.assertIn("`--chain` compte des lots : 0 ou plus", str(refus.exception))
        # Un prochain lot sans tâche prête : rien ne se programme.
        for chemin in BACKLOG:
            (self.partante / chemin).unlink()
        commiter(self.partante, "un lot qui attend une demande", SANS_TACHE_PRETE, date=AVANT)
        self.assertEqual(passation.lot_de_l_etat(self.partante), ("L-0002", ["T-0003"], False))
        with self.assertRaises(passation.PassationRefusee) as refus:
            passation.ecrire(projet, programmee=True)
        self.assertIn("le prochain lot n'a aucune tâche prête", str(refus.exception))
        self.assertEqual(passation.ecrire(projet).chaine, 0)

    def test_le_lot_de_l_etat(self):
        self.assertEqual(passation.lot_de_l_etat(self.partante), ("L-0001", ["T-0002"], True))

    def test_la_passation_dans_la_langue_de_la_memoire(self):
        ecrire(self.partante, ".socle/policy.toml", '[memory]\nlanguage = "en"\n')
        passation.ecrire(self.projet(self.partante), maintenant=HEURE)
        texte = (self.partante / "memory/handoff.md").read_text(encoding="utf-8")
        self.assertEqual(texte, "<!-- socle: layer=handoff zone=public -->\n# Handoff\n\n"
                                "> written : 2026-11-24T10:05:00Z · branch : travail · chain : 0\n\n"
                                "What is waiting: nothing.\n")
        p = memoire.lire_passation(texte)[0]
        self.assertEqual((p.ecrite, p.branche, p.chaine), (HEURE, "travail", 0))
        self.assertEqual(memoire.analyser("memory/handoff.md", texte).couche, "passation")


class TestLaVerificationApresLePush(Depots):
    """La session qui part lance `socle handoff check` après son push, et
    doit y retrouver sa passation, en attente : c'est ce qui remplace le
    refus d'une tête non poussée."""

    def test_poussee_elle_la_retrouve_en_attente(self):
        self.passer()
        trouvee = self.trouver(self.partante)
        self.assertEqual(trouvee.passation.heure, "2026-11-24T10:05:00Z")
        self.assertEqual((trouvee.verdict.refus, trouvee.verdict.place), ([], "origin/travail"))

    def test_non_commitee_elle_est_refusee(self):
        passation.ecrire(self.projet(self.partante), maintenant=HEURE)
        trouvee = self.trouver(self.partante)
        self.assertIsNone(trouvee.passation)
        self.assertEqual(len(trouvee.verdict.refus), 1, trouvee.verdict.refus)
        self.assertIn("des changements ne sont pas commités (memory/handoff.md) : les commiter, la passation en "
                      "dernier", trouvee.verdict.refus[0])
        # Commitée, un fichier suivi changé sans commit ne passe pas non plus.
        self.passer()
        ecrire(self.partante, "app.py", "print('changé')\n")
        refus = self.trouver(self.partante).verdict.refus
        self.assertIn("des changements ne sont pas commités (app.py)", refus[0])

    def test_non_poussee_elle_est_refusee(self):
        self.passer(pousser=False)
        trouvee = self.trouver(self.partante)
        self.assertIsNone(trouvee.passation)
        self.assertEqual(trouvee.verdict.refus, [
            "la passation de ce clone, écrite à 2026-11-24T10:05:00Z, n'est pas poussée : aucune branche de origin "
            "ne la porte ; pousser, puis relancer `socle handoff check`"])

    def test_un_commit_apres_elle_non_pousse_est_refuse(self):
        self.passer()
        sha = commiter(self.partante, "après la passation", {"app.py": "print('plus loin')\n"}, date=APRES)
        refus = self.trouver(self.partante).verdict.refus
        self.assertEqual(len(refus), 1, refus)
        self.assertIn(f"la tête locale {sha[:10]} n'est pas poussée : 1 commit(s) après la passation de ce clone",
                      refus[0])


class TestTrouver(Depots):
    """`socle handoff check` sans argument, dans la session neuve, après
    `git fetch` : la passation la plus récente que l'origine connaît."""

    def test_sans_passation_aucune_n_attend(self):
        trouvee = self.trouver()
        self.assertIsNone(trouvee.passation)
        self.assertEqual(trouvee.verdict.refus, [])
        self.assertIsNone(passation.ligne_etat(self.projet(self.dossier / "neuve")))

    def test_poussee_elle_attend_et_sa_garde_l_accepte(self):
        self.passer()
        trouvee = self.trouver()
        p = trouvee.passation
        self.assertEqual((p.heure, p.branche, p.chaine, p.attente),
                         ("2026-11-24T10:05:00Z", "travail", 0, "Ce qui attend : la CI du commit de tête."))
        self.assertEqual((trouvee.verdict.refus, trouvee.verdict.place, trouvee.verdict.sha),
                         ([], "origin/travail", self.tete))
        connue = passation.connues(self.projet(self.dossier / "neuve"))[p.estampille]
        self.assertEqual((connue.tetes, connue.retraits), (["origin/travail"], []))

    def test_la_plus_recente_seule_compte(self):
        self.passer()
        autre = self.clone("autre")
        git(autre, "checkout", "-q", "-b", "autre", "origin/main")
        passation.ecrire(self.projet(autre), maintenant=HEURE + timedelta(hours=1))
        sha = commiter(autre, "une passation plus récente", {}, date=HEURE + timedelta(hours=1, seconds=30))
        git(autre, "push", "-q", "-u", "origin", "autre")
        trouvee = self.trouver()
        self.assertEqual((trouvee.passation.branche, trouvee.passation.heure), ("autre", "2026-11-24T11:05:00Z"))
        self.assertEqual((trouvee.verdict.refus, trouvee.verdict.place, trouvee.verdict.sha),
                         ([], "origin/autre", sha))

    def test_un_push_sur_la_branche_depuis_la_passation_est_refuse(self):
        self.passer()
        commiter(self.partante, "après la passation", {"memory/active.md": "# Chantier actif\n\nAprès.\n"},
                 date=APRES)
        git(self.partante, "push", "-q", "origin", "travail")
        refus = self.trouver().verdict.refus
        self.assertEqual(len(refus), 1, refus)
        self.assertIn("quelqu'un a poussé sur origin/travail depuis la passation", refus[0])

    def test_la_memoire_ecrite_sur_une_autre_branche_depuis_l_heure_ecrite_est_refusee(self):
        self.passer()
        autre = self.clone("autre")
        git(autre, "checkout", "-q", "-b", "autre-session", "origin/main")
        commiter(autre, "une autre session", {"memory/journal/2026-11-24.md": "# Journal\n"}, date=APRES)
        git(autre, "push", "-q", "origin", "autre-session")
        refus = self.trouver().verdict.refus
        self.assertEqual(len(refus), 1, refus)
        self.assertIn("origin/autre-session porte 1 commit(s) daté(s) d'après 2026-11-24T10:05:00Z", refus[0])

    def test_deja_reprise_sur_une_autre_branche_elle_est_refusee(self):
        self.passer()
        sha = self.reprendre("reprise")
        trouvee = self.trouver()
        self.assertEqual(trouvee.verdict.refus, [
            f"la passation écrite à 2026-11-24T10:05:00Z sur origin/travail est déjà reprise : origin/reprise porte "
            f"son retrait ({sha[:10]}, 2026-11-24T10:15:00Z), qui n'est pas encore dans origin/main : une autre "
            f"session y travaille"])
        self.assertIsNone(trouvee.verdict.place)
        self.assertIsNone(passation.ligne_etat(self.projet(self.dossier / "neuve")))

    def test_deja_reprise_sur_sa_propre_branche_elle_est_refusee(self):
        """La session qui reprend pousse son retrait sur la branche même de
        la passation, dont la tête ne la porte plus."""
        self.passer()
        self.reprendre("travail")
        refus = self.trouver().verdict.refus
        self.assertEqual(len(refus), 1, refus)
        self.assertIn("est déjà reprise : origin/travail porte son retrait", refus[0])

    def test_reprise_puis_fusionnee_aucune_n_attend(self):
        self.passer()
        self.fusionner()
        self.reprendre("reprise")
        github = self.dossier / "github"
        git(github, "fetch", "-q", "origin")
        git(github, "merge", "-q", "--no-ff", "-m", "Merge pull request #2", "origin/reprise", date=APRES)
        git(github, "push", "-q", "origin", "main")
        trouvee = self.trouver()
        self.assertEqual((trouvee.passation, trouvee.verdict.refus), (None, []))

    def test_fusionnee_par_un_commit_de_fusion_sa_branche_supprimee_elle_repart_de_main(self):
        self.passer()
        self.fusionner(supprimer=True)
        trouvee = self.trouver()
        self.assertEqual((trouvee.verdict.refus, trouvee.verdict.place), ([], "origin/main"))
        self.assertEqual(trouvee.verdict.sha, git(self.dossier / "github", "rev-parse", "HEAD").strip())

    def test_fusionnee_par_squash_sa_branche_supprimee_elle_repart_de_main(self):
        """Refusée tant que la garde cherchait la tête nommée : le commit de
        squash qui porte la passation devient la tête, même quand le `git
        fetch` de la session neuve élague."""
        self.passer()
        neuve = self.clone("neuve")
        git(neuve, "config", "fetch.prune", "true")
        self.fusionner(squash=True, supprimer=True)
        trouvee = self.trouver(neuve)
        squash = git(self.dossier / "github", "rev-parse", "HEAD").strip()
        self.assertEqual((trouvee.verdict.refus, trouvee.verdict.place, trouvee.verdict.sha),
                         ([], "origin/main", squash))

    def test_fusionnee_par_rebase_sa_branche_supprimee_elle_repart_de_main(self):
        self.passer()
        github = self.clone("github")
        git(github, "checkout", "-q", "-b", "rejoue", "origin/travail")
        git(github, "rebase", "-q", "--force-rebase", "main", commite=APRES)
        git(github, "push", "-q", "origin", "rejoue:main", ":travail")
        trouvee = self.trouver()
        self.assertEqual((trouvee.verdict.refus, trouvee.verdict.place), ([], "origin/main"))
        self.assertNotEqual(trouvee.verdict.sha, self.tete)

    def test_squash_apres_la_memoire_d_une_autre_session_est_refuse(self):
        """La mémoire d'une autre session, fusionnée avant le squash : un
        ancêtre de la tête, écrit après l'heure `écrite`."""
        self.passer()
        autre = self.clone("autre")
        git(autre, "checkout", "-q", "-b", "autre-session", "origin/main")
        sha = commiter(autre, "une autre session", {"memory/journal/2026-11-24.md": "# Journal\n"}, date=APRES)
        git(autre, "push", "-q", "origin", "autre-session")
        github = self.clone("github")
        git(github, "merge", "-q", "--no-ff", "-m", "Merge pull request #2", "origin/autre-session", date=APRES)
        git(github, "merge", "-q", "--squash", "origin/travail")
        git(github, "commit", "-q", "-m", "Le lot (#1)", date=APRES + timedelta(minutes=1))
        git(github, "push", "-q", "origin", "main", ":travail", ":autre-session")
        refus = self.trouver().verdict.refus
        self.assertEqual(len(refus), 1, refus)
        self.assertIn("porte parmi ses ancêtres 1 commit(s) écrit(s) après 2026-11-24T10:05:00Z qui touche(nt) "
                      f"memory/ (le dernier : {sha[:10]} une autre session) : une autre session a travaillé sur le "
                      "projet depuis la passation", refus[0])

    def test_la_ligne_de_l_etat(self):
        self.passer()
        self.trouver()
        projet = self.projet(self.dossier / "neuve")
        ligne = ("passation : en attente sur origin/travail, écrite à 2026-11-24T10:05:00Z — une demande de reprendre "
                 "(« reprends ») la reprend")
        self.assertEqual(passation.ligne_etat(projet), ligne)
        self.assertIn(ligne, etat.calculer(projet, contenus=False))


class TestLaCouche(unittest.TestCase):
    """La couche `passation` du format : un seul fichier, public, son en-tête
    et son estampille."""

    def erreurs(self, texte: str, chemin: str = "memory/handoff.md") -> list[str]:
        mem = memoire_de((chemin, texte))
        ctx = types.SimpleNamespace(projet=types.SimpleNamespace(chemins=config.FORMAT_ACTUEL), memoire=mem,
                                    fichiers={"memory/canonical.md", "memory/active.md", chemin})
        r = Rapport()
        controles_memoire.format_memoire(ctx, r)
        return [c.message for c in r.erreurs("memoire.format")]

    def test_un_seul_fichier_public(self):
        self.assertEqual(memoire.couche_attendue("memory/handoff.md"), "passation")
        self.assertEqual(memoire.couche_attendue("memory/private/handoff.md"), "inconnue")
        self.assertEqual(memoire.couche_attendue("memory/handoff-2.md"), "inconnue")
        self.assertEqual(config.FORMAT_ACTUEL.passation, "memory/handoff.md")
        self.assertIn("passation", memoire.COUCHES)

    def test_la_passation_ecrite_passe(self):
        self.assertEqual(self.erreurs(PASSATION), [])
        p, fautes, ligne = memoire.lire_passation(PASSATION)
        self.assertEqual((p.heure, p.branche, p.chaine, fautes, ligne), ("2026-11-24T10:05:00Z", "travail", 0, [], 4))
        self.assertEqual(memoire.texte_passation(p, "fr"), PASSATION)

    def test_son_en_tete(self):
        sans = PASSATION.split("\n", 1)[1]
        self.assertIn("en-tête `<!-- socle: couche=… zone=… -->` absent", self.erreurs(sans))
        prive = PASSATION.replace("zone=publique", "zone=privee")
        self.assertIn("zone déclarée « privee » dans un emplacement « publique »", self.erreurs(prive))

    def test_ses_champs_illisibles_sont_refuses(self):
        texte = PASSATION.replace("> écrite : 2026-11-24T10:05:00Z · branche : travail · chaîne : 0",
                                  "> écrite : hier · chaîne : deux")
        self.assertEqual(self.erreurs(texte), [
            "la passation n'a pas d'heure `écrite` lisible : une heure ISO 8601 en UTC (2026-11-25T03:10:00Z)",
            "la passation ne nomme pas sa `branche` : un nom de branche, sans espace",
            "la passation n'a pas de `chaîne` lisible : un entier, 0 ou plus"])
        self.assertIsNone(memoire.lire_passation(texte)[0])

    def test_aucun_budget_ne_lui_est_exige(self):
        """Elle ne s'injecte pas au démarrage : `memoire.budgets` ne lui
        demande pas de budget, quand il le demande à tout autre fichier."""
        canonique = "<!-- socle: couche=canonique zone=publique -->\n# Canonique\n"
        mem = memoire_de(("memory/handoff.md", PASSATION), ("memory/canonical.md", canonique))
        projet = types.SimpleNamespace(chemins=config.FORMAT_ACTUEL, gf=lambda *_, defaut=None: {},
                                       budget_octets=lambda _: None)
        ctx = types.SimpleNamespace(projet=projet, memoire=mem, fichiers={"memory/handoff.md", "memory/canonical.md"},
                                    lire=lambda _: "")
        r = Rapport()
        controles_memoire.budgets(ctx, r)
        self.assertEqual([(c.chemin, c.message) for c in r.erreurs("memoire.budgets")],
                         [("memory/canonical.md", "aucun budget ne couvre ce fichier (`[budgets]` des garde-fous)")])

    def test_elle_ne_definit_aucun_identifiant(self):
        texte = PASSATION + "\n## F-0001 — Un fait\n\n> statut : supposé\n"
        self.assertIn("`F-0001` défini dans la passation, que la session neuve retire : un identifiant stable vit "
                      "dans une couche durable", self.erreurs(texte))


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

    def test_la_commande_ecrit_la_passation_puis_la_trouve_et_juge_sa_garde(self):
        """`cli.cmd_handoff`, rangée parmi les commandes de l'agent."""
        self.assertIs(cli.analyseur()[0].parse_args(["handoff", "write"]).f, cli.cmd_handoff)
        self.assertIn("handoff", cli.GROUPES["pour l'agent"])
        code, sortie, _ = self.lancer(self.partante, "write", "--waiting", "rien de plus")
        self.assertEqual(code, 0)
        p = memoire.lire_passation((self.partante / "memory/handoff.md").read_text(encoding="utf-8"))[0]
        self.assertEqual(sortie.splitlines(), [
            f"passation écrite : memory/handoff.md — écrite à {p.heure}, branche travail, chaîne 0",
            "Ensuite : la commiter en dernier, pousser, puis `python3 .socle/socle handoff check` doit la trouver en "
            "attente ; plus rien ne se pousse après"])
        tete = commiter(self.partante, "la passation", {})
        git(self.partante, "push", "-q", "origin", "travail")
        neuve = self.clone("neuve")
        code, sortie, erreur = self.lancer(neuve, "check")
        self.assertEqual((code, erreur), (0, ""))
        self.assertEqual(sortie.splitlines(), [
            f"passation : écrite à {p.heure} sur origin/travail, chaîne 0",
            f"passation acceptée : se placer sur origin/travail ({tete[:10]})",
            "Ce qui attend : rien de plus.",
            "Premier commit : retirer memory/handoff.md, puis le pousser aussitôt. Chaîne : 1 si la session est "
            "réveillée par la tâche programmée, 0 si l'humain a demandé la reprise."])
        # Poussé depuis : refusée, en disant pourquoi.
        commiter(self.partante, "après", {"memory/active.md": "# Chantier actif\n\nAprès.\n"})
        git(self.partante, "push", "-q", "origin", "travail")
        git(neuve, "fetch", "-q", "origin")
        code, sortie, erreur = self.lancer(neuve, "check")
        self.assertEqual((code, sortie), (1, f"passation : écrite à {p.heure} sur origin/travail, chaîne 0\n"))
        self.assertTrue(erreur.startswith("passation refusée — la tête de origin/travail est "), erreur)
        # La garde seule, avec ses arguments, comme la reprise après une
        # limite d'usage la donne.
        code, sortie, _ = self.lancer(neuve, "check", "--ref", "origin/travail", "--head", tete, "--since", p.heure)
        self.assertEqual((code, sortie), (1, ""))

    def test_sans_passation_la_commande_le_dit(self):
        code, sortie, erreur = self.lancer(self.clone("neuve"), "check")
        self.assertEqual((code, erreur), (0, ""))
        self.assertEqual(sortie, "aucune passation n'attend : faire ce que fait une session neuve, et le dire dans le "
                                 "premier message\n")

    def test_ses_refus_d_usage(self):
        code, _, erreur = self.lancer(self.partante, "check", "--ref", "origin/travail")
        self.assertEqual(code, 2)
        self.assertIn("--ref et --head vont ensemble, --since avec eux ; sans argument, la commande trouve la "
                      "passation", erreur)
        code, _, erreur = self.lancer(self.partante, "check", "--since", "2026-11-24T10:05:00Z")
        self.assertEqual(code, 2)
        self.assertIn("--ref et --head vont ensemble", erreur)
        code, _, erreur = self.lancer(self.partante, "check", "--ref", "origin/travail", "--head", self.tete,
                                      "--since", "hier")
        self.assertEqual(code, 2)
        self.assertIn("une heure ISO 8601", erreur)
        code, _, erreur = self.lancer(self.partante, "check", "--waiting", "x")
        self.assertEqual(code, 2)
        self.assertIn("--chain, --waiting et --scheduled vont avec `write`", erreur)
        code, _, erreur = self.lancer(self.partante, "write", "--head", self.tete)
        self.assertEqual(code, 2)
        self.assertIn("--ref, --head et --since vont avec `check`", erreur)
        code, _, erreur = self.lancer(self.partante, "write", "--scheduled", "--chain", "2")
        self.assertEqual(code, 1)
        self.assertTrue(erreur.startswith("pas de passation : chaîne : 2 lots menés"), erreur)
        self.assertFalse((self.partante / "memory/handoff.md").exists())

    def test_write_remplace_prompt_sans_le_lien_de_la_session_qui_part(self):
        """B-0345 (D-0176), puis D-0190 : `handoff prompt` n'existe plus, et
        la session neuve ne se sert pas du lien de la session qui part ; ni
        la commande, ni le skill ne le nomment."""
        for args in (["handoff", "prompt"], ["handoff", "write", "--session", "https://claude.ai/code/session_x"]):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                cli.analyseur()[0].parse_args(args)
        moteur = Path(__file__).resolve().parent.parent / "engine" / "socle"
        for rel in ("templates/skills/socle-handoff/SKILL.md", "templates/skills/socle-handoff/SKILL.en.md"):
            with self.subTest(gabarit=rel):
                self.assertNotIn("--session", (moteur / rel).read_text(encoding="utf-8"))

    def test_l_heure_en_utc(self):
        self.assertEqual(passation.heure("2026-11-24T10:05:00Z"), HEURE)
        self.assertEqual(passation.heure("2026-11-24T11:05:00+01:00"), HEURE)
        self.assertEqual(passation.heure("2026-11-24T10:05:00"), HEURE)
        with self.assertRaises(ValueError):
            passation.heure("hier")
        self.assertEqual(memoire.heure_utc("2026-11-24T10:05:00Z"), HEURE)

    def test_les_messages_dans_la_langue_de_la_memoire(self):
        self.passer()
        neuve = self.clone("neuve")
        ecrire(neuve, ".socle/policy.toml", '[memory]\nlanguage = "en"\n')
        code, sortie, _ = self.lancer(neuve, "check")
        with messages.dans("en"):
            ligne = passation.ligne_etat(self.projet(neuve))
        self.assertEqual(code, 0)
        self.assertIn("handoff: written at 2026-11-24T10:05:00Z on origin/travail, chain 0", sortie)
        self.assertIn(f"handoff accepted: move to origin/travail ({self.tete[:10]})", sortie)
        self.assertIn("First commit: remove memory/handoff.md, then push it at once.", sortie)
        self.assertEqual(ligne, "handoff: waiting on origin/travail, written at 2026-11-24T10:05:00Z — a request to "
                                "resume (\"resume\") resumes it")


if __name__ == "__main__":
    unittest.main()
