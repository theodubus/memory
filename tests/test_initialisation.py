"""Le jalon 8 : l'installeur qui choisit l'adaptateur, pose la mémoire
privée et montre le diff de politique à la mise à jour ; et les
trois entrées d'initialisation."""

import io
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from socle import config, initialization as initialisation, installer as installeur, memory as memoire
from socle.templates import gabarit

MOTEUR = Path(__file__).resolve().parent.parent / "engine"


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
        politique = (self.racine / config.FORMAT_ACTUEL.politique).read_text()
        self.assertIn('[private]\nmode = "compagnon"\nreview = "lots"\nrequests = true\n', politique)
        self.assertIn("memory/private/", (self.racine / ".gitignore").read_text())
        self.assertIn("dépôt privé absent", sortie)
        self.assertIn("mettre en place le dépôt privé", sortie.split("Et maintenant :")[1])
        etapes = sortie.split("Et maintenant :")[1]
        self.assertIn("mettre en place le dépôt privé", etapes)
        # Son verrou manque, mais ni une correction ni l'adoption n'y peuvent rien.
        self.assertNotIn("--adoption", etapes)
        self.assertIn("sa mise en place revient à l'humain", sortie)

    def test_chiffre_pose_le_filtre(self):
        self.racine = depot({"calc.py": "x = 1\n"})
        code, sortie = installer(self.racine, prive="chiffre", filtre="git-crypt")
        self.assertIn("memory/private/** filter=git-crypt", (self.racine / ".gitattributes").read_text())
        self.assertIn("filtre « git-crypt » non configuré", sortie)

    def test_la_politique_du_gabarit_reecrite(self):
        texte = installeur.politique_privee(gabarit("policy.toml"), "chiffre", None, False)
        self.assertIn('[private]\nmode = "chiffre"\nrequests = false\n', texte)
        self.assertNotIn("# [private]", texte)


class TestInstallationVerte(Base):
    def test_le_code_existant_entre_a_mesurer_et_l_installation_finit_verte(self):
        """B-0034, P1 : sur un projet qui a déjà du code, l'installation
        finissait en échec, faute de plafond de mutation."""
        self.racine = depot({"pyproject.toml": "[tool.pytest.ini_options]\n", "src/calc.py": "def f():\n    return 1\n"})
        code, sortie = installer(self.racine, "python-pytest")
        self.assertEqual(code, 0, sortie)
        self.assertIn('"src/calc.py" = { pending = true }',
                      (self.racine / config.FORMAT_ACTUEL.garde_fous).read_text())

    def test_l_installation_dit_les_outils_que_la_ci_installe(self):
        """B-0090 : la CI installe pytest, mais rien ne disait que
        l'environnement de l'agent en a besoin aussi ; le pilote l'a appris
        par un `verify` rouge."""
        self.racine = depot({"README.md": "# neuf\n"})
        code, sortie = installer(self.racine, "python-pytest")
        self.assertEqual(code, 0, sortie)
        etapes = sortie.split("Et maintenant :")[1]
        self.assertIn("donner à l'agent les outils que la CI installe : `python3 -m pip install pytest mutmut`, "
                      "là où il travaille ; en session cloud, dans le script d'installation de l'environnement",
                      etapes)
        # Un adaptateur sans outil à installer n'en dit rien.
        autre = depot({"calc.py": "x = 1\n"})
        self.addCleanup(shutil.rmtree, autre, ignore_errors=True)
        code, sortie = installer(autre, "python")
        self.assertEqual(code, 0, sortie)
        self.assertNotIn("outils que la CI installe", sortie)

    def test_l_installation_dit_quoi_faire_ensuite(self):
        """B-0034, P2 : l'audit ne montre que ce qui échoue ou avertit, puis
        les étapes de l'humain, dans l'ordre, chacune avec sa commande."""
        self.racine = depot({"calc.py": "x = 1\n"})
        code, sortie = installer(self.racine)
        self.assertRegex(sortie, r"… et \d+ autre\(s\) contrôle\(s\) sans rien à signaler")
        etapes = sortie.split("Et maintenant :")[1].strip().splitlines()
        self.assertIn("socle init --brief", etapes[0])
        self.assertIn("git commit", etapes[1])
        self.assertIn("ouvrir l'agent", etapes[2])

    def test_des_plafonds_deja_mesures_sont_repris(self):
        """B-0009, relevé par l'essai à blanc sur chess : les plafonds qu'un
        projet avait mesurés se perdaient à l'adoption, chaque module « à
        mesurer » jusqu'à un balayage de plusieurs heures."""
        self.racine = depot({"pyproject.toml": "[tool.pytest.ini_options]\n",
                             "src/calc.py": "def f():\n    return 1\n", "src/autre.py": "def g():\n    return 2\n"})
        dossier = Path(tempfile.mkdtemp(prefix="socle-plafonds-"))
        self.addCleanup(shutil.rmtree, dossier, ignore_errors=True)
        caps = dossier / "plafonds.toml"
        caps.write_text('[mutation.caps]\n"src/calc.py" = { max = 3, reason = "mesuré par le projet" }\n'
                        '"src/autre.py" = { max = 0 }\n"src/absent.py" = { max = 1 }\n')
        self.assertEqual(installeur.lire_plafonds(caps)["src/calc.py"], {"max": 3, "reason": "mesuré par le projet"})
        code, sortie = installer(self.racine, "python-pytest", adoption=True, plafonds=caps)
        self.assertEqual(code, 0, sortie)
        gf = (self.racine / config.FORMAT_ACTUEL.garde_fous).read_text()
        self.assertIn('"src/calc.py" = { max = 3, reason = "mesuré par le projet" }', gf)
        self.assertIn('"src/autre.py" = { max = 0, reason = "repris de plafonds.toml à l\'installation" }', gf)
        self.assertIn("plafonds de mutation repris de plafonds.toml : 2", sortie)
        self.assertIn("écartés, faute d'un module de ce nom qui porte du code : src/absent.py", sortie)

    def test_des_plafonds_illisibles_arretent_l_installation_avant_d_ecrire(self):
        self.racine = depot({"src/calc.py": "def f():\n    return 1\n"})
        dossier = Path(tempfile.mkdtemp(prefix="socle-plafonds-"))
        self.addCleanup(shutil.rmtree, dossier, ignore_errors=True)
        caps = dossier / "plafonds.toml"
        for texte, faute in (("[mutation.caps]\n\"src/calc.py\" = { max = -1 }\n", "entier positif ou nul"),
                             ("[autre]\n", "aucune table"), ("= faux", "illisible")):
            caps.write_text(texte)
            with self.assertRaises(ValueError) as e:
                installeur.lire_plafonds(caps)
            self.assertIn(faute, str(e.exception))
        import contextlib
        with contextlib.redirect_stderr(io.StringIO()) as erreurs:
            code, _ = installer(self.racine, "python-pytest", plafonds=caps)
        self.assertEqual(code, 2)
        self.assertIn("illisible", erreurs.getvalue())
        self.assertFalse((self.racine / ".socle").exists())

    def test_garde_fous_initiaux_sans_mutation(self):
        texte = installeur.garde_fous_initiaux(depot({"calc.py": "def f():\n    return 1\n"}),
                                               (MOTEUR / "socle/adapters/python.toml").read_text())
        self.assertNotIn("pending = true }", texte)


