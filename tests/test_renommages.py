"""ADR-0027 (B-0045) : les noms de fichiers et les commandes du socle passent
en anglais, et la mémoire qui ne se réécrit pas garde les chemins d'avant le
renommage."""

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from socle import cli, config, context as contexte, checks_memory as controles_memoire, hooks
from socle import utils as outils
from socle.checks_ratchet import assouplissements
from tests.test_bascule import Projet, git

DOCMAP = {"docmap": [{"code": ["src/vieux.py", "src/outils/*.py"], "docs": ["docs/vieux.md"]}],
          "values": [{"name": "n", "file": "src/vieux.py", "regex": "N = (\\d+)"}]}


class TestRenommagesDeGit(unittest.TestCase):
    """Un dépôt jetable : un fichier renommé et récrit au fil des commits,
    puis renommé encore dans l'arbre de travail."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-renommages-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "a.py").write_text("".join(f"def f{i}():\n    return {i}\n" for i in range(20)))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "a", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        git(self.racine, "mv", "a.py", "b.py")
        git(self.racine, "commit", "-qm", "b", "--no-verify")
        # Récrit aux trois quarts : d'un bloc depuis la base, git ne
        # l'apparierait plus ; commit par commit, si.
        texte = (self.racine / "b.py").read_text().splitlines(keepends=True)
        (self.racine / "b.py").write_text("".join(texte[:10]) + "".join(f"def g{i}():\n    pass\n" for i in range(15)))
        git(self.racine, "commit", "-qam", "récrit", "--no-verify")
        git(self.racine, "mv", "b.py", "c.py")

    def test_les_renommages_se_composent_jusqu_a_l_arbre_de_travail(self):
        self.assertEqual(outils.renommes(self.racine, self.base), {"a.py": "c.py"})
        tete = git(self.racine, "rev-parse", "HEAD").strip()
        self.assertEqual(outils.renommes(self.racine, self.base, tete), {"a.py": "b.py"})

    def test_les_lignes_changees_d_un_fichier_renomme(self):
        # Les cinq premières fonctions n'ont pas bougé depuis la base.
        changees = outils.lignes_changees(self.racine, self.base, None, "c.py", "a.py")
        self.assertEqual(min(changees), 11)
        self.assertIsNone(outils.lignes_changees(self.racine, self.base, None, "c.py"))

    def test_le_contexte_les_donne(self):
        ctx = contexte.Contexte(config.Projet.charger(self.racine), base=self.base)
        self.assertEqual(ctx.renommes, {"a.py": "c.py"})


class TestFusionDUnePullRequest(unittest.TestCase):
    """La CI d'une pull request juge la fusion que GitHub fabrique : son
    premier parent est la base, le second la branche. Parcourue en premier
    parent, la plage n'était que cette fusion, d'un bloc, et un fichier
    renommé puis récrit sur la branche n'y était plus reconnu."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-fusion-pr-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "a.py").write_text("".join(f"def f{i}():\n    return {i}\n" for i in range(20)))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "a", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        git(self.racine, "checkout", "-q", "-b", "branche")
        git(self.racine, "mv", "a.py", "b.py")
        git(self.racine, "commit", "-qm", "b", "--no-verify")
        texte = (self.racine / "b.py").read_text().splitlines(keepends=True)
        (self.racine / "b.py").write_text("".join(texte[:10]) + "".join(f"def g{i}():\n    pass\n" for i in range(15)))
        git(self.racine, "commit", "-qam", "récrit", "--no-verify")
        git(self.racine, "checkout", "-q", "--detach", self.base)
        git(self.racine, "merge", "-q", "--no-ff", "--no-edit", "branche")
        self.fusion = git(self.racine, "rev-parse", "HEAD").strip()

    def test_la_fusion_d_une_pull_request_suit_la_branche(self):
        self.assertEqual(outils.renommes(self.racine, self.base, self.fusion), {"a.py": "b.py"})

    def test_sur_l_arbre_de_travail_aussi(self):
        self.assertEqual(outils.renommes(self.racine, self.base), {"a.py": "b.py"})


