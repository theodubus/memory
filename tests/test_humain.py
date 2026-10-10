import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import config, humain


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestBranchesASupprimer(unittest.TestCase):
    """Le cas de `chess:tools/etat-test.sh`, généralisé : une ligne qui se tait
    presque toujours s'éprouve sur des dépôts fabriqués."""

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-humain-"))
        source = self.dossier / "source"
        source.mkdir()
        git(source, "init", "-q", "-b", "main")
        (source / "f").write_text("un")
        git(source, "add", "f")
        git(source, "commit", "-qm", "un")
        for b in ("fusionnee", "codex/ui", "travail"):
            git(source, "branch", b)
        (source / "f").write_text("deux")
        git(source, "commit", "-qam", "deux")
        git(source, "switch", "-q", "-c", "en-cours")
        (source / "f").write_text("trois")
        git(source, "commit", "-qam", "trois")
        git(source, "switch", "-q", "main")
        self.clone = self.dossier / "clone"
        git(self.dossier, "clone", "-q", str(source), str(self.clone))
        git(self.clone, "switch", "-q", "travail")
        self.projet = config.Projet(racine=self.clone)

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)

    def test_seules_les_branches_contenues_sont_proposees(self):
        self.assertEqual(humain.branches_a_supprimer(self.projet), ["codex/ui", "fusionnee"])

    def test_la_politique_garde_certaines_branches(self):
        self.projet.politique = {"human": {"keep_branches": ["codex/*"]}}
        self.assertEqual(humain.branches_a_supprimer(self.projet), ["fusionnee"])

    def test_elles_apparaissent_dans_ce_qui_revient_a_l_humain(self):
        (self.clone / "memoire").mkdir()
        quoi = [e.quoi for e in humain.a_faire(self.projet)]
        self.assertTrue(any("`fusionnee`" in q for q in quoi), quoi)


class TestDernierMessage(unittest.TestCase):
    def ecrire(self, objets):
        p = Path(tempfile.mkdtemp()) / "t.jsonl"
        p.write_text("\n".join(json.dumps(o) for o in objets) + "\n")
        return p

    def test_dernier_texte_de_l_agent(self):
        p = self.ecrire([
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "ancien"}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}},
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash"}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "Fait.\n\nPour toi : rien.\nEnsuite : B-0001."}]}},
        ])
        message = humain.dernier_message(p)
        self.assertEqual(message, "Fait.\n\nPour toi : rien.\nEnsuite : B-0001.")
        self.assertEqual(humain.recap_manquant(config.Projet(racine=Path(".")), message), [])

    def test_sans_recap(self):
        manque = humain.recap_manquant(config.Projet(racine=Path(".")), "Fait. Rien à signaler pour toi.")
        self.assertEqual(manque, ["Pour toi :", "Ensuite :"])

    def test_transcript_illisible(self):
        self.assertIsNone(humain.dernier_message(Path("/inexistant/t.jsonl")))


if __name__ == "__main__":
    unittest.main()
