"""L6 : une vérification réussie se mémorise. La vérification que l'agent
lance, la fin de tour et le hook avant push ne refont pas les étapes
rapides sur un arbre où elles ont déjà toutes passé ; mesuré sur la copie
d'un projet réel, une fin de tour et un push recompilaient le même arbre."""

import contextlib
import io
import shutil
import subprocess
import tempfile
import tomllib
import unittest
import unittest.mock
from pathlib import Path

from socle import config, installer as installeur, utils as outils, verification
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"


class TestEtapesRapides(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-etapes-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        (self.racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", "--no-verify"],
                       cwd=self.racine, check=True)
        self.compte = Path(tempfile.mkdtemp(prefix="socle-compte-")) / "n"
        self.addCleanup(shutil.rmtree, self.compte.parent, ignore_errors=True)
        self.code = 0

    def lancer(self, refaire=False) -> bool:
        projet = config.Projet.charger(self.racine)
        projet.adaptateur["capabilities"] = {
            "tests": {"command": f"echo . >> {self.compte}; exit {self.code}", "fast": True}}
        return verification.etapes_rapides(projet, Rapport(), refaire=refaire)

    def fois(self) -> int:
        return len(self.compte.read_text().split()) if self.compte.is_file() else 0

    def test_un_arbre_deja_verifie_ne_se_reverifie_pas(self):
        self.assertTrue(self.lancer())
        self.assertFalse(self.lancer())
        self.assertEqual(self.fois(), 1)
        self.assertTrue(self.lancer(refaire=True))
        self.assertEqual(self.fois(), 2)

    def test_un_arbre_change_se_reverifie(self):
        self.lancer()
        avant = outils.empreinte_arbre(self.racine)
        (self.racine / "calc.py").write_text("x = 2\n")
        self.assertNotEqual(outils.empreinte_arbre(self.racine), avant)
        self.assertTrue(self.lancer())
        (self.racine / "neuf.py").write_text("y = 1\n")
        self.assertTrue(self.lancer())
        self.assertEqual(self.fois(), 3)

    def test_un_commit_ou_la_memoire_seule_ne_relancent_pas_les_etapes(self):
        """B-0086, relevé sur chess : la fin de tour avait compilé et testé,
        puis le push recompilait le même contenu, commité, ou dont seule la
        mémoire avait changé."""
        (self.racine / "calc.py").write_text("x = 2\n")
        self.assertTrue(self.lancer())
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x = 2", "--no-verify"],
                       cwd=self.racine, check=True)
        self.assertFalse(self.lancer())
        actif = self.racine / "memory/active.md"
        actif.write_text(actif.read_text() + "\nUne ligne de plus.\n")
        self.assertFalse(self.lancer())
        (self.racine / "calc.py").write_text("x = 3\n")
        self.assertTrue(self.lancer())
        self.assertEqual(self.fois(), 2)

    def test_l_empreinte_du_contenu(self):
        avant = outils.empreinte_contenu(self.racine, ("memory/",))
        (self.racine / "memory/active.md").write_text("autre\n")
        self.assertEqual(outils.empreinte_contenu(self.racine, ("memory/",)), avant)
        self.assertNotEqual(outils.empreinte_contenu(self.racine), avant)
        (self.racine / "neuf.py").write_text("y = 1\n")
        self.assertNotEqual(outils.empreinte_contenu(self.racine, ("memory/",)), avant)

    def test_les_etapes_rapides_le_disent_a_leurs_commandes(self):
        # D-0019 : un test trop long pour une fin de tour se met de côté
        # quand la variable est posée ; toutes les étapes, en CI, la retirent.
        projet = config.Projet.charger(self.racine)
        projet.adaptateur["capabilities"] = {"tests": {
            "command": f"echo \"${{{verification.RAPIDE}:-absente}}\" >> {self.compte}", "fast": True}}
        verification.executer_etapes(projet, True, Rapport())
        with unittest.mock.patch.dict("os.environ", {verification.RAPIDE: "1"}):
            verification.executer_etapes(projet, False, Rapport())
        self.assertEqual(self.compte.read_text().split(), ["1", "absente"])

    def test_un_echec_ne_se_memorise_pas(self):
        self.code = 1
        self.lancer()
        self.assertTrue(self.lancer())
        self.assertEqual(self.fois(), 2)


