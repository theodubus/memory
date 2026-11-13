"""B-0010, ADR-0071 : la sortie du démarrage tient sous la borne des
garde-fous (`[startup] max_bytes`), que Claude Code remet entière à
l'agent : l'état dérivé d'abord, son essentiel dans les 2 000 premiers
octets, puis le chantier actif, les faits par leur titre et les dix
dernières décisions ; au-delà, des lignes entières se coupent depuis la fin,
et une dernière ligne le dit."""

import contextlib
import io
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from socle import config, hooks, installer as installeur, state as etat
from socle.checks_ratchet import assouplissements
from tests.test_bascule import MOTEUR, git

ACTIF = """<!-- socle: couche=actif zone=publique -->
# Chantier actif

## En cours

{lignes}
"""


def decision(n: int, statut: str = "acceptée") -> str:
    return (f"<!-- socle: couche=decisions zone=publique -->\n"
            f"# ADR-{n:04d} — La décision numéro {n}, au titre assez long pour peser dans un index entier\n\n"
            f"> statut : {statut} · date : 2026-10-{10 + n % 18:02d}\n\n## Décision\n\nLa décision {n}.\n")


def fait(n: int, statut: str = "mesuré · preuve : fichier:calc.py") -> str:
    return f"## F-{n:04d} — Le fait numéro {n}, mesuré sur le projet d'essai\n\n> statut : {statut}\n\nSon détail.\n\n"


