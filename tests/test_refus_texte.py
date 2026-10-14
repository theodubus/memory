"""Refus à tort sur du texte, relevé de la passe de recul, section E : un
lien encodé (`%20`) ou une référence suivie de sa ponctuation (B-0020)
déclarés morts ; la virgule décimale qui confondait 3,5 et 35."""

import contextlib
import io
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, context as contexte, checks_memory as controles_memoire, installer as installeur
from socle.checks_docs import _motif_libre, normaliser_valeur
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"


class TestReferencesEcrites(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-texte-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.racine, check=True)
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        (self.racine / "docs").mkdir()
        (self.racine / "docs/mon fichier.md").write_text("# Été\n\nUn titre accentué.\n")

    def erreurs(self, texte: str) -> list[str]:
        (self.racine / "docs/notes.md").write_text(texte)
        r = Rapport()
        controles_memoire.references(contexte.Contexte(config.Projet.charger(self.racine), etage="agent"), r)
        return [c.message for c in r.erreurs()]

    def test_un_lien_encode_designe_le_fichier_et_l_ancre_decodes(self):
        self.assertEqual(self.erreurs("Voir [le fichier](mon%20fichier.md#%C3%A9t%C3%A9).\n"), [])
        self.assertEqual(len(self.erreurs("Voir [le fichier](mon%20autre.md).\n")), 1)

    def test_une_reference_en_fin_de_phrase(self):
        self.assertEqual(self.erreurs("Écrit dans fichier:docs/notes.md. Ou (fichier:docs/notes.md).\n"), [])


class TestValeurs(unittest.TestCase):
    def test_la_virgule_decimale(self):
        self.assertEqual(normaliser_valeur("3,5"), normaliser_valeur("3.5"))
        self.assertNotEqual(normaliser_valeur("3,5"), normaliser_valeur("35"))
        self.assertEqual(normaliser_valeur("70 452"), normaliser_valeur("70,452"))
        self.assertEqual(normaliser_valeur("1 234,56"), "1234.56")

    def test_une_valeur_libre_ne_se_confond_pas(self):
        self.assertTrue(_motif_libre("3,5").search("vaut 3.5 Elo"))
        self.assertFalse(_motif_libre("3,5").search("vaut 35 Elo"))
        self.assertFalse(_motif_libre("35").search("vaut 3,5 Elo"))
        self.assertTrue(_motif_libre("70452").search("70 452 nœuds"))
        self.assertFalse(_motif_libre("8432521").search("84 32 521"))


if __name__ == "__main__":
    unittest.main()
