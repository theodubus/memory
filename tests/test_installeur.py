import io
import os
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from socle import config, context as contexte, checks_memory as controles_memoire, installer as installeur
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
CLAUDE = "# Projet\n\nLes instructions du projet, écrites avant le socle.\n"


def depot(fichiers: dict[str, str]) -> Path:
    racine = Path(tempfile.mkdtemp(prefix="socle-installeur-"))
    env = {**os.environ, "HOME": str(racine), "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True, env=env)
    for chemin, texte in fichiers.items():
        p = racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")
    return racine


def installer(racine: Path, adoption=True):
    with redirect_stdout(io.StringIO()):
        installeur.installer(racine, "python", "@essai", adoption=adoption, source=MOTEUR)


def erreurs_instructions(racine: Path) -> list[str]:
    ctx = contexte.Contexte(config.Projet.charger(racine), etage="agent")
    r = Rapport()
    controles_memoire.source_unique(ctx, r)
    return [c.message for c in r.erreurs("instructions.source-unique")]


class TestAdaptateur(unittest.TestCase):
    def test_un_adaptateur_maintenu_ou_un_fichier(self):
        texte, nom = installeur.charger_adaptateur("rust")
        self.assertEqual(nom, "rust")
        self.assertIn("cargo-mutants", texte)
        d = Path(tempfile.mkdtemp(prefix="socle-adaptateur-"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "maison.toml").write_text('name = "maison"\n', encoding="utf-8")
        self.assertEqual(installeur.charger_adaptateur(str(d / "maison.toml")), ('name = "maison"\n', "maison"))
        with self.assertRaises(SystemExit):
            installeur.charger_adaptateur("cobol")


class TestAdoption(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def test_claude_md_renomme_quand_rien_ne_le_lit(self):
        self.racine = depot({"CLAUDE.md": CLAUDE, "app.py": "print('ok')\n"})
        installer(self.racine)
        self.assertEqual((self.racine / "CLAUDE.md").read_text().strip(), "@AGENTS.md")
        agents = (self.racine / "AGENTS.md").read_text()
        self.assertIn("écrites avant le socle", agents)
        self.assertIn(installeur.DEBUT_SOCLE, agents)

    def test_claude_md_garde_quand_le_projet_le_lit(self):
        # Un projet dont un test lit CLAUDE.md par son nom.
        self.racine = depot({"CLAUDE.md": CLAUDE, "tests/test_doc.py": "open('CLAUDE.md').read()\n"})
        installer(self.racine)
        self.assertFalse((self.racine / "AGENTS.md").exists())
        claude = (self.racine / "CLAUDE.md").read_text()
        self.assertTrue(claude.startswith(CLAUDE.rstrip("\n")))
        self.assertIn(installeur.DEBUT_SOCLE, claude)
        self.assertIn('"CLAUDE.md" = { max_bytes =', (self.racine / ".socle/guardrails.toml").read_text())

    def test_claude_md_garde_fait_foi_seul(self):
        # B-0049, mesuré à R6 : le contrôle exigeait AGENTS.md, que
        # l'installeur n'avait pas posé, et le .gitignore y renvoyait.
        self.racine = depot({"CLAUDE.md": CLAUDE, "tests/test_doc.py": "open('CLAUDE.md').read()\n",
                             ".gitignore": "# Trace locale des hooks du socle (voir AGENTS.md)\n"})
        installer(self.racine)
        self.assertEqual(erreurs_instructions(self.racine), [])
        gitignore = (self.racine / ".gitignore").read_text()
        self.assertEqual(gitignore.count("# Trace locale des hooks du socle"), 1, gitignore)
        (self.racine / ".gitignore").unlink()
        installer(self.racine)
        self.assertIn("(voir CLAUDE.md)", (self.racine / ".gitignore").read_text())
        (self.racine / "CLAUDE.md").write_text(CLAUDE)  # sans la section du socle
        self.assertEqual(len(erreurs_instructions(self.racine)), 1)

    def test_relance_regenere_la_section_sans_la_dupliquer(self):
        self.racine = depot({"app.py": "print('ok')\n"})
        installer(self.racine, adoption=False)
        installer(self.racine, adoption=False)
        agents = (self.racine / "AGENTS.md").read_text()
        self.assertEqual(agents.count(installeur.DEBUT_SOCLE), 1)
        self.assertEqual((self.racine / "CLAUDE.md").read_text().strip(), "@AGENTS.md")


if __name__ == "__main__":
    unittest.main()


class TestRelance(unittest.TestCase):
    """B-0044, L1 : relancer l'installeur ne perd rien."""

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def test_relancee_depuis_le_projet_elle_garde_son_moteur(self):
        """La source était aussi la destination : supprimée avant la copie."""
        self.racine = depot({"app.py": "print('ok')\n"})
        installer(self.racine, adoption=False)
        with redirect_stdout(io.StringIO()) as flux:
            installeur.installer(self.racine, "python", "@essai", source=self.racine / ".socle/engine")
        self.assertTrue((self.racine / ".socle/engine/socle/cli.py").is_file())
        self.assertIn("moteur déjà en place", flux.getvalue())

    def test_un_claude_md_propre_au_projet_passe_dans_agents_md(self):
        """Il était remplacé par la seule ligne d'import dès qu'AGENTS.md existait."""
        self.racine = depot({"AGENTS.md": "# Projet\n", "CLAUDE.md": "Règle propre à Claude : répondre bref.\n"})
        installer(self.racine, adoption=False)
        self.assertEqual((self.racine / "CLAUDE.md").read_text().strip(), "@AGENTS.md")
        self.assertIn("Règle propre à Claude : répondre bref.", (self.racine / "AGENTS.md").read_text())

    def test_une_seconde_adoption_complete_la_liste(self):
        """Elle écrivait une seconde table `[adoption]` : les garde-fous ne se
        lisaient plus."""
        import tomllib

        self.racine = depot({"app.py": "print('ok')\n", "LISEZMOI.md": "Voir [la suite](absent.md).\n"})
        installer(self.racine)
        paragraphe = "Un long paragraphe recopié tel quel dans deux fichiers du projet, " * 4 + "\n"
        (self.racine / "a.md").write_text(paragraphe)
        (self.racine / "b.md").write_text(paragraphe)
        installer(self.racine)
        gf = tomllib.loads((self.racine / ".socle/guardrails.toml").read_text())
        self.assertEqual(sorted(gf["adoption"]["warn_only"]), ["docs.copie", "memoire.references"])

    def test_une_mise_a_jour_nomme_les_reglages_nouveaux_des_garde_fous(self):
        """B-0123 : les garde-fous du projet se gardent, et les réglages
        apparus dans le gabarit n'y arrivaient pas, sans un mot."""
        self.racine = depot({"app.py": "print('ok')\n"})
        installer(self.racine, adoption=False)
        gf = self.racine / ".socle/guardrails.toml"
        texte = gf.read_text()
        avant = texte.replace('# case_paths = ["docs/specs/*.cas.json"]\n', "")
        avant = avant.replace('[specs]\n', "").replace('# paths = ["docs/specs/*.md"]\n', "")
        gf.write_text(avant)
        with redirect_stdout(io.StringIO()) as flux:
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        sortie = flux.getvalue()
        self.assertIn("réglages du gabarit absents de .socle/guardrails.toml (2)", sortie)
        # Déclarés avant que ce moteur soit commité, le pilote les a vus pris pour un assouplissement.
        self.assertIn("une fois ce moteur commité", sortie)
        self.assertIn("`[tests] case_paths` — Les fichiers de cas", sortie)
        self.assertIn("`[specs] paths` — Les spécifications du projet", sortie)
        self.assertEqual(gf.read_text(), avant)
        # Écrits, même en commentaire, ils ne se signalent plus.
        gf.write_text(texte)
        with redirect_stdout(io.StringIO()) as flux:
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        self.assertNotIn("réglages du gabarit absents", flux.getvalue())

    def _deborder(self, nom: str) -> tuple[str, int, int, Path]:
        """Une section d'un moteur plus ancien, plus courte, dans `nom`, et un
        budget au plus juste : la mise à jour la fait grossir au-delà."""
        import re

        f = self.racine / nom
        texte = f.read_text(encoding="utf-8")
        debut, fin = texte.index("### Les skills"), texte.index("### Livrer le travail")
        f.write_text(texte[:debut] + texte[fin:], encoding="utf-8")
        avant = len(f.read_bytes())
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(re.sub(rf'^"{re.escape(nom)}" = \{{ max_bytes = \d+ \}}',
                             f'"{nom}" = {{ max_bytes = {avant + 10} }}', gf.read_text(), flags=re.M))
        with redirect_stdout(io.StringIO()) as flux:
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        return flux.getvalue(), avant, len(f.read_bytes()), gf

    def _budgets(self) -> list[tuple[str, str]]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent")
        r = Rapport()
        controles_memoire.budgets(ctx, r)
        return [(c.chemin, c.message) for c in r.erreurs()]

    def test_une_mise_a_jour_qui_fait_depasser_son_budget_a_agents_md_le_dit(self):
        """B-0129 : la section du socle grossit à la mise à jour, et le budget
        d'AGENTS.md, fixé au plus juste, ne peut que baisser. L'audit le
        disait rouge, avec pour remède « archiver dans le journal »."""
        self.racine = depot({"app.py": "print('ok')\n"})
        installer(self.racine, adoption=False)
        sortie, avant, apres, gf = self._deborder("AGENTS.md")
        self.assertGreater(apres, avant + 10)
        self.assertIn(f"!! AGENTS.md dépasse son budget : {apres} octets pour {avant + 10}, la section du socle, "
                      f"posée ou régénérée, ayant grossi de {apres - avant} ; resserrer la partie propre au projet",
                      sortie)
        self.assertIn("relever le budget par une demande validée, puisque le relever assouplit un garde-fou", sortie)
        # Le contrôle des budgets dit le même remède, et non d'archiver dans le journal.
        self.assertEqual(self._budgets(),
                         [("AGENTS.md", f"{apres} octets pour un budget de {avant + 10} (AGENTS.md) : resserrer la "
                                        "partie propre au projet, hors de la section du socle, ou relever le budget "
                                        "par une demande validée")])
        # Relancée sans que la section grossisse, elle ne l'en accuse pas.
        with redirect_stdout(io.StringIO()) as flux:
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        self.assertNotIn("dépasse son budget", flux.getvalue())
        # Un plafond de lignes reçoit le même remède.
        lignes = (self.racine / "AGENTS.md").read_text(encoding="utf-8").count("\n")
        gf.write_text(gf.read_text().replace(f'"AGENTS.md" = {{ max_bytes = {avant + 10} }}',
                                             '"AGENTS.md" = { max_bytes = 16000, max_lines = 50 }'))
        self.assertEqual(self._budgets(),
                         [("AGENTS.md", f"{lignes} lignes pour un budget de 50 (AGENTS.md) : resserrer la partie "
                                        "propre au projet, hors de la section du socle, ou relever le budget par une "
                                        "demande validée")])

    def test_un_claude_md_garde_comme_source_qui_depasse_son_budget_le_dit(self):
        """B-0129 : un fichier du projet nomme CLAUDE.md, l'adoption le garde
        comme source, et la section du socle y vit."""
        self.racine = depot({"outil.sh": "cat CLAUDE.md\n", "CLAUDE.md": CLAUDE})
        installer(self.racine)
        self.assertFalse((self.racine / "AGENTS.md").exists())
        sortie, avant, apres, _ = self._deborder("CLAUDE.md")
        self.assertIn(f"!! CLAUDE.md dépasse son budget : {apres} octets pour {avant + 10}, la section du socle, "
                      f"posée ou régénérée, ayant grossi de {apres - avant} ;", sortie)
        self.assertIn(("CLAUDE.md", f"{apres} octets pour un budget de {avant + 10} (CLAUDE.md) : resserrer la "
                                    "partie propre au projet, hors de la section du socle, ou relever le budget par "
                                    "une demande validée"), self._budgets())

    def test_le_contenu_repris_de_claude_md_n_est_pas_la_section(self):
        """B-0129 : renommé en AGENTS.md, un CLAUDE.md garde son contenu ; ce
        que la section a ajouté se compte sans lui."""
        self.racine = depot({"CLAUDE.md": CLAUDE + "Une consigne du projet, longue. " * 300 + "\n"})
        with redirect_stdout(io.StringIO()) as flux:
            installeur.installer(self.racine, "python", "@essai", adoption=False, source=MOTEUR)
        texte = (self.racine / "AGENTS.md").read_text(encoding="utf-8")
        octets, section = len(texte.encode("utf-8")), installeur._taille_section(texte)
        self.assertGreater(octets, 16000)
        self.assertGreater(16000, octets - section)
        self.assertIn(f"!! AGENTS.md dépasse son budget : {octets} octets pour 16000, la section du socle, posée ou "
                      f"régénérée, ayant grossi de {section} ;", flux.getvalue())

    def test_un_sous_dossier_d_un_depot_est_refuse(self):
        """Les hooks git et le workflow de CI ne vivent qu'à la racine du
        dépôt : posés plus bas, ils ne tiraient pas, sans un mot."""
        from contextlib import redirect_stderr

        self.racine = depot({"services/api/app.py": "print('ok')\n"})
        flux = io.StringIO()
        with redirect_stdout(flux), redirect_stderr(flux):
            code = installeur.installer(self.racine / "services/api", "python", "@essai", source=MOTEUR)
        self.assertEqual(code, 2)
        self.assertIn("racine du dépôt", flux.getvalue())
        self.assertFalse((self.racine / "services/api/.socle").exists())

    def test_ce_que_le_socle_pose_n_est_pas_ignore_par_le_projet(self):
        """Un `*.lock` du projet empêchait de commiter le verrou du moteur : un
        clone frais disait le socle non installé."""
        self.racine = depot({".gitignore": "*.lock\n", "app.py": "print('ok')\n"})
        installer(self.racine, adoption=False)
        ignore = subprocess.run(["git", "check-ignore", "-q", ".socle/engine.lock"], cwd=self.racine)
        self.assertEqual(ignore.returncode, 1)

    def test_un_fichier_cache_n_entre_pas_dans_l_empreinte(self):
        """Un `.DS_Store` du clone source était copié et compté : un clone
        frais, sans lui, disait le moteur altéré."""
        from socle import config, fingerprint as empreinte

        source = Path(tempfile.mkdtemp(prefix="socle-source-"))
        self.addCleanup(shutil.rmtree, source, ignore_errors=True)
        shutil.copytree(MOTEUR / "socle", source / "socle", ignore=shutil.ignore_patterns("__pycache__"))
        (source / "socle/.DS_Store").write_bytes(b"\0\1")
        self.racine = depot({"app.py": "print('ok')\n"})
        with redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=source)
        self.assertFalse((self.racine / ".socle/engine/socle/.DS_Store").exists())
        (self.racine / ".socle/engine/socle/.DS_Store").write_bytes(b"\0\2")
        verrou = config.Projet.charger(self.racine).lock
        self.assertEqual(empreinte.calculer(self.racine, ".socle/engine")[0], verrou["fingerprint"])
        self.assertFalse(any(p.name == ".DS_Store" for p in empreinte.fichiers_moteur(self.racine, ".socle/engine")))


class TestReglagesNouveaux(unittest.TestCase):
    """B-0123 : les réglages du gabarit qu'un fichier de garde-fous n'écrit
    pas, même en commentaire."""

    def test_reglages_nouveaux_ecrits_ou_commentes(self):
        modele = ("[tests]\n# Les fichiers de cas.\n# case_paths = []\nspec_paths = []\n\n"
                  "# Correspondance code et doc.\n# [[docmap]]\n# code = []\n# docs = []\n\n"
                  '[budgets]\n"AGENTS.md" = { max_bytes = 1 }\n')
        self.assertEqual(installeur.reglages_nouveaux("[tests]\nspec_paths = []\n", modele), [
            ("[tests] case_paths", "Les fichiers de cas."),
            ("[docmap] code", "Correspondance code et doc."),
            ("[docmap] docs", "Correspondance code et doc."),
        ])
        projet = '[tests]\ncase_paths = ["a.json"]\nspec_paths = []\n[[docmap]]\ncode = ["src/**"]\ndocs = ["d.md"]\n'
        self.assertEqual(installeur.reglages_nouveaux(projet, modele), [])
        self.assertEqual(installeur.reglages_nouveaux(modele, modele), [])


class TestDeuxEtats(unittest.TestCase):
    """B-0054 : un projet qui a déjà son état au démarrage le garde, et
    l'installeur dit que chaque session en recevra deux."""

    def test_l_installeur_signale_l_etat_propre_au_projet(self):
        import contextlib
        import io
        import json
        import subprocess
        import tempfile

        racine = Path(tempfile.mkdtemp(prefix="socle-etats-"))
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True)
        (racine / "calc.py").write_text("X = 1\n", encoding="utf-8")
        (racine / ".claude").mkdir()
        (racine / ".claude/settings.json").write_text(json.dumps({"hooks": {"SessionStart": [
            {"hooks": [{"type": "command", "command": "bash tools/etat.sh"}]}]}}), encoding="utf-8")
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            installeur.installer(racine, "python", "@essai", source=MOTEUR)
        self.assertIn("propre état au démarrage (bash tools/etat.sh)", sortie.getvalue())
        conf = json.loads((racine / ".claude/settings.json").read_text(encoding="utf-8"))
        self.assertEqual(installeur.etats_du_projet(conf), ["bash tools/etat.sh"])
        self.assertTrue(any(".socle/socle hook session-start" in h["command"]
                            for b in conf["hooks"]["SessionStart"] for h in b["hooks"]))

    def test_sans_etat_propre_rien_n_est_dit(self):
        self.assertEqual(installeur.etats_du_projet({"hooks": {"SessionStart": [
            {"hooks": [{"type": "command", "command": "python3 .socle/socle hook session-start"}]}]}}), [])

    def test_l_installeur_nomme_le_hook_de_fin_de_tour_du_projet(self):
        """B-0183 : chess avait son hook de fin de tour, qui lançait les
        mêmes étapes que celui du socle ; l'installeur ne le disait pas."""
        import contextlib
        import io
        import json
        import subprocess
        import tempfile

        racine = Path(tempfile.mkdtemp(prefix="socle-fins-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True)
        (racine / "calc.py").write_text("X = 1\n", encoding="utf-8")
        (racine / ".claude").mkdir()
        (racine / ".claude/settings.json").write_text(json.dumps({"hooks": {"Stop": [
            {"hooks": [{"type": "command", "command": "bash tools/verifier.sh"}]}]}}), encoding="utf-8")
        for passage in ("installation", "mise à jour"):
            sortie = io.StringIO()
            with contextlib.redirect_stdout(sortie):
                installeur.installer(racine, "python", "@essai", source=MOTEUR)
            self.assertIn("!! le projet a déjà son propre hook de fin de tour (bash tools/verifier.sh) : il tire à "
                          "chaque fin de tour à côté de celui du socle, et peut le doubler", sortie.getvalue(), passage)
        conf = json.loads((racine / ".claude/settings.json").read_text(encoding="utf-8"))
        self.assertEqual(installeur.fins_de_tour_du_projet(conf), ["bash tools/verifier.sh"])
        self.assertTrue(any(".socle/socle hook stop" in h["command"] for b in conf["hooks"]["Stop"] for h in b["hooks"]))

    def test_la_commande_du_projet_d_un_bloc_du_socle_survit_et_se_nomme(self):
        """B-0328 : la fusion retirait tout bloc qui portait une commande du
        socle, et avec lui la commande du projet qui le partageait, sans le
        dire ; elle ne retire plus que celle du socle, et l'installeur nomme
        celle qu'il garde. Relancé, il ne duplique rien."""
        import json

        for evenement, commande, signal in (
                ("Stop", "bash tools/lint.sh", "!! le projet a déjà son propre hook de fin de tour (bash tools/lint.sh)"),
                ("SessionStart", "bash tools/etat.sh", "!! le projet a déjà son propre état au démarrage (bash "
                                                       "tools/etat.sh)")):
            with self.subTest(evenement=evenement):
                racine = depot({"calc.py": "X = 1\n"})
                self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
                socle = json.loads(installeur.gabarit("settings.json"))["hooks"][evenement][0]["hooks"][0]
                (racine / ".claude").mkdir()
                (racine / ".claude/settings.json").write_text(json.dumps({"hooks": {evenement: [
                    {"hooks": [socle, {"type": "command", "command": commande}]}]}}), encoding="utf-8")
                for passage in ("installation", "mise à jour", "relance"):
                    sortie = io.StringIO()
                    with redirect_stdout(sortie):
                        installeur.installer(racine, "python", "@essai", source=MOTEUR)
                    self.assertIn(signal, sortie.getvalue(), passage)
                    conf = json.loads((racine / ".claude/settings.json").read_text(encoding="utf-8"))
                    commandes = [h["command"] for b in conf["hooks"][evenement] for h in b["hooks"]]
                    self.assertEqual(commandes.count(commande), 1, passage)
                    self.assertEqual(commandes.count(socle["command"]), 1, passage)
                    self.assertEqual(len(commandes), 2, passage)

    def test_un_bloc_sans_le_socle_se_garde_tel_quel(self):
        socle = {"type": "command", "command": "python3 .socle/socle hook stop"}
        projet = {"type": "command", "command": "bash tools/lint.sh"}
        bloc = {"matcher": "Bash", "hooks": [projet]}
        self.assertIs(installeur._sans_le_socle(bloc), bloc)
        self.assertEqual(installeur._sans_le_socle({"matcher": "Bash", "hooks": [socle, projet]}),
                         {"matcher": "Bash", "hooks": [projet]})
        self.assertIsNone(installeur._sans_le_socle({"hooks": [socle]}))

    def test_sans_hook_de_fin_de_tour_propre_rien_n_est_dit(self):
        import json

        conf = json.loads(installeur.gabarit("settings.json"))
        self.assertEqual(installeur.fins_de_tour_du_projet(conf), [])
        self.assertEqual(installeur.fins_de_tour_du_projet({}), [])


class TestEcartDePolitique(unittest.TestCase):
    """B-0195 : chaque mise à jour réaffichait en entier l'écart de la
    politique au gabarit, même fait des lignes que l'humain a écrites
    exprès, déjà montrées à la mise à jour précédente ; sur chess, deux
    lignes voulues revenaient comme nouvelles. Un écart que l'écart au
    gabarit de la copie remplacée contenait déjà tient en une ligne."""

    DEJA = "toutes déjà dans son écart au gabarit de la copie du moteur remplacée"
    ENTIER = "la politique du projet diffère du gabarit de cette version ; rien n'est écrit"
    VOULUE = 'keep_branches = ["gh-pages"]'

    def setUp(self):
        self.racine = depot({"calc.py": "X = 1\n"})
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        self.politique = self.racine / ".socle/policy.toml"

    def installer(self, source: Path = MOTEUR, **options) -> str:
        with redirect_stdout(io.StringIO()) as flux, redirect_stderr(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=source, humain="Théo", **options)
        return flux.getvalue()

    def commit(self):
        env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "SOCLE_HOOKS_OFF": "1"}
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True, env=env)
        subprocess.run(["git", "-c", "user.name=essai", "-c", "user.email=essai@exemple.org", "-c",
                        "core.hooksPath=/dev/null", "commit", "-q", "-m", "essai"], cwd=self.racine, check=True,
                       env=env)

    def remplacer(self, chemin: Path, avant: str, apres: str):
        texte = chemin.read_text(encoding="utf-8")
        self.assertIn(avant, texte)
        chemin.write_text(texte.replace(avant, apres, 1), encoding="utf-8")

    def test_un_ecart_deja_montre_tient_en_une_ligne(self):
        self.installer()
        self.remplacer(self.politique, "keep_branches = []", self.VOULUE)
        self.commit()
        for passage in ("mise à jour", "relance avant son commit"):
            sortie = self.installer()
            self.assertIn("la politique du projet diffère du gabarit de cette version de 2 ligne(s), " + self.DEJA,
                          sortie, passage)
            self.assertIn("Pour le revoir en entier : `git diff --no-index .socle/policy.toml "
                          ".socle/engine/socle/templates/policy.toml`", sortie, passage)
            self.assertNotIn(self.ENTIER, sortie, passage)
            self.assertNotIn(self.VOULUE, sortie, passage)

    def test_un_ecart_nouveau_s_affiche_en_entier(self):
        # La copie d'avant avait un autre `max_attempts`, que la politique
        # tient d'elle : le gabarit de cette version le change.
        source = Path(tempfile.mkdtemp(prefix="socle-source-"))
        self.addCleanup(shutil.rmtree, source, ignore_errors=True)
        shutil.copytree(MOTEUR / "socle", source / "socle", ignore=shutil.ignore_patterns("__pycache__"))
        self.remplacer(source / "socle/templates/policy.toml", "max_attempts = 3", "max_attempts = 5")
        self.installer(source)
        self.remplacer(self.politique, "max_attempts = 3", "max_attempts = 5")
        self.remplacer(self.politique, "keep_branches = []", self.VOULUE)
        self.commit()
        sortie = self.installer()
        self.assertIn(self.ENTIER, sortie)
        self.assertIn("+max_attempts = 3", sortie)
        self.assertIn("-" + self.VOULUE, sortie)
        self.assertNotIn(self.DEJA, sortie)

    def test_sans_commit_l_ecart_s_affiche_en_entier(self):
        self.installer()
        self.remplacer(self.politique, "keep_branches = []", self.VOULUE)
        self.assertIsNone(installeur.politique_d_avant(self.racine, ".socle/engine"))
        sortie = self.installer()
        self.assertIn(self.ENTIER, sortie)
        self.assertIn("-" + self.VOULUE, sortie)

    def test_le_gabarit_d_avant_se_lit_dans_le_dernier_commit_et_la_langue_du_projet(self):
        self.installer(langue_memoire="en")
        self.commit()
        self.assertEqual(installeur.politique_d_avant(self.racine, ".socle/engine"),
                         (MOTEUR / "socle/templates/policy.en.toml").read_text(encoding="utf-8"))
        self.assertIsNone(installeur.politique_d_avant(self.racine, "ailleurs"))
        # Le nom de l'humain et la langue, que l'installeur a écrits, ne sont
        # pas un écart, au gabarit d'avant comme à celui de cette version.
        modele = installeur.politique_d_avant(self.racine, ".socle/engine")
        self.assertEqual(installeur.diff_politique(self.racine, modele), [])
        self.assertEqual(installeur.diff_politique(self.racine), [])

    def test_ecart_deja_montre(self):
        ecart = ["--- a", "+++ b", "@@ -1 +1 @@", " contexte", "-x = 1", "+x = 2"]
        self.assertEqual(installeur.lignes_changees(ecart), ["-x = 1", "+x = 2"])
        self.assertTrue(installeur.ecart_deja_montre(ecart, ecart + ["-y = 1", "+y = 2"]))
        self.assertFalse(installeur.ecart_deja_montre(ecart, ["--- a", "+++ b", "-x = 1", "+x = 3"]))
        self.assertFalse(installeur.ecart_deja_montre(ecart, None))
        self.assertFalse(installeur.ecart_deja_montre([], []))


class TestAuditAdaptateur(unittest.TestCase):
    """B-0011 : à chaque état, un langage que l'adaptateur ne couvre pas est
    dit, pour que l'humain en décide."""

    def projet(self, fichiers: dict[str, str]) -> Path:
        import contextlib
        import io
        import tempfile

        racine = Path(tempfile.mkdtemp(prefix="socle-audit-"))
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True)
        (racine / "calc.py").write_text("X = 1\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(racine, "python", "@essai", source=MOTEUR)
        for chemin, texte in fichiers.items():
            p = racine / chemin
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(texte, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=racine, check=True)
        return racine

    def test_langages_presents_trouve_les_marqueurs_a_toute_profondeur(self):
        self.assertEqual(installeur.langages_presents(["pyproject.toml", "web/package.json", "a/b/go.mod", "x.py"]),
                         {"python": ["pyproject.toml"], "javascript": ["web/package.json"], "go": ["a/b/go.mod"]})

    def test_audit_adaptateur_dit_un_langage_que_l_adaptateur_ne_couvre_pas(self):
        from socle import state as etat

        racine = self.projet({"web/package.json": "{}\n"})
        lignes = etat.audit_adaptateur(config.Projet.charger(racine))
        self.assertEqual(len(lignes), 1)
        self.assertIn("javascript (web/package.json)", lignes[0])
        self.assertIn("(python)", lignes[0])
        self.assertIn("javascript (web/package.json)", etat.calculer(config.Projet.charger(racine), contenus=False))

    def test_rien_a_dire_quand_tout_est_couvert_ou_tiers(self):
        from socle import state as etat

        self.assertEqual(etat.audit_adaptateur(config.Projet.charger(self.projet({"pyproject.toml": ""}))), [])
        racine = self.projet({"_outil/package.json": "{}\n"})
        gf = racine / ".socle/guardrails.toml"
        gf.write_text(installeur.declarer_tiers(gf.read_text(encoding="utf-8"), ["_outil/**"]), encoding="utf-8")
        self.assertEqual(etat.audit_adaptateur(config.Projet.charger(racine)), [])


class TestCopiesEnRetard(unittest.TestCase):
    """B-0218 : en mode amont, le moteur change sans que l'installeur ne
    repasse ; une copie protégée qu'il pose, et qui diffère de ce qu'il
    poserait, se nomme dans l'état, sans rien rendre rouge."""

    SKILL = ".claude/skills/socle-resume/SKILL.md"

    def projet(self, mode: str = config.MODE_AMONT, langue: str | None = None) -> Path:
        racine = depot({"calc.py": "X = 1\n"})
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            installeur.installer(racine, "python", "@essai", mode=mode, source=MOTEUR, langue_memoire=langue)
        return racine

    def retard(self, racine: Path) -> list[str]:
        return installeur.copies_en_retard(config.Projet.charger(racine))

    def changer(self, racine: Path, chemin: str, avant: str, apres: str):
        p = racine / chemin
        texte = p.read_text(encoding="utf-8")
        self.assertIn(avant, texte)
        p.write_text(texte.replace(avant, apres, 1), encoding="utf-8")

    def test_une_copie_egale_a_ce_que_l_installeur_pose_n_est_pas_nommee(self):
        from socle import state as etat

        racine = self.projet()
        self.assertEqual(self.retard(racine), [])
        self.assertEqual(etat.copies_en_retard(config.Projet.charger(racine)), [])
        self.assertNotIn("copies   :", etat.calculer(config.Projet.charger(racine), contenus=False))
        # Le gabarit brut n'est pas ce que l'installeur pose : la CI y a ses
        # marques, que le rendu remplace.
        self.assertNotEqual((MOTEUR / "socle/templates/socle.yml").read_text(encoding="utf-8"),
                            (racine / installeur.CI_DU_SOCLE).read_text(encoding="utf-8"))

    def test_une_copie_qui_differe_ou_manque_est_nommee_par_l_etat(self):
        from socle import state as etat

        racine = self.projet()
        self.changer(racine, self.SKILL, "\n", "\nUne ligne que le gabarit n'a plus.\n")
        self.changer(racine, installeur.CI_DU_SOCLE, "branches-ignore", "branches-ignored")
        (racine / config.GIT_HOOKS / "pre-push").unlink()
        attendus = [self.SKILL, f"{config.GIT_HOOKS}/pre-push", installeur.CI_DU_SOCLE]
        self.assertEqual(sorted(self.retard(racine)), sorted(attendus))
        lignes = etat.copies_en_retard(config.Projet.charger(racine))
        self.assertEqual(len(lignes), 1)
        self.assertIn("3 copie(s) protégée(s)", lignes[0])
        for c in attendus:
            self.assertIn(c, lignes[0])
        self.assertNotIn("socle-review", lignes[0])
        self.assertIn(lignes[0], etat.calculer(config.Projet.charger(racine), contenus=False))

    def test_rendue_dans_la_langue_de_la_memoire_et_avec_le_nom_du_travail_garde(self):
        """Ce que l'installeur poserait, pas le gabarit : la langue de la
        mémoire, et le nom du travail de CI qu'une mise à jour garde."""
        racine = self.projet(langue="en")
        self.assertNotEqual((racine / self.SKILL).read_text(encoding="utf-8"),
                            installeur.gabarit("skills/socle-resume/SKILL.md", "fr"))
        self.assertEqual(self.retard(racine), [])
        ci = (racine / installeur.CI_DU_SOCLE).read_text(encoding="utf-8")
        nom = installeur.outils.nom_du_travail(ci)
        self.changer(racine, installeur.CI_DU_SOCLE, f"    name: {nom}\n", "    name: exigée par la branche\n")
        self.assertEqual(self.retard(racine), [])
        self.assertEqual(installeur.ci_du_socle(racine, [], "en")[1], "exigée par la branche")
        self.assertEqual(installeur.copies_du_socle(racine)[self.SKILL],
                         installeur.skills_du_socle("en")[self.SKILL])

    def test_les_etapes_des_adaptateurs_dans_la_ci_rendue(self):
        rust = installeur.charger_adaptateur("rust")[0]
        etapes = installeur.etapes_traduites([rust, rust])
        self.assertTrue(etapes.endswith("\n") and etapes.strip())
        self.assertEqual(etapes, installeur.etapes_traduites([rust]))
        self.assertEqual(installeur.etapes_traduites(['language = "python"\n']), "")
        racine = self.projet()
        workflow, garde = installeur.ci_du_socle(racine, [rust], "fr")
        self.assertIn(etapes, workflow)
        self.assertNotIn("@@", workflow)
        self.assertIsNone(garde)

    def test_rien_en_mode_projet(self):
        """Une mise à jour y pose chaque copie, et `protege.fichiers` juge
        leur changement."""
        from socle import state as etat

        racine = self.projet(mode=config.MODE_PROJET)
        self.changer(racine, self.SKILL, "\n", "\nUne ligne que le gabarit n'a plus.\n")
        self.assertEqual(self.retard(racine), [])
        self.assertEqual(etat.copies_en_retard(config.Projet.charger(racine)), [])


class TestWorktreesIgnores(unittest.TestCase):
    """B-0217 : le skill socle-batch lance ses sous-agents dans des worktrees,
    sous `.claude/worktrees/` ; non ignorés, le hook de fin de tour de
    l'environnement cloud demande de les commiter."""

    def non_suivis(self, racine: Path) -> list[str]:
        sortie = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=racine,
                                capture_output=True, text=True, check=True).stdout
        return [l[3:] for l in sortie.splitlines() if l.startswith("??")]

    def worktree(self, racine: Path):
        p = racine / installeur.WORKTREES / "agent-essai/calc.py"
        p.parent.mkdir(parents=True)
        p.write_text("X = 2\n", encoding="utf-8")

    def test_le_gitignore_de_ce_depot_les_ignore(self):
        racine = depot({".gitignore": (MOTEUR.parent / ".gitignore").read_text(encoding="utf-8")})
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        self.worktree(racine)
        self.assertEqual(self.non_suivis(racine), [".gitignore"])

    def test_l_installeur_les_ignore_dans_un_projet_qu_il_equipe_sans_doubler_la_ligne(self):
        racine = depot({"calc.py": "X = 1\n"})
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        installer(racine, adoption=False)
        self.worktree(racine)
        self.assertFalse([c for c in self.non_suivis(racine) if c.startswith(installeur.WORKTREES)])
        installer(racine, adoption=False)
        texte = (racine / ".gitignore").read_text(encoding="utf-8")
        self.assertEqual(texte.count(f"/{installeur.WORKTREES}/"), 1, texte)
        self.assertEqual(texte.count("# Les worktrees des sous-agents de Claude Code"), 1, texte)

    def test_une_ligne_qui_les_ignore_deja_ne_se_double_pas(self):
        for ligne in (".claude/worktrees", "/.claude/worktrees", ".claude/worktrees/*", ".claude/", "/.claude/**"):
            with self.subTest(ligne):
                racine = depot({"calc.py": "X = 1\n", ".gitignore": ligne + "\n"})
                self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
                installer(racine, adoption=False)
                self.assertNotIn("worktrees des sous-agents", (racine / ".gitignore").read_text(encoding="utf-8"))
        for texte in ("!.claude/worktrees/\n", "# .claude/worktrees\n", ".claude/worktrees-anciens\n",
                      "worktrees\n"):
            with self.subTest(texte):
                self.assertFalse(installeur.ignore_deja(texte, installeur.WORKTREES))


