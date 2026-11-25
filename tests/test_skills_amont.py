"""En mode amont, les copies des skills du socle et les tests de leur texte
suivent leur gabarit sans validation de l'humain (B-0353, ADR-0110) ; en
mode projet, rien ne change."""

import contextlib
import io
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from socle import (checks_ratchet as controles_cliquet, checks_tests as controles_tests, config,
                   context as contexte, installer as installeur)
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
BATCH = "engine/socle/templates/skills/socle-batch/SKILL.md"
COPIE = ".claude/skills/socle-batch/SKILL.md"
PHRASE = "Un lot réunit ce qui se relit ensemble"
NOUVELLE = "Un lot rassemble ce qui se relit ensemble"
DU_MOTEUR = "Une phrase que le moteur imprime aussi."

TESTS = '''import re
import unittest
from pathlib import Path


def texte():
    gabarit = Path(__file__).resolve().parent.parent / "engine/socle/templates/skills/socle-batch/SKILL.md"
    return " ".join(gabarit.read_text(encoding="utf-8").split())


class TestTextes(unittest.TestCase):
    def test_le_skill_dit_ce_que_reunit_un_lot(self):
        """Le skill dit ce que réunit un lot, et pourquoi on le relit."""
        self.assertIn("Un lot réunit ce qui se relit ensemble", texte())

    def test_le_skill_dit_la_phrase_du_moteur(self):
        self.assertIn("Une phrase que le moteur imprime aussi.", texte())

    def test_le_skill_compte_ses_sections(self):
        self.assertEqual(texte().count("## "), 6)

    def test_le_skill_et_un_comportement(self):
        self.assertIn("Un lot réunit ce qui se relit ensemble", texte())
        self.assertEqual(len("abc"), 3)


class TestComportement(unittest.TestCase):
    def test_le_motif_ne_prend_pas_la_phrase(self):
        self.assertIsNone(re.search(r"^x$", "Un lot réunit ce qui se relit ensemble"))
'''


def git(cwd, *args):
    # Sans `CLAUDECODE` : un commit de ces tests est celui d'un humain.
    env = {**{k: v for k, v in os.environ.items() if k != "CLAUDECODE"}, "GIT_AUTHOR_NAME": "t",
           "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


def changer(racine: Path, chemin: str, avant: str, apres: str):
    p = racine / chemin
    texte = p.read_text(encoding="utf-8")
    assert avant in texte, (chemin, avant)
    p.write_text(texte.replace(avant, apres, 1), encoding="utf-8")


class _Depot(unittest.TestCase):
    """Un dépôt d'essai installé et commité une fois ; chaque test travaille
    sur sa copie, jugée contre le commit d'installation."""

    MODE = config.MODE_AMONT
    modele: Path

    @classmethod
    def setUpClass(cls):
        racine = Path(tempfile.mkdtemp(prefix="socle-skills-amont-"))
        cls.modele = racine
        git(racine, "init", "-q", "-b", "main")
        (racine / "calc.py").write_text("X = 1\n")
        (racine / "tests").mkdir()
        (racine / "tests/__init__.py").write_text("")
        (racine / "tests/test_textes.py").write_text(TESTS, encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            if cls.MODE == config.MODE_AMONT:
                shutil.copytree(MOTEUR, racine / "engine", ignore=shutil.ignore_patterns("__pycache__"))
                # Une phrase du skill que le moteur imprime aussi.
                changer(racine, BATCH, "\n## ", f"\n{DU_MOTEUR}\n\n## ")
                with open(racine / "engine/socle/utils.py", "a", encoding="utf-8") as f:
                    # En deux littéraux concaténés, comme le moteur écrit ses messages.
                    f.write('\n_ESSAI = ("Une phrase que le moteur " "imprime aussi.")\n')
                installeur.installer(racine, "python", "@essai", mode=config.MODE_AMONT, source=racine / "engine")
            else:
                installeur.installer(racine, "python", "@essai", source=MOTEUR)
        git(racine, "add", "-A")
        git(racine, "commit", "-qm", "installation", "--no-verify")
        cls.sha = git(racine, "rev-parse", "HEAD").strip()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.modele, ignore_errors=True)

    def setUp(self):
        self.enterContext(unittest.mock.patch.dict(os.environ))
        os.environ.pop("CLAUDECODE", None)
        dossier = Path(tempfile.mkdtemp(prefix="socle-skills-amont-copie-"))
        self.addCleanup(shutil.rmtree, dossier, ignore_errors=True)
        self.racine = dossier / "depot"
        shutil.copytree(self.modele, self.racine, symlinks=True)

    def contexte(self):
        return contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.sha)

    def poser(self, gabarit: str = BATCH, copie: str = COPIE):
        """La copie que l'installeur du dépôt d'essai poserait : son gabarit
        tel quel (`installer.skills_du_socle`)."""
        (self.racine / copie).write_text((self.racine / gabarit).read_text(encoding="utf-8"), encoding="utf-8")

    def juger(self, controle) -> Rapport:
        r = Rapport()
        controle(self.contexte(), r)
        return r


