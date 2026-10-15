"""Le balayage de mutation planifié (B-0005) : la commande de l'adaptateur,
module par module ; le workflow que pose l'installeur, sauf quand le projet
balaie déjà ; et sa vivacité, que la CI vérifie à chaque push."""

import contextlib
import io
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from socle import (config, context as contexte, checks_tests as controles_tests, installer as installeur, mutation,
                   utils as outils)
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
MAINTENANT = datetime(2026, 10, 13, 12, tzinfo=timezone.utc)


def il_y_a(jours: int) -> str:
    return (MAINTENANT - timedelta(days=jours)).strftime("%Y-%m-%dT%H:%M:%SZ")


def depot(fichiers: dict[str, str] | None = None) -> Path:
    racine = Path(tempfile.mkdtemp(prefix="socle-balayage-"))
    env = {**os.environ, "HOME": str(racine), "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=racine, check=True, env=env)
    for chemin, texte in (fichiers or {}).items():
        p = racine / chemin
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texte, encoding="utf-8")
    return racine


def installer(racine: Path, adaptateur: str = "python") -> str:
    sortie = io.StringIO()
    with contextlib.redirect_stdout(sortie):
        installeur.installer(racine, adaptateur, "@essai", source=MOTEUR)
    return sortie.getvalue()


class TestVivacite(unittest.TestCase):
    def test_un_workflow_endormi_par_github(self):
        niveau, message = mutation.vivacite("disabled_inactivity", il_y_a(70), il_y_a(200), MAINTENANT)
        self.assertEqual(niveau, "erreur")
        self.assertIn("disabled_inactivity", message)
        self.assertIn("Enable workflow", message)

    def test_un_workflow_qui_ne_tourne_plus(self):
        niveau, message = mutation.vivacite("active", il_y_a(16), il_y_a(200), MAINTENANT)
        self.assertEqual(niveau, "erreur")
        self.assertIn("il y a 16 jours", message)

    def test_un_mardi_manque_passe(self):
        self.assertEqual(mutation.vivacite("active", il_y_a(15), il_y_a(200), MAINTENANT)[0], None)
        self.assertEqual(mutation.vivacite("active", il_y_a(3), il_y_a(200), MAINTENANT),
                         (None, "dernier balayage il y a 3 jour(s)"))

    def test_un_workflow_neuf_attend_son_premier_creneau(self):
        niveau, message = mutation.vivacite("active", None, il_y_a(2), MAINTENANT)
        self.assertEqual(niveau, "avertir")
        self.assertIn("pas encore de balayage", message)

    def test_un_workflow_que_github_ne_connait_pas(self):
        # B-0063 : pas encore fusionné, un avertissement ; fusionné mais
        # inconnu, un avertissement le temps du délai, puis une erreur.
        nom = "socle-mutation.yml"
        self.assertEqual(mutation.inconnu_de_github(nom, None, MAINTENANT)[0], "avertir")
        niveau, message = mutation.inconnu_de_github(nom, il_y_a(1), MAINTENANT)
        self.assertEqual(niveau, "avertir")
        self.assertIn("ne le connaît pas encore", message)
        niveau, message = mutation.inconnu_de_github(nom, il_y_a(mutation.DELAI_ENREGISTREMENT), MAINTENANT)
        self.assertEqual(niveau, "erreur")
        self.assertIn("Pousser un commit sur la branche par défaut", message)

    def test_le_remede_dit_de_modifier_le_fichier_du_workflow(self):
        # B-0063, mesuré le 15 oct. : GitHub n'a enregistré le balayage qu'au
        # push qui modifiait son fichier, ni au premier push, ni au suivant.
        _, message = mutation.inconnu_de_github("socle-mutation.yml", il_y_a(10), MAINTENANT)
        self.assertIn("qui modifie ce fichier (une ligne de commentaire suffit", message)
        self.assertIn("qu'au push qui modifie son fichier", message)

    def test_un_workflow_ancien_sans_aucun_balayage(self):
        niveau, message = mutation.vivacite("active", None, il_y_a(40), MAINTENANT)
        self.assertEqual(niveau, "erreur")
        self.assertIn("aucun balayage en 40 jours", message)


class TestWorkflowDeBalayage(unittest.TestCase):
    CAP = {"command": "cargo mutants --file {module} --output {output}", "parser": "cargo-mutants"}

    def trouver(self, fichiers: dict[str, str], sauf_le_sien=False):
        return mutation.workflow_de_balayage(self.CAP, list(fichiers), fichiers.get, sauf_le_sien)

    def test_celui_du_socle_d_abord(self):
        fichiers = {mutation.WORKFLOW: "x", ".github/workflows/mutation.yml": "run: cargo mutants --file a"}
        self.assertEqual(self.trouver(fichiers), mutation.WORKFLOW)
        self.assertEqual(self.trouver(fichiers, sauf_le_sien=True), ".github/workflows/mutation.yml")

    def test_un_workflow_du_projet_qui_nomme_l_outil(self):
        fichiers = {".github/workflows/ci.yml": "run: cargo test",
                    ".github/workflows/socle.yml": "run: cargo mutants",
                    ".github/workflows/nuit.yaml": "run: cargo-mutants --version"}
        self.assertEqual(self.trouver(fichiers), ".github/workflows/nuit.yaml")

    def test_rien(self):
        self.assertIsNone(self.trouver({".github/workflows/ci.yml": "run: cargo test", "outils/cargo-mutants.yml": "x"}))


