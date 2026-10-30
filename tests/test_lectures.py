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


def sujet(racine: Path, num: int, titre: str, meta: str):
    """Un sujet du backlog dans son fichier (ADR-0025)."""
    p = racine / f"memory/backlog/B-{num:04d}-sujet.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"<!-- socle: couche=backlog zone=publique -->\n# B-{num:04d} — {titre}\n\n> {meta}\n")
    return p


class TestIndexAffiche(unittest.TestCase):
    """B-0037 : un sujet nouveau cite l'index qu'il a lu ; si un autre sujet
    se clôt ensuite, le refus conseille de relire l'index par
    `socle show --index backlog` et d'en citer l'empreinte. Cet index compte
    déjà le sujet qui cite : son empreinte doit être acceptée."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-index-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        premier = sujet(self.racine, 1, "Un sujet", "statut : ouvert · origine : fichier:memory/backlog")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        # Un sujet ajouté sur la branche, puis un autre qui lit l'index d'alors.
        lu0 = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        sujet(self.racine, 2, "Un sujet de la branche", f"statut : ouvert · origine : fichier:memory/backlog · "
                                                        f"lu : backlog@{lu0}")
        lu = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        self.nouveau = sujet(self.racine, 3, "Un sujet nouveau", f"statut : ouvert · origine : fichier:memory/backlog "
                                                                 f"· lu : backlog@{lu}")
        # B-0001 se clôt après la lecture : l'index que B-0002 citait change.
        premier.write_text(premier.read_text().replace(
            "> statut : ouvert · origine : fichier:memory/backlog\n",
            "> statut : fait · origine : fichier:memory/backlog · ref : fichier:memory/backlog\n"))
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
        self.nouveau.write_text(self.nouveau.read_text().replace(f"backlog@{self.perimee}", f"backlog@{affichee}"))
        self.assertEqual(self.erreurs(), [])

    def test_l_index_affiche_reste_bon_quand_un_sujet_s_ajoute_apres(self):
        """Le cas de B-0042 : il cite l'index affiché, lui compris ; B-0043,
        ajouté ensuite, ne périme pas sa lecture, commitée ou non."""
        affichee = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        self.nouveau.write_text(self.nouveau.read_text().replace(f"backlog@{self.perimee}", f"backlog@{affichee}"))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "B-0003")
        lu = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        sujet(self.racine, 4, "Un sujet plus tard", f"statut : ouvert · origine : fichier:memory/backlog · "
                                                    f"lu : backlog@{lu}")
        self.assertEqual(self.erreurs(), [])
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "B-0004")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete="HEAD")
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        self.assertEqual([c.message for c in r.erreurs("memoire.lectures")], [])


class TestLectureRecopiee(unittest.TestCase):
    """Une preuve de lecture vaut pour l'entrée qui l'a écrite, pas pour une
    autre qui la recopie."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-recopie-"))
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "memory/backlog").mkdir(parents=True)
        lu = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        sujet(self.racine, 1, "Un sujet", f"statut : ouvert · origine : fichier:memory/backlog · lu : backlog@{lu}")
        lu2 = memoire.empreinte_index(memoire.Memoire.charger(self.racine), "backlog")
        sujet(self.racine, 2, "Un autre sujet, qui change l'index", f"statut : ouvert · origine : "
                                                                    f"fichier:memory/backlog · lu : backlog@{lu2}")
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
        b1_ = sujet(self.racine, 1, "Un sujet", "statut : ouvert · origine : fichier:memory/backlog")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        mem = memoire.Memoire.charger(self.racine)
        b1 = memoire.empreinte_entree(mem.entree("B-0001"))
        lu = memoire.empreinte_index(mem, "decisions")
        (self.racine / "memory/decisions/ADR-0001-une.md").write_text(
            adr(1, f" · lu : decisions@{lu}").replace("La décision 1.", f"Elle s'appuie sur B-0001@{b1}."))
        lu_b = memoire.empreinte_index(mem, "backlog")
        sujet(self.racine, 2, "Un autre", f"statut : ouvert · origine : fichier:memory/backlog · lu : backlog@{lu_b}")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "décision et sujet")
        # Ensuite, B-0001 se clôt : son texte et l'index du backlog changent.
        b1_.write_text(b1_.read_text().replace("statut : ouvert · origine : fichier:memory/backlog\n",
                                               "statut : fait · origine : fichier:memory/backlog · ref : ADR-0001\n"))
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
    d'un sujet plus ancien passait (D) ; et la CI, jugeant depuis une base
    plus ancienne que le hook avant push, refusait l'index lu au milieu de
    la plage (E)."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-unifiee-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        self.ecrire(1, "")
        self.b0 = self.commit("base")

    @staticmethod
    def chemin(n: int) -> str:
        return f"memory/backlog/B-{n:04d}-sujet-{n}.md"

    @staticmethod
    def sujet(n: int, lu: str, statut: str = "ouvert") -> str:
        return (f"<!-- socle: couche=backlog zone=publique -->\n# B-{n:04d} — Sujet {n}\n\n"
                f"> statut : {statut} · origine : fichier:memory/backlog{lu}\n")

    def ecrire(self, n: int, lu: str, statut: str = "ouvert") -> Path:
        p = self.racine / self.chemin(n)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.sujet(n, lu, statut))
        return p

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
        self.ecrire(2, f" · lu : backlog@{vieux}")
        base = self.commit("B-0002, après lecture")
        self.ecrire(3, f" · lu : backlog@{vieux}")
        self.commit("B-0003, lecture recopiée")
        erreurs = self.erreurs(base)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn(f"backlog@{vieux}", erreurs[0])

    def test_le_verdict_ne_retrecit_pas_avec_une_base_plus_ancienne(self):
        self.ecrire(2, f" · lu : backlog@{self.index()}")
        c1 = self.commit("B-0002")
        lu = self.index()  # lu après le push de c1
        self.ecrire(1, "", "abandonné")
        self.ecrire(3, f" · lu : backlog@{lu}")
        self.commit("B-0001 abandonné, B-0003")
        self.assertEqual(self.erreurs(c1), [])       # le hook avant push
        self.assertEqual(self.erreurs(self.b0), [])  # la CI, depuis la branche par défaut

    def test_le_hook_juge_la_recopie_comme_le_controle(self):
        from socle import hooks

        vieux = self.index()
        self.ecrire(2, f" · lu : backlog@{vieux}")
        self.commit("B-0002, après lecture")
        projet = config.Projet.charger(self.racine)
        fautes = hooks.references_inventees(projet, self.chemin(3), "", self.sujet(3, f" · lu : backlog@{vieux}"))
        self.assertTrue(any(f"backlog@{vieux}" in f for f in fautes), fautes)
        self.assertEqual(hooks.references_inventees(projet, self.chemin(3), "",
                                                    self.sujet(3, f" · lu : backlog@{self.index()}")), [])