class TestLesCopiesEnModeAmont(_Depot):
    """T-0184 : la copie d'un skill du socle identique à son gabarit passe
    sans demande ; toute autre écriture reste refusée."""

    def test_une_copie_remise_par_l_installeur_passe_sans_demande(self):
        changer(self.racine, BATCH, PHRASE, NOUVELLE)
        self.poser()
        self.assertIn(NOUVELLE, (self.racine / COPIE).read_text(encoding="utf-8"))
        r = self.juger(controles_cliquet.proteges)
        self.assertEqual([c.chemin for c in r.erreurs("protege.fichiers")], [])
        self.assertIn(f"copie identique à son gabarit `{BATCH}`, en mode amont", r.texte())

    def test_une_copie_qui_differe_de_son_gabarit_reste_refusee(self):
        changer(self.racine, BATCH, PHRASE, NOUVELLE)
        self.poser()
        changer(self.racine, COPIE, NOUVELLE, NOUVELLE + ", sauf ce que l'agent préfère")
        r = self.juger(controles_cliquet.proteges)
        self.assertEqual([c.chemin for c in r.erreurs("protege.fichiers")], [COPIE])
        self.assertIsNone(controles_cliquet.suit_son_gabarit(self.contexte(), COPIE))

    def test_une_copie_changee_sans_son_gabarit_reste_refusee(self):
        changer(self.racine, COPIE, PHRASE, NOUVELLE)
        r = self.juger(controles_cliquet.proteges)
        self.assertEqual([c.chemin for c in r.erreurs("protege.fichiers")], [COPIE])

    def test_une_copie_retiree_avec_son_gabarit_passe(self):
        shutil.rmtree(self.racine / "engine/socle/templates/skills/socle-resume")
        (self.racine / ".claude/skills/socle-resume/SKILL.md").unlink()
        r = self.juger(controles_cliquet.proteges)
        self.assertEqual(r.erreurs("protege.fichiers"), [])
        # Le gabarit gardé, la copie retirée reste refusée.
        git(self.racine, "checkout", "-q", "--", "engine/socle/templates/skills/socle-resume")
        r = self.juger(controles_cliquet.proteges)
        self.assertEqual([c.chemin for c in r.erreurs("protege.fichiers")], [".claude/skills/socle-resume/SKILL.md"])

    def test_le_gabarit_est_celui_de_la_langue_de_la_memoire(self):
        ctx = self.contexte()
        self.assertEqual(controles_cliquet.gabarit_de_la_copie(ctx, COPIE), BATCH)
        self.assertIsNone(controles_cliquet.gabarit_de_la_copie(ctx, ".claude/skills/livrer/SKILL.md"))
        self.assertIsNone(controles_cliquet.gabarit_de_la_copie(ctx, ".claude/settings.json"))
        politique = self.racine / ".socle/policy.toml"
        politique.write_text(politique.read_text(encoding="utf-8") + '\n[memory]\nlanguage = "en"\n',
                             encoding="utf-8")
        self.assertEqual(controles_cliquet.gabarit_de_la_copie(self.contexte(), COPIE),
                         BATCH.replace("SKILL.md", "SKILL.en.md"))


