"""Les skills (ADR-0034) : ceux que pose le socle, ceux qu'écrit l'agent, et
les deux contrôles qui les jugent."""

import io
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from socle import checks_skills as controles, config, context as contexte, hooks, installer as installeur
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"

SAIN = """---
name: livrer
description: Livrer une version du projet, ses tests et son étiquette. À utiliser quand une version est prête à partir.
---

# Livrer

```sh
python3 -m unittest discover -s tests -q
```

Ne jamais lancer `git push --force` : la branche par défaut est protégée.
"""


def depot(fichiers: dict[str, str]) -> Path:
    racine = Path(tempfile.mkdtemp(prefix="socle-skills-"))
    env = {**os.environ, "HOME": str(racine), "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True, env=env)
    for chemin, texte in fichiers.items():
        p = racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")
    return racine


def juger(racine: Path) -> dict[str, list[str]]:
    ctx = contexte.Contexte(config.Projet.charger(racine), etage="agent")
    r = Rapport()
    controles.contrat(ctx, r)
    controles.commandes_lancees(ctx, r)
    return {i: [c.message for c in r.erreurs(i)] for i in ("skills.contrat", "skills.commandes")}


class TestLecture(unittest.TestCase):
    def test_l_entete_sur_une_ligne_ou_en_bloc(self):
        self.assertEqual(controles.entete(SAIN)["name"], "livrer")
        bloc = "---\nname: x\ndescription: >\n  Ce que fait le skill,\n  et quand.\n---\n# x\n"
        self.assertEqual(controles.entete(bloc)["description"], "Ce que fait le skill, et quand.")
        self.assertEqual(controles.entete('---\nname: "x"\n---\n')["name"], "x")
        # L'agent ne lit l'en-tête qu'en tête du fichier.
        self.assertIsNone(controles.entete("\n" + SAIN))
        self.assertIsNone(controles.entete("# Sans en-tête\n"))

    def test_seuls_les_blocs_du_shell_sont_des_commandes(self):
        texte = ("intro `git push --force`\n\n```sh\ngit status\n```\n\n```python\nimport os\n```\n\n"
                 "```console\n$ python3 .socle/socle answer D-NNNN <réponse> --relayed --by <nom> "
                 "--quote-file <fichier>\n```\n")
        blocs = controles.commandes(texte)
        self.assertEqual([l for l, _ in blocs], [3, 11])
        self.assertEqual(blocs[0][1], "git status")
        # L'invite est retirée ; un argument à remplir n'est pas une redirection.
        self.assertEqual(blocs[1][1], "python3 .socle/socle answer D-NNNN ARG --relayed --by ARG --quote-file ARG")


class TestControles(unittest.TestCase):
    def setUp(self):
        self.racine = None

    def tearDown(self):
        if self.racine:
            shutil.rmtree(self.racine, ignore_errors=True)

    def test_un_skill_sain_passe_et_se_trouve(self):
        self.racine = depot({".claude/skills/livrer/SKILL.md": SAIN, "docs/skills/notes.md": "# pas un skill\n"})
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent")
        self.assertEqual(list(controles.skills(ctx)), [".claude/skills/livrer/SKILL.md"])
        self.assertEqual(juger(self.racine), {"skills.contrat": [], "skills.commandes": []})

    def test_le_contrat(self):
        self.racine = depot({
            ".claude/skills/sans-entete/SKILL.md": "# Livrer\n",
            ".claude/skills/autre-nom/SKILL.md": SAIN,
            ".claude/skills/maigre/SKILL.md": SAIN.replace("name: livrer", "name: maigre").replace(
                "Livrer une version du projet, ses tests et son étiquette. À utiliser quand une version est "
                "prête à partir.", "Livrer."),
            ".claude/skills/socle-livrer/SKILL.md": SAIN.replace("name: livrer", "name: socle-livrer"),
        })
        fautes = juger(self.racine)["skills.contrat"]
        self.assertEqual(len(fautes), 4, fautes)
        # Dans l'ordre des chemins : autre-nom, maigre, sans-entete, socle-livrer.
        self.assertIn("« livrer » : son nom est celui de son dossier, « autre-nom »", fautes[0])
        self.assertIn("description trop maigre", fautes[1])
        self.assertIn("sans en-tête", fautes[2])
        self.assertIn("préfixe `socle-` est réservé", fautes[3])

    def test_une_commande_que_le_hook_refuse(self):
        self.racine = depot({".claude/skills/livrer/SKILL.md": SAIN.replace(
            "python3 -m unittest discover -s tests -q", "python3 -m unittest\ngit commit -q --no-verify -m x")})
        fautes = juger(self.racine)["skills.commandes"]
        self.assertEqual(len(fautes), 1, fautes)
        self.assertIn("contourne les hooks du projet", fautes[0])
        self.assertIn("se cite dans le texte", fautes[0])


class TestSkillsDuSocle(unittest.TestCase):
    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n"})

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def test_l_installeur_les_pose_et_la_politique_les_protege(self):
        with redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        for nom in controles.DU_SOCLE:
            texte = (self.racine / installeur.SKILLS / nom / "SKILL.md").read_text()
            self.assertTrue(texte.startswith(f"---\nname: {nom}\n"))
        self.assertEqual(sorted(controles.DU_SOCLE), ["socle-batch", "socle-handoff", "socle-private-memory",
                                                      "socle-request", "socle-resume", "socle-review"])
        self.assertIn(".claude/skills/socle-*/**", config.Projet.charger(self.racine).chemins_proteges())
        self.assertEqual(juger(self.racine), {"skills.contrat": [], "skills.commandes": []})

    def test_les_instructions_ne_nomment_que_les_skills_du_socle_poses(self):
        """Relevé par la revue du lot de D-0075 : un nom de skill faux dans
        les instructions (`socle-reveiw`) passait tous les contrôles, et la
        règle aurait renvoyé l'agent à un skill absent."""
        import re

        from socle.templates import DOSSIER

        for gabarit in ("AGENTS.md", "AGENTS.en.md"):
            cites = set(re.findall(r"`(socle-[a-z-]+)`", (DOSSIER / gabarit).read_text(encoding="utf-8")))
            self.assertEqual(cites, set(controles.DU_SOCLE), gabarit)

    def test_dans_les_deux_langues_ils_passent_leurs_controles(self):
        self.assertEqual(installeur.poser_skills(self.racine, "en"),
                         ["skills du socle posés dans .claude/skills : socle-batch, socle-handoff, "
                          "socle-private-memory, socle-request, socle-resume, socle-review"])
        texte = (self.racine / ".claude/skills/socle-request/SKILL.md").read_text()
        self.assertIn("description: Write a request for a human decision", texte)
        self.assertEqual(juger(self.racine), {"skills.contrat": [], "skills.commandes": []})


class TestLesDemandes(unittest.TestCase):
    """Le skill des demandes : ce qu'une décision prise en séance garde, et
    la variante légère des valeurs attendues mécaniques (D-0134)."""

    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n"})

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def texte(self, lg: str) -> str:
        installeur.poser_skills(self.racine, lg)
        texte = (self.racine / installeur.SKILLS / "socle-request" / "SKILL.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(texte.encode("utf-8")), 10000, lg)
        return " ".join(texte.split())

    def test_un_contenu_valide_en_seance_s_ecrit_d_abord_dans_le_depot(self):
        """T-0097 (B-0286) : la décision désigne le contenu écrit, et les
        tâches le citent ; sans lui, il se perd."""
        attendus = {
            "fr": "Un contenu montré dans la conversation que l'humain valide (un format, un exemple, un texte) "
                  "s'écrit d'abord tel quel dans le dépôt, puis la décision le désigne (`--about <chemin>`), et "
                  "les tâches qui en découlent citent ce chemin",
            "en": "Content shown in the conversation that the human approves (a format, an example, a text) is "
                  "first written as is in the repository, then the decision designates it (`--about <path>`), "
                  "and the tasks that follow from it cite that path",
        }
        for lg, phrase in attendus.items():
            self.assertIn(phrase, self.texte(lg), lg)

    def test_le_relecteur_a_froid_recoit_le_modele_le_plus_capable_a_son_lancement(self):
        """T-0074 (B-0243) : comme le relecteur d'un lot, explicitement, le
        plus capable jusqu'à Opus, quel que soit celui de la session ; Fable
        sur la demande de l'humain seule ; le récap nomme le modèle."""
        attendus = {
            "fr": ("du modèle de la session", [
                "Il reçoit explicitement à son lancement (`model`) le modèle le plus capable disponible jusqu'à "
                "Opus, quel que soit celui de la session, sur la dernière version de sa famille",
                "Fable, s'il est disponible, seulement si l'humain le demande",
                "`Relecture à froid (<modèle>) : <n> points, <k> corrigés"]),
            "en": ("of the session's model", [
                "It receives explicitly at launch (`model`) the most capable model available up to Opus, whatever "
                "the session's, on the latest version of its family",
                "Fable, if available, only if the human asks for it",
                "`Cold reading (<model>): <n> points, <k> fixed"]),
        }
        for lg, (ancien, phrases) in attendus.items():
            texte = self.texte(lg)
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)
            self.assertNotIn(ancien, texte, lg)

    def test_le_relecteur_a_froid_repond_en_un_message_sans_outil(self):
        """T-0034 (B-0197) : mesuré, il ne lit rien hors de son dossier et ne
        coûte que le prix fixe d'un sous-agent ; le skill borne ce qu'il
        reçoit et ce qu'il fait, et un outil lancé se dit."""
        attendus = {
            "fr": ("sans lien ni fichier, et rend", [
                "dont le seul message est le dossier",
                "et rend en un seul message, sans lancer d'outil, ce qu'il en a compris",
                "Un compte rendu qui compte un outil lancé dit une lecture qui n'était pas à froid : le récap le "
                "dit."]),
            "en": ("with no link and no file, and returns", [
                "whose only message is the brief",
                "and returns in a single message, launching no tool, what it understood",
                "A report that counts a tool launched means a reading that was not cold: the recap says so."]),
        }
        for lg, (ancien, phrases) in attendus.items():
            texte = self.texte(lg)
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)
            self.assertNotIn(ancien, texte, lg)

    def test_une_decision_donnee_sans_question_se_consigne_par_unprompted(self):
        """T-0017 (B-0185) : sans question inventée ni réponse à choisir."""
        attendus = {"fr": "--unprompted --relayed --by <nom> --quote-file <fichier>",
                    "en": "--unprompted --relayed --by <name> --quote-file <file>"}
        for lg, phrase in attendus.items():
            self.assertIn(phrase, self.texte(lg), lg)

    def test_la_variante_legere_des_valeurs_attendues_mecaniques(self):
        """T-0095 (B-0289) : ce qui la permet, ce qu'elle demande, et ce qui
        garde la demande écrite."""
        attendus = {
            "fr": ["**La variante légère**, pour des valeurs attendues changées mécaniquement, des tests qui "
                   "lisent un format que l'humain vient de valider : une question dans la conversation qui nomme "
                   "chaque test, avec sa valeur avant et après",
                   "sa réponse se consigne mot pour mot en décision de séance, dont le texte (`--question-file`) "
                   "nomme les tests, et se commite avec eux",
                   "Tout autre changement de valeur attendue, ou suppression d'un test, garde la demande écrite."],
            "en": ["**The light variant**, for expected values changed mechanically, tests that read a format the "
                   "human has just approved: a question in the conversation that names each test, with its value "
                   "before and after",
                   "its answer is recorded word for word as a decision taken in session, whose text "
                   "(`--question-file`) names the tests, and is committed with them",
                   "Any other change of an expected value, or deletion of a test, keeps the written request."],
        }
        for lg, phrases in attendus.items():
            texte = self.texte(lg)
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)


