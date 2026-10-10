import ast
import sys
import unittest
from pathlib import Path

MOTEUR = Path(__file__).resolve().parent.parent / "moteur/socle"


class TestBibliothequeStandard(unittest.TestCase):
    """Le moteur est copié tel quel dans n'importe quel projet : il n'importe
    que la bibliothèque standard et lui-même (ADR-0001)."""

    def test_imports(self):
        hors = []
        for p in sorted(MOTEUR.rglob("*.py")):
            arbre = ast.parse(p.read_text(encoding="utf-8"))
            for noeud in ast.walk(arbre):
                if isinstance(noeud, ast.Import):
                    noms = [a.name for a in noeud.names]
                elif isinstance(noeud, ast.ImportFrom) and noeud.level == 0:
                    noms = [noeud.module or ""]
                else:
                    continue
                for nom in noms:
                    racine = nom.split(".")[0]
                    if racine != "socle" and racine not in sys.stdlib_module_names:
                        hors.append(f"{p.relative_to(MOTEUR)} : {nom}")
        self.assertEqual(hors, [])

    def test_le_parcours_voit_le_moteur(self):
        # Sans ce test, un chemin faux rendrait « aucun import hors stdlib ».
        self.assertGreater(len(list(MOTEUR.rglob("*.py"))), 15)

    def test_syntaxe_python_3_11(self):
        for p in sorted(MOTEUR.rglob("*.py")):
            ast.parse(p.read_text(encoding="utf-8"), feature_version=(3, 11))
        self.assertTrue((MOTEUR / "__init__.py").is_file())


if __name__ == "__main__":
    unittest.main()