class TestCliquetRenomme(unittest.TestCase):
    RENOMMES = {"src/vieux.py": "src/neuf.py", "src/outils/a.py": "src/utils/a.py", "docs/vieux.md": "docs/neuf.md"}
    AVANT = ["src/vieux.py", "src/outils/a.py", "src/outils/b.py", "docs/vieux.md"]

    def apres(self, code, docs=("docs/neuf.md",), fichier="src/neuf.py"):
        return {"docmap": [{"code": code, "docs": list(docs)}],
                "values": [{"name": "n", "file": fichier, "regex": "N = (\\d+)"}]}

    def test_une_correspondance_qui_suit_ses_fichiers_n_assouplit_rien(self):
        apres = self.apres(["src/neuf.py", "src/utils/*.py", "src/outils/*.py"])
        self.assertEqual(assouplissements(DOCMAP, apres, renommes=self.RENOMMES, fichiers_avant=self.AVANT), [])

    def test_sans_les_renommages_c_est_un_retrait(self):
        apres = self.apres(["src/neuf.py", "src/utils/*.py", "src/outils/*.py"])
        self.assertEqual([c for c, _ in assouplissements(DOCMAP, apres)],
                         ['docmap "src/vieux.py"', 'docmap "src/outils/*.py"', 'values "n"'])

    def test_un_fichier_laisse_hors_de_la_correspondance_reste_un_retrait(self):
        # `src/outils/b.py` n'a pas changé de nom et plus rien ne le couvre.
        apres = self.apres(["src/neuf.py", "src/utils/*.py"])
        self.assertEqual([c for c, _ in assouplissements(DOCMAP, apres, renommes=self.RENOMMES, fichiers_avant=self.AVANT)],
                         ['docmap "src/outils/*.py"'])

    def test_une_doc_de_plus_reste_un_assouplissement(self):
        apres = self.apres(["src/neuf.py", "src/utils/*.py", "src/outils/*.py"], docs=("docs/neuf.md", "README.md"))
        self.assertIn('docmap "src/vieux.py"',
                      [c for c, _ in assouplissements(DOCMAP, apres, renommes=self.RENOMMES, fichiers_avant=self.AVANT)])

    def test_une_correspondance_dont_seule_la_doc_est_renommee_n_assouplit_rien(self):
        avant = {"docmap": [{"code": ["src/a.py"], "docs": ["docs/vieux.md"]}]}
        apres = {"docmap": [{"code": ["src/a.py"], "docs": ["docs/neuf.md"]}]}
        self.assertEqual(assouplissements(avant, apres, renommes={"docs/vieux.md": "docs/neuf.md"},
                                          fichiers_avant=["src/a.py", "docs/vieux.md"]), [])
        # Une doc de plus que la doc renommée reste un assouplissement.
        apres = {"docmap": [{"code": ["src/a.py"], "docs": ["docs/neuf.md", "README.md"]}]}
        self.assertEqual([c for c, _ in assouplissements(avant, apres, renommes={"docs/vieux.md": "docs/neuf.md"},
                                                         fichiers_avant=["src/a.py", "docs/vieux.md"])],
                         ['docmap "src/a.py"'])

    def test_une_valeur_liee_suit_son_fichier_et_rien_d_autre(self):
        apres = self.apres(["src/neuf.py", "src/utils/*.py", "src/outils/*.py"], fichier="src/autre.py")
        self.assertEqual([c for c, _ in assouplissements(DOCMAP, apres, renommes=self.RENOMMES, fichiers_avant=self.AVANT)],
                         ['values "n"'])


class TestCommandesHumaines(unittest.TestCase):
    def test_une_commande_de_l_humain_se_reconnait_sous_son_nom(self):
        self.assertEqual(hooks.INSTALLER_PRIVE.search("python3 .socle/socle private install --repo x").group(0),
                         "private install")
        self.assertEqual(hooks.COMMANDES_HUMAINES.search("python3 .socle/socle reviewed --by x").group(0), "reviewed")
        self.assertIsNone(hooks.INSTALLER_PRIVE.search("python3 .socle/socle private lock"))