class TestLaReprise(unittest.TestCase):
    """Le skill de la reprise après une limite d'usage (ADR-0050) : posé dans
    les deux langues, il ne relance que l'agent dont le tour a fini sur une
    limite, et un tour qui finit retire ses réveils."""

    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n"})

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def lire(self, lg: str) -> str:
        installeur.poser_skills(self.racine, lg)
        return (self.racine / installeur.SKILLS / "socle-resume" / "SKILL.md").read_text(encoding="utf-8")

    def test_il_est_pose_dans_les_deux_langues_et_passe_ses_controles(self):
        for lg, reveil in (("fr", "Reprise après limite"), ("en", "Resume after limit")):
            texte = self.lire(lg)
            self.assertTrue(texte.startswith("---\nname: socle-resume\n"), lg)
            self.assertIn(reveil, texte, lg)
            self.assertEqual(juger(self.racine), {"skills.contrat": [], "skills.commandes": []}, lg)

    def test_seul_un_tour_fini_sur_une_limite_relance_l_agent(self):
        sections = {}
        for lg, jamais, fin, reveil, non in (
                ("fr", "ne relance jamais l'agent", "## À la fin de chaque tour", "## Au réveil", "Ne pas reprendre"),
                ("en", "never restarts the agent", "## At the end of every turn", "## On waking", "Do not resume")):
            texte = self.lire(lg)
            self.assertIn(jamais, texte, lg)
            section = texte.split(fin, 1)[1].split("\n## ", 1)[0]
            self.assertIn("delete_trigger", section, lg)
            # Au réveil : la fin du tour d'avant se lit d'abord, et quatre
            # cas, chacun une puce, retiennent l'agent de reprendre.
            au_reveil = texte.split(reveil, 1)[1].split("\n## ", 1)[0]
            self.assertIn("usage_limit_reached", au_reveil, lg)
            cas = au_reveil.split(non, 1)[1].split("\n\n", 1)[0]
            self.assertEqual(len(re.findall(r"^   - ", cas, re.M)), 4, lg)
            sections[lg] = re.findall(r"^## ", texte, re.M)
        self.assertEqual(len(sections["fr"]), len(sections["en"]))

    def test_les_reveils_s_arment_une_fois_par_tour_jamais_dans_le_passe(self):
        # B-0155, ADR-0060 : armés au début du tour, récrits au seul
        # lancement d'un sous-agent, jamais à une heure passée ; un tour
        # qui s'ouvre sur l'humain fait siens les réveils laissés.
        for lg, debut, sous_agent, passe, humain in (
                ("fr", "## Au début de chaque tour", "## Au lancement d'un sous-agent",
                 "**Jamais dans le passé.**", "sur un message de l'humain"),
                ("en", "## At the start of every turn", "## When launching a subagent",
                 "**Never in the past.**", "on a message from the human")):
            texte = self.lire(lg)
            self.assertNotIn("## À chaque étape", texte, lg)
            self.assertNotIn("## At every step", texte, lg)
            self.assertIn(passe, texte, lg)
            self.assertIn("date -u", texte, lg)
            section = texte.split(debut, 1)[1].split("\n## ", 1)[0]
            self.assertIn("send_later", section, lg)
            self.assertIn(humain, section, lg)
            section = texte.split(sous_agent, 1)[1].split("\n## ", 1)[0]
            self.assertIn("update_trigger", section, lg)
            # update_trigger récrit le texte au lancement d'un sous-agent, et
            # au début du tour, dans l'appel qui déplace un réveil laissé :
            # l'heure et le lot du tour ensemble, sans appel de plus.
            self.assertEqual(texte.count("`prompt`"), 2, lg)
            debut_tour = texte.split(debut, 1)[1].split("\n## ", 1)[0]
            self.assertIn("`run_once_at` " + ("et" if lg == "fr" else "and") + " `prompt`", debut_tour, lg)

    def test_sans_list_events_les_reveils_s_arment_a_la_borne(self):
        # B-0181 : une session cloud sans list_events n'en a pas moins le
        # skill ; l'heure ne se lit pas, chaque réveil s'arme à sa borne et
        # celui de cinq heures s'y repousse à chaque tour qui agit et au
        # lancement d'un sous-agent ; au réveil, la conversation seule dit
        # s'il faut reprendre, et l'heure de la coupure reste inconnue.
        for lg, regle, quand, sous_agent, reveil, au_reveil, inconnue in (
                ("fr", "**Sans l'outil `list_events`**", "## Quand", "au lancement d'un sous-agent", "## Au réveil",
                 "**Sans `list_events`**", "coupé à une heure inconnue"),
                ("en", "**Without the `list_events` tool**", "## When", "launching a subagent", "## On waking",
                 "**Without `list_events`**", "cut off at an unknown time")):
            texte = self.lire(lg)
            self.assertNotIn("list_events", texte.split(quand, 1)[1].split("\n## ", 1)[0], lg)
            regle_texte = " ".join(texte.split(regle, 1)[1].split("\n\n", 1)[0].split())
            self.assertIn(sous_agent, regle_texte, lg)
            self.assertIn("list_triggers", regle_texte, lg)
            section = " ".join(texte.split(reveil, 1)[1].split("\n## ", 1)[0].split())
            self.assertIn(au_reveil, section, lg)
            self.assertIn(inconnue, section, lg)

    def test_sans_list_events_la_transcription_locale_dit_la_coupure(self):
        # B-0198, T-0040 : sans list_events, la transcription que Claude
        # Code tient pour le projet dit si le tour d'avant a fini sur une
        # limite (l'enregistrement qui porte quotaLimits), à quelle heure,
        # et quels messages l'humain a tapés depuis ; sans elle, la
        # conversation seule le dit, et l'heure reste inconnue.
        for lg, au_reveil, reveil, sinon, heure in (
                ("fr", "**Sans `list_events`**", "## Au réveil", "Sans transcription",
                 "l'heure de la transcription"),
                ("en", "**Without `list_events`**", "## On waking", "Without a transcript",
                 "the time from the transcript")):
            section = " ".join(self.lire(lg).split(reveil, 1)[1].split("\n## ", 1)[0].split())
            regle = section.split(au_reveil, 1)[1].split(" 2. ", 1)[0]
            for attendu in ("~/.claude/projects/", "`quotaLimits`", "`timestamp`", "`user`"):
                self.assertIn(attendu, regle, (lg, attendu))
            # la transcription d'abord, la conversation à défaut
            self.assertLess(regle.index("`quotaLimits`"), regle.index(sinon), lg)
            self.assertIn(heure, section, lg)

    # Relevés le 23 novembre dans la transcription réelle de la session qui
    # a mené L-0023 (J-2026-11-23-O), les champs que la règle lit gardés : le
    # message que l'humain a tapé, et le chargement d'un skill, un `user` en
    # texte lui aussi.
    TAPE = {"type": "user", "timestamp": "2026-11-23T19:13:35.823Z", "isSidechain": False, "origin": {"kind": "human"},
            "userType": "external",
            "message": {"role": "user", "content": "Reprends le travail du socle dans ce dépôt"}}
    SKILL_CHARGE = {"type": "user", "timestamp": "2026-11-23T19:13:40.909Z", "isSidechain": False, "isMeta": True,
                    "userType": "external",
                    "message": {"role": "user", "content": [{"type": "text", "text": "Base directory for this skill"}]}}

    def test_la_coupure_lue_dans_la_transcription_est_le_premier_refus_apres_le_dernier_appel(self):
        """T-0164 (B-0336) : plusieurs refus peuvent se suivre ; la coupure
        est le premier après le dernier appel du modèle, et tout message tapé
        qui la suit compte, même suivi d'un autre refus. Une transcription
        sans le tour d'avant vaut absence de transcription. Les champs cités
        sont ceux que lit `socle consumption`, éprouvés sur sa fixture du refus
        et sur deux enregistrements relevés d'une transcription réelle."""
        from socle import consumption as conso
        from tests.test_consommation import _ecrire, _limite, _resultat

        for lg, au_reveil, relations, interdits, sans in (
                ("fr", "**Sans `list_events`**",
                 ("le premier enregistrement `quotaLimits` qui suit le dernier appel du modèle, à son `timestamp`",
                  "tout `user` tapé (`origin.kind` à `human`) qui la suit est de l'humain, même suivi d'un autre "
                  "refus"),
                 ("qui précèdent", "le plus ancien", "le dernier enregistrement `quotaLimits`"),
                 ("Sans transcription, ou sans le tour d'avant", "la conversation")),
                ("en", "**Without `list_events`**",
                 ("The cut is the first `quotaLimits` record that follows the model's last call, at its `timestamp`",
                  "every typed `user` record (`origin.kind` set to `human`) that follows it is the human's, even if "
                  "another refusal follows"),
                 ("that precede", "the oldest", "the last `quotaLimits` record"),
                 ("Without a transcript, or without the previous turn", "the conversation"))):
            regle = " ".join(self.lire(lg).split(au_reveil, 1)[1].split("\n2. ", 1)[0].split())
            for relation in relations:
                self.assertIn(relation, regle, lg)
            for interdit in interdits:
                self.assertNotIn(interdit, regle, lg)
            self.assertLess(regle.index(sans[0]), regle.index(sans[1]), lg)
            # Les champs cités, hors des chemins, des commandes et des valeurs.
            cites = set(re.findall(r"`([^`]+)`", regle)) - {"list_events", ".jsonl", "~/.claude/projects/", "tail",
                                                              "human"}
            self.assertEqual(cites, {"quotaLimits", "timestamp", "user", "origin.kind"}, lg)
        # La coupure : les champs de la fixture que `socle consumption` lit
        # comme un refus, à son horodatage.
        refus = _limite(60, 3600)
        self.assertLessEqual({"quotaLimits", "timestamp"}, set(refus))
        with tempfile.TemporaryDirectory() as dossier:
            conv = conso.lire_conversation(_ecrire(Path(dossier) / "t.jsonl", [refus]))
        self.assertEqual([l["horodatage"].isoformat().replace("+00:00", "Z") for l in conv.limites],
                         [refus["timestamp"]])
        # Le message : `user`, le type que lit `socle consumption` ; tapé, il
        # porte `origin.kind` à `human`, que le chargement d'un skill n'a pas.
        self.assertEqual(_resultat(0, "t", "x")["type"], "user")
        self.assertEqual((self.TAPE["type"], self.TAPE["origin"]["kind"]), ("user", "human"))
        self.assertEqual(self.SKILL_CHARGE["type"], "user")
        self.assertNotIn("origin", self.SKILL_CHARGE)
        # Et `socle consumption` lit `user` et `origin.kind` dans les
        # enregistrements relevés : le message tapé compte, le skill chargé et
        # un résultat d'outil, des `user` eux aussi, non.
        with tempfile.TemporaryDirectory() as dossier:
            conv = conso.lire_conversation(_ecrire(Path(dossier) / "t.jsonl",
                                                   [self.TAPE, self.SKILL_CHARGE, _resultat(0, "t", "x")]))
        self.assertEqual([h.isoformat() for h in conv.tapes], ["2026-11-23T19:13:35.823000+00:00"])

    def test_l_attente_a_heure_bornee_et_le_reveil_d_un_travail_interrompu(self):
        """T-0082 (B-0133, D-0163, ADR-0107) : une attente à heure bornée
        garde ses réveils, repoussés après son heure, et un tour refusé
        pendant elle se reprend ; au réveil qui ne reprend pas, un contrôle
        de fin de tour en échec ne fait pas finir le travail interrompu."""
        from socle import cli

        # T-0206 (D-0218) : les règles restent dans le skill, leurs raisons
        # passent au guide, « Pourquoi ces règles ».
        for lg, fin, non, apres, attente, reveil, guide, raisons in (
                ("fr", "## À la fin de chaque tour", "Ne pas reprendre", "\n3. ",
                 ("Les réveils restent : la fin d'un tour n'en retire aucun. Pendant une attente à heure bornée "
                  "(un rappel, une commande en arrière-plan, une CI), jusqu'au tour de l'événement, chacun est "
                  "repoussé après cette heure s'il tombait avant.",
                  "Un tour coupé ou refusé ne retire rien"),
                 "Si l'humain avait interrompu le travail et que le contrôle de fin de tour refuse sur des contrôles "
                 "en échec, le dire en une ligne, sans y toucher ni réarmer.", "HELP.md",
                 ("chacun repoussé après cette heure s'il tombait avant : refusé, ce tour se reprend à la levée.",
                  "sans y toucher ni réarmer : relancé sur le même arbre, il laisse conclure.")),
                ("en", "## At the end of every turn", "Do not resume", "\n3. ",
                 ("The wake-ups remain: the end of a turn removes none. During a wait with a bounded time "
                  "(a reminder, a background command, a CI), until the event's turn, each is pushed back after that "
                  "time if it fell before.",
                  "A turn cut off or refused removes nothing"),
                 "If the human had interrupted the work and the end-of-turn check refuses on failing checks, say so "
                 "in one line, without touching it or re-arming.", "HELP.en.md",
                 ("each pushed back after that time if it fell before: refused, that turn resumes when the limit "
                  "lifts.",
                  "without touching it or re-arming: relaunched on the same tree, it lets the turn conclude."))):
            texte = self.lire(lg)
            section = " ".join(texte.split(fin, 1)[1].split("\n## ", 1)[0].split())
            for attendu in attente:
                self.assertIn(attendu, section, lg)
            # La règle de la réponse d'une ligne est un cas où l'agent ne reprend pas.
            cas = " ".join(texte.split(non, 1)[1].split(apres, 1)[0].split())
            self.assertIn(reveil, cas, lg)
            texte_guide = " ".join((Path(cli.__file__).parent / guide).read_text(encoding="utf-8").split())
            for raison in raisons:
                self.assertIn(raison, texte_guide, lg)

    def test_le_message_qui_provoque_la_coupure_compte_et_le_reveil_qui_a_tire_manque(self):
        """Passe 2 de la revue de L-0023 (J-2026-11-23-U) : avec les réveils
        gardés pendant une attente, le message de l'humain peut ouvrir le
        premier tour refusé, avant le refus qu'il provoque ; il compte, et
        l'agent ne reprend pas par-dessus. Un réveil qui a tiré est éteint :
        il ne se déplace pas, il manque, et le début du tour en arme un."""
        for lg, debut, reveil, attendus_debut, attendus_reveil in (
                ("fr", "## Au début de chaque tour", "## Au réveil",
                 ("fait siens les réveils laissés ; celui qui a tiré, éteint, manque.",
                  "Le réveil qui manque s'arme : `send_later`"),
                 ("Puis, avec `kinds: [\"user\", \"assistant\"]`, les messages arrivés depuis son dernier travail, "
                  "même refusés",
                  "même suivi d'un autre refus, comme celui qui l'a provoquée.",
                  "si l'humain a écrit pendant la limite : répondre à son message")),
                ("en", "## At the start of every turn", "## On waking",
                 ("makes the wake-ups left its own; the one that fired, spent, is missing.",
                  "The missing wake-up is armed: `send_later`"),
                 ("Then, with `kinds: [\"user\", \"assistant\"]`, the messages that arrived since its last work, "
                  "even refused",
                  "even if another refusal follows, like the one that provoked it.",
                  "if the human wrote during the limit: answer their message"))):
            texte = self.lire(lg)
            section = " ".join(texte.split(debut, 1)[1].split("\n## ", 1)[0].split())
            for attendu in attendus_debut:
                self.assertIn(attendu, section, lg)
            section = " ".join(texte.split(reveil, 1)[1].split("\n## ", 1)[0].split())
            for attendu in attendus_reveil:
                self.assertIn(attendu, section, lg)
            self.assertNotIn("depuis la coupure", section, lg)
            self.assertNotIn("since the cut", section, lg)

    def test_les_reveils_d_une_session_archivee_se_disent_a_l_humain(self):
        """T-0127 (B-0301) : ils ne se désactivent qu'à sa demande, et il
        sait où les retrouver lui-même : le skill le dit, et le guide le lui
        dit (T-0206)."""
        from socle import cli

        for lg, debut, jamais, attendus, retrouver, guide, ou in (
                ("fr", "## Au début de chaque tour", "## Ce que l'agent ne fait jamais",
                 ("Au premier tour de la session, ou perdus par un compactage : `list_triggers`",
                  "Ceux d'une session archivée (`get_session` : `SESSION_STATUS_ARCHIVED`) se disent à l'humain "
                  "avec leurs heures, et ne se désactivent (`update_trigger`, `enabled: false`) qu'à sa demande."),
                 ("toucher au réveil d'une autre session sans que l'humain le demande",
                  "la liste des tâches programmées de son compte (claude.ai/code/routines)"), "HELP.md",
                 "la liste des tâches programmées de son compte (claude.ai/code/routines)"),
                ("en", "## At the start of every turn", "## What the agent never does",
                 ("At the session's first turn, or lost to a compaction: `list_triggers`",
                  "Those of an archived session (`get_session`: `SESSION_STATUS_ARCHIVED`) are told to the human "
                  "with their times, and are disabled (`update_trigger`, `enabled: false`) only at their request."),
                 ("touch another session's wake-up without the human asking",
                  "the list of scheduled tasks of their account (claude.ai/code/routines)"), "HELP.en.md",
                 "the list of scheduled tasks of their account (claude.ai/code/routines)")):
            texte = self.lire(lg)
            section = " ".join(texte.split(debut, 1)[1].split("\n## ", 1)[0].split())
            for attendu in attendus:
                self.assertIn(attendu, section, lg)
            section = " ".join(texte.split(jamais, 1)[1].split())
            for attendu in retrouver:
                self.assertIn(attendu, section, lg)
            self.assertIn(ou, " ".join((Path(cli.__file__).parent / guide).read_text(encoding="utf-8").split()), lg)

    def test_les_reveils_restent_d_un_tour_a_l_autre(self):
        """T-0215 (B-0376, D-0235, point 6) : un tour qui trouve ses réveils
        à la bonne heure n'appelle aucun outil de réveil ; la fin d'un tour
        n'en retire aucun ; un réveil sans objet se vérifie et se dit en une
        ligne, sans reprendre ni réarmer ; sans `list_events`, l'heure de la
        fenêtre nommée se lit dans `get_session`, et la borne ne se repousse
        pas. Le guide dit pourquoi."""
        from socle import cli

        for lg, quand, texte_seul, debut, intact, fin, retrait, reveil, sans_objet, borne, guide, raison in (
                ("fr", "## Quand", "Une réponse en texte seul ne touche à aucun réveil",
                 "## Au début de chaque tour",
                 "Un réveil laissé à la bonne heure, pour le même lot, ne se touche pas : le tour n'appelle aucun "
                 "outil de réveil.",
                 "## À la fin de chaque tour",
                 ("la fin d'un tour n'en retire aucun", "Ils ne se retirent (`delete_trigger`) qu'au rangement "
                  "d'une session qui passe la main, ou quand l'humain dit d'arrêter."),
                 "## Au réveil",
                 "Répondre alors pourquoi en une ligne, puis les lignes de fin du projet, sans reprendre le "
                 "travail : le réveil restant reste, et cette réponse n'arme rien.",
                 ("`get_session` sans argument donne, quand il porte `rate_limit_info`, l'heure de la seule "
                  "fenêtre que nomme `rateLimitType`", "Un réveil à la borne ne s'y repousse ni au début d'un "
                  "tour ni au lancement d'un sous-agent"),
                 "HELP.md", "Les réveils restent d'un tour à l'autre : les armer au début de chaque tour et les "
                            "retirer à sa fin coûtait environ un appel d'outil sur dix d'une séance"),
                ("en", "## When", "A text-only answer touches no wake-up",
                 "## At the start of every turn",
                 "A wake-up left at the right time, for the same batch, is not touched: the turn calls no wake-up "
                 "tool.",
                 "## At the end of every turn",
                 ("the end of a turn removes none", "They are removed (`delete_trigger`) only when a session that "
                  "hands over tidies up, or when the human says to stop."),
                 "## On waking",
                 "Then answer why in one line, then the project's closing lines, without resuming the work: the "
                 "remaining wake-up stays, and this answer arms nothing.",
                 ("`get_session` without argument gives, when it carries `rate_limit_info`, the time of the only "
                  "window that `rateLimitType` names", "A wake-up at the bound is not pushed back to it, neither "
                  "at the start of a turn nor when launching a subagent"),
                 "HELP.en.md", "The wake-ups remain from one turn to the next: arming them at the start of every "
                               "turn and removing them at its end cost about one tool call in ten of a sitting")):
            texte = self.lire(lg)

            def section(titre):
                return " ".join(texte.split(titre, 1)[1].split("\n## ", 1)[0].split())

            self.assertIn(texte_seul, section(quand), lg)
            self.assertIn(intact, section(debut), lg)
            for attendu in retrait:
                self.assertIn(attendu, section(fin), lg)
            self.assertIn(sans_objet, section(reveil), lg)
            for attendu in borne:
                self.assertIn(attendu, " ".join(texte.split()), lg)
            # Plus rien ne retire les réveils avant la réponse finale.
            self.assertNotIn("Avant la réponse finale", texte, lg)
            self.assertNotIn("Before the final answer", texte, lg)
            texte_guide = " ".join((Path(cli.__file__).parent / guide).read_text(encoding="utf-8").split())
            self.assertIn(raison, texte_guide, lg)

    def test_un_sous_agent_ne_touche_a_aucun_reveil(self):
        for lg, regle in (("fr", "Un sous-agent ne touche à aucun réveil"), ("en", "A subagent\ntouches no wake-up")):
            self.assertIn(regle, self.lire(lg), lg)

    def test_au_reveil_la_garde_de_la_passation_et_au_premier_tour_la_passation_qui_attend(self):
        """T-0081 (D-0174) : la vérification du réveil appelle la garde de la
        passation, la tête distante lue avant son `git fetch` et l'heure de la
        coupure ; au premier tour, une passation programmée qui attend se dit
        à l'humain, comme les réveils d'une session archivée, et ne s'annule
        qu'à sa demande."""
        for lg, reveil, non, garde, avant, debut, attente in (
                ("fr", "## Au réveil", "Ne pas reprendre",
                 "si la garde refuse : `git fetch`, puis `python3 .socle/socle handoff check --ref origin/<branche> "
                 "--head <sa tête avant le fetch> --since <la coupure, si connue>` ;", "puis comparer",
                 "## Au début de chaque tour",
                 "qu'à sa demande. Une passation qui attend (« Passation — <dépôt> ») de même."),
                ("en", "## On waking", "Do not resume",
                 "if the guard refuses: `git fetch`, then `python3 .socle/socle handoff check --ref origin/<branch> "
                 "--head <its head before the fetch> --since <the cut, if known>`;", "then compare",
                 "## At the start of every turn",
                 "only at their request. A handoff that is waiting (\"Handoff — <repository>\") likewise.")):
            texte = self.lire(lg)
            cas = " ".join(texte.split(reveil, 1)[1].split(non, 1)[1].split("\n\n", 1)[0].split())
            self.assertIn(garde, cas, lg)
            self.assertNotIn(avant, texte, lg)
            section = " ".join(texte.split(debut, 1)[1].split("\n## ", 1)[0].split())
            self.assertIn(attente, section, lg)
            self.assertLessEqual(len(texte.encode("utf-8")), 10000, lg)


