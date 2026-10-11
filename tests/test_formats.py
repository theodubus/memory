"""B-0032 : les chemins d'un projet passent en anglais au format 2 de la
mémoire. Le moteur lit les deux formats, la migration renomme sans réécrire
la mémoire, et la CI d'une plage qui migre lit la base sous les noms de la
tête."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, contexte, controles_cliquet, controles_memoire, demandes, installeur, memoire, migrations, prive
from socle.rapport import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "moteur"


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestChemins(unittest.TestCase):
    def test_traduire_un_chemin_dans_les_deux_sens(self):
        paires = [("memoire/canonique.md", "memory/canonical.md"), ("memoire/actif.md", "memory/active.md"),
                  ("memoire/demandes/D-0001-x.reponse.toml", "memory/requests/D-0001-x.answer.toml"),
                  ("memoire/prive/termes.txt", "memory/private/terms.txt"),
                  (".socle/politique.toml", ".socle/policy.toml"), (".socle/garde-fous.toml", ".socle/guardrails.toml"),
                  (".socle/moteur/socle/cli.py", ".socle/engine/socle/cli.py"), ("docs/a.md", "docs/a.md"),
                  ("moteur/socle/cli.py", "moteur/socle/cli.py")]
        for un, deux in paires:
            with self.subTest(un=un):
                self.assertEqual(config.traduire(un, vers=2), deux)
                self.assertEqual(config.traduire(deux, vers=1), un)

    def test_un_chemin_qui_mele_les_deux_formats(self):
        self.assertEqual(config.sous_le_format("memory/demandes/D-0001.md", 2), "memory/requests/D-0001.md")
        self.assertEqual(config.sous_le_format("memoire/actif.md", 2), "memory/active.md")

    def test_le_miroir_prive(self):
        self.assertEqual(config.FORMAT_2.dans_prive("memory/canonical.md"), "memory/private/canonical.md")
        self.assertEqual(config.FORMAT_1.dans_prive("memoire/demandes"), "memoire/prive/demandes")

    def test_la_memoire_se_reconnait_sous_ses_deux_noms(self):
        for un, deux in (("memoire/journal/2026-10.md", "memory/journal/2026-10.md"),
                         ("memoire/prive/canonique.md", "memory/private/canonical.md")):
            self.assertEqual(memoire.couche_attendue(un), memoire.couche_attendue(deux))
        self.assertTrue(memoire.est_memoire("memory/active.md") and memoire.est_memoire("memoire/actif.md"))
        self.assertFalse(memoire.est_memoire("docs/memoire/x.md"))
        self.assertTrue(memoire.est_prive("memory/private/x.md"))
        self.assertEqual(memoire.hors_zone_privee("memory/private/requests/D-0001.md"), "requests/D-0001.md")
        self.assertEqual(memoire.chemins_de("memoire/actif.md"), config.FORMAT_1)
        self.assertEqual(memoire.chemins_de("memory/active.md"), config.FORMAT_2)

    def test_une_reponse_a_cote_de_sa_demande(self):
        self.assertEqual(demandes.chemin_reponse("memory/requests/D-0001-x.md"), "memory/requests/D-0001-x.answer.toml")
        self.assertEqual(demandes.chemin_reponse("memoire/demandes/D-0001-x.md"), "memoire/demandes/D-0001-x.reponse.toml")
        for r in ("memory/requests/D-0001-x.answer.toml", "memoire/demandes/D-0001-x.reponse.toml"):
            self.assertTrue(memoire.est_reponse(r))
            self.assertTrue(memoire.demande_de_reponse(r).endswith("D-0001-x.md"))

    def test_les_garde_fous_se_traduisent_cle_et_valeur(self):
        avant = {"budgets": {"memoire/actif.md": {"max_bytes": 6000}}, "tests": {"spec_paths": ["memoire/decisions/**"]}}
        self.assertEqual(controles_cliquet.traduire_profond(avant, 2),
                         {"budgets": {"memory/active.md": {"max_bytes": 6000}},
                          "tests": {"spec_paths": ["memory/decisions/**"]}})

    def test_une_ancre_ecrite_avant_la_migration(self):
        self.assertEqual(controles_memoire.ancre_au_format_2("politique-dautonomie-soclepolitiquetoml-x"),
                         "politique-dautonomie-soclepolicytoml-x")

    def test_les_chemins_d_un_texte(self):
        texte = ('protected = ["memoire/demandes/*.reponse.toml", ".socle/politique.toml"]\n'
                 "[lien](../memoire/actif.md), `memoire/`, /memoire/prive/, memoire.py, moteur/socle/x.py\n")
        self.assertEqual(migrations.traduire_texte(texte),
                         'protected = ["memory/requests/*.answer.toml", ".socle/policy.toml"]\n'
                         "[lien](../memory/active.md), `memory/`, /memory/private/, memoire.py, moteur/socle/x.py\n")


class Projet(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-format-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        config.oublier_formats()

    def vers_format_1(self):
        """Le même projet, tel qu'un socle d'avant B-0032 l'aurait posé."""
        git(self.racine, "add", "-A")
        for f in git(self.racine, "ls-files").split("\n"):
            if f and config.traduire(f, vers=1) != f:
                (self.racine / config.traduire(f, vers=1)).parent.mkdir(parents=True, exist_ok=True)
                git(self.racine, "mv", f, config.traduire(f, vers=1))
        for f in (".socle/politique.toml", ".socle/garde-fous.toml", ".socle/moteur.lock", ".github/CODEOWNERS"):
            p = self.racine / f
            texte = p.read_text()
            for deux, un in (("memory/requests", "memoire/demandes"), ("memory/active.md", "memoire/actif.md"),
                             ("memory/canonical.md", "memoire/canonique.md"), (".answer.toml", ".reponse.toml"),
                             ("memory/", "memoire/"), (".socle/policy.toml", ".socle/politique.toml"),
                             (".socle/adapter.toml", ".socle/adaptateur.toml"), (".socle/engine", ".socle/moteur"),
                             ("format = 2", "format = 1")):
                texte = texte.replace(deux, un)
            p.write_text(texte)
        shutil.rmtree(self.racine / "memory", ignore_errors=True)
        config.oublier_formats()


