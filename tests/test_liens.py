import os
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from socle import config, links as liens

DEPOT = "https://github.com/essai/calc"


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestAdresses(unittest.TestCase):
    def test_adresse_du_depot_selon_la_forme_du_distant(self):
        self.assertEqual(liens.depuis_distant("https://github.com/theodubus/memory"), "https://github.com/theodubus/memory")
        self.assertEqual(liens.depuis_distant("https://jeton@github.com/o/r.git"), "https://github.com/o/r")
        self.assertEqual(liens.depuis_distant("git@github.com:o/r.git"), "https://github.com/o/r")
        self.assertEqual(liens.depuis_distant("ssh://git@github.com:22/o/r.git"), "https://github.com/o/r")

    def test_un_relais_local_ne_dit_pas_ou_l_humain_lit(self):
        self.assertIsNone(liens.depuis_distant("http://proxy@127.0.0.1:4242/git/o/r"))
        self.assertIsNone(liens.depuis_distant("/tmp/origine"))
        self.assertIsNone(liens.depuis_distant(""))

    def test_ancre_d_un_titre_comme_github(self):
        self.assertEqual(liens.ancre("B-0014 — Exiger un test, et pour du code qu'on découvre"),
                         "b-0014--exiger-un-test-et-pour-du-code-quon-découvre")
        self.assertEqual(liens.ancre("J-2026-10-10-P — Backlog clos : B-0007, B-0015"),
                         "j-2026-10-10-p--backlog-clos--b-0007-b-0015")
        self.assertEqual(liens.ancre("`socle` « x » — a.b"), "socle--x---ab")

    def test_une_seule_ancre_pour_les_liens_et_leur_controle(self):
        # B-0017 : deux copies divergeaient. L'une gardait les soulignés du
        # gras, que GitHub ne rend pas ; l'autre perdait l'accent décomposé.
        from socle import checks_memory as controles_memoire

        self.assertEqual(liens.ancre("B-0017 — __Deux__ **fonctions**"), "b-0017--deux-fonctions")
        self.assertEqual(liens.ancre("Cafe\u0301 noir"), "cafe\u0301-noir")
        self.assertFalse(hasattr(controles_memoire, "slug"), "la copie du contrôle est retirée")
        # Les ancres d'un fichier, comme le contrôle des liens les voit : un
        # titre répété prend le suffixe de GitHub, un titre en code n'en est pas un.
        self.assertEqual(controles_memoire.ancres("## B-0017 — __Deux__\n\n## B-0017 — __Deux__\n"
                                                  "```\n## pas un titre\n```\n"),
                         {"b-0017--deux", "b-0017--deux-1"})

    def test_ce_qui_ressemble_a_un_chemin(self):
        self.assertEqual(liens.ressemble_a_un_chemin("moteur/socle/liens.py"), "moteur/socle/liens.py")
        self.assertEqual(liens.ressemble_a_un_chemin("tests/test_humain.py:65"), "tests/test_humain.py")
        self.assertEqual(liens.ressemble_a_un_chemin("memoire/"), "memoire/")
        self.assertEqual(liens.ressemble_a_un_chemin("AGENTS.md"), "AGENTS.md")
        for pas_un_chemin in ("origin/main", "outils.git", "socle url D-0005", "outil:CLAUDE.md",
                              "**/*.md", "ADR-0007@ac16270e", "/home/user/x.md", "python3.11"):
            self.assertIsNone(liens.ressemble_a_un_chemin(pas_un_chemin), pas_un_chemin)