class TestLaConduiteDUnLot(unittest.TestCase):
    """B-0199, ADR-0079 : le skill qui conduit un lot, posé et protégé
    comme les autres skills du socle, sans rien de l'atelier qui le
    fabrique (ADR-0033)."""

    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n"})

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def texte(self, lg: str) -> str:
        installeur.poser_skills(self.racine, lg)
        return (self.racine / installeur.SKILLS / "socle-batch" / "SKILL.md").read_text(encoding="utf-8")

    def test_il_est_pose_protege_et_passe_ses_controles_dans_les_deux_langues(self):
        from socle import utils as outils

        with redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        proteges = config.Projet.charger(self.racine).chemins_proteges()
        self.assertTrue(outils.correspond(".claude/skills/socle-batch/SKILL.md", proteges))
        for lg in ("fr", "en"):
            texte = self.texte(lg)
            self.assertTrue(texte.startswith("---\nname: socle-batch\n"), lg)
            # Le plafond des garde-fous d'un projet neuf.
            self.assertLessEqual(len(texte.encode("utf-8")), 10000, lg)
            self.assertEqual(juger(self.racine), {"skills.contrat": [], "skills.commandes": []}, lg)

    def test_il_ne_renvoie_pas_a_l_atelier(self):
        atelier = re.compile(r"\b(?:ADR|[BDFJ])-\d|fabrication|chess|Théo|delegate-lot|Opus|Sonnet|Haiku")
        for lg in ("fr", "en"):
            self.assertIsNone(atelier.search(self.texte(lg)), lg)

    def test_il_dit_la_consommation_le_changement_de_session_et_l_apres_fusion(self):
        """B-0220 : après la fusion, rien ne se pousse sans travail neuf ;
        le chantier actif et le journal s'écrivent avant."""
        attendus = {
            "fr": ["deux à la fois au plus", "85 %", "60 % de la fenêtre de cinq heures",
                   "**La session est l'unité de budget.**", "git format-patch", "dit de demander la reprise",
                   "Le chantier actif et le journal s'écrivent avant la fusion",
                   "ne se pousse qu'avec le premier commit du lot suivant"],
            "en": ["two at a time at most", "85%", "60% of the five-hour window",
                   "**The session is the budget unit.**", "git format-patch", "says to ask for the resumption",
                   "The active work and the journal are written before the merge",
                   "is pushed only with the first commit of the next batch"],
        }
        for lg, phrases in attendus.items():
            texte = " ".join(self.texte(lg).split())
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)

    def test_il_dit_quand_compacter_et_quel_modele_pour_quel_travail(self):
        """B-0173 : l'agent demande le compactage, mémoire écrite, à la fin
        d'un lot et avant une attente longue, jamais après. Le modèle se
        choisit pour la qualité du travail, jamais un moindre pour tenir une
        limite (J-2026-11-15-D) ; entre ceux qui font aussi bien, celui qui
        pèse le moins ; un sous-agent reçoit le sien à son lancement."""
        attendus = {
            "fr": ["L'agent ne compacte pas lui-même", "il écrit la mémoire (chantier actif, journal)",
                   "si l'humain garde la session au-delà de ce seuil", "lui demande `/compact`",
                   "celui que demande la qualité du travail, jamais un moindre pour tenir une limite",
                   "une limite retarde un lot, elle ne l'allège pas",
                   "Entre ceux qui le font aussi bien, celui qui consomme le moins de la limite par jeton",
                   "l'humain choisit celui de la session, sur le conseil de l'agent",
                   "Celui que fixent les instructions du projet prime",
                   "Un sous-agent reçoit le sien explicitement à son lancement"],
            "en": ["The agent does not compact by itself", "it writes the memory (active work, journal)",
                   "if the human keeps the session beyond that threshold", "asks them for `/compact`",
                   "the one the quality of the work calls for, never a lesser one to stay within a limit",
                   "a limit delays a batch, it does not lighten it",
                   "Among those that do it equally well, the one that uses the least of the limit per token",
                   "the human chooses the session's, on the agent's advice",
                   "The one set by the project's instructions prevails",
                   "A subagent receives its own explicitly at launch"],
        }
        for lg, phrases in attendus.items():
            texte = " ".join(self.texte(lg).split())
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)


    def lire(self, attendus: dict[str, list[str]]) -> None:
        for lg, phrases in attendus.items():
            texte = " ".join(self.texte(lg).split())
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)

    def test_un_sous_agent_implemente_quand_il_paie(self):
        """T-0183 (D-0194, section 4 de la page validée) : l'agent qui
        orchestre implémente ; un sous-agent, seulement pour des tâches
        indépendantes en parallèle ou une lecture qui saturerait la
        conversation. Remplace le seuil de la petite tâche (D-0134)."""
        self.lire({
            "fr": ["L'agent qui orchestre implémente, une tâche après l'autre, un commit chacune.",
                   "**Un sous-agent implémente quand il paie** : des tâches indépendantes qui avancent en "
                   "parallèle, ou une tâche dont la lecture saturerait la conversation qui orchestre (plus de 400 "
                   "lignes changées, ou des fichiers longs à lire)."],
            "en": ["The orchestrating agent implements, one task after the other, one commit each.",
                   "**A subagent implements when it pays**: independent tasks that move forward in parallel, or a "
                   "task whose reading would saturate the orchestrating conversation (more than 400 lines changed, "
                   "or long files to read)."],
        })
        for lg, avant in (("fr", "petite tâche"), ("en", "small task")):
            self.assertNotIn(avant, self.texte(lg), lg)

    def test_un_sous_agent_se_lance_si_ce_qui_reste_couvre_son_cout_et_le_rangement(self):
        """T-0037 (B-0249) : le seuil fixe devient le coût mesuré d'un
        sous-agent et du rangement ; le rangement a sa marge fixe ; les
        anciens seuils ne valent que sans mesure."""
        self.lire({
            "fr": ["Les coûts se mesurent : l'utilisation de chaque fenêtre, avant chaque lancement et à chaque "
                   "compte rendu",
                   "La clôture note au journal le coût de chaque sous-agent, du relecteur, de chaque demande et du "
                   "rangement",
                   "Un sous-agent se lance si ce qui reste de chaque fenêtre couvre son coût mesuré et celui du "
                   "rangement ; sans mesure, aucun au-delà de 85 % de la semaine",
                   "Le rangement commence au plus tard à dix points d'une limite"],
            "en": ["Costs are measured: the use of each window, before each launch and at each report",
                   "The closure notes in the journal the cost of each subagent, of the reviewer, of each request "
                   "and of the tidying up",
                   "A subagent is launched if what remains of each window covers its measured cost and that of "
                   "the tidying up; without a measure, none beyond 85% of the week",
                   "The tidying up starts at the latest ten points from a limit"],
        })

    def test_resserre_sous_son_plafond_il_garde_ses_regles(self):
        """Relevé par la revue de L-0018 : le gabarit, resserré sous son
        plafond, avait perdu trois règles."""
        self.lire({
            "fr": ["Un sous-agent arrêté (une vérification en arrière-plan dont il n'a pas repris le fil) se "
                   "reprend depuis sa copie isolée, par l'agent qui orchestre",
                   "une tâche qui demande plus de réflexion se commence quand même",
                   "il hérite de la session ; sinon, le dire à l'humain"],
            "en": ["A stopped subagent (a background check whose thread it did not pick up) is resumed from its "
                   "isolated copy, by the orchestrating agent",
                   "a task that needs more thought is started anyway",
                   "it inherits the session's; otherwise, tell the human"],
        })

    def test_le_cout_d_un_lot_s_estime_a_son_annonce(self):
        """T-0099 (B-0291) : à l'annonce, le coût du lot s'estime sur les
        coûts mesurés ; s'il ne tient pas, découper, réduire ou attendre."""
        self.lire({
            "fr": ["estimer le coût du lot : s'il ne tient pas dans ce qui reste de la fenêtre, le découper, "
                   "commencer par un lot plus petit ou attendre la remise à zéro",
                   "le jalon servi, le coût estimé", "celui d'un lot s'estime sur ces mesures"],
            "en": ["estimate the batch's cost: if it does not fit in what remains of the window, split it, start "
                   "with a smaller batch or wait for the reset",
                   "the milestone served, the estimated cost", "a batch's cost is estimated on these measures"],
        })

    def test_le_reveil_d_une_attente_n_existe_qu_en_session_cloud(self):
        """T-0011 (B-0226) : `send_later` n'existe qu'en session cloud ;
        ailleurs, rien ne réveille l'agent, et l'humain le relance."""
        self.lire({
            "fr": ["Une attente annoncée a son réveil en session cloud (`send_later`) ; ailleurs, `Ensuite :` le "
                   "dit, et l'humain relance l'agent."],
            "en": ["An announced wait has its wake-up in a cloud session (`send_later`); elsewhere, `Next:` says "
                   "so, and the human restarts the agent."],
        })
        for lg, avant in (("fr", "sous Claude Code, `send_later`"), ("en", "under Claude Code, `send_later`")):
            self.assertNotIn(avant, " ".join(self.texte(lg).split()), lg)

    def test_apres_sa_fusion_l_agent_attend_les_workflows_qu_elle_lance(self):
        """T-0064 (B-0279) : l'agent qui fusionne sa pull request, quand la
        politique le permet, attend les workflows que la fusion lance sur la
        branche par défaut, et le récap dit s'ils ont réussi."""
        self.lire({
            "fr": ["l'agent, la sienne, si la politique le permet",
                   "Il attend de même les workflows que la fusion lance sur la branche par défaut ; le récap dit "
                   "s'ils ont réussi."],
            "en": ["the agent, its own, if the policy allows it",
                   "It then waits likewise for the workflows the merge starts on the default branch; the recap "
                   "says whether they succeeded."],
        })

    def test_apres_la_fusion_l_agent_supprime_ses_branches_contenues(self):
        """T-0192 (B-0351, ADR-0114) : après la fusion, l'agent supprime
        ses branches que la branche par défaut contient désormais."""
        for lg, (fusion, commande) in {
                "fr": ("Le chantier actif et le journal s'écrivent avant la fusion",
                       "Après la fusion, `python3 .socle/socle prune-branches` supprime les branches de l'agent "
                       "contenues"),
                "en": ("The active work and the journal are written before the merge",
                       "After the merge, `python3 .socle/socle prune-branches` deletes the agent's contained "
                       "branches")}.items():
            texte = " ".join(self.texte(lg).split())
            self.assertIn(commande, texte, lg)
            self.assertLess(texte.index(fusion), texte.index(commande), lg)

    def test_un_ensemble_qu_une_session_ne_mene_pas_se_forme_en_jalon(self):
        """T-0073 (B-0233) : à la formation d'un lot, un ensemble trop
        grand pour une session devient un jalon, ses lots dessous."""
        self.lire({
            "fr": ["dit ce qui les réunit. Un ensemble qu'une session ne mène pas se forme en jalon, ses lots "
                   "dessous."],
            "en": ["says what brings them together. A whole that one session does not carry through is formed as "
                   "a milestone, its batches under it."],
        })

    def test_la_tache_qui_change_un_comportement_nomme_le_test_contraire_avant_le_lot(self):
        """T-0134 (B-0303, D-0141) : la tâche qui change un comportement
        nomme le test qui affirme le contraire, et sa demande se pose avant
        le lot, non en son milieu ; le format de la mémoire le dit aussi."""
        self.lire({
            "fr": ["une tâche qui change un comportement nomme le test qui affirme le contraire, sa demande posée "
                   "aussitôt, avant le lot"],
            "en": ["a task that changes a behaviour names the test that asserts the opposite, its request made at "
                   "once, before the batch"],
        })
        format_ = " ".join((MOTEUR / "socle/FORMAT.md").read_text(encoding="utf-8").split())
        self.assertIn("une tâche qui dit ce qu'un comportement doit devenir nomme, dès son écriture, le test qui "
                      "affirme le contraire, et la demande qui autorise à le changer se pose aussitôt, avant le "
                      "lancement du lot", format_)

    def test_a_la_cloture_une_tache_que_la_revue_ouvre_rejoint_un_lot_ou_en_forme_un(self):
        """T-0162 (B-0335) : à la clôture d'un lot, une tâche que sa revue a
        ouverte rejoint le prochain lot dont la règle s'applique, sinon un
        lot neuf dans le jalon de son besoin : elle ne reste hors de tout
        lot."""
        self.lire({
            "fr": ["une tâche que sa revue ouvre rejoint le prochain lot dont la règle s'applique, sinon un lot neuf "
                   "dans le jalon de son besoin"],
            "en": ["a task its review opens joins the next batch whose rule applies, otherwise a new batch in its "
                   "need's milestone"],
        })

    def test_les_constats_de_la_revue_suivent_le_tri_de_socle_review(self):
        """T-0014 (B-0242) : un constat qui ne bloque pas suit le tri de
        `socle-review` (backlog ou écarté), il ne va plus d'office au
        backlog."""
        self.lire({
            "fr": ["Skill `socle-review`, sur le lot commité, et son tri des constats. Un bloquant retourne"],
            "en": ["Skill `socle-review`, on the committed batch, and its sorting of the findings. A blocking "
                   "finding goes back"],
        })
        for lg, avant in (("fr", "Le reste va au backlog"), ("en", "The rest goes to the backlog")):
            self.assertNotIn(avant, self.texte(lg), lg)

    def test_la_consigne_des_sous_agents_porte_la_ligne_economie(self):
        """T-0063 (B-0278) : la consigne d'un sous-agent lui dit d'économiser
        sa lecture et ses vérifications."""
        lignes = {"fr": "Économie : lire ce qui sert, pas les fichiers entiers ; pas de suite complète relancée "
                        "sans raison.",
                  "en": "Economy: read what serves, not whole files; no full suite rerun without reason."}
        for lg, ligne in lignes.items():
            consigne = self.texte(lg).split("```text\n", 1)[1].split("```", 1)[0]
            self.assertIn(ligne, consigne.splitlines(), lg)

    def test_aucun_sous_agent_n_implemente_sur_fable_sans_l_humain(self):
        """T-0015 (B-0243, D-0119) : comme pour la revue, aucun sous-agent
        sur Fable sauf si l'humain le veut."""
        self.lire({
            "fr": ["Un sous-agent reçoit le sien explicitement à son lancement (`model`), jamais Fable sauf si "
                   "l'humain le veut"],
            "en": ["A subagent receives its own explicitly at launch (`model`), never Fable unless the human "
                   "wants it"],
        })

    def test_changer_de_session_range_puis_renvoie_a_socle_handoff(self):
        """T-0079 (B-0156, D-0174) : « Changer de session » se réduit au
        rangement, puis au skill `socle-handoff`, qui programme la session
        suivante ou donne le prompt à copier ; le prompt lui-même vient de
        `socle handoff prompt`. Et l'agent sans l'humain pour compacter ne
        l'attend pas : il change de session."""
        for lg, titre, rangement, renvoi, absent in (
                ("fr", "## Changer de session",
                 ("1. le chantier actif dit le lot et ce qui attend, le journal la passation ;",
                  "3. tout est commité ;", "Plus rien ne se pousse ensuite."),
                 "Puis le skill `socle-handoff` : la passation écrite, commitée et poussée, avant toute fusion. Plus "
                 "rien ne se pousse ensuite. Selon le mode, il programme la session suivante, ou dit de "
                 "demander la reprise.",
                 "sinon, elle change de session."),
                ("en", "## Changing sessions",
                 ("1. the active work gives the batch and what is waiting, the journal the handoff;",
                  "3. everything is committed;", "Nothing is pushed afterwards."),
                 "Then the `socle-handoff` skill: the handoff written, committed and pushed, before any merge. "
                 "Nothing is pushed afterwards. Depending on the mode, it schedules the next session, or "
                 "says to ask for the resumption.",
                 "otherwise, it changes sessions.")):
            texte = self.texte(lg)
            section = texte.split(titre, 1)[1].split("\n## ", 1)[0]
            self.assertNotIn("```", section, lg)
            section = " ".join(section.split())
            for phrase in (*rangement, renvoi):
                self.assertIn(phrase, section, lg)
            self.assertIn(absent, " ".join(texte.split()), lg)