class TestCouchesGelees(Projet):
    """Un fichier renommé après qu'une entrée de journal l'a cité."""

    def setUp(self):
        super().setUp()
        # Le dossier reste : un chemin ne se juge que sous une racine du dépôt.
        (self.racine / "scripts").mkdir()
        (self.racine / "scripts/vieux.py").write_text("x = 1\n")
        (self.racine / "scripts/autre.py").write_text("y = 1\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "un outil", "--no-verify")
        git(self.racine, "mv", "scripts/vieux.py", "scripts/old.py")
        git(self.racine, "commit", "-qm", "renommé", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def citer(self, fichier: str, texte: str):
        p = self.racine / fichier
        p.write_text(p.read_text().rstrip("\n") + "\n" + texte)

    def test_le_journal_garde_un_chemin_qui_a_existe(self):
        journal = next((self.racine / "memory/journal").glob("*.md")).relative_to(self.racine)
        self.citer(str(journal), "\n## J-2026-10-13-Z — Un outil\n\n"
                                 "Écrit dans `scripts/vieux.py`, voir [le source](../../scripts/vieux.py) "
                                 "et fichier:scripts/vieux.py.\n")
        self.assertEqual(self.erreurs(), [])

    def test_un_chemin_qui_n_a_jamais_existe_reste_refuse(self):
        journal = next((self.racine / "memory/journal").glob("*.md")).relative_to(self.racine)
        self.citer(str(journal), "\n## J-2026-10-13-Z — Un outil\n\nÉcrit dans `scripts/jamais.py`.\n")
        self.assertEqual(self.erreurs(), ["chemin cité inexistant : `scripts/jamais.py`"])

    def test_une_reference_d_une_couche_gelee(self):
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.base)
        self.assertIsNotNone(controles_memoire.verifier_ref(ctx, "fichier", "scripts/vieux.py"))
        self.assertIsNone(controles_memoire.verifier_ref(ctx, "fichier", "scripts/vieux.py", historique=True))
        self.assertIsNotNone(controles_memoire.verifier_ref(ctx, "fichier", "scripts/jamais.py", historique=True))

    def test_un_lien_relatif_se_lit_depuis_l_ancien_nom_de_son_fichier(self):
        # Écrite ailleurs, la décision a rejoint la mémoire : son lien
        # relatif menait à `scripts/autre.py` depuis son ancien dossier.
        (self.racine / "notes").mkdir()
        (self.racine / "notes/ADR-0002-ancienne.md").write_text(
            "<!-- socle: couche=decisions zone=publique -->\n# ADR-0002 — Ancienne\n\n"
            "> statut : acceptée · date : 2026-10-11\n\nVoir [l'outil](../scripts/autre.py).\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "une note", "--no-verify")
        git(self.racine, "mv", "notes/ADR-0002-ancienne.md", "memory/decisions/ADR-0002-ancienne.md")
        git(self.racine, "commit", "-qm", "dans la mémoire", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        self.assertEqual(self.erreurs(), [])
        # Le même lien, dans un fichier qui n'a jamais eu d'autre nom, est mort.
        (self.racine / "memory/decisions/ADR-0003-neuve.md").write_text(
            "<!-- socle: couche=decisions zone=publique -->\n# ADR-0003 — Neuve\n\n"
            "> statut : acceptée · date : 2026-10-11\n\nVoir [l'outil](../scripts/autre.py).\n")
        self.assertIn("lien mort : ../scripts/autre.py", self.erreurs())

    def test_le_contexte_lit_la_base(self):
        git(self.racine, "mv", "scripts/old.py", "scripts/neuf.py")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.base)
        self.assertIn("scripts/old.py", ctx.fichiers_base)
        self.assertNotIn("scripts/neuf.py", ctx.fichiers_base)
        self.assertEqual(ctx.lire_base("scripts/old.py"), "x = 1\n")
        self.assertIsNone(ctx.lire_base("scripts/neuf.py"))

    def test_un_chemin_barre_ne_se_juge_pas(self):
        """B-0087, relevé sur chess : un chemin barré dit qu'il n'existe plus,
        et le contrôle le refusait comme un chemin vivant."""
        self.citer("memory/active.md", "\nL'outil vivait dans <s>`scripts/jamais.py`</s>, puis "
                                       "~~`scripts/plus.py`~~ ; voir <del>[l'ancien](../scripts/jamais.py)</del>.\n")
        self.assertEqual(self.erreurs(), [])
        self.citer("memory/active.md", "\nEt `scripts/jamais.py`, qui n'est pas barré.\n")
        self.assertEqual(self.erreurs(), ["chemin cité inexistant : `scripts/jamais.py`"])

    def test_le_chantier_actif_suit_le_renommage(self):
        # Le chantier actif se réécrit : il cite le nom d'aujourd'hui.
        self.citer("memory/active.md", "\nL'outil vit dans `scripts/vieux.py`.\n")
        self.assertEqual(self.erreurs(), ["chemin cité inexistant : `scripts/vieux.py`"])


class TestSousLeursModulesRenommes(Projet):
    """Les commandes dont seul l'import du module a changé de nom : elles
    marchent sous le nouveau."""

    def sortie(self, f, **kw):
        from argparse import Namespace

        with contextlib.redirect_stdout(io.StringIO()) as s:
            code = f(Namespace(root=str(self.racine), **kw))
        return code, s.getvalue()

    def test_l_etat_l_identifiant_l_empreinte_et_l_archivage(self):
        code, sortie = self.sortie(cli.cmd_state, short=True)
        self.assertEqual(code, 0)
        self.assertIn("commit", sortie)
        self.assertEqual(self.sortie(cli.cmd_next_id, type="backlog", private=False), (0, "B-0002\n"))
        code, sortie = self.sortie(cli.cmd_fingerprint, files=["calc.py"])
        self.assertTrue(sortie.rstrip().endswith("calc.py"), sortie)
        self.assertEqual(self.sortie(cli.cmd_archive)[0], 0)

    def test_le_demarrage_de_session(self):
        with contextlib.redirect_stdout(io.StringIO()) as s:
            self.assertEqual(hooks.session_start(config.Projet.charger(self.racine), {}), 0)
        self.assertIn("état dérivé", s.getvalue())

    def test_l_auto_test_sous_sa_commande(self):
        self.assertIs(cli.analyseur()[0].parse_args(["selftest"]).f, cli.cmd_selftest)


class TestEtageCi(unittest.TestCase):
    def test_un_projet_sain_passe_l_etage_ci_de_l_auto_test(self):
        from socle import selftest as autotest

        import socle

        a = autotest.Atelier(Path(socle.__file__).resolve().parent.parent, False)
        self.addCleanup(a.nettoyer)
        a.preparer()
        self.assertEqual(autotest.etage_ci(a, a.clone()), "")


if __name__ == "__main__":
    unittest.main()
