import io
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
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
        self.assertIn("`[tests] case_paths` — Les fichiers de cas", sortie)
        self.assertIn("`[specs] paths` — Les spécifications du projet", sortie)
        self.assertEqual(gf.read_text(), avant)
        # Écrits, même en commentaire, ils ne se signalent plus.
        gf.write_text(texte)
        with redirect_stdout(io.StringIO()) as flux:
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        self.assertNotIn("réglages du gabarit absents", flux.getvalue())

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