class TestLaPassation(unittest.TestCase):
    """T-0079 et T-0081 (B-0156, B-0259, D-0174) : le skill qui passe la main
    à une session neuve, posé et protégé comme les autres skills du socle,
    sans rien de l'atelier ; les deux modes et leur commutateur, le moment,
    les bornes, les deux appels de la session programmée, la garde, la pull
    request d'une passation, voir et arrêter ; les instructions et le guide
    le disent."""

    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n"})

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def texte(self, lg: str) -> str:
        installeur.poser_skills(self.racine, lg)
        return (self.racine / installeur.SKILLS / "socle-handoff" / "SKILL.md").read_text(encoding="utf-8")

    def lire(self, attendus: dict[str, list[str]]) -> None:
        for lg, phrases in attendus.items():
            texte = " ".join(self.texte(lg).split())
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)

    def test_il_est_pose_protege_sous_son_budget_et_passe_ses_controles(self):
        from socle import utils as outils

        with redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        proteges = config.Projet.charger(self.racine).chemins_proteges()
        self.assertTrue(outils.correspond(".claude/skills/socle-handoff/SKILL.md", proteges))
        for lg in ("fr", "en"):
            texte = self.texte(lg)
            self.assertTrue(texte.startswith("---\nname: socle-handoff\n"), lg)
            self.assertLessEqual(len(texte.encode("utf-8")), 10000, lg)
            # Ses commandes, dans des blocs de code, jugées comme le hook.
            self.assertEqual(len(controles.commandes(texte)), 2, lg)
            self.assertEqual(juger(self.racine), {"skills.contrat": [], "skills.commandes": []}, lg)
        self.assertEqual(len(re.findall(r"^## ", self.texte("fr"), re.M)),
                         len(re.findall(r"^## ", self.texte("en"), re.M)))

    def test_il_ne_renvoie_pas_a_l_atelier(self):
        atelier = re.compile(r"\b(?:ADR|JA|[BDFJLT])-\d|fabrication|chess|Théo|delegate-lot|Opus|Sonnet|Haiku|Fable")
        for lg in ("fr", "en"):
            self.assertIsNone(atelier.search(self.texte(lg)), lg)

    def test_ses_commandes_sont_celles_du_moteur(self):
        """Le prompt d'une session programmée et celui à copier : chaque
        commande du skill, ses arguments remplis, est une commande que le
        moteur accepte."""
        from socle import cli

        for lg in ("fr", "en"):
            for _, commande in controles.commandes(self.texte(lg)):
                argv = commande.replace("ARG", "1").replace('"', "").split()
                self.assertEqual(argv[:3], ["python3", ".socle/socle", "handoff"], lg)
                self.assertIn(argv[3], ("write", "check"), lg)
                args = cli.analyseur()[0].parse_args(argv[2:])
                self.assertIs(args.f, cli.cmd_handoff, lg)
            self.assertIn("--scheduled", self.texte(lg))

    def test_les_deux_modes_et_leur_commutateur(self):
        self.lire({
            "fr": ["**Session programmée**, par défaut", "**Prompt à copier**",
                   "Le mode est celui que dit une consigne en vigueur ; sans elle, la session programmée.",
                   "L'humain en change en le disant : l'agent consigne sa parole en séance, lève la consigne "
                   "d'avant et écrit la nouvelle (`socle new directive`), avec son texte exact (skill "
                   "`socle-request`).",
                   "Passer au prompt à copier annule ce qui est programmé, la tâche supprimée (`delete_trigger`) "
                   "et la session créée archivée (`archive_session`), et le dit, avec le lien de chaque session "
                   "annulée."],
            "en": ["**Scheduled session**, by default", "**Prompt to copy**",
                   "The mode is the one a directive in force states; without one, the scheduled session.",
                   "The human changes it by saying so: the agent records their words in session, lifts the "
                   "previous directive and writes the new one (`socle new directive`), with its exact text (skill "
                   "`socle-request`).",
                   "Switching to the prompt to copy cancels what is scheduled, the task deleted (`delete_trigger`) "
                   "and the created session archived (`archive_session`), and says so, with the link of each "
                   "cancelled session."],
        })

    def test_le_moment_ses_seuils_et_les_bornes(self):
        self.lire({
            "fr": ["| Lot livré | tout de suite : la minute qui suit |",
                   "la remise à zéro de cette fenêtre, plus cinq minutes", "| la fin de l'attente |",
                   "Une session ne part que si le coût estimé de son lot tient dans ce qui reste de la fenêtre de "
                   "cinq heures, la marge du rangement comprise, et jamais sur une semaine au-delà de 75 %",
                   "quand le prochain lot n'a aucune tâche prête dans l'état",
                   "après deux lots menés sans message de l'humain, le lot en cours compris",
                   "quand la plateforme refuse de créer la session",
                   "0 si l'humain a écrit dans la session ; sinon, celle de sa passation, plus un."],
            "en": ["| Batch delivered | right away: the next minute |",
                   "the reset of that window, plus five minutes", "| the end of the wait |",
                   "A session starts only if its batch's estimated cost fits in what remains of the five-hour "
                   "window, the tidying-up margin included, and never on a week beyond 75%",
                   "when the next batch has no ready task in the state",
                   "after two batches run without a message from the human, the current batch included",
                   "when the platform refuses to create the session",
                   "0 if the human wrote in the session; otherwise, that of its handoff, plus one."],
        })

    def test_en_session_programmee_le_rangement_programme_la_session_neuve(self):
        """T-0081, T-0182 (D-0190) : le rangement, la passation écrite avec
        `--scheduled`, commitée, poussée et retrouvée par la garde, puis
        `create_session` et `create_trigger`, dans cet ordre et avec leurs
        paramètres, la tâche programmée envoyant son texte à elle ; rien ne
        se pousse après ; un appel en échec rend le prompt à copier."""
        for lg, ecrire, programmer, apres, repli, reveil in (
                ("fr", "## Écrire la passation", "## Programmer", "Plus rien ne se pousse ensuite",
                 "Si un appel échoue, la session créée s'archive, et le prompt à copier remplace la passation "
                 "programmée", "`prompt` « reprends — session programmée »"),
                ("en", "## Writing the handoff", "## Scheduling", "Nothing is pushed afterwards",
                 "If a call fails, the created session is archived, and the prompt to copy replaces the scheduled "
                 "handoff", "`prompt` \"resume — scheduled session\"")):
            texte = self.texte(lg)
            section = " ".join(texte.split(ecrire, 1)[1].split("\n## ", 1)[0].split())
            self.assertIn("`socle-batch`", section, lg)
            self.assertIn(apres, section, lg)
            ordre = [section.index(x) for x in ("`--scheduled`", "handoff write", "handoff check")]
            self.assertEqual(ordre, sorted(ordre), lg)
            self.assertLess(texte.index(ecrire), texte.index(programmer), lg)
            section = " ".join(texte.split(programmer, 1)[1].split("\n## ", 1)[0].split())
            self.assertIn(repli, section, lg)
            self.assertIn(reveil, section, lg)
            self.assertLess(section.index("`create_session`"), section.index("`create_trigger`"), lg)
            session = section.split("`create_session`", 1)[1].split("`create_trigger`", 1)[0]
            for parametre in ("`source_url`", "`source_revision`", "`outcome_branch`", "`model`", "`effort`",
                              "`title`", "`tags`"):
                self.assertIn(parametre, session, (lg, parametre))
            tache = section.split("`create_trigger`", 1)[1]
            for parametre in ("`name`", "`persistent_session_id`", "`run_once_at`", "`prompt`"):
                self.assertIn(parametre, tache, (lg, parametre))

    def test_la_passation_s_ecrit_avant_toute_fusion_et_le_guide_le_dit(self):
        """T-0194 (B-0356, D-0211) : la passation se pousse avant toute fusion
        de la pull request ; quand l'agent la fusionne, elle en est le dernier
        commit, et la branche que l'hébergeur supprime ne se repousse plus ;
        la session programmée part alors de la branche par défaut ; le guide
        le dit, avec ce que l'humain y gagne."""
        from socle import cli

        for lg, ecrire, phrases, guide, gain in (
                ("fr", "## Écrire la passation",
                 ("La passation se commite en dernier et se pousse, avant toute fusion de la pull request",
                  "quand l'agent la fusionne lui-même, elle en est le dernier commit, `--waiting` disant la "
                  "fusion à venir",
                  "la branche, que l'hébergeur supprime, ne se repousse plus",
                  "un commit nécessaire après, avant la fusion, réécrit la passation"),
                 "HELP.md", "aucune branche de session ne vous reste à supprimer"),
                ("en", "## Writing the handoff",
                 ("The handoff is committed last and pushed, before any merge of the pull request",
                  "when the agent merges it itself, the handoff is its last commit, `--waiting` stating the "
                  "merge to come",
                  "the branch, which the host deletes, is not pushed again",
                  "a commit needed later, before the merge, rewrites the handoff"),
                 "HELP.en.md", "no session branch is left for you to delete")):
            texte = self.texte(lg)
            section = " ".join(texte.split(ecrire, 1)[1].split("\n## ", 1)[0].split())
            for phrase in phrases:
                self.assertIn(phrase, section, (lg, phrase))
            self.assertLess(section.index(phrases[0]), section.index("handoff check"), lg)
            aide = " ".join((Path(cli.__file__).parent / guide).read_text(encoding="utf-8").split())
            self.assertIn(gain, aide, guide)
            depart = {"fr": "`source_revision` la branche de travail, ou la branche par défaut quand la fusion "
                            "l'a supprimée ; `outcome_branch` la branche de travail",
                      "en": "`source_revision` the work branch, or the default branch when the merge deleted "
                            "it; `outcome_branch` the work branch"}[lg]
            self.assertIn(depart, " ".join(texte.split()), lg)

    def test_apres_le_retrait_de_la_passation_l_agent_supprime_la_branche_d_avant(self):
        """T-0192 (B-0351, ADR-0114) : le retrait de la passation poussé, la
        branche de la session d'avant est contenue dans la sienne ; l'agent
        la supprime."""
        for lg, (retrait, commande) in {
                "fr": ("son premier commit retire la passation, poussé aussitôt",
                       "puis `python3 .socle/socle prune-branches` supprime la branche de la session d'avant, que "
                       "la sienne contient désormais"),
                "en": ("its first commit removes the handoff, pushed at once",
                       "then `python3 .socle/socle prune-branches` deletes the previous session's branch, which its "
                       "own now contains")}.items():
            texte = " ".join(self.texte(lg).split())
            self.assertIn(commande, texte, lg)
            self.assertLess(texte.index(retrait), texte.index(commande), lg)

    def test_la_garde_la_pull_request_voir_et_arreter_et_l_ancienne_session(self):
        self.lire({
            "fr": ["Sur un premier message qui demande de reprendre ou de continuer le travail, quelle qu'en soit "
                   "la forme (« reprends », « continue », « reprends les travaux »), ou sur celui de la tâche "
                   "programmée, l'agent lance `git fetch --prune origin`, puis la garde sans argument.",
                   "ne fait rien d'autre que le dire",
                   "son premier commit retire la passation, poussé aussitôt",
                   "Sans passation, elle fait ce que fait une session neuve, et le dit dans son premier message.",
                   "continue la pull request ouverte de sa branche sans la demander : elle devient la sienne.",
                   "Elle la fusionne si la politique le permet à l'agent",
                   "en écrivant « arrête » dans la session qui l'a programmée",
                   "ne l'annule qu'à sa demande",
                   "Elle le dit en une ligne et ne fait rien d'autre.",
                   "Les réveils de `socle-resume` restent, dans les deux modes"],
            "en": ["On a first message that asks to resume or continue the work, whatever its form (\"resume\", "
                   "\"continue\", \"pick the work back up\"), or on the scheduled task's, the agent runs `git fetch "
                   "--prune origin`, then the guard without arguments.",
                   "does nothing else but say so",
                   "its first commit removes the handoff, pushed at once",
                   "Without a handoff, it does what a new session does, and says so in its first message.",
                   "continues the open pull request of its branch without asking: it becomes its own.",
                   "It merges it if the policy allows the agent to",
                   "by writing \"stop\" in the session that scheduled it",
                   "cancels it only at their request",
                   "It says so in one line and does nothing else.",
                   "The wake-ups of `socle-resume` remain, in both modes"],
        })

    def test_les_instructions_et_le_guide_le_disent(self):
        """Le gabarit d'`AGENTS.md` nomme le skill et donne à la session d'une
        passation acceptée la pull request ouverte ; le guide dit les deux
        modes, comment en changer, et la commande."""
        from socle import cli
        from socle.templates import gabarit

        for lg, skill, exception, reprise, guide, phrases in (
                ("fr", "`socle-handoff` (passer la main à une session neuve",
                 "partie d'une passation que sa garde accepte, elle y continue, et cette pull request "
                 "devient la sienne.",
                 "Un premier message qui demande de reprendre ou de continuer, quelle qu'en soit la forme "
                 "(« reprends »), cherche d'abord la passation : le skill `socle-handoff`.", "HELP.md",
                 ("**L'enchaînement des sessions.**", "la **session programmée**", "Le **prompt à copier**",
                  "Pour changer de mode, dites-le à l'agent", "`python3 .socle/socle handoff write`",
                  "`python3 .socle/socle handoff check`")),
                ("en", "`socle-handoff` (handing over to a new session",
                 "started from a handoff that its guard accepts, it continues on it, and that pull request "
                 "becomes its own.",
                 "A first message that asks to resume or continue, whatever its form (\"resume\"), first looks "
                 "for the handoff: the `socle-handoff` skill.", "HELP.en.md",
                 ("**Chaining sessions.**", "the **scheduled session**", "The **prompt to copy**",
                  "To change the mode, tell the agent", "`python3 .socle/socle handoff write`",
                  "`python3 .socle/socle handoff check`"))):
            agents = " ".join(gabarit("AGENTS.md", lg).split())
            self.assertIn(skill, agents, lg)
            self.assertIn(exception, agents, lg)
            self.assertIn(reprise, agents, lg)
            texte = " ".join((Path(cli.__file__).parent / guide).read_text(encoding="utf-8").split())
            for phrase in phrases:
                self.assertIn(phrase, texte, (lg, phrase))


