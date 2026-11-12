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
        self.assertEqual(sorted(controles.DU_SOCLE), ["socle-private-memory", "socle-request", "socle-resume",
                                                      "socle-review"])
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
                         ["skills du socle posés dans .claude/skills : socle-private-memory, socle-request, "
                          "socle-resume, socle-review"])
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


class TestRefusBash(unittest.TestCase):
    def test_le_meme_jugement_que_le_hook(self):
        projet = config.Projet.charger(Path(__file__).resolve().parent.parent)
        self.assertIsNone(hooks.refus_bash(projet, "git status\npython3 -m unittest"))
        self.assertIn("contourne les hooks du projet", hooks.refus_bash(projet, "git commit -q --no-verify -m x"))
        self.assertIn("répond jamais à la place de l'humain",
                      hooks.refus_bash(projet, "python3 .socle/socle answer D-0001 valider"))


if __name__ == "__main__":
    unittest.main()