class TestLesTestsDuTexteEnModeAmont(_Depot):
    """T-0185 : un test qui perd des phrases qu'un gabarit de skill a
    quittées passe sans validation ; tout autre changement de valeur
    attendue reste refusé."""

    def erreurs(self) -> list[str]:
        r = self.juger(controles_tests.attendus)
        self.rapport = r
        return [c.message for c in r.erreurs("tests.attendus")]

    def test_une_assertion_qui_suit_le_gabarit_passe_sans_validation(self):
        changer(self.racine, BATCH, PHRASE, NOUVELLE)
        changer(self.racine, "tests/test_textes.py", PHRASE, NOUVELLE)
        self.assertEqual(self.erreurs(), [])
        self.assertIn(f"il suit le gabarit `{BATCH}`, en mode amont", self.rapport.texte())

    def test_un_test_supprime_qui_suivait_le_gabarit_passe_sans_validation(self):
        changer(self.racine, BATCH, PHRASE, NOUVELLE)
        texte = (self.racine / "tests/test_textes.py").read_text(encoding="utf-8")
        debut = texte.index("    def test_le_skill_dit_ce_que_reunit_un_lot")
        fin = texte.index("    def test_le_skill_dit_la_phrase_du_moteur")
        (self.racine / "tests/test_textes.py").write_text(texte[:debut] + texte[fin:], encoding="utf-8")
        self.assertEqual(self.erreurs(), [])

    def test_une_phrase_que_le_moteur_imprime_reste_refusee(self):
        changer(self.racine, BATCH, DU_MOTEUR, "")
        changer(self.racine, "tests/test_textes.py", DU_MOTEUR, PHRASE)
        fautes = self.erreurs()
        self.assertEqual(len(fautes), 1, fautes)
        self.assertIn("test_le_skill_dit_la_phrase_du_moteur", fautes[0])

    def test_une_phrase_que_le_gabarit_garde_reste_refusee(self):
        changer(self.racine, BATCH, "# Mener un lot", "# Mener un lot du backlog")
        changer(self.racine, "tests/test_textes.py", PHRASE, "Mener un lot du backlog")
        fautes = self.erreurs()
        self.assertEqual(len(fautes), 1, fautes)
        self.assertIn("test_le_skill_dit_ce_que_reunit_un_lot", fautes[0])

    def test_une_assertion_sans_phrase_reste_refusee(self):
        changer(self.racine, BATCH, PHRASE, NOUVELLE + "\n\n## Une section de plus\n")
        changer(self.racine, "tests/test_textes.py", 'count("## "), 6)', 'count("## "), 7)')
        fautes = self.erreurs()
        self.assertEqual(len(fautes), 1, fautes)
        self.assertIn("test_le_skill_compte_ses_sections", fautes[0])

    def test_une_assertion_sans_phrase_ne_passe_pas_avec_la_phrase_du_meme_test(self):
        """ADR-0111 : chaque assertion perdue a ses phrases ; une valeur de
        comportement ne passe pas avec la phrase d'un skill."""
        changer(self.racine, BATCH, PHRASE, NOUVELLE)
        avant = f'self.assertIn("{PHRASE}", texte())\n        self.assertEqual(len("abc"), 3)'
        changer(self.racine, "tests/test_textes.py", avant,
                f'self.assertIn("{NOUVELLE}", texte())\n        self.assertEqual(len("abc"), 4)')
        fautes = self.erreurs()
        self.assertEqual(len(fautes), 1, fautes)
        self.assertIn("test_le_skill_et_un_comportement", fautes[0])
        # Supprimé en entier, le test garde son assertion sans phrase.
        changer(self.racine, "tests/test_textes.py", "len(\"abc\"), 4)", "len(\"abc\"), 3)")
        texte = (self.racine / "tests/test_textes.py").read_text(encoding="utf-8")
        debut = texte.index("    def test_le_skill_et_un_comportement")
        fin = texte.index("class TestComportement")
        (self.racine / "tests/test_textes.py").write_text(texte[:debut] + "\n" + texte[fin:], encoding="utf-8")
        fautes = self.erreurs()
        self.assertEqual(len(fautes), 1, fautes)
        self.assertIn("test_le_skill_et_un_comportement", fautes[0])

    def test_un_test_qui_ne_lit_aucun_skill_reste_refuse(self):
        """ADR-0111 : la phrase d'un gabarit, entrée d'un test de comportement
        (le motif d'un hook), ne le fait pas juger sur le texte des skills."""
        changer(self.racine, BATCH, PHRASE, NOUVELLE)
        changer(self.racine, "tests/test_textes.py", f'r"^x$", "{PHRASE}"', 'r"^x$", "autre chose encore"')
        fautes = self.erreurs()
        self.assertEqual(len(fautes), 1, fautes)
        self.assertIn("test_le_motif_ne_prend_pas_la_phrase", fautes[0])

    def test_sans_gabarit_de_skill_change_le_juge_ne_dit_rien(self):
        juge = controles_tests.juge_des_skills(self.contexte())
        self.assertIsNone(juge([PHRASE]))
        changer(self.racine, "tests/test_textes.py", PHRASE, NOUVELLE)
        self.assertEqual(len(self.erreurs()), 1)


