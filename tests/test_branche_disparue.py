"""B-0167, ADR-0104 : le hook avant push garde le dernier commit que ce
clone a poussé vers chaque référence distante ; une branche distante
disparue sans fusion se juge depuis lui, comme si elle y était encore. Une
branche fusionnée puis repartie de la branche par défaut se juge comme une
branche neuve, contre elle ; un premier push, sans trace, comme avant."""

import contextlib
import io
import json
import shutil
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from socle import config, hooks, installer as installeur
from tests.test_attendus import MOTEUR, TEST, git

NUL = "0" * 40
TEST_TRIPLE = ("import unittest\n\nfrom calc import triple\n\n\nclass T(unittest.TestCase):\n"
               "    def test_triple(self):\n        self.assertEqual(triple(2), {attendu})\n")


class TestBrancheDisparue(unittest.TestCase):
    """Un projet installé, poussé sur une origine nue ; la branche de
    travail y ajoute un test, que seule elle a."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-branche-disparue-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        self.origine = self.racine.parent / (self.racine.name + "-origine.git")
        self.addCleanup(shutil.rmtree, self.origine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n\n\ndef triple(x):\n    return 3 * x\n")
        (self.racine / "tests").mkdir()
        (self.racine / "tests/test_calc.py").write_text(TEST.format(attendu=4))
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        self.commit("base")
        git(self.racine.parent, "init", "-q", "--bare", str(self.origine))
        git(self.racine, "remote", "add", "origin", str(self.origine))
        git(self.racine, "push", "-q", "--no-verify", "origin", "main")
        git(self.racine, "checkout", "-qb", "travail")

    def commit(self, message, *options):
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", message, "--no-verify", *options)

    def tete(self) -> str:
        return git(self.racine, "rev-parse", "HEAD").strip()

    def projet(self) -> config.Projet:
        return config.Projet.charger(self.racine)

    def pousser(self, branche: str = "travail") -> tuple[int, str]:
        """Le hook avant push, sur le push de la branche vers son homonyme,
        avec le commit distant que l'origine a vraiment ; le push part s'il
        laisse passer."""
        distant = git(self.racine, "ls-remote", "origin", f"refs/heads/{branche}").split()
        ligne = f"refs/heads/{branche} {self.tete()} refs/heads/{branche} {distant[0] if distant else NUL}\n"
        with unittest.mock.patch("sys.stdin", io.StringIO(ligne)), contextlib.redirect_stderr(io.StringIO()) as flux:
            code = hooks.git_pre_push(self.projet())
        if code == 0:
            git(self.racine, "push", "-q", "--no-verify", "--force", "origin", f"HEAD:refs/heads/{branche}")
        return code, flux.getvalue()

    def supprimer_la_branche_distante(self, branche: str = "travail"):
        """Ce que seul l'humain fait : la branche distante disparaît, sans
        que ce clone le sache autrement que par le push suivant."""
        git(self.racine, "push", "-q", "--no-verify", "origin", "--delete", branche)

    def pousser_le_test(self) -> str:
        (self.racine / "tests/test_triple.py").write_text(TEST_TRIPLE.format(attendu=6))
        self.commit("Le test de triple")
        code, sortie = self.pousser()
        self.assertEqual(code, 0, sortie)
        return self.tete()

    def test_une_valeur_poussee_puis_affaiblie_apres_la_suppression_de_la_branche_est_refusee(self):
        pousse = self.pousser_le_test()
        self.supprimer_la_branche_distante()
        # La valeur affaiblie, l'historique réécrit : contre la branche par
        # défaut, où le test n'existe pas, rien ne le verrait.
        (self.racine / "tests/test_triple.py").write_text(TEST_TRIPLE.format(attendu=6.0))
        self.commit("Le test de triple", "--amend")
        code, sortie = self.pousser()
        self.assertEqual(code, 1, sortie)
        self.assertIn("tests.attendus", sortie)
        self.assertIn(f"le dernier commit que ce clone y a poussé ({pousse[:10]})", sortie)
        self.assertIn("Supprimer la branche distante n'est pas une issue", sortie)
        lignes = [f"refs/heads/travail {self.tete()} refs/heads/travail {NUL}"]
        self.assertIn("tests.attendus", hooks.plage_poussee(self.projet(), lignes).controles_en_echec())
        self.assertEqual(hooks.dernier_pousse(self.projet(), "refs/heads/travail"), pousse)
        # Rétablie, la valeur repart.
        (self.racine / "tests/test_triple.py").write_text(TEST_TRIPLE.format(attendu=6))
        self.commit("Le test de triple", "--amend")
        code, sortie = self.pousser()
        self.assertEqual(code, 0, sortie)

    def test_une_branche_fusionnee_puis_repartie_de_la_branche_par_defaut_n_est_pas_refusee(self):
        self.pousser_le_test()
        # L'humain fusionne, puis change sur la branche par défaut la valeur
        # que la branche avait poussée ; GitHub supprime la branche distante.
        git(self.racine, "checkout", "-q", "main")
        git(self.racine, "merge", "-q", "--no-ff", "--no-verify", "-m", "Fusion de travail", "travail")
        (self.racine / "tests/test_triple.py").write_text(TEST_TRIPLE.format(attendu=6.0))
        self.commit("L'humain change la valeur")
        git(self.racine, "push", "-q", "--no-verify", "origin", "main")
        self.supprimer_la_branche_distante()
        git(self.racine, "fetch", "-q", "origin")
        git(self.racine, "checkout", "-q", "-B", "travail", "origin/main")
        (self.racine / "calc.py").write_text((self.racine / "calc.py").read_text() + "\n\nUN = 1\n")
        self.commit("La suite")
        self.assertIsNone(hooks.dernier_pousse(self.projet(), "refs/heads/travail"))
        code, sortie = self.pousser()
        self.assertEqual(code, 0, sortie)
        self.assertNotIn("Supprimer la branche distante", sortie)

    def test_un_premier_push_sans_trace_se_juge_comme_avant(self):
        (self.racine / "tests/test_triple.py").write_text(TEST_TRIPLE.format(attendu=6))
        self.commit("Le test de triple")
        (self.racine / "tests/test_triple.py").write_text(TEST_TRIPLE.format(attendu=6.0))
        self.commit("Le test de triple, réécrit avant tout push")
        projet = self.projet()
        self.assertIsNone(hooks.dernier_pousse(projet, "refs/heads/travail"))
        lignes = [f"refs/heads/travail {self.tete()} refs/heads/travail {NUL}"]
        self.assertEqual(hooks.plage_poussee(projet, lignes).constats, [])
        code, sortie = self.pousser()
        self.assertEqual(code, 0, sortie)
        self.assertEqual(hooks.dernier_pousse(projet, "refs/heads/travail"), self.tete())

    def test_garder_pousses_dans_le_repertoire_commun_sans_rien_effacer_a_la_suppression(self):
        (self.racine / "tests/test_triple.py").write_text(TEST_TRIPLE.format(attendu=6))
        self.commit("Le test de triple")
        pousse = self.tete()
        hooks.garder_pousses(self.racine, [f"refs/heads/travail {pousse} refs/heads/travail {NUL}",
                                           f"refs/heads/proto/x {pousse} refs/heads/proto/x {NUL}"])
        hooks.garder_pousses(self.racine, [f"(delete) {NUL} refs/heads/travail {pousse}"])
        garde = json.loads((self.racine / ".git/socle/pushed.json").read_text())
        self.assertEqual(garde, {"refs/heads/proto/x": pousse, "refs/heads/travail": pousse})
        # Un autre worktree du clone lit la même trace.
        ailleurs = self.racine.parent / (self.racine.name + "-ailleurs")
        self.addCleanup(shutil.rmtree, ailleurs, ignore_errors=True)
        git(self.racine, "worktree", "add", "-q", "-b", "autre", str(ailleurs))
        self.assertEqual(hooks.dernier_pousse(config.Projet.charger(ailleurs), "refs/heads/travail"), pousse)
        # Une branche jetable reste hors du jugement de la plage (D-0087).
        (self.racine / "tests/test_triple.py").write_text(TEST_TRIPLE.format(attendu=6.0))
        self.commit("Le test de triple", "--amend")
        travail = [f"refs/heads/travail {self.tete()} refs/heads/travail {NUL}"]
        self.assertIn("tests.attendus", hooks.plage_poussee(self.projet(), travail).controles_en_echec())
        jetable = [f"refs/heads/proto/x {self.tete()} refs/heads/proto/x {NUL}"]
        self.assertEqual(hooks.plage_poussee(self.projet(), jetable).constats, [])


if __name__ == "__main__":
    unittest.main()