class TestLiensDuDepot(unittest.TestCase):
    """Un dépôt et son origine, fabriqués : ce qui est poussé a un lien,
    ce qui ne l'est pas n'en a pas."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-liens-"))
        source = self.dossier / "source"
        (source / "docs").mkdir(parents=True)
        git(source, "init", "-q", "-b", "main")
        (source / "docs/a.md").write_text("# A\n")
        (source / ".socle").mkdir()
        (source / ".socle/policy.toml").write_text(f'[human]\nrepo_url = "{DEPOT}"\n')
        git(source, "add", "-A")
        git(source, "commit", "-qm", "un")
        self.clone = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(source), str(self.clone))
        git(self.clone, "switch", "-q", "-c", "claude/essai")
        (self.clone / "docs/b.md").write_text("# B\n")
        git(self.clone, "add", "-A")
        git(self.clone, "commit", "-qm", "deux")
        self.projet = config.Projet.charger(self.clone)
        self.main = git(self.clone, "rev-parse", "origin/main").strip()

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)

    def test_permalien_au_commit_pousse(self):
        url, avertissement = liens.lien(self.projet, "docs/a.md")
        self.assertEqual(url, f"{DEPOT}/blob/{self.main}/docs/a.md")
        self.assertEqual(avertissement, "")

    def test_permalien_a_la_branche_distante_du_meme_nom(self):
        """B-0134 : une branche repartie de `origin/main` le suit ; ses
        fichiers se poussent sous son nom, et le permalien les y trouve."""
        git(self.clone, "checkout", "-q", "-B", "travail", "origin/main")
        self.assertEqual(git(self.clone, "rev-parse", "--abbrev-ref", "@{upstream}").strip(), "origin/main")
        (self.clone / "docs/c.md").write_text("# C\n")
        git(self.clone, "add", "-A")
        git(self.clone, "commit", "-qm", "trois")
        git(self.clone, "push", "-q", "origin", "travail")
        pousse = git(self.clone, "rev-parse", "origin/travail").strip()
        url, avertissement = liens.lien(config.Projet.charger(self.clone), "docs/c.md")
        self.assertEqual(url, f"{DEPOT}/blob/{pousse}/docs/c.md")
        self.assertEqual(avertissement, "")
        self.assertEqual(liens.commit_pousse(self.clone), pousse)

    def test_une_branche_distante_perimee_du_meme_nom_cede_a_la_plus_recente(self):
        """Repartie de `origin/main` après une fusion, la branche garde sa
        branche distante du même nom, à l'ancien travail, jusqu'au push
        suivant : le permalien vise `origin/main`, plus récent."""
        git(self.clone, "push", "-q", "origin", "claude/essai")
        source = self.dossier / "source"
        (source / "docs/d.md").write_text("# D\n")
        git(source, "add", "-A")
        git(source, "commit", "-qm", "fusion")
        git(self.clone, "fetch", "-q", "origin")
        git(self.clone, "checkout", "-q", "-B", "claude/essai", "origin/main")
        main = git(self.clone, "rev-parse", "origin/main").strip()
        url, avertissement = liens.lien(config.Projet.charger(self.clone), "docs/d.md")
        self.assertEqual(url, f"{DEPOT}/blob/{main}/docs/d.md")
        self.assertEqual(liens.commit_pousse(self.clone), main)

    def test_la_branche_du_meme_nom_se_cherche_sur_son_distant(self):
        """Une branche qui suit un autre distant qu'`origin` se cherche sur
        lui ; une qui suit une branche locale (`.`), sur `origin`."""
        source = self.dossier / "source"
        git(self.clone, "remote", "add", "amont", str(source))
        git(self.clone, "fetch", "-q", "amont")
        git(self.clone, "checkout", "-q", "-B", "ailleurs", "amont/main")
        self.assertEqual(git(self.clone, "config", "--get", "branch.ailleurs.remote").strip(), "amont")
        (self.clone / "docs/e.md").write_text("# E\n")
        git(self.clone, "add", "-A")
        git(self.clone, "commit", "-qm", "quatre")
        git(self.clone, "push", "-q", "amont", "ailleurs")
        self.assertEqual(liens.commit_pousse(self.clone), git(self.clone, "rev-parse", "amont/ailleurs").strip())
        git(self.clone, "push", "-q", "origin", "ailleurs:locale")
        git(self.clone, "fetch", "-q", "origin")
        git(self.clone, "checkout", "-q", "-b", "locale", "--track", "ailleurs")
        self.assertEqual(git(self.clone, "config", "--get", "branch.locale.remote").strip(), ".")
        # La branche locale suivie avance sans elle : le commit poussé est
        # celui de `origin/locale`.
        git(self.clone, "checkout", "-q", "ailleurs")
        git(self.clone, "commit", "-q", "--allow-empty", "-m", "cinq")
        git(self.clone, "checkout", "-q", "locale")
        self.assertEqual(liens.commit_pousse(self.clone), git(self.clone, "rev-parse", "origin/locale").strip())

    def test_la_ci_d_une_pull_request_lie_une_demande_posee_sur_sa_branche(self):
        """T-0085 : la CI d'une pull request tourne sur une HEAD détachée,
        le commit de fusion que GitHub prépare ; une demande posée sur la
        branche se lie à la tête de la pull request, pas à `origin/main`."""
        dossier = config.FORMAT_ACTUEL.demandes
        demande = f"{dossier}/D-0001-une-question.md"
        (self.clone / dossier).mkdir(parents=True)
        (self.clone / demande).write_text("# D-0001 — Une question\n")
        git(self.clone, "add", "-A")
        git(self.clone, "commit", "-qm", "la demande")
        git(self.clone, "push", "-q", "origin", "claude/essai")
        tete = git(self.clone, "rev-parse", "HEAD").strip()
        # La branche par défaut a avancé : la tête de la pull request n'en
        # descend plus.
        source = self.dossier / "source"
        (source / "docs/d.md").write_text("# D\n")
        git(source, "add", "-A")
        git(source, "commit", "-qm", "sur main")
        git(self.clone, "fetch", "-q", "origin")
        git(self.clone, "checkout", "-q", "--detach", "origin/main")
        git(self.clone, "merge", "-q", "--no-ff", "-m", "Merge claude/essai into main", tete)
        ci = {"GITHUB_HEAD_REF": "claude/essai", "GITHUB_WORKSPACE": str(self.clone)}
        with unittest.mock.patch.dict(os.environ, ci):
            url, avertissement = liens.lien(config.Projet.charger(self.clone), demande)
        self.assertEqual(url, f"{DEPOT}/blob/{tete}/{demande}")
        self.assertEqual(avertissement, "")
        # Un autre dépôt que celui que la CI a extrait (un dépôt de test, le
        # dépôt compagnon) garde la règle de sa branche : la revue de la CI
        # de la PR 73, où un dépôt sans commit faisait planter le lien.
        ailleurs = {"GITHUB_HEAD_REF": "claude/essai", "GITHUB_WORKSPACE": str(self.dossier / "source")}
        with unittest.mock.patch.dict(os.environ, ailleurs):
            self.assertEqual(liens.commit_pousse(self.clone), git(self.clone, "rev-parse", "origin/main").strip())
            vide = self.dossier / "vide"
            vide.mkdir()
            git(vide, "init", "-q")
            self.assertIsNone(liens.commit_pousse(vide))
        with unittest.mock.patch.dict(os.environ, {**ci, "GITHUB_WORKSPACE": str(vide)}):
            self.assertIsNone(liens.commit_pousse(vide))

    def test_pas_de_lien_vers_ce_qui_n_est_pas_pousse(self):
        url, avertissement = liens.lien(self.projet, "docs/b.md")
        self.assertIsNone(url)
        self.assertIn("pousser d'abord", avertissement)

    def test_une_version_locale_non_poussee_est_signalee(self):
        (self.clone / "docs/a.md").write_text("# A modifié\n")
        url, avertissement = liens.lien(self.projet, "docs/a.md")
        self.assertEqual(url, f"{DEPOT}/blob/{self.main}/docs/a.md")
        self.assertIn("pas poussée", avertissement)

    def test_l_ancien_numero_d_une_entree_renumerotee_mene_a_elle(self):
        """T-0051 : `socle url B-0005`, ancien numéro d'un lot renuméroté
        (ADR-0083), répondait « aucune entrée » ; il donne le lien de
        l'entrée qui le porte, et le dit."""
        import contextlib
        import io

        from socle import cli

        lot = "memory/backlog/L-0001-un-lot.md"
        (self.clone / "memory/backlog").mkdir(parents=True)
        (self.clone / lot).write_text("<!-- socle: couche=backlog zone=publique -->\n# L-0001 — Un lot\n\n"
                                      "> statut : ouvert · ancien : B-0005\n\nPour l'essai.\n")
        git(self.clone, "add", "-A")
        git(self.clone, "commit", "-qm", "le lot")
        git(self.clone, "push", "-q", "origin", "claude/essai")
        pousse = git(self.clone, "rev-parse", "origin/claude/essai").strip()
        url, avertissement = liens.lien(self.projet, "B-0005")
        self.assertEqual(url, f"{DEPOT}/blob/{pousse}/{lot}")
        self.assertEqual(avertissement, "B-0005 est l'ancien numéro de L-0001")
        self.assertEqual(liens.lien(self.projet, "L-0001"), (url, ""))
        self.assertIsNone(liens.lien(self.projet, "B-0006")[0])
        with contextlib.redirect_stdout(io.StringIO()) as sortie, \
                contextlib.redirect_stderr(io.StringIO()) as erreurs:
            code = cli.main(["--root", str(self.clone), "url", "B-0005"])
        self.assertEqual((code, sortie.getvalue()), (0, f"[B-0005]({url})\n"))
        self.assertIn("ancien numéro de L-0001", erreurs.getvalue())

    def test_liens_morts_d_un_message(self):
        message = (
            "Voir [la doc](docs/a.md), `docs/absent.md` et "
            f"{DEPOT}/blob/{self.main}/docs/b.md.\n"
            "```\ncat docs/exemple-dans-un-bloc.md `docs/rien.md`\n```\n"
        )
        morts, sans_lien = liens.problemes(self.projet, message)
        self.assertEqual(len(morts), 3, morts)
        self.assertIn("lien relatif « docs/a.md »", morts[0])
        self.assertIn("`docs/absent.md`", morts[1])
        self.assertIn("docs/b.md n'existe pas", morts[2])
        self.assertEqual(sans_lien, [])

    def test_un_chemin_present_sur_le_disque_seulement_d_un_message(self):
        """B-0166 : un chemin donné à l'humain vaut s'il est suivi par git, ou
        livré par le prochain `git add` ; un dossier qu'une règle locale de
        git ignore (`.git/info/exclude`) n'est que dans le conteneur."""
        (self.clone / "docs/local.md").write_text("# Local\n")
        self.assertEqual(liens.problemes(self.projet, "Voir `docs/local.md`."), ([], []))
        (self.clone / "docs/essais").mkdir()
        (self.clone / "docs/essais/x.md").write_text("x\n")
        (self.clone / ".git/info").mkdir(exist_ok=True)
        (self.clone / ".git/info/exclude").write_text("docs/essais/\n")
        morts, _ = liens.problemes(self.projet, "Voir `docs/essais/`.")
        self.assertEqual(len(morts), 1, morts)
        self.assertIn("ignoré par git", morts[0])

    def test_un_depot_imbrique_ou_un_fichier_supprime_d_un_message(self):
        """Revue de B-0166, constats 4 à 6 : un dépôt git imbriqué non suivi
        n'est pas livré par `git add`, et le message le dit ; un fichier suivi
        mais supprimé du disque est refusé."""
        imbrique = self.clone / "docs/copie"
        imbrique.mkdir()
        git(imbrique, "init", "-q")
        (imbrique / "a.md").write_text("a\n")
        for cite in ("docs/copie/a.md", "docs/copie/"):
            morts, _ = liens.problemes(self.projet, f"Voir `{cite}`.")
            self.assertEqual(len(morts), 1, morts)
            self.assertIn("dépôt git imbriqué `docs/copie/`", morts[0])
        (self.clone / "docs/a.md").unlink()
        morts, _ = liens.problemes(self.projet, "Voir `docs/a.md`.")
        self.assertEqual(len(morts), 1, morts)

    def test_liens_vivants_d_un_message(self):
        git(self.clone, "push", "-q", "origin", "claude/essai")
        message = (
            f"Voir {DEPOT}/blob/{self.main}/docs/a.md, {DEPOT}/blob/claude/essai/docs/b.md, "
            f"{DEPOT}/tree/main/docs, {DEPOT}/pull/3, `docs/a.md` et `origin/main`."
        )
        self.assertEqual(liens.problemes(self.projet, message), ([], []))


    def test_une_pull_request_se_cite_par_son_lien(self):
        """B-0110 : l'agent du pilote donnait « la pull request 2 » à fusionner,
        sans lien."""
        for message in ("Fusionne la pull request 2.", "La PR #2 reste à fusionner.", "Voir la PR 2 et la PR 14."):
            with self.subTest(message=message):
                morts, _ = liens.problemes(self.projet, message)
                self.assertTrue(any("pull request 2 citée sans son lien" in m for m in morts), morts)
        message = f"La PR #3 est ouverte : {DEPOT}/pull/3."
        self.assertEqual(liens.problemes(self.projet, message), ([], []))
        self.assertTrue(liens.problemes(self.projet, f"La PR #3 : {DEPOT}/pull/31.")[0])

    def test_un_chemin_barre_d_un_message_ne_se_juge_pas(self):
        """B-0087 : un chemin barré dit ce qui n'est plus."""
        from socle import memory as memoire

        self.assertEqual(memoire.sans_barre("a ~~`docs/x.md`~~ b <s>`docs/y.md`</s> c <DEL>z</DEL>"), "a   b   c  ")
        message = "L'ancien guide, ~~`docs/absent.md`~~, puis <s>[l'autre](docs/parti.md)</s>."
        self.assertEqual(liens.problemes(self.projet, message), ([], []))


