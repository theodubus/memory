import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, contexte, controles_memoire, memoire
from socle.rapport import Rapport


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


def adr(num: int, lu: str) -> str:
    return (f"<!-- socle: couche=decisions zone=publique -->\n# ADR-{num:04d} — Décision {num}\n\n"
            f"> statut : acceptée · date : 2026-10-10{lu}\n\n## Décision\n\nLa décision {num}.\n")


class TestLecturesSuccessives(unittest.TestCase):
    """Une branche ajoute trois décisions, chacune après avoir lu l'index tel
    qu'il était : l'ajout des suivantes ne périme pas la lecture des
    premières."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-lectures-"))
        git(self.racine, "init", "-q", "-b", "main")
        self.decisions = self.racine / "memory/decisions"
        self.decisions.mkdir(parents=True)
        (self.decisions / "ADR-0001-une.md").write_text(adr(1, ""))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        for num in (2, 3, 4):
            lu = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "decisions")
            (self.decisions / f"ADR-{num:04d}-suivante.md").write_text(adr(num, f" · lu : decisions@{lu}"))

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def erreurs(self) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete=None)
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        return [c.message for c in r.erreurs("memoire.lectures")]

    def test_chaque_lecture_reste_valide(self):
        self.assertEqual(self.erreurs(), [])

    def test_une_empreinte_inventee_reste_refusee(self):
        p = self.decisions / "ADR-0003-suivante.md"
        p.write_text(adr(3, " · lu : decisions@0badc0de"))
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("decisions@0badc0de", erreurs[0])


class TestArchivage(unittest.TestCase):
    """Un sujet clos s'archive dans le journal avec sa preuve de lecture : la
    même entrée, déplacée, n'a pas à relire un index qui a changé depuis."""

    def setUp(self):
        from socle import archivage

        self.archivage = archivage
        self.racine = Path(tempfile.mkdtemp(prefix="socle-archivage-"))
        git(self.racine, "init", "-q", "-b", "main")
        backlog = self.racine / "memory/backlog.md"
        backlog.parent.mkdir(parents=True)
        backlog.write_text("<!-- socle: couche=backlog zone=publique -->\n# Backlog\n")
        lu = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        backlog.write_text(backlog.read_text() + "\n## B-0001 — Un sujet\n\n> statut : ouvert · origine : "
                           f"fichier:memory/backlog.md · lu : backlog@{lu}\n")
        lu2 = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        backlog.write_text(backlog.read_text() + "\n## B-0002 — Un autre sujet, qui change l'index\n\n> statut : "
                           f"ouvert · origine : fichier:memory/backlog.md · lu : backlog@{lu2}\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        self.lu = lu

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def erreurs(self) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete=None)
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        return [c.message for c in r.erreurs("memoire.lectures")]

    def test_un_sujet_archive_garde_sa_lecture(self):
        backlog = self.racine / "memory/backlog.md"
        backlog.write_text(backlog.read_text().replace(
            "> statut : ouvert · origine : fichier:memory/backlog.md · lu : backlog@" + self.lu,
            "> statut : fait · origine : fichier:memory/backlog.md · lu : backlog@" + self.lu + " · ref : B-0002"))
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()):
            self.archivage.archiver_backlog(config.Projet.charger(self.racine))
        journal = next((self.racine / "memory/journal").glob("*.md")).read_text()
        self.assertIn(f"backlog@{self.lu}", journal)
        self.assertEqual(self.erreurs(), [])

    def creer_puis_archiver(self, lu: str):
        """Un sujet créé sur la branche (commité), puis un autre qui change
        l'index, puis le premier clos et archivé au journal."""
        backlog = self.racine / "memory/backlog.md"
        backlog.write_text(backlog.read_text() + "\n## B-0003 — Créé sur la branche\n\n> statut : ouvert · origine : "
                           f"fichier:memory/backlog.md · lu : backlog@{lu}\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "B-0003")
        lu4 = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        backlog.write_text(backlog.read_text() + "\n## B-0004 — Un de plus\n\n> statut : ouvert · origine : "
                           f"fichier:memory/backlog.md · lu : backlog@{lu4}\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "B-0004")
        backlog.write_text(backlog.read_text().replace(f"lu : backlog@{lu}\n", f"lu : backlog@{lu} · ref : B-0004\n")
                           .replace("## B-0003 — Créé sur la branche\n\n> statut : ouvert",
                                    "## B-0003 — Créé sur la branche\n\n> statut : fait"))
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()):
            self.archivage.archiver_backlog(config.Projet.charger(self.racine))

    def test_un_sujet_cree_puis_archive_sur_la_branche_garde_sa_lecture(self):
        lu = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        self.creer_puis_archiver(lu)
        self.assertEqual(self.erreurs(), [])

    def test_une_lecture_inventee_reste_refusee_meme_archivee(self):
        self.creer_puis_archiver("0badc0de")
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("backlog@0badc0de", erreurs[0])

    def test_une_lecture_recopiee_dans_une_autre_entree_reste_refusee(self):
        journal = self.racine / "memory/journal/2026-10.md"
        journal.parent.mkdir(parents=True)
        journal.write_text("<!-- socle: couche=journal zone=publique -->\n# Journal — 2026-10\n\n"
                           "## J-2026-10-11-A — Une entrée qui recopie une vieille lecture\n\n"
                           f"> type : décision · ref : B-0002 · lu : backlog@{self.lu}\n")
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn(f"backlog@{self.lu}", erreurs[0])

if __name__ == "__main__":
    unittest.main()


class TestCitationsDeLaPlage(unittest.TestCase):
    """Une citation écrite plus tôt sur la branche vaut pour la version
    qu'elle a lue, même si l'entrée citée change ensuite : une demande
    répondue est gelée et ne pourrait pas suivre."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-plage-"))
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "memory/decisions").mkdir(parents=True)
        (self.racine / "memory/backlog.md").write_text(
            "<!-- socle: couche=backlog zone=publique -->\n# Backlog\n\n"
            "## B-0001 — Un sujet\n\n> statut : ouvert · origine : fichier:memory/backlog.md\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        mem = memoire.Memoire.charger(self.racine)
        b1 = memoire.empreinte_entree(mem.entree("B-0001"))
        lu = memoire.empreinte_index(mem, "decisions")
        (self.racine / "memory/decisions/ADR-0001-une.md").write_text(
            adr(1, f" · lu : decisions@{lu}").replace("La décision 1.", f"Elle s'appuie sur B-0001@{b1}."))
        backlog = self.racine / "memory/backlog.md"
        lu_b = memoire.empreinte_index(mem, "backlog")
        backlog.write_text(backlog.read_text() + f"\n## B-0002 — Un autre\n\n> statut : ouvert · origine : fichier:memory/backlog.md · lu : backlog@{lu_b}\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "décision et sujet")
        # Ensuite, B-0001 se clôt : son texte et l'index du backlog changent.
        backlog.write_text(backlog.read_text().replace("statut : ouvert · origine : fichier:memory/backlog.md\n",
                                                       "statut : fait · origine : fichier:memory/backlog.md · ref : ADR-0001\n", 1))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "clôture")

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def test_les_citations_restent_valides(self):
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete=None)
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        self.assertEqual([c.message for c in r.erreurs()], [])

    def test_une_empreinte_qui_n_a_jamais_existe_reste_refusee(self):
        adr_ = self.racine / "memory/decisions/ADR-0001-une.md"
        adr_.write_text(re.sub(r"B-0001@[0-9a-f]{8}", "B-0001@0badc0de", adr_.read_text()))
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete=None)
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        self.assertEqual(len(r.erreurs()), 1)
        self.assertIn("B-0001@0badc0de", r.erreurs()[0].message)

    def test_une_citation_neuve_d_une_version_perimee_est_refusee(self):
        # La version de B-0001 citée a existé dans la plage, mais la citation
        # est écrite maintenant, après la clôture : elle a lu une version
        # qui n'était plus la bonne.
        mem = memoire.Memoire.charger(self.racine, self.base)
        ancienne = memoire.empreinte_entree(mem.entree("B-0001"))
        journal = self.racine / "memory/journal/2026-10.md"
        journal.parent.mkdir(parents=True)
        journal.write_text("<!-- socle: couche=journal zone=publique -->\n# Journal\n\n"
                           f"## J-2026-10-10-A — Constat\n\nVoir B-0001@{ancienne}.\n")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete=None)
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        self.assertEqual(len(r.erreurs()), 1, [c.message for c in r.erreurs()])
        self.assertIn(f"B-0001@{ancienne}", r.erreurs()[0].message)


if __name__ == "__main__":
    unittest.main()