class TestCommandesDeBalayage(unittest.TestCase):
    def setUp(self):
        self.racine = depot()
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)

    def projet(self, mutation_, caps=None):
        p = config.Projet(self.racine)
        p.adaptateur = {"capabilities": {"mutation": mutation_}}
        p.garde_fous = {"mutation": {"caps": caps or {}}}
        return p

    def test_une_commande_par_module_chacune_dans_son_dossier(self):
        p = self.projet({"command": "outil --file {module} --output {output}"},
                        {"src/b c.rs": {"max": 0}, "src/a.rs": {"pending": True}})
        commandes, dossier, faute = mutation.commandes_de_balayage(p)
        self.assertIsNone(faute)
        self.assertEqual(dossier, self.racine / mutation.SORTIES)
        self.assertEqual(commandes, [f"outil --file src/a.rs --output {dossier / '000'}",
                                     f"outil --file 'src/b c.rs' --output {dossier / '001'}"])

    def test_module_par_module_sans_dossier_de_sortie(self):
        p = self.projet({"command": "outil --file {module}"}, {"src/a.rs": {"max": 0}})
        commandes, _, faute = mutation.commandes_de_balayage(p)
        self.assertEqual(commandes, [])
        self.assertIn("écraserait le précédent", faute)

    def test_tout_le_projet_d_un_coup(self):
        p = self.projet({"command": "mutmut run"}, {"calc.py": {"max": 0}})
        self.assertEqual(mutation.commandes_de_balayage(p), (["mutmut run"], self.racine, None))

    def test_sans_mutation(self):
        p = self.projet({"absent": "pas d'outil"})
        self.assertEqual(mutation.commandes_de_balayage(p)[2], "capacité absente : pas d'outil")


class TestBalayer(unittest.TestCase):
    """La commande tourne, son verdict suit ; un module que la commande n'a
    pas couvert casse."""

    def setUp(self):
        self.racine = depot({"calc.py": "def double(x):\n    return 2 * x\n",
                             "unites.py": "def centimes(x):\n    return 100 * x\n"})
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)

    def projet(self, commande, caps):
        p = config.Projet(self.racine)
        p.adaptateur = {"capabilities": {"mutation": {"command": commande, "parser": "mutmut"}}}
        p.garde_fous = {"mutation": {"caps": caps}}
        return p

    def ecrire(self, lignes: str, dans: str = ".") -> str:
        """Une commande qui écrit un résultat de mutmut, comme l'outil."""
        return (f"{sys.executable} -c \"import pathlib, sys; d = pathlib.Path(sys.argv[1]); d.mkdir(parents=True, "
                f"exist_ok=True); (d / 'mutmut-results.txt').write_text(sys.argv[2])\" {dans} '{lignes}'")

    def test_module_par_module(self):
        # Un outil factice qui, comme cargo-mutants, balaie un fichier et
        # écrit dans le dossier qu'on lui donne ; mutmut nomme le module
        # sans son extension.
        outil = self.racine.parent / f"{self.racine.name}-outil.py"
        self.addCleanup(outil.unlink)
        outil.write_text("import pathlib, sys\nm, d = sys.argv[2], pathlib.Path(sys.argv[4])\n"
                         "d.mkdir(parents=True)\n"
                         "(d / 'mutmut-results.txt').write_text(m.removesuffix('.py') + '.x_f__mutmut_1: killed')\n")
        p = self.projet(f"{sys.executable} {outil} --file {{module}} --output {{output}}",
                        {"calc.py": {"max": 0}, "unites.py": {"max": 0}})
        (self.racine / mutation.SORTIES / "vieux").mkdir(parents=True)
        flux = io.StringIO()
        r = mutation.balayer(p, flux=flux)
        self.assertTrue(r.reussi, r.texte())
        self.assertEqual(sorted(x.name for x in (self.racine / mutation.SORTIES).iterdir()), ["000", "001"],
                         "les sorties d'un balayage précédent sont effacées")
        self.assertIn("--file calc.py", flux.getvalue())

    def test_un_module_que_le_balayage_n_a_pas_couvert_casse(self):
        p = self.projet(self.ecrire("calc.x_f__mutmut_1: killed"), {"calc.py": {"max": 0}, "unites.py": {"max": 0}})
        r = mutation.balayer(p, flux=io.StringIO())
        self.assertEqual([c.message for c in r.erreurs()],
                         ["unites.py : aucun résultat — le balayage n'a pas tourné sur ce module"])

    def test_un_survivant_au_dela_du_plafond_casse(self):
        p = self.projet(self.ecrire("calc.x_f__mutmut_1: survived"), {"calc.py": {"max": 0}})
        self.assertFalse(mutation.balayer(p, flux=io.StringIO()).reussi)

    def test_la_commande_sans_dossier_de_sortie_ne_tourne_pas(self):
        temoin = self.racine / "lance"
        p = self.projet(f"touch {temoin} {{module}}", {"calc.py": {"max": 0}})
        r = mutation.balayer(p, flux=io.StringIO())
        self.assertFalse(r.reussi)
        self.assertFalse(temoin.exists())