class TestSousDossiers(unittest.TestCase):
    """B-0168 : l'essai à blanc sur chess, un dépôt Rust dont l'interface
    JavaScript vit dans `ui/`, avec son propre manifeste."""

    def setUp(self):
        self.racine = depot({"Cargo.toml": "[package]\nname = \"essai\"\n", "src/lib.rs": "pub fn f() {}\n",
                             "ui/package.json": "{}\n", "ui/src/app.js": "export const x = 1;\n"})

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def installer(self, *adaptateurs, adoption=False) -> tuple[int, str, str]:
        sortie, erreurs = io.StringIO(), io.StringIO()
        with redirect_stdout(sortie), redirect_stderr(erreurs):
            code = installeur.installer(self.racine, list(adaptateurs) or "auto", "@essai", adoption=adoption,
                                        source=MOTEUR)
        return code, sortie.getvalue(), erreurs.getvalue()

    def test_un_manifeste_d_un_sous_dossier_ne_recoit_pas_d_adaptateur(self):
        self.assertEqual(installeur.langages_en_sous_dossier(self.racine), {"javascript": ["ui/package.json"]})
        self.assertEqual(installeur.detecter_adaptateurs(self.racine), ["rust"])
        dit = installeur.sous_dossiers_sans_adaptateur(self.racine, {"rust"})
        self.assertEqual(len(dit), 1)
        self.assertIn("ui/package.json", dit[0])
        self.assertIn('[thirdparty] paths = ["ui/**"]', dit[0])
        self.assertIn("--adapter <fichier.toml>", dit[0])
        self.assertEqual(installeur.sous_dossiers_sans_adaptateur(self.racine, {"rust", "javascript"}), [])

    def test_un_manifeste_a_la_racine_garde_son_adaptateur(self):
        (self.racine / "package.json").write_text("{}\n", encoding="utf-8")
        self.assertEqual(installeur.langages_en_sous_dossier(self.racine), {})
        self.assertEqual(installeur.detecter_adaptateurs(self.racine), ["rust", "javascript"])

    def test_l_installeur_le_dit_et_ne_pose_que_l_adaptateur_de_la_racine(self):
        _, sortie, _ = self.installer()
        self.assertFalse((self.racine / ".socle/adapters/javascript.toml").exists())
        self.assertIn("!! javascript", sortie)
        self.assertNotIn("npm ci", (self.racine / ".github/workflows/socle.yml").read_text(encoding="utf-8"))

    def test_la_fin_dit_que_les_capacites_n_ont_pas_ete_lancees(self):
        _, sortie, _ = self.installer()
        self.assertIn(installeur.note_d_audit(), sortie)
        self.assertIn("python3 .socle/socle verify --fast", sortie.split("Et maintenant :", 1)[1])
        commit = next(e for e in installeur.et_maintenant(self.racine, False, []) if "git commit" in e)
        self.assertIn("Avant de commiter, lancer `python3 .socle/socle verify --fast`", commit)
        self.assertIn("git switch", commit)
        commit = next(e for e in installeur.et_maintenant(self.racine, True, []) if "git commit" in e)
        self.assertIn("verify --fast", commit)
        self.assertNotIn("git switch", commit)

    def test_un_adaptateur_propre_au_projet_se_pose_et_se_garde(self):
        propre = Path(tempfile.mkdtemp(prefix="socle-adaptateur-propre-"))
        self.addCleanup(shutil.rmtree, propre, ignore_errors=True)
        texte = (installeur.ADAPTATEURS / "rust.toml").read_text(encoding="utf-8").replace(
            "[capabilities.tests]\n", "# Propre au projet.\n[capabilities.tests]\n", 1)
        (propre / "chess-rust.toml").write_text(texte, encoding="utf-8")
        code, _, erreurs = self.installer(str(propre / "chess-rust.toml"))
        self.assertIn(code, (0, 1), erreurs)
        self.assertEqual((self.racine / ".socle/adapter.toml").read_text(encoding="utf-8"), texte)
        # À la mise à jour, une copie que le projet a adaptée se garde (ADR-0052).
        _, sortie, _ = self.installer()
        self.assertEqual((self.racine / ".socle/adapter.toml").read_text(encoding="utf-8"), texte)
        self.assertIn("adapté par le projet : conservé", sortie)

    def test_avec_un_adaptateur_donne_l_installeur_le_dit_aussi(self):
        # B-0178 : sur chess, `--adapter <fichier>` pour le Rust ; rien n'était
        # dit du JavaScript de `ui/`, sauf en détection automatique.
        propre = Path(tempfile.mkdtemp(prefix="socle-adaptateur-propre-"))
        self.addCleanup(shutil.rmtree, propre, ignore_errors=True)
        (propre / "chess-rust.toml").write_text((installeur.ADAPTATEURS / "rust.toml").read_text(encoding="utf-8")
                                                + "\n# Propre au projet.\n", encoding="utf-8")
        for adaptateur in (str(propre / "chess-rust.toml"), "rust"):
            shutil.rmtree(self.racine / ".socle", ignore_errors=True)
            code, sortie, erreurs = self.installer(adaptateur)
            self.assertIn(code, (0, 1), erreurs)
            self.assertIn("!! javascript", sortie, adaptateur)
            self.assertIn('[thirdparty] paths = ["ui/**"]', sortie, adaptateur)
        # Le manifeste sous un chemin tiers déjà déclaré : plus rien à dire.
        gf = self.racine / config.FORMAT_ACTUEL.garde_fous
        gf.write_text(gf.read_text(encoding="utf-8").replace("[thirdparty]\n", '[thirdparty]\npaths = ["ui/**"]\n', 1)
                      .replace("\npaths = []\n", "\n", 1), encoding="utf-8")
        self.assertEqual(installeur.sous_dossiers_sans_adaptateur(self.racine, {"rust"}), [])
        _, sortie, _ = self.installer(str(propre / "chess-rust.toml"))
        self.assertNotIn("!! javascript", sortie)

    def test_un_adaptateur_donne_sans_langage_est_nomme(self):
        # Revue du lot de B-0178 : un adaptateur propre au projet sans clé
        # `language` faisait dire « aucun adaptateur ne lui est posé ».
        propre = Path(tempfile.mkdtemp(prefix="socle-adaptateur-propre-"))
        self.addCleanup(shutil.rmtree, propre, ignore_errors=True)
        texte = (installeur.ADAPTATEURS / "javascript.toml").read_text(encoding="utf-8")
        texte = "\n".join(l for l in texte.splitlines() if not l.startswith("language")) + "\n"
        (propre / "ui.toml").write_text(texte.replace('command = "npx vitest run"', 'command = "cd ui && npx vitest run"'),
                                        encoding="utf-8")
        code, sortie, erreurs = self.installer("rust", str(propre / "ui.toml"))
        self.assertIn(code, (0, 1), erreurs)
        self.assertNotIn("aucun adaptateur ne lui est posé", sortie)
        self.assertIn(f"{propre / 'ui.toml'} ne déclare pas `language`", sortie)
        self.assertIn('ajouter `language = "javascript"` à ce fichier', sortie)
        self.assertEqual(installeur.adaptateurs_sans_langage(self.racine, config.FORMAT_ACTUEL),
                         [".socle/adapters/ui.toml"])
        dit = installeur.sous_dossiers_sans_adaptateur(self.racine, {"rust"}, [".socle/adapters/ui.toml"])
        self.assertIn(".socle/adapters/ui.toml ne déclare pas `language`", dit[0])

    def test_un_adaptateur_propre_hors_contrat_est_refuse(self):
        propre = Path(tempfile.mkdtemp(prefix="socle-adaptateur-propre-"))
        self.addCleanup(shutil.rmtree, propre, ignore_errors=True)
        (propre / "maison.toml").write_text('language = "rust"\n[capabilities.tests]\ncommand = "cargo test"\n',
                                            encoding="utf-8")
        self.assertTrue(installeur.est_un_fichier(str(propre / "maison.toml")))
        self.assertFalse(installeur.est_un_fichier("rust"))
        code, _, erreurs = self.installer(str(propre / "maison.toml"))
        self.assertEqual(code, 2)
        self.assertIn("contrat des adaptateurs", erreurs)
        self.assertIn("« format »", erreurs)
        self.assertFalse((self.racine / ".socle").exists())
        with self.assertRaises(SystemExit):
            installeur.charger_adaptateur(str(propre / "absent.toml"))

    def commit(self):
        env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "SOCLE_HOOKS_OFF": "1"}
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True, env=env)
        subprocess.run(["git", "-c", "user.name=essai", "-c", "user.email=essai@exemple.org", "-c",
                        "core.hooksPath=/dev/null", "commit", "-q", "-m", "essai"], cwd=self.racine, check=True,
                       env=env)

    def test_une_mise_a_jour_compte_les_adaptateurs_deja_poses(self):
        # Revue de B-0168, constat 1 : l'adaptateur de `ui/`, propre au
        # projet, posé ; la relance automatique ne le dit plus manquant.
        propre = Path(tempfile.mkdtemp(prefix="socle-adaptateur-propre-"))
        self.addCleanup(shutil.rmtree, propre, ignore_errors=True)
        texte = (installeur.ADAPTATEURS / "javascript.toml").read_text(encoding="utf-8").replace(
            'command = "npx vitest run"', 'command = "cd ui && npx vitest run"')
        (propre / "ui.toml").write_text(texte, encoding="utf-8")
        code, _, erreurs = self.installer("rust", str(propre / "ui.toml"))
        self.assertIn(code, (0, 1), erreurs)
        self.assertEqual(installeur.langages_en_place(self.racine, config.FORMAT_ACTUEL), {"rust", "javascript"})
        self.commit()
        _, sortie, _ = self.installer()
        self.assertNotIn("!! javascript", sortie)

    def test_un_adaptateur_donne_qu_un_principal_en_place_ecarte_le_dit(self):
        # Revue de B-0168, constat 4 : l'essai non commité, l'installeur
        # relancé garde le principal ; il ne nomme plus l'autre comme posé.
        self.installer("rust")
        propre = Path(tempfile.mkdtemp(prefix="socle-adaptateur-propre-"))
        self.addCleanup(shutil.rmtree, propre, ignore_errors=True)
        texte = (installeur.ADAPTATEURS / "rust.toml").read_text(encoding="utf-8") + "\n# Propre au projet.\n"
        (propre / "own-rust.toml").write_text(texte, encoding="utf-8")
        _, sortie, _ = self.installer(str(propre / "own-rust.toml"))
        self.assertIn("!! own-rust non posé : .socle/adapter.toml existe déjà pour rust, et se garde", sortie)
        self.assertNotIn("adaptateur : own-rust", sortie)
        self.assertNotEqual((self.racine / ".socle/adapter.toml").read_text(encoding="utf-8"), texte)

    def test_un_python_de_sous_dossier_ne_se_lance_que_s_il_tourne_de_la_racine(self):
        # Revue de B-0168, constat 2 : `unittest discover -s tests` échoue à
        # la racine sans `tests/` ; pytest parcourt les sous-dossiers.
        (self.racine / "ui").rename(self.racine / "hors")
        shutil.rmtree(self.racine / "hors")
        for chemin, texte in (("tools/pyproject.toml", "[project]\nname = \"t\"\n"),
                              ("tools/tests/test_t.py", "import unittest\n")):
            (self.racine / chemin).parent.mkdir(parents=True, exist_ok=True)
            (self.racine / chemin).write_text(texte, encoding="utf-8")
        self.assertEqual(installeur.detecter_adaptateurs(self.racine), ["rust"])
        self.assertIn("python", installeur.langages_en_sous_dossier(self.racine))
        (self.racine / "tests").mkdir()
        (self.racine / "tests/test_racine.py").write_text("import unittest\n", encoding="utf-8")
        self.assertEqual(installeur.detecter_adaptateurs(self.racine), ["rust", "python"])

    def test_un_python_sans_manifeste_aux_tests_a_la_racine_garde_son_adaptateur(self):
        racine = depot({"app.py": "X = 1\n", "tests/test_app.py": "import unittest\n"})
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        self.assertEqual(installeur.detecter_adaptateurs(racine), ["python"])
        self.assertEqual(installeur.langages_en_sous_dossier(racine), {})

    def test_gradle_lance_de_la_racine_garde_kotlin(self):
        # Revue de B-0168, constat 3 : un build Groovy et le wrapper à la
        # racine, le module Kotlin dans `app/`.
        racine = depot({"pyproject.toml": "[project]\nname = \"x\"\n", "x.py": "X = 1\n",
                        "settings.gradle": "include ':app'\n", "gradlew": "#!/bin/sh\n",
                        "app/build.gradle.kts": "plugins { kotlin(\"jvm\") }\n",
                        "app/src/main/kotlin/app/App.kt": "package app\n\nfun main() {}\n"})
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        self.assertEqual(installeur.detecter_adaptateurs(racine), ["python", "kotlin"])
        self.assertTrue(installeur.lancable_de_la_racine(racine, "kotlin", ["app/build.gradle.kts"], ["gradlew"]))
        self.assertFalse(installeur.lancable_de_la_racine(racine, "kotlin", ["app/build.gradle.kts"], []))

    def test_le_contrat_juge_un_adaptateur_lu(self):
        from socle import checks_tests

        self.assertEqual(checks_tests.ecarts_au_contrat(tomllib.loads(
            (installeur.ADAPTATEURS / "rust.toml").read_text(encoding="utf-8"))), [])
        ecarts = checks_tests.ecarts_au_contrat({"capabilities": {"format": {"absent": "rien"}}})
        self.assertIn("capacité « format » : ni `command`, ni `absent` avec `replacement`", ecarts)
        self.assertTrue(any("`[tests]`" in e for e in ecarts))


class TestBudgetDAdoption(unittest.TestCase):
    def test_la_taille_plus_un_dixieme_au_millier_superieur(self):
        self.assertEqual(installeur.budget_d_adoption(138934), 153000)
        self.assertEqual(installeur.budget_d_adoption(10000), 11000)
        self.assertEqual(installeur.budget_d_adoption(1), 1000)

    def test_l_adoption_laisse_une_marge_au_fichier_d_instructions(self):
        racine = depot({"CLAUDE.md": "# Projet\n" + "x" * 30000 + "\n",
                        "tests/test_doc.py": "open('CLAUDE.md').read()\n"})
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        sortie = io.StringIO()
        with redirect_stdout(sortie):
            installeur.installer(racine, "python", "@essai", adoption=True, source=MOTEUR)
        taille = len((racine / "CLAUDE.md").read_bytes())
        budgets = tomllib.loads((racine / ".socle/guardrails.toml").read_text(encoding="utf-8"))["budgets"]
        self.assertGreaterEqual(budgets["CLAUDE.md"]["max_bytes"] - taille, taille // 10)
        self.assertIn("plus un dixième", sortie.getvalue())