class TestDemandeLue(unittest.TestCase):
    """B-0022 : une réponse ne se relaie qu'à une demande que l'humain a pu
    lire, poussée telle qu'elle est."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-relais-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        origine = self.dossier / "origine.git"
        git(self.dossier, "init", "-q", "--bare", str(origine))
        self.racine = self.dossier / "projet"
        (self.racine / ".socle").mkdir(parents=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / ".socle/policy.toml").write_text(f'[human]\nrepo_url = "{DEPOT}"\n')
        self.demande = self.racine / "memory/requests/D-0001-essai.md"
        self.demande.parent.mkdir(parents=True)
        self.demande.write_text("<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Essai ?\n")
        git(self.racine, "remote", "add", "origin", str(origine))
        self.projet = config.Projet.charger(self.racine)

    def illisible(self):
        from socle import cli, requests as demandes

        d = next(x for x in demandes.toutes(self.racine) if x.id == "D-0001")
        return cli.demande_illisible(self.projet, d)

    def pousser(self):
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "demande")
        git(self.racine, "push", "-q", "-u", "origin", "main")

    def test_une_demande_jamais_poussee_n_a_pas_pu_etre_lue(self):
        self.assertIn("pousser", self.illisible())

    def test_une_demande_poussee_telle_quelle_a_pu_etre_lue(self):
        self.pousser()
        self.assertIsNone(self.illisible())

    def test_cmd_answer_refuse_de_relayer_une_reponse_a_une_demande_non_lue(self):
        import argparse
        import contextlib
        import io

        from socle import cli

        (self.racine / "citation.txt").write_text("oui")
        args = argparse.Namespace(root=str(self.racine), request="D-0001", answer="valider", text="", by="Théo",
                                  relayed=True, quote=None, quote_file=str(self.racine / "citation.txt"))
        erreurs = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(erreurs):
            self.assertEqual(cli.cmd_answer(args), 2)
        self.assertIn("n'a pas pu être lue par l'humain", erreurs.getvalue())
        self.assertEqual(list(self.demande.parent.glob("*.answer.toml")), [])

    def test_une_demande_changee_depuis_le_push_n_est_pas_celle_qu_il_a_lue(self):
        self.pousser()
        self.demande.write_text(self.demande.read_text() + "\nUn ajout après coup.\n")
        self.assertIn("diffère", self.illisible())


class TestBranchesASupprimerCitees(unittest.TestCase):
    """B-0311 (D-0178) : le récap donnait à Théo une branche à supprimer que
    GitHub n'avait plus, reprise d'une entrée du journal sans la vérifier ;
    la fin de tour la vérifie sur l'origine."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-branches-citees-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        source = self.dossier / "source"
        source.mkdir()
        git(source, "init", "-q", "-b", "main")
        (source / "f").write_text("un")
        git(source, "add", "f")
        git(source, "commit", "-qm", "un")
        git(source, "branch", "morceau")
        self.clone = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(source), str(self.clone))
        self.projet = config.Projet(racine=self.clone)

    @staticmethod
    def message(pour_toi):
        return f"Lot clos.\n\nPour toi : {pour_toi}\nEnsuite : rien."

    def test_les_branches_que_pour_toi_donne_a_supprimer(self):
        m = ("Lot clos ; la branche `ancienne` est fusionnée, à supprimer.\n\n"
             "Pour toi :\n- supprimer la branche distante `origin/fantome`, déjà contenue dans `main` ;\n"
             "- supprimer la branche locale `locale-x` ;\n"
             "- supprimer le fichier `notes.txt` ;\n"
             "- delete the branch `effacee` and `a b` ;\n"
             "```text\nsupprimer la branche `dans-un-bloc`\n```\n"
             "Ensuite : supprimer la branche `apres`.")
        self.assertEqual(liens.branches_a_supprimer_citees(self.projet, m), ["fantome", "main", "effacee"])
        self.assertEqual(liens.branches_a_supprimer_citees(self.projet, "Supprimer la branche `x`.\n\nEnsuite : rien."),
                         [])

    def test_celles_que_l_origine_n_a_plus(self):
        m = self.message("supprimer les branches distantes `morceau` et `fantome`.")
        self.assertEqual(liens.branches_absentes(self.projet, m), (["fantome"], []))
        # Sans réponse de l'origine, aucune n'est dite absente : elles sont
        # dites non vérifiées.
        git(self.clone, "remote", "set-url", "origin", str(self.dossier / "absente"))
        self.assertEqual(liens.branches_absentes(self.projet, m), ([], ["morceau", "fantome"]))

    def test_sans_branche_a_supprimer_l_origine_n_est_pas_interrogee(self):
        with unittest.mock.patch("socle.human.branches_de_l_origine") as origine:
            self.assertEqual(liens.branches_absentes(self.projet, self.message("rien.")), ([], []))
        self.assertEqual(origine.call_count, 0)

    def test_la_fin_de_tour_le_refuse_une_fois(self):
        import contextlib
        import io
        import json

        from socle import hooks

        transcript = self.dossier / "t.jsonl"

        def fin(texte, rappel=False):
            transcript.write_text(json.dumps({"type": "assistant", "message": {"content": texte}}))
            sortie = io.StringIO()
            with contextlib.redirect_stdout(sortie):
                hooks.exiger_recap(self.projet, {"session_id": "b", "transcript_path": str(transcript),
                                                 "stop_hook_active": rappel})
            return sortie.getvalue()

        absente = self.message("supprimer la branche distante `fantome`.")
        refus = json.loads(fin(absente))
        self.assertEqual(refus["decision"], "block")
        self.assertIn("à supprimer `fantome`, que l'origine n'a plus", refus["reason"])
        # Au second essai, la fin de tour conclut, et l'humain le lit.
        self.assertIn("1 branche(s) à supprimer que l'origine n'a plus", json.loads(fin(absente, True))["systemMessage"])
        self.assertEqual(fin(self.message("supprimer la branche distante `morceau`.")), "")
        git(self.clone, "remote", "set-url", "origin", str(self.dossier / "absente"))
        self.assertIn("non vérifiée(s), l'origine ne répondant pas : `fantome`",
                      json.loads(fin(absente))["systemMessage"])


if __name__ == "__main__":
    unittest.main()
