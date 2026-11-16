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

    def journal(self) -> tuple[str, str]:
        """Le fichier du journal que l'installeur a posé, nommé d'après le mois
        en cours, et un identifiant daté de ce mois : un identifiant d'un autre
        mois y serait refusé (le test échouait depuis le 1er novembre)."""
        journal = next((self.racine / "memory/journal").glob("*.md")).relative_to(self.racine)
        return str(journal), f"J-{journal.stem[:7]}-13-Z"

    def test_le_journal_garde_un_chemin_qui_a_existe(self):
        journal, ident = self.journal()
        self.citer(journal, f"\n## {ident} — Un outil\n\n"
                                 "Écrit dans `scripts/vieux.py`, voir [le source](../../scripts/vieux.py) "
                                 "et fichier:scripts/vieux.py.\n")
        self.assertEqual(self.erreurs(), [])

    def test_un_chemin_qui_n_a_jamais_existe_reste_refuse(self):
        journal, ident = self.journal()
        self.citer(journal, f"\n## {ident} — Un outil\n\nÉcrit dans `scripts/jamais.py`.\n")
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

    def test_une_demande_cite_un_fichier_protege_qu_elle_propose_d_ajouter(self):
        """B-0127 : une mise à jour du socle pose un skill nouveau, protégé ;
        la demande qui le cite avec son empreinte, encore absent, était
        refusée, et la mise à jour ne se faisait pas valider."""
        from socle import checks_memory

        demande = "memory/requests/D-0001-un-skill.md"
        (self.racine / demande).write_text(
            "<!-- socle: couche=demandes zone=publique -->\n# D-0001 — Un skill\n\n> date : 2026-11-02\n\n"
            "Valider `.claude/skills/socle-neuf/SKILL.md` et `sha256:0123456789abcdef`.\n")
        self.assertEqual(self.erreurs(), [])
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.base)
        self.assertTrue(checks_memory.protege_cite(ctx, ".claude/skills/socle-neuf/SKILL.md"))
        self.assertFalse(checks_memory.protege_cite(ctx, "scripts/jamais.py"))
        # Hors d'une demande, ou pour un fichier qui n'est pas protégé, le
        # chemin absent reste refusé.
        self.citer("memory/active.md", "\nLe skill `.claude/skills/socle-neuf/SKILL.md`.\n")
        self.assertEqual(self.erreurs(), ["chemin cité inexistant : `.claude/skills/socle-neuf/SKILL.md`"])

    def test_le_chantier_actif_suit_le_renommage(self):
        # Le chantier actif se réécrit : il cite le nom d'aujourd'hui.
        self.citer("memory/active.md", "\nL'outil vit dans `scripts/vieux.py`.\n")
        self.assertEqual(self.erreurs(), ["chemin cité inexistant : `scripts/vieux.py`"])

    def avertissements(self) -> list[str]:
        from socle.report import AVERTISSEMENT, Rapport

        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.base)
        r = Rapport()
        controles_memoire.references(ctx, r)
        return [c.message for c in r.constats if c.gravite == AVERTISSEMENT]

    def test_un_fichier_neuf_pas_encore_ajoute_est_averti(self):
        """B-0166, ADR-0063 : un chemin cité vaut s'il est suivi par git,
        l'index compris. Un fichier neuf qu'un `git add` livrerait est averti
        sur l'arbre de travail ; le commit, qui juge l'index, le refuse s'il
        ne l'ajoute pas."""
        (self.racine / "scripts/neuf.py").write_text("z = 1\n")
        self.citer("memory/active.md", "\nL'outil vit dans `scripts/neuf.py`, voir [le source](../scripts/neuf.py).\n")
        self.assertEqual(self.erreurs(), [])
        averti = self.avertissements()
        self.assertEqual(len(averti), 2, averti)
        self.assertTrue(any("non suivi par git : `scripts/neuf.py`" in m for m in averti), averti)
        self.assertTrue(any(m.startswith("lien mort : ../scripts/neuf.py") and "git add" in m for m in averti), averti)
        # L'index, figé en arbre, est ce que juge le hook avant commit : la
        # citation ajoutée, sans le fichier, y est refusée.
        git(self.racine, "add", "memory/active.md")
        index = outils.arbre_de_l_index(self.racine)
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="git", base=self.base, tete=index)
        from socle.report import Rapport
        r = Rapport()
        controles_memoire.references(ctx, r)
        self.assertTrue(any("scripts/neuf.py" in c.message for c in r.erreurs()))
        # Ajouté à l'index, pas encore commité : il passe.
        git(self.racine, "add", "scripts/neuf.py")
        self.assertEqual(self.erreurs(), [])
        self.assertEqual(self.avertissements(), [])

    def test_un_dossier_ignore_seulement_en_local_est_refuse(self):
        """B-0166, l'incident : un dossier que seul `.git/info/exclude`
        ignore passait en local et échouait dans un clone neuf. Ignoré par un
        `.gitignore` suivi, il passe."""
        (self.racine / "scripts/locaux").mkdir()
        (self.racine / "scripts/locaux/x.txt").write_text("x\n")
        exclude = self.racine / ".git/info/exclude"
        exclude.parent.mkdir(exist_ok=True)
        exclude.write_text("scripts/locaux/\n")
        controles_memoire._ignore.cache_clear()
        self.citer("memory/active.md", "\nLes essais vivent dans `scripts/locaux/`.\n")
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("`scripts/locaux/`", erreurs[0])
        ignore = self.racine / "scripts/.gitignore"
        ignore.write_text("locaux/\n")
        git(self.racine, "add", "scripts/.gitignore")
        controles_memoire._ignore.cache_clear()
        self.assertEqual(self.erreurs(), [])

    def test_une_regle_du_gitignore_pas_encore_ajoutee_ne_compte_pas(self):
        """Revue de B-0166, constat 1 : une règle écrite dans un `.gitignore`
        commité, sans `git add`, manque à un clone neuf. Refusée jusqu'à ce
        que l'index l'ait."""
        ignore = self.racine / "scripts/.gitignore"
        ignore.write_text("*.tmp\n")
        git(self.racine, "add", "scripts/.gitignore")
        git(self.racine, "commit", "-qm", "un gitignore", "--no-verify")
        ignore.write_text("*.tmp\nlocaux/\n")
        (self.racine / "scripts/locaux").mkdir()
        (self.racine / "scripts/locaux/x.txt").write_text("x\n")
        controles_memoire._ignore.cache_clear()
        self.citer("memory/active.md", "\nLes essais vivent dans `scripts/locaux/`.\n")
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("ignoré par git : `scripts/locaux/`", erreurs[0])
        git(self.racine, "add", "scripts/.gitignore")
        controles_memoire._ignore.cache_clear()
        self.assertEqual(self.erreurs(), [])

    def test_un_dossier_ignore_cite_sans_barre_finale(self):
        """Revue de B-0166, constat 2 : sans barre finale, un dossier ignoré
        passait s'il était sur le disque, et échouait dans un clone neuf, où
        il manque. Refusé dans les deux cas ; avec la barre, il passe."""
        ignore = self.racine / "scripts/.gitignore"
        ignore.write_text("locaux/\n")
        git(self.racine, "add", "scripts/.gitignore")
        controles_memoire._ignore.cache_clear()
        self.citer("memory/active.md", "\nLes essais vivent dans `scripts/locaux`.\n")
        absent = self.erreurs()
        self.assertEqual(absent, ["chemin cité inexistant : `scripts/locaux`"])
        (self.racine / "scripts/locaux").mkdir()
        (self.racine / "scripts/locaux/x.txt").write_text("x\n")
        controles_memoire._ignore.cache_clear()
        present = self.erreurs()
        self.assertEqual(len(present), 1, present)
        self.assertIn("sans barre finale", present[0])
        self.assertIn("`scripts/locaux/`", present[0])
        texte = (self.racine / "memory/active.md").read_text().replace("`scripts/locaux`", "`scripts/locaux/`")
        (self.racine / "memory/active.md").write_text(texte)
        self.assertEqual(self.erreurs(), [])
        shutil.rmtree(self.racine / "scripts/locaux")
        controles_memoire._ignore.cache_clear()
        self.assertEqual(self.erreurs(), [])

    def test_un_script_neuf_cite_par_cmd_est_averti(self):
        """Revue de B-0166, constat 3 : `cmd:` suit la règle de `fichier:`."""
        (self.racine / "scripts/lancer.sh").write_text("echo\n")
        self.citer("memory/active.md", "\nLancer cmd:scripts/lancer.sh pour l'essai.\n")
        self.assertEqual(self.erreurs(), [])
        self.assertTrue(any("`cmd:scripts/lancer.sh`" in m and "git add" in m for m in self.avertissements()))

    def test_un_chemin_d_un_depot_imbrique(self):
        """Revue de B-0166, constats 4 et 5 : un dépôt git imbriqué, comme un
        worktree d'agent non ignoré, n'est pas livré par `git add` ; le
        message le dit, et non qu'une règle l'ignore."""
        imbrique = self.racine / "scripts/copie"
        imbrique.mkdir()
        git(imbrique, "init", "-q")
        (imbrique / "a.md").write_text("a\n")
        self.assertEqual(outils.depot_imbrique(self.racine, "scripts/copie/a.md"), "scripts/copie")
        self.assertIsNone(outils.depot_imbrique(self.racine, "scripts/vieux.py"))
        self.assertFalse(outils.chemin_suivi(self.racine, "scripts/copie/a.md", a_ajouter=True))
        self.assertFalse(outils.chemin_suivi(self.racine, "scripts/copie/", a_ajouter=True))
        self.citer("memory/active.md", "\nVoir `scripts/copie/a.md`.\n")
        erreurs = self.erreurs()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("dépôt git imbriqué `scripts/copie/`", erreurs[0])

    def test_les_fichiers_suivis(self):
        (self.racine / "scripts/neuf.py").write_text("z = 1\n")
        self.assertNotIn("scripts/neuf.py", outils.fichiers_suivis(self.racine))
        self.assertFalse(outils.chemin_suivi(self.racine, "scripts/neuf.py"))
        self.assertTrue(outils.chemin_suivi(self.racine, "scripts/"))
        git(self.racine, "add", "scripts/neuf.py")
        self.assertIn("scripts/neuf.py", outils.fichiers_suivis(self.racine))
        self.assertTrue(outils.chemin_suivi(self.racine, "scripts/neuf.py"))
        hors = Path(tempfile.mkdtemp(prefix="socle-hors-depot-"))
        self.addCleanup(shutil.rmtree, hors, ignore_errors=True)
        (hors / "a.md").write_text("a\n")
        self.assertIsNone(outils.fichiers_suivis(hors))
        self.assertTrue(outils.chemin_suivi(hors, "a.md"))
        self.assertFalse(outils.chemin_suivi(hors, "b.md"))


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
        self.assertEqual(self.sortie(cli.cmd_next_id, type="need", private=False), (0, "B-0002\n"))
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