class TestModuleLectures(TestLectureUnifiee):
    """Les fonctions de `socle.lectures`, appelées directement."""

    def test_les_fonctions(self):
        from socle import readings as lectures

        lu0 = self.index()
        self.ecrire(2, f" · lu : backlog@{lu0}")
        c1 = self.commit("B-0002")
        mem = memoire.Memoire.charger(self.racine)
        plage = lectures.Plage(self.racine, memoire.Memoire.charger(self.racine, self.b0), mem, [c1])
        deux, un = self.chemin(2), self.chemin(1)
        soi = lectures.entree_englobante(mem, deux, 4)
        self.assertEqual(soi.id, "B-0002")
        self.assertEqual(plage.parution(deux, f"backlog@{lu0}", soi), 0)
        self.assertEqual(plage.changeant("B"), [c1])
        self.assertTrue(lectures.index_lu(plage, deux, soi, "backlog", lu0))
        self.assertFalse(lectures.index_lu(plage, deux, soi, "backlog", "0badc0de"))
        b1 = memoire.empreinte_entree(mem.entree("B-0001"))
        self.assertTrue(lectures.entree_lue(plage, deux, soi, "B-0001", b1))
        self.assertFalse(lectures.entree_lue(plage, deux, soi, "B-0001", "0badc0de"))
        base = memoire.Memoire.charger(self.racine, c1)
        self.assertTrue(lectures.deja_citee(soi, f"backlog@{lu0}", base, ""))
        autre = lectures.entree_englobante(mem, un, 4)
        self.assertFalse(lectures.deja_citee(autre, f"backlog@{lu0}", base, ""))
        self.assertTrue(lectures.deja_citee(None, f"backlog@{lu0}", base, f"lu : backlog@{lu0}"))


class TestDecisionEnSeance(unittest.TestCase):
    """B-0100 : la question d'une décision en séance recopie ce que l'humain a
    lu ; elle citait ADR-0031 sans empreinte, et sa réponse, protégée, ne
    laissait plus la corriger."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-seance-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "memory/decisions").mkdir(parents=True)
        (self.racine / "memory/decisions/ADR-0001-une.md").write_text(adr(1, ""))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        (self.racine / "memory/requests").mkdir(parents=True)

    def demande(self, titre: str, forme: str, corps: str):
        (self.racine / "memory/requests/D-0001-une.md").write_text(
            f"<!-- socle: couche=demandes zone=publique -->\n# D-0001 — {titre}\n\n"
            f"> date : 2026-10-30{forme}\n\n{corps}")

    def erreurs(self) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete=None)
        r = Rapport()
        controles_memoire.lectures(ctx, r)
        return [c.message for c in r.erreurs("memoire.lectures")]

    def test_sans_question_de_seance_ne_retire_que_la_question_d_une_seance(self):
        seance = ("# D-0001 — Titre\n\n> date : 2026-10-30 · forme : séance\n\n"
                  "## Question posée\n\nLa question (ADR-0001).\n\n## Suite\n\nLe reste.\n")
        texte = controles_memoire.sans_question_de_seance(seance)
        self.assertNotIn("ADR-0001", texte)
        self.assertIn("Le reste.", texte)
        en_file = seance.replace(" · forme : séance", "")
        self.assertEqual(controles_memoire.sans_question_de_seance(en_file), en_file)

    def test_la_question_d_une_seance_n_a_pas_a_prouver_ses_lectures(self):
        self.demande("Retirer un outil", " · forme : séance",
                     "## Question posée\n\nRetirer l'outil, la règle (ADR-0001) restant ?\n")
        self.assertEqual(self.erreurs(), [])

    def test_hors_de_la_question_la_lecture_se_prouve_encore(self):
        self.demande("Retirer ce que dit ADR-0001", " · forme : séance",
                     "## Question posée\n\nRetirer l'outil ?\n")
        self.assertTrue(any("ADR-0001" in e for e in self.erreurs()))
        # Une demande posée en file prouve ce que sa question cite.
        self.demande("Retirer un outil", "", "## Question posée\n\nRetirer l'outil (ADR-0001) ?\n")
        self.assertTrue(any("ADR-0001" in e for e in self.erreurs()))