class TestLesPhrases(unittest.TestCase):
    """Ce que le juge lit d'un test : ses phrases, sans sa documentation ; et
    du moteur : ses chaînes assemblées, coupées à leurs paramètres."""

    def test_les_chaines_du_moteur_assemblees_et_coupees_a_leurs_parametres(self):
        module = 'X = trad("fichier protégé {f} modifié " "sans validation humaine", f=f)\nY = f"court {a} b"\n'
        self.assertEqual(controles_tests.chaines_du_moteur(module),
                         ["fichier protégé", "modifié sans validation humaine"])
        self.assertEqual(controles_tests.chaines_du_moteur("def ("), ["def ("])

    def test_une_valeur_de_phrase(self):
        self.assertTrue(controles_tests.valeurs_de_phrase(['"une phrase assez longue"', '""']))
        self.assertFalse(controles_tests.valeurs_de_phrase(['"une phrase assez longue"', "3"]))
        self.assertFalse(controles_tests.valeurs_de_phrase(['"fr"']))

    CFG = {"strings": r'"(?:\\.|[^"\\])*"'}

    def test_les_phrases_d_un_test_sans_guillemets_ni_nombres(self):
        texte = 'self.assertIn("Un lot réunit ce qui\\n se relit", t)\nself.assertEqual(n, 123456789012345)\n' \
                'x = {"fr": "court", "en": "--unprompted --relayed"}'
        self.assertEqual(controles_tests.phrases([texte], self.CFG),
                         ["Un lot réunit ce qui\\n se relit", "--unprompted --relayed"])
        self.assertEqual(controles_tests.phrases(['"a b"', "12"], self.CFG), [])

    def test_la_documentation_qui_ouvre_le_corps_n_est_pas_une_phrase(self):
        corps = '        """Le skill dit ce que réunit\n        un lot."""\n        self.assertIn("Une phrase du skill", t)\n'
        reste = controles_tests.sans_documentation(corps)
        self.assertNotIn("réunit", reste)
        self.assertEqual(controles_tests.phrases([reste], self.CFG), ["Une phrase du skill"])
        # Une chaîne qui n'est pas seule sur sa ligne n'est pas une documentation.
        corps = '        "Une phrase du skill" in t or self.fail()\n'
        self.assertEqual(controles_tests.sans_documentation(corps), corps)


class TestEnModeProjet(_Depot):
    """En mode projet (chess), la copie suit son gabarit sous une demande,
    comme avant : rien ne change."""

    MODE = config.MODE_PROJET

    def test_la_copie_identique_a_son_gabarit_reste_refusee_et_le_juge_ne_dit_rien(self):
        gabarit = ".socle/engine/socle/templates/skills/socle-batch/SKILL.md"
        changer(self.racine, gabarit, PHRASE, NOUVELLE)
        self.poser(gabarit)
        self.assertEqual((self.racine / COPIE).read_text(encoding="utf-8"),
                         (self.racine / gabarit).read_text(encoding="utf-8"))
        ctx = self.contexte()
        self.assertIsNone(controles_cliquet.gabarit_de_la_copie(ctx, COPIE))
        r = self.juger(controles_cliquet.proteges)
        self.assertIn(COPIE, [c.chemin for c in r.erreurs("protege.fichiers")])
        self.assertIsNone(controles_tests.juge_des_skills(ctx)([PHRASE]))


if __name__ == "__main__":
    unittest.main()
