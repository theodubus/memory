import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, context as contexte, checks_memory as controles_memoire, memory as memoire
from socle.report import Rapport


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


class TestIndexAffiche(unittest.TestCase):
    """B-0037 : un sujet nouveau cite l'index qu'il a lu ; si un autre sujet
    se clôt ensuite, le refus conseille de relire l'index par
    `socle show --index backlog` et d'en citer l'empreinte. Cet index compte
    déjà le sujet qui cite : son empreinte doit être acceptée."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-index-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        self.backlog = self.racine / "memory/backlog.md"
        self.backlog.parent.mkdir(parents=True)
        self.backlog.write_text("<!-- socle: couche=backlog zone=publique -->\n# Backlog\n\n## B-0001 — Un sujet\n\n"
                                "> statut : ouvert · origine : fichier:memory/backlog.md\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        # Un sujet ajouté sur la branche, puis un autre qui lit l'index d'alors.
        lu0 = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        self.backlog.write_text(self.backlog.read_text() + "\n## B-0002 — Un sujet de la branche\n\n> statut : "
                                f"ouvert · origine : fichier:memory/backlog.md · lu : backlog@{lu0}\n")
        lu = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        self.backlog.write_text(self.backlog.read_text() + "\n## B-0003 — Un sujet nouveau\n\n> statut : ouvert · "
                                f"origine : fichier:memory/backlog.md · lu : backlog@{lu}\n")
        # B-0001 se clôt après la lecture : l'index que B-0002 citait change.
        self.backlog.write_text(self.backlog.read_text().replace(
            "> statut : ouvert · origine : fichier:memory/backlog.md\n",
            "> statut : fait · origine : fichier:memory/backlog.md · ref : fichier:memory/backlog.md\n", 1))
        self.perimee = lu

    def erreurs(self) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.base, tete=None)
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        return [c.message for c in r.erreurs("memoire.lectures")]

    def test_l_empreinte_perimee_est_refusee(self):
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn(f"backlog@{self.perimee}", erreurs[0])

    def test_l_empreinte_que_le_refus_conseille_est_acceptee(self):
        affichee = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        self.backlog.write_text(self.backlog.read_text().replace(f"backlog@{self.perimee}", f"backlog@{affichee}"))
        self.assertEqual(self.erreurs(), [])

    def test_l_index_affiche_reste_bon_quand_un_sujet_s_ajoute_apres(self):
        """Le cas de B-0042 : il cite l'index affiché, lui compris ; B-0043,
        ajouté ensuite, ne périme pas sa lecture, commitée ou non."""
        affichee = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        self.backlog.write_text(self.backlog.read_text().replace(f"backlog@{self.perimee}", f"backlog@{affichee}"))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "B-0003")
        lu = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        self.backlog.write_text(self.backlog.read_text() + "\n## B-0004 — Un sujet plus tard\n\n> statut : ouvert · "
                                f"origine : fichier:memory/backlog.md · lu : backlog@{lu}\n")
        self.assertEqual(self.erreurs(), [])
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "B-0004")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete="HEAD")
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        self.assertEqual([c.message for c in r.erreurs("memoire.lectures")], [])


class TestArchivage(unittest.TestCase):
    """Un sujet clos s'archive dans le journal avec sa preuve de lecture : la
    même entrée, déplacée, n'a pas à relire un index qui a changé depuis."""

    def setUp(self):
        from socle import archive as archivage

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

    def test_un_sujet_archive_garde_ses_sous_titres_et_son_ancre(self):
        """B-0044, L1 : seul le titre du sujet descendait d'un niveau ; son
        sous-titre devenait un frère et quittait l'entrée, et un lien vers
        l'ancre du sujet dans le backlog mourait à l'archivage."""
        backlog = self.racine / "memory/backlog.md"
        backlog.write_text(backlog.read_text().replace(
            "> statut : ouvert · origine : fichier:memory/backlog.md · lu : backlog@" + self.lu + "\n",
            "> statut : fait · origine : fichier:memory/backlog.md · lu : backlog@" + self.lu + " · ref : B-0002\n"
            "\nRésumé.\n\n### Détails\n\nLe détail du sujet.\n"))
        (self.racine / "LISEZMOI.md").write_text("Voir [le sujet](memory/backlog.md#b-0001--un-sujet).\n")
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()):
            self.archivage.archiver_backlog(config.Projet.charger(self.racine))
        mem = memoire.Memoire.charger(self.racine)
        archive = mem.entree("B-0001")
        self.assertTrue(archive.archivee)
        self.assertIn("Le détail du sujet.", archive.texte)
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent", tete=None)
        r = Rapport()
        controles_memoire.references(ctx, r)
        self.assertEqual([c.message for c in r.erreurs()], [])

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