GH = """#!{python}
import json, sys
chemin = sys.argv[2] if sys.argv[1:2] == ["api"] else ""
reponses = json.loads({reponses!r})
for cle, valeur in reponses.items():
    if chemin.endswith(cle):
        if valeur is None:
            sys.stderr.write("gh: Not Found (HTTP 404)\\n")
            sys.exit(1)
        print(json.dumps(valeur))
        sys.exit(0)
sys.exit(1)
"""


class TestEtatDuBalayage(unittest.TestCase):
    """La vivacité lue par `gh`, simulé : l'état du workflow, puis sa
    dernière exécution."""

    def setUp(self):
        self.racine = depot()
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        self.bin = self.racine / "bin"
        self.bin.mkdir()
        chemin = os.environ.get("PATH", "")
        self.addCleanup(os.environ.__setitem__, "PATH", chemin)
        os.environ["PATH"] = f"{self.bin}{os.pathsep}{chemin}"

    def gh(self, reponses: dict):
        p = self.bin / "gh"
        p.write_text(GH.format(python=sys.executable, reponses=json.dumps(reponses)))
        p.chmod(p.stat().st_mode | stat.S_IXUSR)

    def etat(self, fichiers=(mutation.WORKFLOW,), url="https://github.com/essai/calc"):
        p = config.Projet(self.racine)
        p.adaptateur = {"capabilities": {"mutation": {"command": "mutmut run", "parser": "mutmut"}}}
        p.politique = {"human": {"repo_url": url}} if url else {}
        return mutation.etat_du_balayage(p, list(fichiers), lambda f: "")

    def test_endormi(self):
        self.gh({"/socle-mutation.yml": {"state": "disabled_inactivity", "created_at": "2026-01-01T00:00:00Z"},
                 "/runs?per_page=1&status=completed": {"workflow_runs": []}})
        niveau, message, flux, page = self.etat()
        self.assertEqual((niveau, flux), ("erreur", mutation.WORKFLOW))
        self.assertEqual(page, "https://github.com/essai/calc/actions/workflows/socle-mutation.yml")

    def test_vivant(self):
        hier = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.gh({"/socle-mutation.yml": {"state": "active", "created_at": "2026-01-01T00:00:00Z"},
                 "/runs?per_page=1&status=completed": {"workflow_runs": [{"created_at": hier}]}})
        self.assertEqual(self.etat()[:2], (None, "dernier balayage il y a 1 jour(s)"))

    def test_pas_encore_sur_la_branche_par_defaut(self):
        self.gh({"/socle-mutation.yml": None})
        niveau, message, _, _ = self.etat()
        self.assertEqual(niveau, "avertir")
        self.assertIn("pas encore sur la branche par défaut", message)

    def test_present_sur_la_branche_par_defaut_mais_inconnu_de_github(self):
        # B-0063 : le fichier est fusionné depuis dix jours, GitHub rend 404.
        (self.racine / ".github/workflows").mkdir(parents=True)
        (self.racine / mutation.WORKFLOW).write_text("name: Socle — mutation\n")
        il_y_a_dix_jours = (datetime.now(timezone.utc) - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t", "GIT_COMMITTER_DATE": il_y_a_dix_jours, "GIT_AUTHOR_DATE": il_y_a_dix_jours}
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True, env=env)
        subprocess.run(["git", "commit", "-qm", "balayage", "--no-verify"], cwd=self.racine, check=True, env=env)
        subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], cwd=self.racine, check=True)
        self.assertEqual(mutation.arrivee_sur_la_branche_par_defaut(self.racine, mutation.WORKFLOW)[:10],
                         il_y_a_dix_jours[:10])
        self.gh({"/socle-mutation.yml": None})
        niveau, message, _, _ = self.etat()
        self.assertEqual(niveau, "erreur")
        self.assertIn(f"est sur la branche par défaut depuis le {il_y_a_dix_jours[:10]}, mais GitHub ne le "
                      "connaît pas : son cron ne part jamais", message)

    def test_sans_jeton(self):
        self.gh({})
        self.assertEqual(self.etat()[0], "indisponible")

    def test_aucun_workflow(self):
        niveau, message, _, _ = self.etat(fichiers=())
        self.assertEqual(niveau, "erreur")
        self.assertIn(mutation.WORKFLOW, message)

    def test_hors_de_github(self):
        self.assertEqual(self.etat(url="https://gitlab.com/essai/calc")[0], "indisponible")

    def test_le_controle_le_dit_en_ci(self):
        self.gh({"/socle-mutation.yml": {"state": "disabled_manually", "created_at": "2026-01-01T00:00:00Z"}})
        installer(self.racine, "python-pytest")
        (self.racine / ".socle/policy.toml").write_text(
            (self.racine / ".socle/policy.toml").read_text().replace(
                "[human]\n", '[human]\nrepo_url = "https://github.com/essai/calc"\n', 1))
        r = Rapport()
        controles_tests.vivante(contexte.Contexte(config.Projet.charger(self.racine), etage="ci"), r)
        self.assertEqual([(c.chemin, "disabled_manually" in c.message) for c in r.erreurs("mutation.vivante")],
                         [(mutation.WORKFLOW, True)])


