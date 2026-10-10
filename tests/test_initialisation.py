"""Le jalon 8 : l'installeur qui choisit l'adaptateur, pose la mémoire
privée, migre et montre le diff de politique à la mise à jour ; et les
trois entrées d'initialisation."""

import io
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from socle import config, initialisation, installeur, memoire, migrations
from socle.modeles import gabarit

MOTEUR = Path(__file__).resolve().parent.parent / "moteur"


def depot(fichiers: dict[str, str]) -> Path:
    racine = Path(tempfile.mkdtemp(prefix="socle-init-"))
    env = {**os.environ, "HOME": str(racine), "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True, env=env)
    for chemin, texte in fichiers.items():
        p = racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")
    return racine


def installer(racine: Path, adaptateur="python", **options) -> tuple[int, str]:
    flux = io.StringIO()
    with redirect_stdout(flux):
        code = installeur.installer(racine, adaptateur, "@essai", source=MOTEUR, **options)
    return code, flux.getvalue()


class Base(unittest.TestCase):
    racine = None

    def tearDown(self):
        if self.racine:
            shutil.rmtree(self.racine, ignore_errors=True)


class TestAdaptateurDetecte(Base):
    def test_selon_les_fichiers(self):
        self.racine = depot({"Cargo.toml": "[package]\n"})
        self.assertEqual(installeur.detecter_adaptateur(self.racine), "rust")
        (self.racine / "Cargo.toml").unlink()
        (self.racine / "calc.py").write_text("x = 1\n")
        self.assertEqual(installeur.detecter_adaptateur(self.racine), "python")
        (self.racine / "pyproject.toml").write_text("[tool.pytest.ini_options]\n")
        self.assertEqual(installeur.detecter_adaptateur(self.racine), "python-pytest")

    def test_rien_a_detecter_la_question_revient_a_l_humain(self):
        self.racine = depot({})
        self.assertIsNone(installeur.detecter_adaptateur(self.racine))
        flux = io.StringIO()
        with redirect_stdout(flux), __import__("contextlib").redirect_stderr(flux):
            self.assertEqual(installeur.installer(self.racine, "auto", source=MOTEUR), 2)
        self.assertIn("langage non détecté", flux.getvalue())


class TestMemoirePriveeALInstallation(Base):
    def test_compagnon_sans_clone_le_dit(self):
        self.racine = depot({"calc.py": "x = 1\n"})
        code, sortie = installer(self.racine, prive="compagnon", relecture="lots", demandes_privees=True)
        politique = (self.racine / config.POLITIQUE).read_text()
        self.assertIn('[private]\nmode = "compagnon"\nreview = "lots"\nrequests = true\n', politique)
        self.assertIn("memoire/prive/", (self.racine / ".gitignore").read_text())
        self.assertIn("dépôt privé absent", sortie)

    def test_chiffre_pose_le_filtre(self):
        self.racine = depot({"calc.py": "x = 1\n"})
        code, sortie = installer(self.racine, prive="chiffre", filtre="git-crypt")
        self.assertIn("memoire/prive/** filter=git-crypt", (self.racine / ".gitattributes").read_text())
        self.assertIn("filtre « git-crypt » non configuré", sortie)

    def test_la_politique_du_gabarit_reecrite(self):
        texte = installeur.politique_privee(gabarit("politique.toml"), "chiffre", None, False)
        self.assertIn('[private]\nmode = "chiffre"\nrequests = false\n', texte)
        self.assertNotIn("# [private]", texte)


class TestMiseAJour(Base):
    def setUp(self):
        self.racine = depot({"calc.py": "x = 1\n"})
        installer(self.racine)

    def test_le_verrou_note_le_format(self):
        self.assertIn(f"format = {migrations.FORMAT}", (self.racine / config.LOCK).read_text())

    def test_la_politique_changee_est_montree_jamais_ecrasee(self):
        p = self.racine / config.POLITIQUE
        p.write_text(p.read_text().replace("max_attempts = 3", "max_attempts = 5"))
        self.assertTrue(installeur.diff_politique(self.racine))
        code, sortie = installer(self.racine)
        self.assertIn("mise à jour : moteur", sortie)
        self.assertIn("+max_attempts = 3", sortie)
        self.assertIn("max_attempts = 5", p.read_text())

    def test_les_migrations_s_appliquent_dans_l_ordre(self):
        faites = []
        avant = dict(migrations.MIGRATIONS), migrations.FORMAT
        migrations.MIGRATIONS.update({1: lambda c: faites.append(1) or ["un"], 2: lambda c: faites.append(2) or []})
        try:
            self.assertEqual(migrations.migrer(self.racine, 1, 3), ["format 1 → 2 : un", "format 2 → 3"])
            self.assertEqual(faites, [1, 2])
            with self.assertRaises(RuntimeError):
                migrations.migrer(self.racine, 1, 4)
        finally:
            migrations.MIGRATIONS.clear()
            migrations.MIGRATIONS.update(avant[0])


class TestEntrees(Base):
    def charger(self):
        return config.Projet.charger(self.racine)

    def test_rien(self):
        self.racine = depot({})
        installer(self.racine)
        with redirect_stdout(io.StringIO()) as flux:
            self.assertEqual(initialisation.initialiser(self.charger()), 0)
        questions = initialisation.questions_de_depart(self.charger(), None, False)
        self.assertEqual(len(questions), 5)
        self.assertTrue(all(q.defaut and q.effet for q in questions))
        d = next((self.racine / "memoire/demandes").glob("D-0001-*.md")).read_text()
        self.assertIn("Défaut : aucun", d)
        self.assertIn("Ce qui revient maintenant à l'agent", flux.getvalue())

    def test_cadrage_archive_tel_quel(self):
        self.racine = depot({})
        installer(self.racine)
        doc = self.racine.parent / f"{self.racine.name}-cadrage.md"
        doc.write_text("# Cadrage\n\n## Objectif\n\nUn but.\n")
        try:
            archive, emp = initialisation.archiver_cadrage(self.racine, doc)
            self.assertEqual((self.racine / archive).read_bytes(), doc.read_bytes())
            self.assertTrue(emp.startswith("sha256:"))
            with redirect_stdout(io.StringIO()):
                initialisation.initialiser(self.charger(), cadrage=doc)
        finally:
            doc.unlink()
        journal = next((self.racine / "memoire/journal").glob("*.md")).read_text()
        self.assertIn("Document de cadrage archivé tel quel", journal)
        demande = next((self.racine / "memoire/demandes").glob("D-*.md")).read_text()
        self.assertIn("celui du document de cadrage", demande)

    def test_depot_seulement_du_verifiable(self):
        self.racine = depot({"pyproject.toml": "[project]\n", "README.md": "# Projet\n",
                             ".github/workflows/ci.yml": "name: CI\n",
                             "tests/test_calc.py": "def test_un():\n    assert 1 == 1 + 0\n"})
        installer(self.racine, "python-pytest")
        faits = initialisation.auditer_depot(self.charger())
        self.assertEqual([f.preuve for f in faits],
                         ["pyproject.toml", "tests/test_calc.py", ".github/workflows/ci.yml", "README.md"])
        with redirect_stdout(io.StringIO()):
            initialisation.initialiser(self.charger(), depot=True)
        mem = memoire.Memoire.charger(self.racine)
        self.assertTrue(all(e.statut == "mesure" and e.refs("preuve") for e in mem.entrees("F")))
        self.assertFalse(initialisation.detecter(self.charger()) is None)


class TestCommandes(Base):
    def test_install_puis_init_par_la_ligne_de_commande(self):
        import argparse

        from socle import cli, demandes

        self.racine = depot({"calc.py": "x = 1\n"})
        ns = argparse.Namespace(target=str(self.racine), adapter="auto", owner="@essai", adoption=False,
                                mode=config.MODE_PROJET, private=None, review=None, private_requests=False,
                                filter="git-crypt")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli.cmd_install(ns), 0)
            self.assertEqual(cli.cmd_init(argparse.Namespace(root=str(self.racine), cadrage=None, depot=True)), 0)
        projet = config.Projet.charger(self.racine)
        texte = initialisation.demande_de_depart(projet, "D-0009", initialisation.questions_de_depart(projet, None, True),
                                                 None, "un dépôt existant")
        d = demandes.charger(self.racine, None, "memoire/demandes/D-0009-questions-de-depart.md", texte)
        self.assertEqual(demandes.linter(d, projet), [])
        self.assertEqual(d.reponses_possibles(), ["defauts", "reponses", "contexte-insuffisant"])