class TestLaRevue(unittest.TestCase):
    """B-0214 : le skill de la revue, posé dans les deux langues, donne au
    relecteur son modèle (D-0117), trie les constats selon la règle 1 de
    D-0112, et dit ce que donne le dossier et où s'écrit le modèle de
    menace, de la même manière que les instructions et FORMAT.md
    (ADR-0073)."""

    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n"})

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def texte(self, lg: str) -> str:
        installeur.poser_skills(self.racine, lg)
        return (self.racine / installeur.SKILLS / "socle-review" / "SKILL.md").read_text(encoding="utf-8")

    def test_il_est_pose_sous_son_budget_et_passe_ses_controles(self):
        for lg in ("fr", "en"):
            texte = self.texte(lg)
            self.assertTrue(texte.startswith("---\nname: socle-review\n"), lg)
            self.assertLessEqual(len(texte.encode("utf-8")), 10000, lg)
            self.assertEqual(juger(self.racine), {"skills.contrat": [], "skills.commandes": []}, lg)

    def test_le_relecteur_recoit_le_modele_le_plus_capable_a_son_lancement(self):
        """D-0117 : explicitement, à son lancement, le plus capable jusqu'à
        Opus, jamais un moindre que celui qui a implémenté ; Fable sur la
        demande de l'humain seule ; découplé du modèle de la session."""
        attendus = {
            "fr": ("du modèle de la session", [
                "Il reçoit explicitement à son lancement (`model`) le modèle le plus capable disponible jusqu'à "
                "Opus, jamais un moindre que celui qui a implémenté le lot",
                "quel que soit celui de la session, que la règle du modèle de `socle-batch` peut faire moins coûteux",
                "Fable, s'il est disponible, seulement si l'humain le demande"]),
            "en": ("of the session's model", [
                "It receives explicitly at launch (`model`) the most capable model available up to Opus, never a "
                "lesser one than the one that implemented the batch",
                "whatever the session's, which the model rule of `socle-batch` may make cheaper",
                "Fable, if available, only if the human asks for it"]),
        }
        for lg, (ancien, phrases) in attendus.items():
            texte = " ".join(self.texte(lg).split())
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)
            self.assertNotIn(ancien, texte, lg)

    def test_un_lot_implemente_sur_fable_fait_demander_fable_pour_le_relecteur(self):
        """T-0015 (B-0243, D-0119) : le lot, pas la session qui orchestre ;
        l'humain répond avant la revue."""
        attendus = {
            "fr": "Un lot implémenté sur Fable (le lot, pas la session qui orchestre) fait demander à l'humain, "
                  "avant la revue, s'il veut aussi Fable pour le relecteur.",
            "en": "A batch implemented on Fable (the batch, not the orchestrating session) has the human asked, "
                  "before the review, whether they also want Fable for the reviewer.",
        }
        for lg, phrase in attendus.items():
            self.assertIn(phrase, " ".join(self.texte(lg).split()), lg)

    def test_il_dit_quand_donner_le_dossier_court(self):
        """B-0288 : un petit lot qui ne touche ni un garde-fou ni un format
        que d'autres parties du projet lisent reçoit le dossier court ; tout
        autre, le dossier complet."""
        attendus = {
            "fr": ["Un petit lot (moins de 150 lignes de code et de tests) qui ne touche ni un garde-fou ni un "
                   "format que d'autres parties du projet lisent reçoit le dossier court, `--short` : le diff et "
                   "les critères de ses tâches, à juger sans explorer au-delà des fichiers touchés ; tout autre "
                   "lot, le dossier complet.",
                   "`--short` refuse un lot qui touche un chemin que la politique protège ou que les garde-fous "
                   "déclarent."],
            "en": ["A small batch (under 150 lines of code and tests) that touches neither a guardrail nor a format "
                   "other parts of the project read gets the short brief, `--short`: the diff and its tasks' "
                   "criteria, to judge without exploring beyond the files touched; any other batch, the full brief.",
                   "`--short` refuses a batch that touches a path the policy protects or the guardrails declare."],
        }
        for lg, phrases in attendus.items():
            texte = " ".join(self.texte(lg).split())
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)

    def test_le_relecteur_recoit_le_chemin_du_dossier_pas_son_texte(self):
        """B-0277, T-0062 : le dossier n'entre pas dans la conversation qui
        orchestre ; le relecteur reçoit son chemin, avec la consigne de le
        lire en entier et de le suivre tel quel."""
        attendus = {
            "fr": ("dont le seul message est ce dossier",
                   "la sortie de `socle review` s'écrit dans un fichier hors du dépôt, et le seul message du "
                   "relecteur (sous Claude Code, un sous-agent, outil `Agent`) donne son chemin, avec la consigne "
                   "de le lire en entier et de le suivre tel quel."),
            "en": ("whose only message is this brief",
                   "the output of `socle review` is written to a file outside the repository, and the reviewer's "
                   "only message (under Claude Code, a subagent, the `Agent` tool) gives its path, with the "
                   "instruction to read it in full and follow it as is."),
        }
        for lg, (ancien, phrase) in attendus.items():
            texte = " ".join(self.texte(lg).split())
            self.assertIn(phrase, texte, lg)
            self.assertNotIn(ancien, texte, lg)

    def test_la_passe_ecrite_se_commite_et_le_dossier_se_produit_sur_la_branche_d_integration(self):
        """T-0055 : écrite sans commit là où `socle review` tourne, la passe se
        perdait, et la suivante récrivait « Passe 1 »."""
        attendus = {
            "fr": ("Commiter la passe écrite, et ce qu'on y consigne : sinon, elle se perd là où `socle review` a "
                   "tourné.",),
            "en": ("Commit the written pass, and what is recorded in it: otherwise, it is lost where `socle review` "
                   "ran.",),
        }
        for lg, phrases in attendus.items():
            texte = " ".join(self.texte(lg).split())
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)
        atelier = Path(__file__).resolve().parent.parent / ".claude/skills/delegate-lot/SKILL.md"
        self.assertIn("Le dossier du lot se produit sur la branche d'intégration, jamais dans le worktree d'un "
                      "sous-agent, où la passe que `socle review` écrit dans le lot se perdrait : la passe s'y "
                      "commite", " ".join(atelier.read_text(encoding="utf-8").split()))

    def test_les_constats_le_dossier_et_le_modele_de_menace_d_une_seule_maniere(self):
        """D-0112, règle 1 : ce qui va au backlog, ce qui s'écarte ; ADR-0073 :
        le modèle de menace dans la section du sujet ou dans la décision
        qu'il cite, et le dossier donne les décisions que le lot écrit."""
        from socle.templates import DOSSIER

        attendus = {
            "fr": ["**Pour le backlog** : un constat qui ne bloque pas va au backlog seulement s'il est important et "
                   "a été vu en usage réel (une session, une CI, un message de l'humain le montre), ou si son effet "
                   "serait irréversible",
                   "**Écarté** : tout autre constat, dont un cas imaginé et jamais vu, une légère gêne que l'agent "
                   "règle lui-même (ce que rattrape un contrôle, la CI ou une erreur qu'il voit aussitôt), un "
                   "contournement hors du modèle de menace, et un constat infondé. En cas de doute, il s'écarte. Une ligne du récap dit pourquoi chacun est écarté ; il revient s'il est vu "
                   "en usage réel.",
                   "dans sa section `## Modèle de menace` ou dans la décision qu'il cite",
                   "les décisions et les demandes que le lot écrit, puis celles que ses entrées citent"],
            "en": ["**For the backlog**: a finding that does not block goes to the backlog only if it matters and has "
                   "been seen in real use (a session, a CI run, a message from the human shows it), or if its effect "
                   "would be irreversible",
                   "**Dismissed**: any other finding, including a case imagined and never seen",
                   "One line of the recap says why each is dismissed; it comes back if seen in real use.",
                   "in its `## Threat model` section or in the decision it cites",
                   "the decisions and requests the batch writes, then those its entries cite"],
        }
        for lg, phrases in attendus.items():
            texte = " ".join(self.texte(lg).split())
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)
        instructions = {
            "AGENTS.md": ["(sa section `## Modèle de menace`, ou la décision qu'il cite)",
                          "un autre va au backlog s'il est important et vu en usage réel, ou d'effet irréversible ; "
                          "sinon il s'écarte, et revient s'il est vu"],
            "AGENTS.en.md": ["(its `## Threat model` section, or the decision it cites)",
                             "another goes to the backlog if it matters and was seen in real use, or if its effect "
                             "would be irreversible; otherwise it is dismissed, and comes back if seen"],
            "../FORMAT.md": ["dans une section `## Modèle de menace` (`## Threat model` en anglais) ou dans la "
                             "décision qu'il cite"],
        }
        for nom, phrases in instructions.items():
            texte = " ".join((DOSSIER / nom).read_text(encoding="utf-8").split())
            for phrase in phrases:
                self.assertIn(phrase, texte, nom)