class Demarrage(unittest.TestCase):
    """Un projet installé, public : quarante décisions, vingt faits, un
    chantier actif de quarante lignes, une demande en attente."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-demarrage-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        decisions = self.racine / "memory/decisions"
        decisions.mkdir(exist_ok=True)
        for n in range(1, 41):
            (decisions / f"ADR-{n:04d}-decision-{n}.md").write_text(decision(n, "remplacée" if n == 35 else "acceptée"))
        canonique = self.racine / "memory/canonical.md"
        entete = canonique.read_text().split("\n## ", 1)[0].rstrip() + "\n\n"
        canonique.write_text(entete + "".join(fait(n, "supposé · source : calc.py" if n == 7 else
                                                   "mesuré · preuve : fichier:calc.py") for n in range(1, 21)))
        (self.racine / "memory/active.md").write_text(ACTIF.format(lignes="\n".join(
            f"- Étape {n} du chantier en cours, dite sur une ligne entière." for n in range(1, 41))))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")

    def projet(self, borne: int | None = None) -> config.Projet:
        if borne is not None:
            gf = self.racine / ".socle/guardrails.toml"
            texte, n = re.subn(r"(\[startup\][^\[]*?)max_bytes = \d+", rf"\g<1>max_bytes = {borne}", gf.read_text())
            self.assertEqual(n, 1)
            gf.write_text(texte)
        return config.Projet.charger(self.racine)

    def sortie(self, borne: int | None = None) -> str:
        return etat.calculer(self.projet(borne))

    def test_l_essentiel_tient_dans_les_2000_premiers_octets(self):
        """L'index des décisions ne s'intercale plus au milieu de l'état
        dérivé : ce qui demande d'agir est dans l'aperçu de Claude Code."""
        sortie = self.sortie()
        premiers = sortie.encode("utf-8")[:2000].decode("utf-8", errors="ignore")
        for ligne in ("commit   :", "base     :", "CI       :", "mémoire  :", "demandes humaines en attente :",
                      "branche  :", "ce qui revient à l'humain", "hooks    :", "mémoire privée :", "backlog  :",
                      "vérifier :"):
            self.assertIn(ligne, premiers)
        self.assertNotIn("ADR-", premiers)
        self.assertLess(sortie.index("--- memory/active.md ---"), sortie.index("--- memory/canonical.md"))
        self.assertLess(sortie.index("--- memory/canonical.md"), sortie.index("dernières décisions sur 40"))

    def test_sous_la_borne_rien_ne_se_coupe(self):
        sortie = self.sortie()
        self.assertLessEqual(len((sortie + "\n").encode("utf-8")), 9500)
        self.assertNotIn("!! coupé", sortie)
        lignes = sortie.splitlines()
        # Le chantier actif entier.
        self.assertIn("- Étape 40 du chantier en cours, dite sur une ligne entière.", lignes)
        # Les faits par leur titre, le statut quand il n'est pas « mesuré ».
        self.assertIn("--- memory/canonical.md : 20 fait(s) par leur titre ; un en entier : `python3 .socle/socle "
                      "show F-NNNN` ---", lignes)
        self.assertIn("F-0001 — Le fait numéro 1, mesuré sur le projet d'essai", lignes)
        self.assertIn("F-0007 — Le fait numéro 7, mesuré sur le projet d'essai (supposé)", lignes)
        self.assertNotIn("Son détail.", sortie)
        # Les dix dernières décisions, la plus récente d'abord, et leur nombre.
        debut = lignes.index("--- les 10 dernières décisions sur 40, la plus récente d'abord ; avant toute décision "
                             "de conception, l'index entier : `python3 .socle/socle show --index decisions` ---")
        self.assertEqual([l.split(" — ")[0] for l in lignes[debut + 1:]],
                         [f"ADR-{n:04d}" for n in (35, 17, 34, 16, 33, 15, 32, 14, 31, 13)])
        self.assertIn("(remplacee)", sortie)
        self.assertNotIn("decisions@", sortie)

    def test_au_dela_de_la_borne_les_decisions_puis_les_faits_se_coupent_et_la_coupe_se_dit(self):
        # Sous une borne très haute : l'arbre est modifié comme sous la vraie.
        entiere = self.sortie(10 ** 6).splitlines()
        borne = len("\n".join(entiere[:entiere.index("F-0012 — Le fait numéro 12, mesuré sur le projet d'essai")])
                    .encode("utf-8")) + 250
        sortie = self.sortie(borne)
        lignes = sortie.splitlines()
        self.assertLessEqual(len((sortie + "\n").encode("utf-8")), borne)
        # Des lignes entières, depuis la fin : ce qui reste est le début de la
        # sortie entière.
        self.assertEqual(lignes[:-1], entiere[:len(lignes) - 1])
        self.assertNotIn("dernières décisions sur 40", sortie)
        self.assertTrue(lignes[-1].startswith(f"!! coupé à la borne du démarrage ({borne} octets, `[startup] "
                                              "max_bytes` des garde-fous) : "), lignes[-1])
        coupes = 20 - sum(l.startswith("F-") for l in lignes)
        self.assertGreater(coupes, 0)
        self.assertIn(f"{coupes} fait(s) sur 20 : lire memory/canonical.md", lignes[-1])
        self.assertIn("10 des 10 dernières décisions : `python3 .socle/socle show --index decisions`", lignes[-1])
        self.assertIn("- Étape 40 du chantier en cours, dite sur une ligne entière.", lignes)

    def test_le_chantier_actif_se_coupe_en_dernier_recours_avec_son_chemin(self):
        entiere = self.sortie(10 ** 6).splitlines()
        borne = len("\n".join(entiere[:entiere.index("--- memory/active.md ---")]).encode("utf-8")) + 600
        sortie = self.sortie(borne)
        lignes = sortie.splitlines()
        self.assertLessEqual(len((sortie + "\n").encode("utf-8")), borne)
        self.assertEqual(lignes[:-1], entiere[:len(lignes) - 1])
        self.assertIn("--- memory/active.md ---", lignes)
        self.assertNotIn("F-0001", sortie)
        self.assertRegex(lignes[-1], r"la fin du chantier actif, \d+ ligne\(s\) sur \d+ : lire memory/active\.md ; "
                                     r"20 fait\(s\) sur 20 : lire memory/canonical\.md ; 10 des 10 dernières")

    def test_l_etat_derive_ne_se_coupe_pas(self):
        sortie = self.sortie(100)
        self.assertIn("vérifier :", sortie)
        self.assertNotIn("--- memory/active.md ---", sortie)
        self.assertIn("lire memory/active.md", sortie.splitlines()[-1])

    def test_la_sortie_du_hook_compte_ses_propres_lignes(self):
        """Toute la sortie du hook de démarrage tient sous la borne, les
        lignes des outils de l'adaptateur et des hooks git comprises, qui
        précèdent le backlog."""
        projet = self.projet(4000)
        outils_installes = ["outils de l'adaptateur installés (session cloud) : `pip install -r requirements.txt`"]
        with mock.patch.object(hooks, "installer_outils", return_value=list(outils_installes)), \
                mock.patch.object(hooks, "installer_hooks_git", return_value=False), \
                contextlib.redirect_stdout(io.StringIO()) as flux:
            self.assertEqual(hooks.session_start(projet, {}), 0)
        sortie = flux.getvalue()
        self.assertLessEqual(len(sortie.encode("utf-8")), 4000)
        self.assertLess(sortie.index(outils_installes[0]), sortie.index("backlog  :"))
        self.assertLess(sortie.index("!! hooks git non branchés"), sortie.index("backlog  :"))
        self.assertTrue(sortie.splitlines()[-1].startswith("!! coupé à la borne du démarrage (4000 octets"))

    def test_la_borne_vient_des_garde_fous_celle_du_gabarit_a_defaut(self):
        self.assertEqual(self.projet().borne_demarrage(), 9500)
        self.assertEqual(self.projet(7000).borne_demarrage(), 7000)
        projet = self.projet()
        for valeur in (None, 0, -5, "beaucoup", True):
            projet.garde_fous["startup"] = {} if valeur is None else {"max_bytes": valeur}
            self.assertEqual(projet.borne_demarrage(), config.BORNE_DEMARRAGE)


class TestBorner(unittest.TestCase):
    def test_borner_retire_des_lignes_entieres_depuis_la_fin_et_le_dit(self):
        a = [f"a{i}" + "." * 98 for i in (1, 2)]
        b = [f"b{i}" + "." * 98 for i in (1, 2, 3)]
        parties = [etat.Partie(["", "--- a ---"], a, lambda n, t: f"{n}/{t} de a"),
                   etat.Partie(["", "--- b ---"], b, lambda n, t: f"{n}/{t} de b")]
        self.assertEqual(etat.borner(["état"], parties, 600), ["état", "", "--- a ---", *a, "", "--- b ---", *b])
        # La partie b disparaît avec son en-tête, puis la dernière ligne de a.
        self.assertEqual(etat.borner(["état"], parties, 340)[:-1], ["état", "", "--- a ---", *a])
        coupee = etat.borner(["état"], parties, 240)
        self.assertLessEqual(sum(len(l.encode()) + 1 for l in coupee), 240)
        self.assertEqual(coupee, ["état", "", "--- a ---", a[0], "!! coupé à la borne du démarrage (240 octets, "
                                  "`[startup] max_bytes` des garde-fous) : 1/2 de a ; 3/3 de b"])
        # L'état dérivé reste, même au-delà de la borne.
        self.assertEqual(etat.borner(["état"], parties, 10)[0], "état")

    def test_parties_injectees_sans_memoire_lisible_donne_le_chantier_actif_seul(self):
        racine = Path(tempfile.mkdtemp(prefix="socle-parties-"))
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        (racine / "memory").mkdir()
        (racine / "memory/active.md").write_text("# Chantier actif\n\nUne ligne.\n")
        projet = config.Projet(racine=racine)
        parties = etat.parties_injectees(projet, None)
        self.assertEqual([(p.entete, p.lignes) for p in parties],
                         [(["", "--- memory/active.md ---"], ["# Chantier actif", "", "Une ligne."])])


class TestCliquetDeLaBorne(unittest.TestCase):
    def test_relever_la_borne_assouplit_la_baisser_durcit(self):
        self.assertEqual(assouplissements({}, {"startup": {"max_bytes": 9500}}), [])
        self.assertEqual(assouplissements({}, {"startup": {"max_bytes": 8000}}), [])
        (cle, pourquoi), = assouplissements({}, {"startup": {"max_bytes": 20000}})
        self.assertEqual((cle, pourquoi), ("startup.max_bytes", "9500 → 20000"))
        self.assertEqual([c for c, _ in assouplissements({"startup": {"max_bytes": 8000}}, {})],
                         ["startup.max_bytes"])


if __name__ == "__main__":
    unittest.main()
