"""ADR-0026 (B-0053) : deux branches parties du même commit prenaient le
même identifiant, et la fusion le définissait deux fois. `socle new` voit
les branches distantes, `memoire.collisions` le dit avant la fusion, et
`socle renumber` le répare."""

import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from socle import (cli, config, context as contexte, checks_memory as controles_memoire, identifiers as identifiants,
                   installer as installeur, memory as memoire)
from socle.report import Rapport
from tests.test_bascule import P, git

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
SUJET = "# {id} — {titre}\n\n> statut : ouvert · origine : fichier:calc.py\n"


class Depot(unittest.TestCase):
    """Un projet installé et poussé ; la branche `x` prend `B-0001`, puis la
    branche par défaut reçoit, d'une autre branche, un autre `B-0001`."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-identifiants-"))
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        origine = self.dossier / "origine.git"
        git(self.dossier, "init", "-q", "--bare", "-b", "main", str(origine))
        self.racine = self.dossier / "projet"
        self.racine.mkdir()
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("x = 1\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "installation", "--no-verify")
        git(self.racine, "remote", "add", "origin", str(origine))
        git(self.racine, "push", "-q", "--no-verify", "-u", "origin", "main")
        git(self.racine, "switch", "-q", "-c", "y")
        self.sujet("B-0001", "Le sujet de la branche y")
        git(self.racine, "switch", "-q", "main")
        git(self.racine, "merge", "-q", "y")
        git(self.racine, "push", "-q", "--no-verify", "origin", "main")
        git(self.racine, "switch", "-q", "-c", "x", "HEAD~1")
        self.sujet("B-0001", "Le sujet de la branche x")

    def sujet(self, ident, titre):
        p = self.racine / config.FORMAT_ACTUEL.backlog / f"{ident}-{memoire.nom_de_fichier(titre)}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("<!-- socle: couche=backlog zone=publique -->\n" + SUJET.format(id=ident, titre=titre))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", titre, "--no-verify")

    def collisions(self) -> list[str]:
        projet = config.Projet.charger(self.racine)
        ctx = contexte.Contexte(projet, etage="agent", base=git(self.racine, "merge-base", "HEAD", "main").strip())
        r = Rapport()
        controles_memoire.collisions(ctx, r)
        return [c.message for c in r.erreurs("memoire.collisions")]

    def socle(self, *args) -> tuple[int, str]:
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            code = cli.main(["--root", str(self.racine), *args])
        return code, sortie.getvalue()


class TestProchainLibre(unittest.TestCase):
    def test_le_numero_qui_suit_le_plus_grand(self):
        # Un identifiant privé ne s'écrit pas en clair dans un fichier public.
        pris = {"B-0001", "B-0007", P + "B-0009", "F-0012"}
        self.assertEqual(memoire.prochain_libre("B", pris), "B-0008")
        self.assertEqual(memoire.prochain_libre("B", pris, prive=True), P + "B-0010")
        self.assertEqual(memoire.prochain_libre("ADR", pris), "ADR-0001")

    def test_la_lettre_suivante_du_jour(self):
        pris = {"J-2026-10-13-A", "J-2026-10-13-B", "J-2026-10-12-C"}
        self.assertEqual(memoire.prochain_libre("J", pris, date="2026-10-13"), "J-2026-10-13-C")
        with self.assertRaises(ValueError):
            memoire.prochain_libre("J", pris)


class TestCollisions(Depot):
    def test_la_collision_se_dit_avant_la_fusion(self):
        erreurs = self.collisions()
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("`B-0001` est pris aussi sur la branche par défaut", erreurs[0])
        self.assertIn("« Le sujet de la branche y »", erreurs[0])
        self.assertIn("socle renumber B-0001", erreurs[0])

    def test_la_tete_de_la_branche_par_defaut_s_ajoute_a_la_base(self):
        # Le point de divergence ne voit rien de ce que la branche par
        # défaut a reçu depuis : sa tête se compare aussi.
        self.assertEqual(identifiants.bases_a_comparer(self.racine, "abc"), ["abc", "origin/main"])
        self.assertEqual(identifiants.bases_a_comparer(self.racine, None), ["origin/main"])

    def test_renumerotee_elle_disparait_et_les_citations_suivent(self):
        from argparse import Namespace

        h = memoire.empreinte_entree(memoire.Memoire.charger(self.racine).entree("B-0001"))
        notes = self.racine / "docs/notes.md"
        notes.parent.mkdir(exist_ok=True)
        notes.write_text(f"Voir B-0001, lu en B-0001@{h} ; pas B-00011.\n")
        with contextlib.redirect_stdout(io.StringIO()) as s, contextlib.redirect_stderr(s):
            code = cli.cmd_renumber(Namespace(root=str(self.racine), id="B-0001"))
        sortie = s.getvalue()
        self.assertEqual(code, 0, sortie)
        self.assertIn("B-0001 → B-0002", sortie)
        neuf = memoire.Memoire.charger(self.racine).entree("B-0002")
        self.assertEqual(neuf.titre, "Le sujet de la branche x")
        self.assertEqual(notes.read_text(),
                         f"Voir B-0002, lu en B-0002@{memoire.empreinte_entree(neuf)} ; pas B-00011.\n")
        git(self.racine, "commit", "-qam", "renuméroté", "--no-verify")
        self.assertEqual(self.collisions(), [])

    def test_ce_qui_existait_avant_la_branche_ne_se_renumerote_pas(self):
        # L'entrée de journal que l'installation a ouverte, avant la branche.
        ouverture = next(i for i in memoire.Memoire.charger(self.racine).definitions() if i.startswith("J-"))
        code, sortie = self.socle("renumber", ouverture)
        self.assertEqual(code, 1, sortie)
        self.assertIn("existait avant la branche", sortie)

    def test_une_branche_dont_la_base_descend_n_a_rien_a_dire(self):
        git(self.racine, "switch", "-q", "main")
        git(self.racine, "switch", "-q", "-c", "z")
        self.sujet("B-0002", "Un sujet de plus")
        self.assertEqual(self.collisions(), [])


class TestBranchesDistantes(Depot):
    def test_un_identifiant_neuf_saute_ceux_des_branches_poussees(self):
        git(self.racine, "push", "-q", "--no-verify", "origin", "x")
        git(self.racine, "fetch", "-q", "origin")
        self.assertEqual(identifiants.pris_ailleurs(self.racine, "B"), {"B-0001"})
        mem = memoire.Memoire.charger(self.racine)
        self.assertEqual(mem.prochain_id("B", pris_ailleurs={"B-0004"}), "B-0005")
        git(self.racine, "switch", "-q", "main")
        git(self.racine, "switch", "-q", "-c", "w")
        # `x`, poussée, a pris B-0001 aussi, et `main` en a un : le suivant
        # est B-0002 ; sans les branches distantes, ce serait le même.
        code, sortie = self.socle("new", "need", "Un sujet de w", "--public")
        self.assertEqual(code, 0, sortie)
        self.assertIn("B-0002\t", sortie)


class TestFichierDuSujet(Depot):
    def test_le_fichier_du_sujet_change_de_nom(self):
        lignes = identifiants.renumeroter(config.Projet.charger(self.racine), "B-0001")
        self.assertEqual(lignes[:2], ["B-0001 → B-0002", "memory/backlog/B-0001-le-sujet-de-la-branche-x.md → "
                                      "memory/backlog/B-0002-le-sujet-de-la-branche-x.md"])
        self.assertEqual(memoire.dossier_propre("memory/backlog/B-0002-le-sujet-de-la-branche-x.md"), "memory/backlog")
        self.assertIsNone(memoire.dossier_propre("memory/backlog.md"))
        self.assertEqual(memoire.dossier_propre("memory/decisions/ADR-0001-x.md"), "memory/decisions")
        self.assertTrue((self.racine / "memory/backlog/B-0002-le-sujet-de-la-branche-x.md").is_file())
        self.assertFalse((self.racine / "memory/backlog/B-0001-le-sujet-de-la-branche-x.md").exists())
        self.assertIn("# B-0002 — Le sujet de la branche x",
                      (self.racine / "memory/backlog/B-0002-le-sujet-de-la-branche-x.md").read_text())


if __name__ == "__main__":
    unittest.main()