class TestLOrganisationProportionnee(unittest.TestCase):
    """T-0183 (B-0352, D-0194, D-0195) : les skills, le gabarit d'`AGENTS.md`
    et le guide disent les sections 1 à 4 de la page validée : la session
    unité de budget, la question d'intention avant la spécification, la
    revue selon le risque, le sous-agent quand il paie et la relecture à
    froid d'une demande longue seule."""

    ATTENDUS = {
        "fr": {
            "socle-batch": ["Un lot réunit ce qui se relit ensemble", "le former une fois, par thème",
                            "**La session est l'unité de budget.** À la fin d'un lot, elle enchaîne le suivant si "
                            "son coût estimé tient dans ce qui reste de la fenêtre de cinq heures et de la semaine, "
                            "la marge du rangement comprise, et si sa conversation reste sous 150 000 jetons de "
                            "contexte, deux lots au plus sans message de l'humain ; sinon, elle change de session.",
                            "Fichiers temporaires : dans le dossier temporaire commun, nommés de l'identifiant de "
                            "ta tâche."],
            "socle-request": ["## Une conception à trancher",
                              "pose d'abord sa question d'intention, dans la conversation, en quelques lignes : le "
                              "besoin tel que l'agent le comprend, le choix qui reste, sa recommandation ; la "
                              "réponse se consigne en séance",
                              "Puis sa spécification et son code se font dans le même lot, la spécification "
                              "d'abord. Ce qui reste coûteux à défaire va ensuite en demande, courte",
                              "Une demande qui passe la moitié de son budget (`new request` le donne) se fait "
                              "relire à froid avant d'être poussée ; une demande plus courte, ou qui ne fait "
                              "qu'approuver des fichiers protégés par leurs empreintes, part sans elle."],
            "socle-review": ["Une revue adversariale, avant le push, pour un lot qui la justifie : il pose ou change "
                             "un garde-fou (un contrôle, un refus, un hook), un format que d'autres parties du projet "
                             "lisent (la mémoire, le contrat d'un adaptateur, la CI), ou plus de 150 lignes de code "
                             "et de tests.",
                             "l'agent le relit lui-même, sur le dossier court (plus bas), contre les critères de ses "
                             "tâches, et le récap le dit.",
                             "Une spécification, de la documentation ou de la mémoire seules n'ont pas de revue "
                             "adversariale : l'humain en juge l'intention."],
            "socle-handoff": ["Une session enchaîne les lots que son budget permet"],
        },
        "en": {
            "socle-batch": ["A batch gathers what is reviewed together", "form it once, by theme",
                            "**The session is the budget unit.** At the end of a batch, it chains the next one if "
                            "its estimated cost fits in what remains of the five-hour window and of the week, the "
                            "tidying-up margin included, and if its conversation stays under 150,000 tokens of "
                            "context, two batches at most without a message from the human; otherwise, it changes "
                            "sessions.",
                            "Temporary files: in the shared temporary directory, named with your task's identifier."],
            "socle-request": ["## A design to settle",
                              "first asks its question of intent, in the conversation, in a few lines: the need as "
                              "the agent understands it, the choice that remains, its recommendation; the answer "
                              "is recorded in session",
                              "Then its specification and its code are done in the same batch, the specification "
                              "first. What remains costly to undo then goes into a request, a short one",
                              "A request beyond half its budget (`new request` gives it) is read cold before being "
                              "pushed; a shorter request, or one that only approves protected files by their "
                              "fingerprints, leaves without it."],
            "socle-review": ["An adversarial review, before the push, for a batch that warrants it: it adds or "
                             "changes a guardrail (a check, a refusal, a hook), a format that other parts of the "
                             "project read (the memory, an adapter's contract, the CI), or more than 150 lines of "
                             "code and tests.",
                             "the agent rereads itself, on the short brief (below), against its tasks' criteria, "
                             "and the recap says so.",
                             "A specification, documentation or memory alone get no adversarial review: the human "
                             "judges their intent."],
            "socle-handoff": ["A session chains the batches its budget allows"],
        },
    }
    INSTRUCTIONS = {
        "fr": ["pose d'abord sa question d'intention, en quelques lignes, dans la conversation ; sa spécification "
               "et son code se font ensuite dans le même lot.",
               "à la fin du lot, il enchaîne le suivant si la session le permet",
               "Avant le push d'un lot qui pose ou change un garde-fou, un format que d'autres parties lisent, ou "
               "plus de 150 lignes de code et de tests, il le fait relire par un relecteur sans contexte",
               "un autre lot, il le relit lui-même (le skill `socle-review`)."],
        "en": ["first asks its question of intent, in a few lines, in the conversation; its specification and its "
               "code are then done in the same batch.",
               "at the end of the batch, it chains the next one if the session allows it",
               "Before the push of a batch that adds or changes a guardrail, a format other parts read, or more "
               "than 150 lines of code and tests, it has it reviewed by a reviewer without context",
               "another batch, it rereads itself (the `socle-review` skill)."],
    }
    GUIDE = {
        "HELP.md": ["**L'enchaînement des sessions.** La session est l'unité de budget",
                    "150 000 jetons de contexte", "deux lots au plus sans message de votre part",
                    "**La question d'intention.**",
                    "Une spécification, de la documentation ou de la mémoire seules n'ont pas de revue",
                    "Une demande longue, au-delà de la moitié de son budget"],
        "HELP.en.md": ["**Chaining sessions.** The session is the budget unit",
                       "150,000 tokens of context", "two batches at most without a message from you",
                       "**The question of intent.**",
                       "A specification, documentation or memory alone get no review",
                       "A long request, beyond half its budget"],
    }
    RETIRES = {"fr": ["Un lot par session", "15 %", "qu'une petite tâche", "ne se reprend pas",
                      "une spécification se soumet avant son code"],
               "en": ["One batch per session", "15%", "only a small task", "is not resumed",
                      "a specification is submitted before its code"]}

    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n"})

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def test_les_skills_disent_les_regles_de_la_page_validee(self):
        for lg, skills in self.ATTENDUS.items():
            installeur.poser_skills(self.racine, lg)
            for nom, phrases in skills.items():
                texte = " ".join((self.racine / installeur.SKILLS / nom / "SKILL.md").read_text(
                    encoding="utf-8").split())
                for phrase in phrases:
                    self.assertIn(phrase, texte, (lg, nom))
                for avant in self.RETIRES[lg]:
                    self.assertNotIn(avant, texte, (lg, nom, avant))

    def test_les_instructions_et_le_guide_les_disent(self):
        from socle import cli
        from socle.templates import gabarit

        for lg, phrases in self.INSTRUCTIONS.items():
            agents = " ".join(gabarit("AGENTS.md", lg).split())
            for phrase in phrases:
                self.assertIn(phrase, agents, lg)
            for avant in self.RETIRES[lg]:
                self.assertNotIn(avant, agents, (lg, avant))
        for nom, phrases in self.GUIDE.items():
            texte = " ".join((Path(cli.__file__).parent / nom).read_text(encoding="utf-8").split())
            for phrase in phrases:
                self.assertIn(phrase, texte, nom)
            self.assertNotIn("un lot par session" if nom == "HELP.md" else "one batch per session", texte.lower())


