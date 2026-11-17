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
        self.assertEqual(sorted(controles.DU_SOCLE), ["socle-batch", "socle-private-memory", "socle-request",
                                                      "socle-resume", "socle-review"])
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
                         ["skills du socle posés dans .claude/skills : socle-batch, socle-private-memory, "
                          "socle-request, socle-resume, socle-review"])
        texte = (self.racine / ".claude/skills/socle-request/SKILL.md").read_text()
        self.assertIn("description: Write a request for a human decision", texte)
        self.assertEqual(juger(self.racine), {"skills.contrat": [], "skills.commandes": []})


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

    def test_un_sous_agent_ne_touche_a_aucun_reveil(self):
        for lg, regle in (("fr", "Un sous-agent ne touche à aucun réveil"), ("en", "A subagent\ntouches no wake-up")):
            self.assertIn(regle, self.lire(lg), lg)


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
            self.assertLessEqual(len(texte.encode("utf-8")), 8000, lg)
            self.assertEqual(juger(self.racine), {"skills.contrat": [], "skills.commandes": []}, lg)

    def test_il_ne_renvoie_pas_a_l_atelier(self):
        atelier = re.compile(r"\b(?:ADR|[BDFJ])-\d|fabrication|chess|Théo|delegate-lot|Opus|Sonnet|Haiku|Fable")
        for lg in ("fr", "en"):
            self.assertIsNone(atelier.search(self.texte(lg)), lg)

    def test_il_dit_la_consommation_le_changement_de_session_et_l_apres_fusion(self):
        """B-0220 : après la fusion, rien ne se pousse sans travail neuf ;
        le chantier actif et le journal s'écrivent avant."""
        attendus = {
            "fr": ["deux à la fois au plus", "75 %", "85 %", "60 % de la fenêtre de cinq heures",
                   "Un lot par session", "git format-patch", "prompt de la suivante",
                   "Le chantier actif et le journal s'écrivent avant la fusion",
                   "ne se pousse qu'avec le premier commit du lot suivant", "**Sans sous-agents**"],
            "en": ["two at a time at most", "75%", "85%", "60% of the five-hour window",
                   "One batch per session", "git format-patch", "prompt of the next one",
                   "The active work and the journal are written before the merge",
                   "is pushed only with the first commit of the next batch", "**Without subagents**"],
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
                   "le demande à l'humain", "`/compact`", "à la fin d'un lot si l'humain garde la session",
                   "avant toute attente qui peut passer l'heure sans changer de session",
                   "Près d'une limite, le seuil plus haut prime : changer de session",
                   "Après la pause, il est trop tard",
                   "celui que demande la qualité du travail, jamais un moindre pour tenir une limite",
                   "une limite retarde un lot, elle ne l'allège pas",
                   "Entre ceux qui le font aussi bien, celui qui consomme le moins de la limite par jeton",
                   "l'humain choisit celui de la session, sur le conseil de l'agent",
                   "Celui que fixent les instructions du projet prime",
                   "Un sous-agent reçoit le sien explicitement à son lancement"],
            "en": ["The agent does not compact by itself", "it writes the memory (active work, journal)",
                   "asks the human to", "`/compact`", "at the end of a batch if the human keeps the session",
                   "before any wait that may exceed an hour without changing sessions",
                   "Near a limit, the threshold above prevails: change sessions",
                   "After the pause, it is too late",
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
            self.assertLessEqual(len(texte.encode("utf-8")), 8000, lg)
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

    def test_les_constats_le_dossier_et_le_modele_de_menace_d_une_seule_maniere(self):
        """D-0112, règle 1 : ce qui va au backlog, ce qui s'écarte ; ADR-0073 :
        le modèle de menace dans la section du sujet ou dans la décision
        qu'il cite, et le dossier donne les décisions que le lot écrit."""
        from socle.templates import DOSSIER

        attendus = {
            "fr": ["**Pour le backlog** : un constat qui ne bloque pas va au backlog s'il peut se produire dans "
                   "l'usage normal du projet, ou si rien ne rattrape ensuite son effet",
                   "**Écarté** : un constat exotique (un geste rare, une forme qu'on n'écrit que pour contourner, un "
                   "cas jamais reproduit) dont l'effet est rattrapé, par un contrôle, la CI ou une erreur que "
                   "l'agent voit aussitôt ; et un constat infondé. Une ligne du récap dit pourquoi chacun est écarté.",
                   "dans sa section `## Modèle de menace` ou dans la décision qu'il cite",
                   "les décisions et les demandes que le lot écrit, puis celles que ses sujets citent"],
            "en": ["**For the backlog**: a finding that does not block goes to the backlog if it can occur in the "
                   "project's normal use, or if nothing catches its effect afterwards",
                   "**Dismissed**: an exotic finding", "One line of the recap says why each is dismissed.",
                   "in its `## Threat model` section or in the decision it cites",
                   "the decisions and requests the batch writes, then those its topics cite"],
        }
        for lg, phrases in attendus.items():
            texte = " ".join(self.texte(lg).split())
            for phrase in phrases:
                self.assertIn(phrase, texte, lg)
        instructions = {
            "AGENTS.md": ["(sa section `## Modèle de menace`, ou la décision qu'il cite)",
                          "un autre va au backlog s'il peut se produire dans l'usage normal du projet, ou si rien ne "
                          "rattrape ensuite son effet ; sinon, exotique et rattrapé, ou infondé, il s'écarte"],
            "AGENTS.en.md": ["(its `## Threat model` section, or the decision it cites)",
                             "another goes to the backlog if it can occur in the project's normal use, or if nothing "
                             "catches its effect afterwards; otherwise, exotic and caught, or unfounded, it is "
                             "dismissed"],
            "../FORMAT.md": ["dans une section `## Modèle de menace` (`## Threat model` en anglais) ou dans la "
                             "décision qu'il cite"],
        }
        for nom, phrases in instructions.items():
            texte = " ".join((DOSSIER / nom).read_text(encoding="utf-8").split())
            for phrase in phrases:
                self.assertIn(phrase, texte, nom)

    def test_une_forme_du_shell_qu_un_agent_n_ecrit_pas_s_ecarte_pour_la_liste(self):
        """D-0120, ADR-0082 : ni bloquante, même refusée avant le lot par
        accident, ni pour le backlog ; écartée, d'une ligne, pour la liste
        des formes connues que le hook ne juge pas."""
        attendus = {
            "fr": "**Une forme du shell qu'un agent n'écrit pas** dans son travail (ni vue dans une session "
                  "d'agent, ni dans un skill, ni dans une documentation courante), et qui échappe au hook de "
                  "l'agent : elle ne se classe pas bloquante, même refusée avant le lot par accident, ni pour le "
                  "backlog, quel qu'en soit l'effet. Elle s'écarte, et va d'une ligne à la liste des formes connues "
                  "que le hook ne juge pas, que tient le guide du socle (`python3 .socle/socle help`).",
            "en": "**A shell form an agent does not write** in its work (seen neither in an agent session, nor in "
                  "a skill, nor in current documentation), and that escapes the agent's hook: it is not classed as "
                  "blocking, even if refused before the batch by accident, nor for the backlog, whatever its "
                  "effect. It is dismissed, and goes in one line to the list of known forms the hook does not "
                  "judge, which the socle's guide keeps (`python3 .socle/socle help`).",
        }
        for lg, phrase in attendus.items():
            self.assertIn(phrase, " ".join(self.texte(lg).split()), lg)

    def test_dans_un_projet_equipe_la_forme_se_signale_au_depot_du_socle(self):
        """B-0270, T-0048 : dans un projet équipé, le guide est sous le moteur
        installé, protégé ; l'agent ne peut pas y inscrire la forme. Le skill
        la lui fait nommer au récap et proposer à l'humain de la signaler au
        dépôt du socle, qui tient la liste."""
        from socle import utils as outils

        with redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        projet = config.Projet.charger(self.racine)
        self.assertTrue(outils.correspond(f"{projet.chemins.moteur}/socle/HELP.md", projet.chemins_proteges()))
        attendus = {
            "fr": "Dans un projet équipé, ce guide est protégé : le récap nomme la forme, et « Pour toi » propose "
                  "de la signaler au dépôt du socle (https://github.com/theodubus/socle), qui tient la liste.",
            "en": "In an equipped project, this guide is protected: the recap names the form, and “For you” "
                  "suggests reporting it to the socle's repository (https://github.com/theodubus/socle), which "
                  "keeps the list.",
        }
        for lg, phrase in attendus.items():
            texte = " ".join(self.texte(lg).split())
            self.assertIn(phrase, texte, lg)
            self.assertLessEqual(len(self.texte(lg).encode("utf-8")), 8000, lg)


class TestRefusBash(unittest.TestCase):
    def test_le_meme_jugement_que_le_hook(self):
        projet = config.Projet.charger(Path(__file__).resolve().parent.parent)
        self.assertIsNone(hooks.refus_bash(projet, "git status\npython3 -m unittest"))
        self.assertIn("contourne les hooks du projet", hooks.refus_bash(projet, "git commit -q --no-verify -m x"))
        self.assertIn("répond jamais à la place de l'humain",
                      hooks.refus_bash(projet, "python3 .socle/socle answer D-0001 valider"))


if __name__ == "__main__":
    unittest.main()