class TestLectureUnifiee(unittest.TestCase):
    """ADR-0023, relevé de la passe de recul : une lecture d'index recopiée
    d'un sujet plus ancien du même fichier passait (D) ; et la CI, jugeant
    depuis une base plus ancienne que le hook avant push, refusait l'index
    lu au milieu de la plage (E)."""

    ENTETE = "<!-- socle: couche=backlog zone=publique -->\n# Backlog\n"

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-unifiee-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        self.backlog = self.racine / "memory/backlog.md"
        self.backlog.parent.mkdir(parents=True)
        self.backlog.write_text(self.ENTETE + self.sujet(1, ""))
        self.b0 = self.commit("base")

    @staticmethod
    def sujet(n: int, lu: str, statut: str = "ouvert") -> str:
        return f"\n## B-{n:04d} — Sujet {n}\n\n> statut : {statut} · origine : fichier:memory/backlog.md{lu}\n"

    def index(self) -> str:
        return memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")

    def commit(self, message) -> str:
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", message)
        return git(self.racine, "rev-parse", "HEAD").strip()

    def erreurs(self, base) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=base, tete="HEAD")
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        return [c.message for c in r.erreurs("memoire.lectures")]

    def test_une_lecture_recopiee_d_un_sujet_plus_ancien_est_refusee(self):
        vieux = self.index()
        self.backlog.write_text(self.backlog.read_text() + self.sujet(2, f" · lu : backlog@{vieux}"))
        base = self.commit("B-0002, après lecture")
        self.backlog.write_text(self.backlog.read_text() + self.sujet(3, f" · lu : backlog@{vieux}"))
        self.commit("B-0003, lecture recopiée")
        erreurs = self.erreurs(base)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn(f"backlog@{vieux}", erreurs[0])

    def test_le_verdict_ne_retrecit_pas_avec_une_base_plus_ancienne(self):
        self.backlog.write_text(self.backlog.read_text() + self.sujet(2, f" · lu : backlog@{self.index()}"))
        c1 = self.commit("B-0002")
        lu = self.index()  # lu après le push de c1
        texte = self.backlog.read_text().replace("statut : ouvert · origine : fichier:memory/backlog.md\n",
                                                 "statut : abandonné · origine : fichier:memory/backlog.md\n", 1)
        self.backlog.write_text(texte + self.sujet(3, f" · lu : backlog@{lu}"))
        self.commit("B-0001 abandonné, B-0003")
        self.assertEqual(self.erreurs(c1), [])       # le hook avant push
        self.assertEqual(self.erreurs(self.b0), [])  # la CI, depuis la branche par défaut

    def test_le_hook_juge_la_recopie_comme_le_controle(self):
        from socle import hooks

        vieux = self.index()
        self.backlog.write_text(self.backlog.read_text() + self.sujet(2, f" · lu : backlog@{vieux}"))
        self.commit("B-0002, après lecture")
        avant = self.backlog.read_text()
        projet = config.Projet.charger(self.racine)
        fautes = hooks.references_inventees(projet, "memory/backlog.md", avant,
                                            avant + self.sujet(3, f" · lu : backlog@{vieux}"))
        self.assertTrue(any(f"backlog@{vieux}" in f for f in fautes), fautes)
        self.assertEqual(hooks.references_inventees(projet, "memory/backlog.md", avant,
                                                    avant + self.sujet(3, f" · lu : backlog@{self.index()}")), [])


class TestModuleLectures(TestLectureUnifiee):
    """Les fonctions de `socle.lectures`, appelées directement."""

    def test_les_fonctions(self):
        from socle import readings as lectures

        lu0 = self.index()
        self.backlog.write_text(self.backlog.read_text() + self.sujet(2, f" · lu : backlog@{lu0}"))
        c1 = self.commit("B-0002")
        mem = memoire.Memoire.charger(self.racine)
        plage = lectures.Plage(self.racine, memoire.Memoire.charger(self.racine, self.b0), mem, [c1])
        lignes = self.backlog.read_text().splitlines()
        ligne = lambda titre: next(i for i, l in enumerate(lignes, start=1) if l.startswith(titre)) + 2
        soi = lectures.entree_englobante(mem, "memory/backlog.md", ligne("## B-0002"))
        self.assertEqual(soi.id, "B-0002")
        self.assertEqual(plage.parution("memory/backlog.md", f"backlog@{lu0}", soi), 0)
        self.assertEqual(plage.changeant("B"), [c1])
        self.assertTrue(lectures.index_lu(plage, "memory/backlog.md", soi, "backlog", lu0))
        self.assertFalse(lectures.index_lu(plage, "memory/backlog.md", soi, "backlog", "0badc0de"))
        b1 = memoire.empreinte_entree(mem.entree("B-0001"))
        self.assertTrue(lectures.entree_lue(plage, "memory/backlog.md", soi, "B-0001", b1))
        self.assertFalse(lectures.entree_lue(plage, "memory/backlog.md", soi, "B-0001", "0badc0de"))
        base = memoire.Memoire.charger(self.racine, c1)
        self.assertTrue(lectures.deja_citee(soi, f"backlog@{lu0}", base, ""))
        autre = lectures.entree_englobante(mem, "memory/backlog.md", ligne("## B-0001"))
        self.assertFalse(lectures.deja_citee(autre, f"backlog@{lu0}", base, ""))
        self.assertTrue(lectures.deja_citee(None, f"backlog@{lu0}", base, f"lu : backlog@{lu0}"))