class TestCommande(unittest.TestCase):
    def test_un_balayage_qui_casse_rend_un_code_non_nul(self):
        from argparse import Namespace

        from socle import cli

        racine = depot({"calc.py": "def double(x):\n    return 2 * x\n"})
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        installer(racine, "python-pytest")
        adaptateur = racine / ".socle/adapter.toml"
        texte = adaptateur.read_text()
        debut = texte.index("command = ", texte.index("[capabilities.mutation]"))
        fin = texte.index("\n", debut)
        # Le module est hors de `src/`, que l'adaptateur balaie : le plafond
        # reste vide, et un vert y serait silencieux.
        adaptateur.write_text(texte[:debut] + 'command = "true"' + texte[fin:])
        with contextlib.redirect_stdout(io.StringIO()) as sortie:
            code = cli.cmd_mutation_run(Namespace(root=str(racine), poser=False))
        self.assertEqual(code, 1)
        self.assertIn("plafond vide", sortie.getvalue())
        self.assertIn("$ true", sortie.getvalue())


class TestInstallation(unittest.TestCase):
    def setUp(self):
        self.racine = None

    def tearDown(self):
        shutil.rmtree(self.racine, ignore_errors=True)

    def test_le_workflow_et_sa_ligne_quand_l_adaptateur_balaie(self):
        self.racine = depot({"Cargo.toml": "[package]\nname = \"calc\"\n", "src/lib.rs": "pub fn f() {}\n"})
        journal = installer(self.racine, "rust")
        flux = (self.racine / mutation.WORKFLOW).read_text()
        self.assertIn("run: |\n          cargo install cargo-mutants --locked\n", flux)
        self.assertIn("rustup show active-toolchain", flux)
        self.assertIn("python3 .socle/socle mutation-run --record", flux)
        self.assertNotIn("@@", flux)
        self.assertIn("`.github/workflows/socle-mutation.yml`", (self.racine / "AGENTS.md").read_text())
        self.assertIn(mutation.WORKFLOW, journal)
        self.assertIn(mutation.WORKFLOW, config.Projet.charger(self.racine).chemins_proteges())

    def test_rien_sans_mutation(self):
        self.racine = depot({"calc.py": "def f():\n    return 1\n"})
        installer(self.racine, "python")
        self.assertFalse((self.racine / mutation.WORKFLOW).exists())
        agents = (self.racine / "AGENTS.md").read_text()
        self.assertNotIn("socle-mutation", agents)
        self.assertNotIn("@@", agents)

    def test_un_projet_qui_balaie_deja_n_en_recoit_pas_un_second(self):
        # Le cas du projet d'échecs : son propre workflow lance cargo-mutants.
        self.racine = depot({"Cargo.toml": "[package]\nname = \"calc\"\n", "src/lib.rs": "pub fn f() {}\n",
                             ".github/workflows/mutation.yml": "jobs:\n  m:\n    steps:\n      - run: cargo mutants\n"})
        journal = installer(self.racine, "rust")
        self.assertFalse((self.racine / mutation.WORKFLOW).exists())
        self.assertIn("`.github/workflows/mutation.yml` le lance déjà", journal)
        fichiers = outils.fichiers_courants(self.racine)
        cap = config.Projet.charger(self.racine).adaptateur["capabilities"]["mutation"]
        self.assertEqual(mutation.workflow_de_balayage(cap, fichiers, lambda f: outils.lire_a(self.racine, None, f)),
                         ".github/workflows/mutation.yml")


if __name__ == "__main__":
    unittest.main()