class TestDetection(Projet):
    def test_un_projet_neuf_est_au_format_2(self):
        self.assertEqual(config.chemins(self.racine), config.FORMAT_2)
        self.assertTrue((self.racine / ".socle/engine.lock").is_file())
        self.assertTrue((self.racine / "memory/canonical.md").is_file())
        self.assertEqual(prive.dossier(self.racine), "memory/private")
        self.assertEqual(prive.fichier_verrou(self.racine), ".socle/private.lock")
        self.assertEqual(prive.fichier_termes(self.racine), "memory/private/terms.txt")

    def test_un_projet_d_avant_se_lit_au_format_1(self):
        self.vers_format_1()
        projet = config.Projet.charger(self.racine)
        self.assertEqual(projet.chemins, config.FORMAT_1)
        self.assertTrue(projet.installe)
        self.assertIn("memoire/archives/**", projet.exclusions_docs())
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "format 1", "--no-verify")
        config.oublier_formats()
        self.assertEqual(config.chemins(self.racine, "HEAD"), config.FORMAT_1)


class TestMigration(Projet):
    def test_la_migration_renomme_et_la_ci_lit_la_base_sous_les_noms_de_la_tete(self):
        self.vers_format_1()
        (self.racine / "README.md").write_text("Voir `memoire/actif.md` et [le backlog](memoire/backlog.md).\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "format 1", "--no-verify")
        base = git(self.racine, "rev-parse", "HEAD").strip()
        lignes = migrations.migrer(self.racine, 1)
        self.assertTrue(any("memoire/ → memory/" in l for l in lignes), lignes)
        self.assertTrue((self.racine / ".socle/policy.toml").is_file())
        self.assertFalse((self.racine / "memoire").exists())
        self.assertIn("`memory/active.md`", (self.racine / "README.md").read_text())
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "migration", "--no-verify")
        config.oublier_formats()
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=base, tete="HEAD")
        self.assertTrue(ctx.migre)
        self.assertEqual(ctx.format_base, config.FORMAT_1)
        self.assertIn("memory/active.md", ctx.fichiers_base)
        self.assertIsNotNone(ctx.lire_base("memory/active.md"))
        r = Rapport()
        for f in (controles_cliquet.cliquet, controles_memoire.ajout_seul, controles_memoire.references):
            f(ctx, r)
        self.assertEqual([c.message for c in r.erreurs()], [])

    def test_l_ancien_chemin_d_une_entree_gelee_reste_valide(self):
        journal = next((self.racine / "memory/journal").glob("*.md"))
        journal.write_text(journal.read_text() + "\nVoir `memoire/actif.md` et fichier:memoire/backlog.md ici\n")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent")
        r = Rapport()
        controles_memoire.references(ctx, r)
        self.assertEqual([c.message for c in r.erreurs()], [])


if __name__ == "__main__":
    unittest.main()