class TestMiseAJour(Base):
    def setUp(self):
        self.racine = depot({"calc.py": "x = 1\n"})
        installer(self.racine)

    def test_le_verrou_note_le_format(self):
        self.assertIn(f"format = {config.FORMAT}", (self.racine / config.FORMAT_ACTUEL.lock).read_text())

    def test_la_politique_changee_est_montree_jamais_ecrasee(self):
        p = self.racine / config.FORMAT_ACTUEL.politique
        p.write_text(p.read_text().replace("max_attempts = 3", "max_attempts = 5"))
        self.assertTrue(installeur.diff_politique(self.racine))
        code, sortie = installer(self.racine)
        self.assertIn("mise à jour : moteur", sortie)
        self.assertIn("+max_attempts = 3", sortie)
        self.assertIn("max_attempts = 5", p.read_text())

    def test_la_memoire_privee_s_ajoute_a_un_projet_installe(self):
        """P4 du relevé du parcours (B-0034) : l'option annonçait la mémoire
        privée sans écrire la politique, qui la laissait non configurée."""
        code, sortie = installer(self.racine, prive="compagnon", relecture="lots")
        politique = (self.racine / config.FORMAT_ACTUEL.politique).read_text()
        self.assertIn('[private]\nmode = "compagnon"\nreview = "lots"\nrequests = false\n', politique)
        self.assertIn("mémoire privée ajoutée à la politique", sortie)
        self.assertEqual(config.Projet.charger(self.racine).pol("private", "mode"), "compagnon")

    def test_une_memoire_privee_deja_choisie_n_est_pas_reecrite(self):
        installer(self.racine, prive="chiffre")
        installer(self.racine, prive="compagnon")
        self.assertEqual(config.Projet.charger(self.racine).pol("private", "mode"), "chiffre")

    def test_une_mise_a_jour_propose_d_abord_l_approbation(self):
        etapes = installeur.et_maintenant(self.racine, True, ["protege.fichiers", "docs.liens"])
        self.assertIn("socle approve --text", etapes[0])
        self.assertIn("1 contrôle(s) en échec ci-dessus (docs.liens)", etapes[1])
        self.assertIn('git commit -m "Mettre à jour le socle', etapes[2])
        self.assertFalse(any("socle init" in e for e in etapes))

    def test_une_installation_dit_de_proteger_la_branche(self):
        """B-0044, L2 (R1) : rien ne disait à l'humain d'exiger la CI avant
        de fusionner, sans quoi une CI rouge n'empêche rien."""
        etapes = installeur.et_maintenant(self.racine, False, [])
        protection = next(e for e in etapes if "protéger la branche par défaut" in e)
        self.assertIn("« Socle — verify, contrôles, auto-test »", protection)
        self.assertLess(etapes.index(protection), len(etapes) - 1)
        self.assertFalse(any("protéger la branche" in e for e in installeur.et_maintenant(self.racine, True, [])))


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
        d = next((self.racine / "memory/requests").glob("D-0001-*.md")).read_text()
        self.assertIn("Défaut : aucun", d)
        self.assertIn("Ce qui revient maintenant à l'agent", flux.getvalue())
        humain = flux.getvalue().split("Pour toi :")[1].split("Ce qui revient")[0]
        self.assertIn("la demande D-0001 doit être sur GitHub", humain)
        self.assertEqual(len(initialisation.pour_toi("D-0042")), 3)

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
        journal = next((self.racine / "memory/journal").glob("*.md")).read_text()
        self.assertIn("Document de cadrage archivé tel quel", journal)
        demande = next((self.racine / "memory/requests").glob("D-*.md")).read_text()
        self.assertIn("celui du document de cadrage", demande)

    def test_avec_une_memoire_privee_le_cadrage_s_archive_en_prive(self):
        """B-0044, L3 : le cadrage, d'où viennent les termes privés, était
        archivé en public même avec une mémoire privée."""
        self.racine = depot({})
        installer(self.racine, prive="chiffre")
        dossier = Path(tempfile.mkdtemp(prefix="socle-cadrages-"))
        self.addCleanup(shutil.rmtree, dossier, ignore_errors=True)
        doc = dossier / "cadrage.md"
        doc.write_text("# Cadrage\n\nLe projet Mistral.\n")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(initialisation.initialiser(self.charger(), cadrage=doc), 0)
        self.assertEqual((self.racine / "memory/private/archives/cadrage.md").read_text(), doc.read_text())
        self.assertFalse((self.racine / "memory/archives/cadrage.md").exists())
        journal = next((self.racine / "memory/private/journal").glob("*.md")).read_text()
        self.assertIn("zone=privee", journal)
        self.assertIn(f"## {'P'}J-", journal)

    def test_un_second_cadrage_n_ecrase_pas_le_premier(self):
        """B-0044, L1 : l'archive « telle quelle » était écrasée par un second
        document du même nom, et un nom avec une espace cassait sa référence."""
        self.racine = depot({})
        installer(self.racine)
        dossier = Path(tempfile.mkdtemp(prefix="socle-cadrages-"))
        self.addCleanup(shutil.rmtree, dossier, ignore_errors=True)
        doc = dossier / "mon cadrage.md"
        doc.write_text("# Premier\n")
        premiere, emp1 = initialisation.archiver_cadrage(self.racine, doc)
        self.assertNotIn(" ", premiere)
        self.assertEqual(initialisation.archiver_cadrage(self.racine, doc), (premiere, emp1))
        doc.write_text("# Second\n")
        seconde, emp2 = initialisation.archiver_cadrage(self.racine, doc)
        self.assertNotEqual(seconde, premiere)
        self.assertEqual((self.racine / premiere).read_text(), "# Premier\n")
        self.assertEqual((self.racine / seconde).read_text(), "# Second\n")

    def test_la_demande_de_depart_renvoie_au_fichier_d_instructions_qui_existe(self):
        """Quand l'installeur garde CLAUDE.md, lu par le projet, le lien vers
        AGENTS.md était mort."""
        self.racine = depot({"CLAUDE.md": "# Projet\n", "tests/test_doc.py": "open('CLAUDE.md').read()\n"})
        installer(self.racine)
        projet = self.charger()
        texte = initialisation.demande_de_depart(projet, "D-0009", initialisation.questions_de_depart(projet, None, False),
                                                 None, "rien du tout")
        self.assertIn("[CLAUDE.md](../../CLAUDE.md)", texte)

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

        from socle import cli, requests as demandes

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
        d = demandes.charger(self.racine, None, "memory/requests/D-0009-questions-de-depart.md", texte)
        self.assertEqual(demandes.linter(d, projet), [])
        self.assertEqual(d.reponses_possibles(), ["defauts", "reponses", "contexte-insuffisant"])