class TestCommitDUnePullRequest(unittest.TestCase):
    """B-0117 : la mémoire citait un commit que seule une branche supprimée
    portait. GitHub le garde dans sa pull request, mais un clone ne
    récupère que les branches et les étiquettes : la CI le disait absent."""

    def test_un_commit_qui_n_est_plus_que_dans_une_pull_request_se_retrouve(self):
        dossier = Path(tempfile.mkdtemp(prefix="socle-pull-"))
        self.addCleanup(shutil.rmtree, dossier, ignore_errors=True)
        origine, depot, clone = dossier / "origine.git", dossier / "depot", dossier / "clone"
        git(dossier, "init", "-q", "--bare", str(origine))
        depot.mkdir()
        git(depot, "init", "-q", "-b", "main")
        (depot / "a.txt").write_text("a\n")
        git(depot, "add", "-A")
        git(depot, "commit", "-qm", "départ", "--no-verify")
        git(depot, "remote", "add", "origin", str(origine))
        git(depot, "push", "-q", "--no-verify", "origin", "main")
        git(depot, "checkout", "-q", "-b", "sujet")
        (depot / "b.txt").write_text("b\n")
        git(depot, "add", "-A")
        git(depot, "commit", "-qm", "sujet", "--no-verify")
        sha = git(depot, "rev-parse", "HEAD").strip()
        # La pull request garde le commit ; sa branche n'est pas sur l'origine.
        git(depot, "push", "-q", "--no-verify", "origin", "HEAD:refs/pull/1/head")
        # `--no-local` : un clone local recopierait tous les objets de l'origine.
        git(dossier, "clone", "-q", "--no-local", str(origine), str(clone))
        self.assertFalse(outils.objet_existe(clone, sha))
        ctx = contexte.Contexte(config.Projet.charger(clone), etage="ci")
        self.assertIsNone(controles_memoire.verifier_ref(ctx, "commit", sha[:7]))
        self.assertTrue(outils.objet_existe(clone, sha))
        # Une fois par dépôt et par processus : la seconde fois, rien n'est récupéré.
        self.assertFalse(outils.recuperer_pull_requests(clone))
        # Un commit qui n'existe nulle part reste refusé.
        self.assertIn("ni dans ses pull requests", controles_memoire.verifier_ref(ctx, "commit", "0123456"))

    def test_un_clone_d_un_clone_retrouve_les_pull_requests_que_son_origine_a_recuperees(self):
        """B-0175 : un clone local (`--no-local`) d'un clone de GitHub n'a pas
        les `refs/pull/*` ; son origine n'en a que les copies qu'elle a
        récupérées, `refs/socle/pull/*`. Un objet que l'origine garde sans
        aucun ref reste refusé."""
        dossier = Path(tempfile.mkdtemp(prefix="socle-pull-"))
        self.addCleanup(shutil.rmtree, dossier, ignore_errors=True)
        travail, clone = dossier / "travail", dossier / "clone"
        travail.mkdir()
        git(travail, "init", "-q", "-b", "main")
        (travail / "a.txt").write_text("a\n")
        git(travail, "add", "-A")
        git(travail, "commit", "-qm", "départ", "--no-verify")
        shas = []
        for nom in ("garde", "perdu"):
            git(travail, "checkout", "-q", "-b", nom)
            (travail / f"{nom}.txt").write_text(f"{nom}\n")
            git(travail, "add", "-A")
            git(travail, "commit", "-qm", nom, "--no-verify")
            shas.append(git(travail, "rev-parse", "HEAD").strip())
            git(travail, "checkout", "-q", "main")
            git(travail, "branch", "-q", "-D", nom)
        garde, perdu = shas
        # La copie d'une tête de pull request, telle que B-0117 la récupère.
        git(travail, "update-ref", "refs/socle/pull/10", garde)
        self.assertTrue(outils.objet_existe(travail, perdu))
        git(dossier, "clone", "-q", "--no-local", str(travail), str(clone))
        self.assertFalse(outils.objet_existe(clone, garde))
        ctx = contexte.Contexte(config.Projet.charger(clone), etage="ci")
        self.assertIsNone(controles_memoire.verifier_ref(ctx, "commit", garde[:7]))
        self.assertIn("ni dans ses pull requests", controles_memoire.verifier_ref(ctx, "commit", perdu[:7]))
        self.assertFalse(outils.objet_existe(clone, perdu))
