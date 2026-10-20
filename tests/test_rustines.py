"""B-0008 : un chemin qu'une rustine suivie du dépôt écrit existe une fois
la rustine appliquée ; le citer n'est pas un lien mort."""

import contextlib
import io
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, context as contexte, installer as installeur

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
RUSTINE = "--- /dev/null\n+++ b/attic/sondes/lecteur.py\n@@ -0,0 +1 @@\n+X = 1\n"


def projet(fichiers: dict[str, str]) -> Path:
    racine = Path(tempfile.mkdtemp(prefix="socle-rustines-"))
    env = {**os.environ, "HOME": str(racine), "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True, env=env)
    (racine / "calc.py").write_text("X = 1\n", encoding="utf-8")
    with contextlib.redirect_stdout(io.StringIO()):
        installeur.installer(racine, "python", "@essai", source=MOTEUR)
    for chemin, texte in fichiers.items():
        p = racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=racine, check=True, env=env)
    return racine


def morts(racine: Path) -> str:
    rapport = contexte.executer(contexte.Contexte(config.Projet.charger(racine), etage="ci", base=None),
                                ids=["memoire.references"])
    return "\n".join(c.message for c in rapport.constats if "inexistant" in c.message)


class TestRustines(unittest.TestCase):
    def test_un_chemin_ecrit_par_une_rustine_suivie_n_est_pas_mort(self):
        racine = projet({"attic/sondes.patch": RUSTINE,
                         "docs/sondes.md": "Le lecteur `attic/sondes/lecteur.py` vient de la rustine.\n"})
        self.assertEqual(morts(racine), "")

    def test_ses_dossiers_non_plus(self):
        racine = projet({"attic/sondes.diff": RUSTINE, "docs/sondes.md": "Voir `attic/sondes/`.\n"})
        self.assertEqual(morts(racine), "")

    def test_sans_la_rustine_le_chemin_reste_mort(self):
        racine = projet({"attic/autre.txt": "x\n",
                         "docs/sondes.md": "Le lecteur `attic/sondes/lecteur.py` vient de la rustine.\n"})
        self.assertIn("attic/sondes/lecteur.py", morts(racine))

    def test_une_rustine_qui_retire_un_fichier_ne_le_fait_pas_exister(self):
        racine = projet({"attic/retrait.patch": "--- a/attic/vieux.py\n+++ /dev/null\n",
                         "docs/sondes.md": "L'ancien `attic/vieux.py`.\n"})
        self.assertIn("attic/vieux.py", morts(racine))


if __name__ == "__main__":
    unittest.main()