class TestLaPlaceDesReglesSuivantes(unittest.TestCase):
    """T-0206 (B-0354, D-0218) : les skills du produit et la section du socle
    d'`AGENTS.md`, chargés en entier à chaque usage, gardent leur plafond et
    une marge pour une règle de plus ; ce qui justifiait une règle sans la
    dire est passé au guide, « Pourquoi ces règles », et n'est plus dans le
    texte qu'il justifiait. Le plafond des skills relevé à 10 000 octets
    (D-0223, D-0224), chacun a sa marge."""

    MARGE = 600
    # Les skills qui n'ont pas encore leur marge : aucun depuis D-0224.
    # L'ensemble ne fait que rétrécir : un skill qui atteint sa marge en
    # sort, le test le dit.
    PAS_ENCORE: set[tuple[str, str]] = set()
    # Mot pour mot, d'où chacun est sorti ; la règle qu'il justifiait reste.
    SORTIS = {
        "fr": {
            "AGENTS.md": ["(la session a démarré hors de la racine du projet ; `socle state` le dit en tête, et le "
                          "hook avant commit refuse alors le commit)", "un compactage peut la perdre",
                          "où l'humain lit un texte brut sans liens à suivre (le hook le refuse)",
                          "la CI ne la juge pas aux envois", "(le hook `Stop` le vérifie)",
                          "le hook `Stop` refuse de conclure sans les deux lignes",
                          "l'humain lit dans la conversation ou sur GitHub, pas dans le conteneur de l'agent",
                          "le hook les refuse", "le hook de l'agent le refuse sur le dépôt du projet, et la CI "
                          "exécute tout", "de l'agent : le hook le refuse"],
            "socle-batch": ["une fois poussées, une décision et une entrée de journal ne se réécrivent plus",
                            "la ligne « CI » de l'état suit la tête"],
            "socle-resume": ["Une limite d'usage, sur cinq heures ou sept jours, coupe la session jusqu'au message "
                             "suivant de l'humain", "il tirerait aussitôt", "date d'une fenêtre close",
                             "refusé, ce tour se reprend à la levée", "c'est ce qui le fait reprendre",
                             "relancé sur le même arbre, il laisse conclure",
                             "L'humain arrête tout en écrivant « arrête » dans la session, ou supprime les réveils "
                             "de la liste des tâches programmées de son compte (claude.ai/code/routines)."],
            "socle-request": ["Une demande est lue quand le contexte est perdu : elle se suffit à elle-même.",
                              "ne comptent pas dans le budget de la demande", "l'humain ne la voit plus en attente",
                              "l'humain doit avoir pu la lire", "l'état ne la dit plus alors à réécrire",
                              "sans lui, la décision ne garde que la question et la réponse, et le contenu se perd"],
            "socle-handoff": ["d'un compte comme d'un autre",
                              "le mode de qui a plusieurs comptes ou veut garder la main",
                              "sans quoi la session neuve n'a pas où pousser",
                              "La session créée paraît aussitôt dans la liste des sessions de l'humain, sous son "
                              "titre, prête à relire tant qu'elle attend son réveil.",
                              "une session coupée avant d'avoir rangé reprend à la levée"],
        },
        "en": {
            "AGENTS.md": ["(the session started outside the project root; `socle state` says so at the top, and "
                          "the pre-commit hook then refuses the commit)", "a compaction may lose it",
                          "where the human reads raw text with no links to follow (the hook refuses it)",
                          "the CI does not judge it on push", "(the `Stop` hook checks it)",
                          "the `Stop` hook refuses to conclude without the two lines",
                          "the human reads in the conversation or on GitHub, not in the agent's container",
                          "the hook refuses them", "the agent's hook refuses it on the project's repository, and "
                          "the CI runs everything", "question widget: the hook refuses it"],
            "socle-batch": ["once pushed, a decision and a journal entry are no longer rewritten",
                            "the \"CI\" line of the state follows the head"],
            "socle-resume": ["A usage limit of the account, over five hours or seven days, cuts the session off; "
                             "the agent then resumes only at the human's next message", "it would fire at once",
                             "belongs to a closed window", "refused, that turn resumes when the limit lifts",
                             "that is what makes it resume", "relaunched on the same tree, it lets the turn conclude",
                             "The human stops everything by writing \"stop\" in the session, or deletes the "
                             "wake-ups from the list of scheduled tasks of their account (claude.ai/code/routines)."],
            "socle-request": ["A request is read once the context is lost: it stands on its own.",
                              "do not count in the request's budget", "the human no longer sees it pending",
                              "the human must have been able to read it", "the state then no longer says to rewrite it",
                              "without it, the decision keeps only the question and the answer, and the content is "
                              "lost"],
            "socle-handoff": ["from one account or another",
                              "the mode of whoever has several accounts or wants to keep control",
                              "without which the new session has nowhere to push",
                              "The created session appears at once in the human's list of sessions, under its "
                              "title, ready for review while it waits for its wake-up.",
                              "a session cut off before tidying up resumes when the limit lifts"],
        },
    }

    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n"})
        self.atelier = Path(__file__).resolve().parent.parent
        self.budgets = config.Projet.charger(self.atelier).gf("budgets", defaut={})

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def section(self, lg: str) -> str:
        """L'`AGENTS.md` de ce dépôt, sa partie propre gardée, la section du
        socle telle que la pose l'installeur dans cette langue."""
        (self.racine / "AGENTS.md").write_text((self.atelier / "AGENTS.md").read_text(encoding="utf-8"),
                                               encoding="utf-8")
        (self.racine / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            installeur._instructions(self.racine, "engine", lg)
        return (self.racine / "AGENTS.md").read_text(encoding="utf-8")

    def test_chaque_skill_du_produit_laisse_sa_marge_sous_son_plafond(self):
        plafond = self.budgets[".claude/skills/*/SKILL.md"]["max_bytes"]
        for lg in ("fr", "en"):
            installeur.poser_skills(self.racine, lg)
            skills = sorted((self.racine / installeur.SKILLS).glob("socle-*/SKILL.md"))
            self.assertEqual(len(skills), 6, lg)
            for f in skills:
                marge = plafond - len(f.read_bytes())
                with self.subTest(langue=lg, skill=f.parent.name, marge=marge):
                    if (lg, f.parent.name) in self.PAS_ENCORE:
                        self.assertLess(marge, self.MARGE, "il a sa marge : le retirer de PAS_ENCORE")
                        self.assertGreaterEqual(marge, 0)
                    else:
                        self.assertGreaterEqual(marge, self.MARGE)

    def test_la_section_du_socle_laisse_sa_marge_sous_le_plafond_de_ce_depot(self):
        plafond = self.budgets["AGENTS.md"]["max_bytes"]
        for lg in ("fr", "en"):
            texte = self.section(lg)
            self.assertIn(config.DEBUT_SOCLE, texte, lg)
            self.assertTrue(texte.startswith("# memory"), lg)
            marge = plafond - len(texte.encode("utf-8"))
            self.assertGreaterEqual(marge, self.MARGE, (lg, marge))

    def test_chaque_passage_sorti_se_lit_au_guide_et_plus_dans_son_texte(self):
        from socle import cli
        from socle.templates import gabarit

        for lg, textes in self.SORTIS.items():
            guide = " ".join((Path(cli.__file__).parent / ("HELP.md" if lg == "fr" else "HELP.en.md")).read_text(
                encoding="utf-8").split())
            installeur.poser_skills(self.racine, lg)
            for nom, passages in textes.items():
                source = (gabarit(nom, lg) if nom == "AGENTS.md" else
                          (self.racine / installeur.SKILLS / nom / "SKILL.md").read_text(encoding="utf-8"))
                source = " ".join(source.split()).lower()
                for passage in passages:
                    p = " ".join(passage.split()).lower()
                    with self.subTest(langue=lg, texte=nom, passage=passage):
                        self.assertTrue(p in guide.lower(), "absent du guide")
                        self.assertFalse(p in source, "encore dans le texte qu'il justifiait")


class TestRefusBash(unittest.TestCase):
    def test_le_meme_jugement_que_le_hook(self):
        projet = config.Projet.charger(Path(__file__).resolve().parent.parent)
        self.assertIsNone(hooks.refus_bash(projet, "git status\npython3 -m unittest"))
        self.assertIn("contourne les hooks du projet", hooks.refus_bash(projet, "git commit -q --no-verify -m x"))
        self.assertIn("répond jamais à la place de l'humain",
                      hooks.refus_bash(projet, "python3 .socle/socle answer D-0001 valider"))


if __name__ == "__main__":
    unittest.main()
