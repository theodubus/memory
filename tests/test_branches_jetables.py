"""Les branches jetables (D-0087, ADR-0055) : des prototypes qu'on ne
fusionne pas, déclarés par le début de leur nom (`proto/` par défaut). La CI
du socle ne les juge pas aux envois ; hors de la CI, les liens morts d'un
fichier qu'elles ajoutent ne sont qu'un avertissement ; une pull request qui
en part les juge en entier."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from socle import checks_memory as controles_memoire, checks_ratchet as cliquet, config, context as contexte
from socle import hooks, installer as installeur, memory as memoire, utils as outils
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestReglage(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-jetables-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        (self.racine / ".socle").mkdir()

    def projet(self, garde_fous: str = "") -> config.Projet:
        (self.racine / ".socle/guardrails.toml").write_text(garde_fous)
        return config.Projet.charger(self.racine)

    def test_proto_par_defaut(self):
        projet = self.projet()
        self.assertEqual(projet.branches_jetables(), ["proto/"])
        self.assertTrue(projet.branche_jetable("proto/essai"))
        self.assertFalse(projet.branche_jetable("travail"))
        self.assertFalse(projet.branche_jetable(None))

    def test_le_projet_les_declare(self):
        projet = self.projet('[branches]\ndisposable = ["essai/", ""]\n')
        self.assertEqual(projet.branches_jetables(), ["essai/"])
        self.assertTrue(projet.branche_jetable("essai/x"))
        self.assertFalse(projet.branche_jetable("proto/x"))
        self.assertEqual(self.projet("[branches]\ndisposable = []\n").branches_jetables(), [])

    def test_en_ajouter_assouplit_les_retirer_durcit(self):
        defaut = {"branches": {"disposable": ["proto/"]}}
        self.assertEqual(cliquet.assouplissements({}, defaut), [])
        self.assertEqual(cliquet.assouplissements(defaut, {}), [])
        self.assertEqual(cliquet.assouplissements({}, {"branches": {"disposable": []}}), [])
        plus = cliquet.assouplissements({}, {"branches": {"disposable": ["proto/", "essai/"]}})
        self.assertEqual([cle for cle, _ in plus], ["branches.disposable"])

    def test_la_ci_les_ecarte_des_envois(self):
        # Les étiquettes se nomment : sans elles, GitHub ne lancerait plus la
        # CI pour une étiquette poussée.
        self.assertEqual(installeur.ignorer_aux_envois(self.projet()),
                         '    branches-ignore: ["proto/**"]\n    tags: ["**"]\n')
        self.assertEqual(installeur.ignorer_aux_envois(self.projet('[branches]\ndisposable = ["essai-", "x/"]\n')),
                         '    branches-ignore: ["essai-**", "x/**"]\n    tags: ["**"]\n')
        self.assertEqual(installeur.ignorer_aux_envois(self.projet("[branches]\ndisposable = []\n")), "")

    def test_un_prefixe_a_caractere_de_motif_est_ignore_des_deux_cotes(self):
        # La CI lirait `essai-*` ou `wip+` en motif, les contrôles locaux en
        # préfixe littéral : ils ne désigneraient pas les mêmes branches.
        projet = self.projet('[branches]\ndisposable = ["essai-*", "wip+", "exp?", "a[b]", "!x", "bon.1_/"]\n')
        self.assertEqual(projet.branches_jetables(), ["bon.1_/"])
        self.assertFalse(projet.branche_jetable("essai-x"))
        self.assertFalse(projet.branche_jetable("wip+a"))
        self.assertEqual(installeur.ignorer_aux_envois(projet), '    branches-ignore: ["bon.1_/**"]\n    tags: ["**"]\n')
        self.assertEqual(self.projet('[branches]\ndisposable = "proto/"\n').branches_jetables(), [])


class TestSurUnProjet(unittest.TestCase):
    """Un projet équipé, sa branche par défaut commitée."""

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-jetables-projet-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR)
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()

    def references(self, etage: str) -> Rapport:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage=etage, base=self.base, tete=None)
        r = Rapport()
        controles_memoire.references(ctx, r)
        return r

    def test_la_ci_posee_ecarte_les_branches_jetables_des_envois(self):
        ci = (self.racine / ".github/workflows/socle.yml").read_text()
        self.assertIn('  push:\n    branches-ignore: ["proto/**"]\n    tags: ["**"]\n  pull_request:\n', ci)

    def test_branche_courante(self):
        self.assertEqual(outils.branche_courante(self.racine), "main")
        # Une étiquette du même nom ne fait pas lire `heads/proto/x`.
        git(self.racine, "checkout", "-q", "-b", "proto/x")
        git(self.racine, "tag", "proto/x")
        self.assertEqual(outils.branche_courante(self.racine), "proto/x")
        git(self.racine, "checkout", "-q", "--detach")
        self.assertIsNone(outils.branche_courante(self.racine))

    def contexte(self, **reglages) -> contexte.Contexte:
        reglages.setdefault("base", self.base)
        return contexte.Contexte(config.Projet.charger(self.racine), etage="git", tete=None, **reglages)

    def test_la_memoire_privee_reste_jugee_sur_une_branche_jetable(self):
        # Aucune CI ne relit la mémoire privée : la relâcher ici, ce serait
        # ne plus la juger nulle part.
        git(self.racine, "checkout", "-q", "-b", "proto/essai")
        prive = f"{memoire.DOSSIER_PRIVE}/canonical.md"
        self.assertEqual(controles_memoire.ajoutes_par_une_branche_jetable(self.contexte(), [prive, "vendu/A.md"]),
                         {"vendu/A.md"})

    def test_sans_base_rien_n_est_relache(self):
        # Sans branche par défaut, rien ne dit ce que la branche ajoute.
        git(self.racine, "checkout", "-q", "-b", "proto/essai")
        self.assertEqual(controles_memoire.ajoutes_par_une_branche_jetable(self.contexte(base=None), ["vendu/A.md"]),
                         set())

    def test_avant_un_push_chaque_branche_qui_le_recoit_doit_etre_jetable(self):
        # Depuis `proto/x`, `git push origin HEAD:travail` : la CI de
        # `travail` jugera tout, le hook aussi.
        git(self.racine, "checkout", "-q", "-b", "proto/x")
        ajoutes = controles_memoire.ajoutes_par_une_branche_jetable
        self.assertEqual(ajoutes(self.contexte(branches=["travail"]), ["vendu/A.md"]), set())
        self.assertEqual(ajoutes(self.contexte(branches=["proto/x", "travail"]), ["vendu/A.md"]), set())
        self.assertEqual(ajoutes(self.contexte(branches=["proto/y"]), ["vendu/A.md"]), {"vendu/A.md"})
        # Un push d'une branche jetable vers une autre, depuis `travail`.
        git(self.racine, "checkout", "-q", "-b", "travail")
        self.assertEqual(ajoutes(self.contexte(branches=["proto/y"]), ["vendu/A.md"]), {"vendu/A.md"})

    def test_les_branches_envoyees(self):
        zero, sha = "0" * 40, "a" * 40
        lignes = [f"refs/heads/proto/x {sha} refs/heads/travail {sha}",
                  f"refs/heads/y {zero} refs/heads/proto/z {sha}",
                  f"refs/tags/v1 {sha} refs/tags/v1 {zero}"]
        self.assertEqual(hooks.branches_envoyees(lignes), ["travail", "refs/tags/v1"])

    def test_un_lien_mort_d_un_fichier_ajoute_par_une_branche_jetable_est_averti_hors_de_la_ci(self):
        git(self.racine, "checkout", "-q", "-b", "proto/essai")
        (self.racine / "vendu").mkdir()
        (self.racine / "vendu/LISEZMOI.md").write_text("Voir [la doc](docs/absente.md).\n")
        r = self.references("git")
        self.assertEqual(r.erreurs("memoire.references"), [])
        self.assertTrue(any("branche jetable, fichier qu'elle ajoute" in c.message for c in r.constats))
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="git", base=self.base, tete=None)
        self.assertEqual(controles_memoire.ajoutes_par_une_branche_jetable(ctx, ["vendu/LISEZMOI.md", "calc.py"]),
                         {"vendu/LISEZMOI.md"})
        # La CI, celle de sa pull request, le juge en entier.
        self.assertEqual(len(self.references("ci").erreurs("memoire.references")), 1)

    def test_ailleurs_le_lien_mort_reste_refuse(self):
        git(self.racine, "checkout", "-q", "-b", "travail")
        (self.racine / "vendu").mkdir()
        (self.racine / "vendu/LISEZMOI.md").write_text("Voir [la doc](docs/absente.md).\n")
        self.assertEqual(len(self.references("git").erreurs("memoire.references")), 1)

    def test_un_fichier_deja_la_reste_juge_sur_une_branche_jetable(self):
        (self.racine / "LISEZMOI.md").write_text("Le projet.\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "lisez-moi", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        git(self.racine, "checkout", "-q", "-b", "proto/essai")
        (self.racine / "LISEZMOI.md").write_text("Voir [la doc](docs/absente.md).\n")
        self.assertEqual(len(self.references("git").erreurs("memoire.references")), 1)

    def test_la_plage_poussee_d_une_branche_jetable_n_est_pas_jugee_comme_la_ci(self):
        # Un seuil relâché dans la plage qui part : la CI le refuserait.
        gf = self.racine / ".socle/guardrails.toml"
        gf.write_text(gf.read_text().replace("max_bytes = 16000", "max_bytes = 99000", 1))
        git(self.racine, "commit", "-qam", "seuil relâché", "--no-verify")
        local = git(self.racine, "rev-parse", "HEAD").strip()
        projet = config.Projet.charger(self.racine)
        jugee = hooks.plage_poussee(projet, [f"refs/heads/travail {local} refs/heads/travail {self.base}"])
        self.assertIn("cliquet.garde-fous", jugee.controles_en_echec())
        jetable = hooks.plage_poussee(projet, [f"refs/heads/proto/x {local} refs/heads/proto/x {self.base}"])
        self.assertEqual(jetable.controles_en_echec(), [])
        # C'est la branche distante qui compte, celle dont la CI tournera.
        vers_travail = hooks.plage_poussee(projet, [f"refs/heads/proto/x {local} refs/heads/travail {self.base}"])
        self.assertIn("cliquet.garde-fous", vers_travail.controles_en_echec())
        vers_proto = hooks.plage_poussee(projet, [f"refs/heads/travail {local} refs/heads/proto/x {self.base}"])
        self.assertEqual(vers_proto.controles_en_echec(), [])


if __name__ == "__main__":
    unittest.main()