class TestDureeDesEtapes(unittest.TestCase):
    """B-0258, T-0045 : `verify --fast` n'imprimait aucune durée, et rien ne
    signalait qu'elle avait passé de 143 s à près de douze minutes. Chaque
    étape lancée dit sa durée, puis leur total ; au-delà du seuil des
    garde-fous, un avertissement nomme la plus longue."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-durees-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        (self.racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", "--no-verify"],
                       cwd=self.racine, check=True)
        self.code = 0

    def projet(self, seuil=None) -> config.Projet:
        projet = config.Projet.charger(self.racine)
        projet.adaptateur["capabilities"] = {
            "lint": {"command": "sleep 0.3", "fast": True},
            "tests": {"command": f"exit {self.code}", "fast": True},
            "build": {"command": "true"}}
        if seuil is not None:
            projet.garde_fous["verify"] = {"fast_max_seconds": seuil}
        return projet

    def lancer(self, seuil=None, refaire=False) -> tuple[Rapport, str]:
        rapport, flux = Rapport(), io.StringIO()
        verification.etapes_rapides(self.projet(seuil), rapport, flux=flux, refaire=refaire)
        return rapport, flux.getvalue()

    def avertissements(self, rapport: Rapport) -> list[str]:
        return [c.message for c in rapport.constats if c.controle == verification.CONTROLE_DUREE]

    def test_chaque_etape_dit_sa_duree_au_bout_de_sa_ligne_puis_le_total(self):
        _, sortie = self.lancer()
        lignes = sortie.splitlines()
        self.assertRegex(lignes[0], r"^  … verify\.lint : sleep 0\.3 — 0,[3-9] s$")
        self.assertRegex(lignes[1], r"^  … verify\.tests : exit 0 — \d+,\d s$")
        self.assertRegex(lignes[2], r"^  … total des étapes lancées : 0,[3-9] s$")
        self.assertEqual(len(lignes), 3)  # l'étape qui n'est pas rapide ne tourne pas

    def test_la_verification_complete_et_la_ci_impriment_les_durees_sans_seuil(self):
        """Point 5 : la CI lance toutes les étapes, sur une autre machine."""
        rapport, flux = Rapport(), io.StringIO()
        durees = verification.executer_etapes(self.projet(seuil=0.1), False, rapport, flux)
        self.assertEqual([n for n, _ in durees], ["verify.lint", "verify.build", "verify.tests"])
        self.assertRegex(flux.getvalue().splitlines()[-1], r"^  … total des étapes lancées : \d+,\d s$")
        self.assertEqual(self.avertissements(rapport), [])
        self.assertFalse((self.racine / verification.DUREES).exists())

    def test_au_dela_du_seuil_un_avertissement_nomme_la_plus_longue(self):
        rapport, _ = self.lancer(seuil=0.1)
        self.assertTrue(rapport.reussi)
        (message,) = self.avertissements(rapport)
        self.assertRegex(message, r"^durée des étapes rapides au dernier passage complet : 0,[3-9] s, au-delà du seuil "
                                  r"de 0,1 s \(`\[verify\] fast_max_seconds` des garde-fous\) ; la plus longue : "
                                  r"`verify\.lint`, 0,[3-9] s")

    def test_sous_le_seuil_rien_n_avertit(self):
        rapport, _ = self.lancer()
        self.assertEqual(self.avertissements(rapport), [])
        self.assertIsNone(verification.alerte_duree(self.projet()))

    def test_les_etapes_deja_passees_redisent_l_avertissement_sur_leur_ligne(self):
        self.lancer(seuil=0.1)
        rapport, sortie = self.lancer(seuil=0.1)
        self.assertRegex(sortie, r"^  … étapes rapides déjà passées sur cet arbre exact : non relancées \(`--redo` "
                                 r"pour les relancer\) — !! durée des étapes rapides au dernier passage complet : "
                                 r"0,[3-9] s, au-delà du seuil de 0,1 s .*la plus longue : `verify\.lint`")
        self.assertEqual(rapport.constats, [])
        _, sortie = self.lancer(seuil=300)
        self.assertNotIn("!!", sortie)

    def test_l_etat_le_dit_tant_que_le_dernier_passage_complet_depasse_le_seuil(self):
        from socle import state as etat

        self.lancer(seuil=0.1)
        self.assertIn("!! durée des étapes rapides au dernier passage complet", etat.calculer(self.projet(0.1),
                                                                                              contenus=False))
        self.assertNotIn("durée des étapes rapides", etat.calculer(self.projet(), contenus=False))
        self.lancer(seuil=0.1)  # déjà passées : la trace reste
        self.assertIsNotNone(verification.alerte_duree(self.projet(0.1)))
        self.lancer(seuil=10, refaire=True)  # un passage complet sous ce seuil-là la remplace
        self.assertIsNone(verification.alerte_duree(self.projet(10)))

    def test_un_passage_ou_une_etape_echoue_ne_garde_pas_sa_duree(self):
        """ADR-0086 : son total ne mesure pas des étapes qui passent ; une
        erreur courte effacerait la dérive."""
        verification.garder_duree(self.racine, [("verify.tests", 400.0)])
        self.code = 1
        rapport, sortie = self.lancer(seuil=0.1)
        self.assertFalse(rapport.reussi)
        self.assertRegex(sortie, r"  … total des étapes lancées : \d+,\d s")
        self.assertEqual(self.avertissements(rapport), [])
        self.assertEqual(verification.derniere_duree(self.racine)["total"], 400.0)

    def test_une_trace_illisible_ne_dit_rien(self):
        fichier = self.racine / verification.DUREES
        fichier.parent.mkdir(parents=True, exist_ok=True)
        for texte in ("pas du json", "[1, 2]", '{"total": true, "duree": 1}', '{"total": 500}'):
            fichier.write_text(texte)
            self.assertIsNone(verification.derniere_duree(self.racine), texte)
            self.assertIsNone(verification.alerte_duree(self.projet(0.1)), texte)

    def test_secondes_au_dixieme_dans_la_langue_du_projet(self):
        from socle import messages

        self.assertEqual(verification.secondes(163.64), "163,6 s")
        self.assertEqual(verification.secondes(300), "300 s")
        with messages.dans("en"):
            self.assertEqual(verification.secondes(163.64), "163.6 s")


class TestDureeDiteParLesHooks(unittest.TestCase):
    """Revue du lot L-0012, passe 2 : le passage complet que lancent la fin
    de tour et le hook avant envoi gardait sa trace, mais son avertissement
    se perdait ; seuls l'état et un `verify --fast` relancé à la main le
    disaient ensuite. Le hook avant envoi le dit sur sa sortie d'erreur ; la
    fin de tour, qu'il ne bloque pas, le dit à l'humain."""

    AVERTISSEMENT = (r"socle — avertissement \(verify\.duree\) : durée des étapes rapides au dernier passage "
                     r"complet : 0,[3-9] s, au-delà du seuil de 0,1 s .*la plus longue : `verify\.lint`")

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-durees-hooks-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        (self.racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", "--no-verify"],
                       cwd=self.racine, check=True)
        self.n = 1

    def projet(self, seuil) -> config.Projet:
        projet = config.Projet.charger(self.racine)
        projet.adaptateur["capabilities"] = {"lint": {"command": "sleep 0.3", "fast": True}}
        projet.garde_fous["verify"] = {"fast_max_seconds": seuil}
        return projet

    def changer_le_code(self):
        """Un contenu neuf : les étapes rapides ne sont pas déjà passées
        dessus, et le hook les relance."""
        self.n += 1
        (self.racine / "calc.py").write_text(f"x = {self.n}\n")

    def avant_envoi(self, seuil) -> tuple[int, str]:
        from socle import context as contexte, hooks

        with unittest.mock.patch("sys.stdin", io.StringIO("")), \
                unittest.mock.patch.object(contexte, "executer", return_value=Rapport()), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as flux:
            code = hooks.git_pre_push(self.projet(seuil))
        return code, flux.getvalue()

    def fin_de_tour(self, seuil, dernier_message: str | None = None, relance: bool = False,
                    rapport: Rapport | None = None) -> dict:
        import json

        from socle import context as contexte, hooks

        entree = {"session_id": "d", "stop_hook_active": relance}
        if dernier_message is not None:
            transcript = self.racine / ".socle/trace/essai-transcript.jsonl"
            transcript.parent.mkdir(parents=True, exist_ok=True)
            transcript.write_text(json.dumps({"type": "assistant", "message": {"content": dernier_message}}) + "\n")
            entree["transcript_path"] = str(transcript)
        with unittest.mock.patch.object(contexte, "executer", return_value=rapport or Rapport()), \
                contextlib.redirect_stdout(io.StringIO()) as sortie, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(hooks.stop(self.projet(seuil), entree), 0)
        return json.loads(sortie.getvalue()) if sortie.getvalue().strip() else {}

    def test_le_hook_avant_envoi_dit_l_avertissement_et_laisse_passer(self):
        code, sortie = self.avant_envoi(300)
        self.assertEqual((code, sortie), (0, ""))
        self.changer_le_code()
        code, sortie = self.avant_envoi(0.1)
        self.assertEqual(code, 0, sortie)
        self.assertRegex(sortie, self.AVERTISSEMENT)
        self.assertEqual(len(sortie.splitlines()), 1, sortie)

    def test_la_fin_de_tour_le_joint_a_son_message_sans_bloquer_pour_lui(self):
        recap = "Fait.\n\nPour toi : rien.\nEnsuite : rien."
        # Sous le seuil, rien de plus : un récap complet ne fait rien imprimer.
        self.changer_le_code()
        self.assertEqual(self.fin_de_tour(300, recap), {})
        # Au-delà, un récap complet : le message à l'humain, et lui seul.
        self.changer_le_code()
        sortie = self.fin_de_tour(0.1, recap)
        self.assertEqual(list(sortie), ["systemMessage"])
        self.assertRegex(sortie["systemMessage"], "^" + self.AVERTISSEMENT)
        # Un transcript illisible : le message qu'imprimait déjà le hook, puis l'avertissement.
        self.changer_le_code()
        sortie = self.fin_de_tour(0.1)
        self.assertEqual(list(sortie), ["systemMessage"])
        self.assertRegex(sortie["systemMessage"], r"^récap de fin d'intervention non vérifiable : transcript "
                                                  r"illisible\n\n" + self.AVERTISSEMENT)

    def test_la_fin_de_tour_qui_bloque_deja_le_dit_aussi_a_l_agent(self):
        self.changer_le_code()
        sortie = self.fin_de_tour(0.1, "Fait.")
        self.assertEqual(sortie["decision"], "block")
        self.assertTrue(sortie["reason"].startswith("Tu as agi pendant ce tour, et ton dernier message n'a pas"))
        self.assertRegex(sortie["reason"], r"\n\n" + self.AVERTISSEMENT + "[^\n]*$")
        self.assertRegex(sortie["systemMessage"], "^" + self.AVERTISSEMENT)
        # La relance que le hook a provoquée ne bloque plus : le message
        # qu'il imprimait, puis l'avertissement.
        self.changer_le_code()
        sortie = self.fin_de_tour(0.1, "Fait.", relance=True)
        self.assertNotIn("decision", sortie)
        self.assertRegex(sortie["systemMessage"], r"^fin d'intervention sans .*, malgré un rappel\n\n"
                         + self.AVERTISSEMENT)

    def test_la_fin_de_tour_qui_echoue_pour_un_autre_controle_le_dit_aussi_a_l_humain(self):
        """Passe 3 de la revue de L-0012 : un autre contrôle en échec (du code
        changé sans la mémoire, le tour même où la fin de tour lance les
        étapes) bloquait avec l'avertissement dans la raison seule, que
        l'agent lit ; la relance sur le même arbre ne relance pas les étapes,
        et l'humain n'en recevait rien."""

        def echec() -> Rapport:
            rapport = Rapport()
            rapport.erreur("memoire.retard", "du code changé sans la mémoire")
            return rapport

        # Sous le seuil, le blocage d'avant : rien pour l'humain.
        self.changer_le_code()
        sortie = self.fin_de_tour(300, "Fait.", rapport=echec())
        self.assertEqual(list(sortie), ["decision", "reason"])
        self.assertNotIn("verify.duree", sortie["reason"])
        # Au-delà : l'agent le lit dans le rapport de sa raison, l'humain dans
        # le message, qui ne dit que lui.
        self.changer_le_code()
        sortie = self.fin_de_tour(0.1, "Fait.", rapport=echec())
        self.assertEqual(sortie["decision"], "block")
        self.assertIn("memoire.retard", sortie["reason"])
        self.assertIn("verify.duree", sortie["reason"])
        self.assertRegex(sortie["systemMessage"], "^" + self.AVERTISSEMENT)
        self.assertEqual(len(sortie["systemMessage"].splitlines()), 1, sortie["systemMessage"])
        # L'escalade, au bout des tentatives, porte déjà le rapport à
        # l'humain, l'avertissement compris.
        self.changer_le_code()
        sortie = self.fin_de_tour(0.1, "Fait.", rapport=echec())
        self.assertEqual(list(sortie), ["systemMessage"])
        self.assertIn("ARRÊT ET ESCALADE", sortie["systemMessage"])
        self.assertIn("verify.duree", sortie["systemMessage"])


class TestSeuilDesEtapesRapides(unittest.TestCase):
    """B-0258 : le seuil, `[verify] fast_max_seconds` des garde-fous ; le
    relever exige une demande validée, le baisser est libre."""

    def seuil(self, garde_fous: dict):
        return config.Projet(Path("."), garde_fous=garde_fous).seuil_rapide()

    def test_le_seuil_des_garde_fous_et_sa_valeur_par_defaut(self):
        self.assertEqual(config.SEUIL_RAPIDE, 300)
        self.assertEqual(self.seuil({}), 300)
        self.assertEqual(self.seuil({"verify": {"fast_max_seconds": 120}}), 120)
        self.assertEqual(self.seuil({"verify": {"fast_max_seconds": 2.5}}), 2.5)
        self.assertEqual(self.seuil({"verify": {"fast_max_seconds": "beaucoup"}}), 300)
        # Ce que le cliquet laisse écrire librement ne relâche jamais le seuil ;
        # `nan`, qu'il refuse sans demande, se lit le plus strict.
        self.assertEqual(self.seuil({"verify": {"fast_max_seconds": 0}}), 0)
        self.assertEqual(self.seuil({"verify": {"fast_max_seconds": float("nan")}}), 0)
        self.assertEqual(self.seuil({"verify": {"fast_max_seconds": True}}), 1)

    def test_le_gabarit_pose_le_seuil_par_defaut_dans_les_deux_langues(self):
        for nom in ("guardrails.toml", "guardrails.en.toml"):
            gabarit = tomllib.loads((MOTEUR / "socle/templates" / nom).read_text())
            self.assertEqual(gabarit["verify"]["fast_max_seconds"], config.SEUIL_RAPIDE, nom)

    def test_le_cliquet_connait_la_cle(self):
        from socle.checks_ratchet import assouplissements

        self.assertEqual(assouplissements({}, {"verify": {"fast_max_seconds": 300}}), [])
        self.assertEqual(assouplissements({}, {"verify": {"fast_max_seconds": 120}}), [])
        self.assertEqual(assouplissements({"verify": {"fast_max_seconds": 300}}, {}), [])
        self.assertEqual(assouplissements({}, {"verify": {"fast_max_seconds": 900}}),
                         [("verify.fast_max_seconds", "300 → 900")])
        self.assertEqual(assouplissements({"verify": {"fast_max_seconds": 120}}, {}),
                         [("verify.fast_max_seconds", "120 → 300")])

    def test_nan_ne_releve_pas_le_seuil_en_deux_temps(self):
        """Revue du lot L-0012, passe 2 : `nan` s'écrivait librement (lu
        comme zéro), puis, depuis une base qui le portait, le seuil se
        relevait à 900 ou se retirait sans demande : `vb > va` est toujours
        faux avec `nan`."""
        from socle.checks_ratchet import assouplissements

        nan, cle = float("nan"), "verify.fast_max_seconds"
        self.assertEqual(assouplissements({"verify": {"fast_max_seconds": 300}}, {"verify": {"fast_max_seconds": nan}}),
                         [(cle, "300 → nan")])
        self.assertEqual(assouplissements({}, {"verify": {"fast_max_seconds": nan}}), [(cle, "300 → nan")])
        base = {"verify": {"fast_max_seconds": nan}}
        self.assertEqual(assouplissements(base, {"verify": {"fast_max_seconds": 900}}), [(cle, "nan → 900")])
        self.assertEqual(assouplissements(base, {}), [(cle, "nan → 300")])
        self.assertEqual(assouplissements(base, {"verify": {"fast_max_seconds": nan}}), [])
        # `inf` et `-inf` s'ordonnent, et se jugent comme avant.
        self.assertEqual(assouplissements({}, {"verify": {"fast_max_seconds": float("inf")}}), [(cle, "300 → inf")])
        self.assertEqual(assouplissements({}, {"verify": {"fast_max_seconds": float("-inf")}}), [])


class TestAutotestUneFois(unittest.TestCase):
    """L6 : `socle ci` lançait l'auto-test deux fois, dans la suite de tests
    de ce dépôt puis lui-même."""

    def test_la_suite_sait_que_l_autotest_suit(self):
        import argparse
        import os
        from unittest import mock

        from socle import selftest as autotest, cli, context as contexte

        vus = []
        with mock.patch.object(cli, "_projet", return_value=mock.Mock()), \
                mock.patch.object(cli, "_base", return_value=None), \
                mock.patch.object(verification, "executer_etapes",
                                  lambda *a, **k: vus.append(os.environ.get(autotest.ENSUITE))), \
                mock.patch.object(contexte, "executer", return_value=Rapport()), \
                mock.patch.object(contexte, "Contexte"), \
                mock.patch.object(autotest, "executer", return_value=Rapport()), \
                contextlib.redirect_stdout(io.StringIO()):
            cli.cmd_ci(argparse.Namespace(base=None, no_selftest=False))
            cli.cmd_ci(argparse.Namespace(base=None, no_selftest=True))
        self.assertEqual(vus, ["1", None])
        self.assertIsNone(os.environ.get(autotest.ENSUITE))

    def test_verify_rapide_passe_par_la_memoire_et_refaire_la_contourne(self):
        import argparse
        from unittest import mock

        from socle import cli, context as contexte

        appels = []
        with mock.patch.object(cli, "_projet", return_value=mock.Mock()), \
                mock.patch.object(cli, "_base", return_value=None), \
                mock.patch.object(verification, "etapes_rapides",
                                  lambda projet, rapport, flux=None, refaire=False: appels.append(("rapides", refaire))), \
                mock.patch.object(verification, "executer_etapes", lambda *a, **k: appels.append(("toutes", None))), \
                mock.patch.object(contexte, "executer", return_value=Rapport()), \
                mock.patch.object(contexte, "Contexte"), \
                contextlib.redirect_stdout(io.StringIO()):
            cli.cmd_verify(argparse.Namespace(base=None, fast=True, refaire=False))
            cli.cmd_verify(argparse.Namespace(base=None, fast=True, refaire=True))
            cli.cmd_verify(argparse.Namespace(base=None, fast=False, refaire=False))
        self.assertEqual(appels, [("rapides", False), ("rapides", True), ("toutes", None)])


class TestSansAucunTest(unittest.TestCase):
    """B-0026 : un projet qui commence n'a pas encore de test, et unittest
    le dit par un échec ; l'adaptateur le reconnaît, et `verify` avertit au
    lieu d'échouer."""

    def test_un_projet_sans_test_avertit(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-sans-test-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True)
        (racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(racine, "python", "@essai", source=MOTEUR)
        projet = config.Projet.charger(racine)
        for dossier in (None, "tests"):  # sans dossier, puis un dossier vide
            if dossier:
                (racine / dossier).mkdir()
                (racine / dossier / "__init__.py").write_text("")
            rapport = Rapport()
            verification.executer_etapes(projet, True, rapport)
            self.assertEqual(rapport.erreurs("verify.tests"), [], dossier)
            self.assertIn("aucun test trouvé", rapport.texte())
        # Un vrai échec reste un échec.
        (racine / "tests/test_x.py").write_text("import unittest\n\nclass T(unittest.TestCase):\n"
                                                "    def test_x(self):\n        self.fail('non')\n")
        rapport = Rapport()
        verification.executer_etapes(projet, True, rapport)
        self.assertTrue(rapport.erreurs("verify.tests"))


class TestSansCode(unittest.TestCase):
    """B-0089 : un projet neuf s'installe avant son premier fichier, et la
    commande de test de presque tout adaptateur y échoue (pas de manifeste,
    pas d'outil, aucun test). Sans aucun fichier source à lui, `verify`
    avertit sans lancer ses étapes ; le premier fichier les relance."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-sans-code-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        (self.racine / "README.md").write_text("# neuf\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python-pytest", "@essai", source=MOTEUR)
        self.projet = config.Projet.charger(self.racine)
        self.tests = self.projet.adaptateur["capabilities"]["tests"]

    def verifier(self) -> Rapport:
        rapport = Rapport()
        verification.executer_etapes(self.projet, True, rapport)
        return rapport

    def test_sans_code_les_etapes_avertissent_sans_tourner(self):
        # Une commande qui échoue toujours, comme cargo sans manifeste.
        self.tests["command"] = "python3 -c 'raise SystemExit(3)'"
        tiers = self.racine / ".claude/skills/bmad-essai/scripts/outil.py"
        tiers.parent.mkdir(parents=True)
        tiers.write_text("x = 1\n")
        with unittest.mock.patch.object(self.projet, "chemins_tiers", return_value=["**/skills/bmad-*/**"]):
            # Le moteur du socle et les fichiers tiers ne sont pas du code du projet.
            self.assertTrue(verification.sans_code(self.projet))
            rapport = self.verifier()
            self.assertEqual(rapport.erreurs(), [])
            self.assertIn("pas encore de code (aucun fichier `**/*.py`)", rapport.texte())
            # Le premier fichier relance les étapes.
            (self.racine / "app.py").write_text("x = 1\n")
            self.assertFalse(verification.sans_code(self.projet))
            self.assertTrue(self.verifier().erreurs("verify.tests"))

    def test_pytest_sans_aucun_test_avertit(self):
        (self.racine / "app.py").write_text("x = 1\n")
        self.tests["command"] = "python3 -c \"print('no tests ran in 0.01s'); raise SystemExit(5)\""
        rapport = self.verifier()
        self.assertEqual(rapport.erreurs("verify.tests"), [])
        self.assertIn("aucun test trouvé", rapport.texte())

    def test_un_outil_absent_se_dit_avec_les_commandes_de_la_ci(self):
        """B-0090 : le pilote n'avait que « No module named pytest », sans
        savoir que la CI l'installe, ni comment."""
        (self.racine / "app.py").write_text("x = 1\n")
        for commande in ("python3 -m module_qui_n_existe_pas", "commande-qui-n-existe-pas"):
            self.tests["command"] = commande
            texte = "\n".join(c.message for c in self.verifier().erreurs("verify.tests"))
            self.assertIn("l'outil manque à cet environnement ; la CI l'installe ainsi : "
                          "`python3 -m pip install pytest mutmut`", texte, commande)
        # Un échec ordinaire ne parle pas d'outil.
        self.tests["command"] = "python3 -c 'raise SystemExit(1)'"
        erreurs = self.verifier().erreurs("verify.tests")
        self.assertTrue(erreurs)
        self.assertNotIn("l'outil manque", erreurs[0].message)

    def test_commandes_ci_lit_les_etapes_de_chaque_adaptateur(self):
        # `npm ci` attend `package.json`, comme dans la CI (B-0179).
        (self.racine / "package.json").write_text("{}\n")
        attendu = {
            "python-pytest": ["python3 -m pip install pytest mutmut"],
            "javascript": ["npm ci"],
            "rust": ["rustup show active-toolchain || rustup toolchain install stable --profile minimal "
                     "--component rustfmt,clippy ; rustc --version && cargo --version"],
            "python": [],
        }
        for nom, commandes in attendu.items():
            texte = (MOTEUR / "socle/adapters" / f"{nom}.toml").read_text()
            self.projet.adaptateur["ci_setup"] = tomllib.loads(texte).get("ci_setup", "")
            self.assertEqual(verification.commandes_ci(self.projet), commandes, nom)



class TestEssentielDesEchecs(unittest.TestCase):
    """B-0290 : la fin de tour en échec recopiait le rapport entier, sortie
    des tests comprise, environ 10 000 jetons que chaque étape suivante de
    la conversation relisait. Elle ne donne plus que le nom de chaque
    contrôle en échec, la première ligne utile de chaque test en échec et la
    commande qui montre tout."""

    UNITTEST = ("======================================================================\n"
                "FAIL: test_a (tests.test_x.T.test_a)\n"
                "----------------------------------------------------------------------\n"
                "Traceback (most recent call last):\n"
                '  File "tests/test_x.py", line 7, in test_a\n'
                "    self.fail('raté')\n"
                "AssertionError: raté\n\n"
                "======================================================================\n"
                "ERROR: test_b (tests.test_x.T.test_b)\n"
                "----------------------------------------------------------------------\n"
                "Traceback (most recent call last):\n"
                "ValueError: invalide\n\n"
                "----------------------------------------------------------------------\n"
                "Ran 2 tests in 0.001s\n\n"
                "FAILED (failures=1, errors=1)\n")

    def test_lignes_d_echec_d_une_sortie_unittest(self):
        self.assertEqual(verification.lignes_d_echec(self.UNITTEST),
                         ["FAIL: test_a (tests.test_x.T.test_a)", "ERROR: test_b (tests.test_x.T.test_b)",
                          "FAILED (failures=1, errors=1)"])

    def test_lignes_d_echec_d_autres_outils(self):
        self.assertEqual(verification.lignes_d_echec(
            "___ test_c ___\n    assert 1 == 2\nE   assert 1 == 2\nFAILED tests/test_y.py::test_c - assert 1 == 2\n"
            "==== 1 failed in 0.02s ====\n"), ["FAILED tests/test_y.py::test_c - assert 1 == 2"])
        self.assertEqual(verification.lignes_d_echec("=== RUN TestD\n--- FAIL: TestD (0.00s)\n    d_test.go:9: x\nFAIL\n"),
                         ["--- FAIL: TestD (0.00s)", "FAIL"])
        self.assertEqual(verification.lignes_d_echec("running 1 test\ntest tests::e ... FAILED\n"),
                         ["test tests::e ... FAILED"])
        # Aucune ligne d'échec reconnue : la dernière ligne utile, le bilan.
        self.assertEqual(verification.lignes_d_echec("x ✗\n\n2 passing, 1 pending\n=====\n\n"),
                         ["2 passing, 1 pending"])

    def test_lignes_d_echec_bornees(self):
        sortie = "".join(f"FAIL: test_{i}\n" for i in range(verification.MAXIMUM_LIGNES_D_ECHEC + 3))
        lignes = verification.lignes_d_echec(sortie)
        self.assertEqual(len(lignes), verification.MAXIMUM_LIGNES_D_ECHEC + 1)
        self.assertEqual(lignes[-1], "… et 3 autre(s) ligne(s) d'échec")

    def test_premiere_ligne_utile_saute_le_vide_et_le_decor(self):
        from socle.report import ligne_utile, premiere_ligne_utile

        self.assertFalse(ligne_utile("  ====----**  "))
        self.assertFalse(ligne_utile(""))
        self.assertTrue(ligne_utile("Ran 2 tests"))
        self.assertEqual(premiere_ligne_utile("\n=====\n  le message  \nla suite\n"), "le message")

    def test_le_rapport_essentiel_ne_garde_que_l_essentiel(self):
        from socle import hooks
        from socle.report import Constat

        rapport = Rapport()
        rapport.execute("memoire.format")
        rapport.erreur("memoire.preuves", "fait sans preuve\nle détail qui suit", "memory/canonical.md", 3)
        rapport.erreur("verify.tests", "`python3 -m unittest` a rendu 1\n        " + self.UNITTEST,
                       essentiel=["`python3 -m unittest` a rendu 1", *verification.lignes_d_echec(self.UNITTEST)])
        rapport.avertir("verify.duree", "trop long")
        rapport.indisponible("verify.format", "capacité absente : une longue explication")
        self.assertEqual(Constat("x", "m\nsuite", "a.md", 2).lignes_essentielles(), ["a.md:2 — m"])
        texte = hooks.essentiel_des_echecs(rapport)
        for attendu in ("memoire.preuves", "| memory/canonical.md:3 — fait sans preuve", "verify.tests",
                        "| `python3 -m unittest` a rendu 1", "| FAIL: test_a (tests.test_x.T.test_a)",
                        "| ERROR: test_b (tests.test_x.T.test_b)", "! trop long",
                        "ECHEC — 2 contrôle(s) : memoire.preuves, verify.tests",
                        "… et 1 contrôle(s) indisponible(s), que le détail explique : verify.format",
                        "`python3 .socle/socle check --stage agent`, `python3 .socle/socle verify --fast`"):
            self.assertIn(attendu, texte)
        for absent in ("le détail qui suit", "Traceback", "=====", "AssertionError", "Ran 2 tests", "memoire.format",
                       "une longue explication"):
            self.assertNotIn(absent, texte)
        # Un seul genre d'échec, une seule commande.
        seul = Rapport()
        seul.erreur("memoire.preuves", "fait sans preuve")
        self.assertTrue(hooks.essentiel_des_echecs(seul).endswith(": `python3 .socle/socle check --stage agent`"))
        # Le rapport entier, lui, garde tout.
        self.assertIn("Traceback", rapport.texte())
