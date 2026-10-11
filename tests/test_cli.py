"""Les commandes de lecture et d'écriture de la mémoire, et ce qu'elles
calculent, sur un projet fabriqué dont une branche est poussée."""

import argparse
import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import cli, config, hooks, humain, liens, memoire

DEPOT = "https://github.com/essai/memoire"

BACKLOG = """<!-- socle: couche=backlog zone=publique -->
# Backlog

## B-0001 — Ajouter une fonction triple

> statut : ouvert · origine : fichier:calc.py

Pour l'essai.
"""

ADR = """<!-- socle: couche=decisions zone=publique -->
# ADR-0001 — Une seule constante de multiplication

> statut : acceptée · date : 2026-10-10

## Décision

Une seule constante.
"""

ACTIF = """<!-- socle: couche=actif zone=publique -->
# Chantier actif

## En cours

L'essai.

## Prochaines étapes

1. Ajouter triple (B-0001).
"""


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


def sortie(commande, **args) -> tuple[int, str]:
    flux = io.StringIO()
    with contextlib.redirect_stdout(flux), contextlib.redirect_stderr(io.StringIO()):
        code = commande(argparse.Namespace(**args))
    return code, flux.getvalue()


class TestCommandes(unittest.TestCase):
    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-cli-"))
        source = self.dossier / "source"
        source.mkdir()
        git(source, "init", "-q", "-b", "main")
        (source / ".socle").mkdir()
        (source / ".socle/policy.toml").write_text(f'[human]\nrepo_url = "{DEPOT}"\n')
        (source / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        for chemin, texte in (("memory/backlog.md", BACKLOG), ("memory/active.md", ACTIF),
                              ("memory/decisions/ADR-0001-une-seule-constante.md", ADR)):
            (source / chemin).parent.mkdir(parents=True, exist_ok=True)
            (source / chemin).write_text(texte)
        git(source, "add", "-A")
        git(source, "commit", "-qm", "base")
        self.racine = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(source), str(self.racine))
        self.projet = config.Projet.charger(self.racine)
        self.pousse = git(self.racine, "rev-parse", "origin/main").strip()

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)

    def test_show_donne_l_empreinte(self):
        mem = memoire.Memoire.charger(self.racine)
        attendue = memoire.empreinte_entree(mem.entree("B-0001"))
        code, texte = sortie(cli.cmd_show, root=str(self.racine), ids=["B-0001"], index=None)
        self.assertEqual(code, 0)
        self.assertIn(f"--- B-0001@{attendue} (memory/backlog.md:4) ---", texte)
        code, texte = sortie(cli.cmd_show, root=str(self.racine), ids=["B-0099"], index="backlog")
        self.assertEqual(code, 1)
        self.assertIn(f"index backlog@{memoire.empreinte_index(mem, 'backlog')}", texte)

    def test_index_du_backlog_ouvert(self):
        mem = memoire.Memoire.charger(self.racine)
        self.assertEqual(memoire.lignes_index(mem, "backlog"), ["B-0001 — Ajouter une fonction triple (ouvert)"])
        avant = memoire.empreinte_index(mem, "backlog")
        p = self.racine / "memory/backlog.md"
        p.write_text(p.read_text().replace("statut : ouvert", "statut : fait · ref : fichier:calc.py"))
        mem = memoire.Memoire.charger(self.racine)
        self.assertEqual(memoire.lignes_index(mem, "backlog"), [])
        self.assertNotEqual(memoire.empreinte_index(mem, "backlog"), avant)

    def test_url_donne_le_permalien(self):
        code, texte = sortie(cli.cmd_url, root=str(self.racine), cibles=["B-0001", "ADR-0001", "absent.md"])
        self.assertEqual(code, 1)
        self.assertIn(f"[B-0001]({DEPOT}/blob/{self.pousse}/memory/backlog.md#b-0001--ajouter-une-fonction-triple)", texte)
        self.assertIn(f"[ADR-0001]({DEPOT}/blob/{self.pousse}/memory/decisions/ADR-0001-une-seule-constante.md)", texte)
        self.assertNotIn("absent.md", texte)

    def test_new_adr_prouve_la_lecture_de_l_index(self):
        mem = memoire.Memoire.charger(self.racine)
        code, texte = sortie(cli.cmd_new, root=str(self.racine), type="adr", title="Garder la constante")
        self.assertEqual(code, 0)
        adr = (self.racine / "memory/decisions/ADR-0002-garder-la-constante.md").read_text()
        self.assertIn(f"lu : decisions@{memoire.empreinte_index(mem, 'decisions')}", adr)

    def test_prochaines_etapes_du_chantier_actif(self):
        self.assertEqual(humain.prochaines_etapes(self.projet), "1. Ajouter triple (B-0001).")

    def test_adresse_et_commit_pousse(self):
        self.assertEqual(liens.url_depot(self.projet), DEPOT)
        self.assertEqual(liens.commit_pousse(self.racine), self.pousse)
        self.assertIsNone(liens.url_morte(self.racine, DEPOT, f"{DEPOT}/blob/main/calc.py"))
        self.assertIn("n'existe pas", liens.url_morte(self.racine, DEPOT, f"{DEPOT}/blob/main/triple.py"))
        self.assertIn("inconnue", liens.url_morte(self.racine, DEPOT, f"{DEPOT}/blob/travail/calc.py"))

    def test_trace_commune_aux_worktrees(self):
        autre = self.dossier / "autre"
        git(self.racine, "worktree", "add", "-q", "-b", "autre", str(autre))
        trace = config.chemin_trace(self.racine)
        self.assertEqual(trace, config.chemin_trace(autre))
        self.assertEqual(trace, (self.racine / ".git/socle/hooks.log").resolve())
        ancienne = self.racine / config.TRACE
        ancienne.parent.mkdir(parents=True, exist_ok=True)
        ancienne.write_text("ancienne\n")
        trace.parent.mkdir(parents=True, exist_ok=True)
        trace.write_text("nouvelle\n")
        self.assertEqual(config.lire_trace(self.racine), ["ancienne", "nouvelle"])
        self.assertEqual(config.lire_trace(autre), ["nouvelle"])
        hooks.tracer(autre, "Stop", "session")
        self.assertRegex(config.lire_trace(self.racine)[-1], r"^\S+\tStop\tsession\t$")


if __name__ == "__main__":
    unittest.main()
