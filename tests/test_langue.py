"""B-0031 : la langue de la mémoire se choisit par projet. Les mots-clés du
format et les gabarits s'écrivent dans la sienne ; la lecture accepte toutes
les langues, pour qu'une mémoire en ajout seul n'ait rien à réécrire."""

import contextlib
import io
import os
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from socle import (cli, config, context as contexte, checks_memory as controles_memoire,
                   requests as demandes, human as humain, installer as installeur, language as langue,
                   memory as memoire, messages, utils as outils)
from socle.report import Rapport

MOTEUR = Path(__file__).resolve().parent.parent / "engine"
DEMANDE = """<!-- socle: layer=requests zone=public -->
# D-0001 — Choose the rounding mode of the calculator

> date : 2026-10-11

## Decision requested

Choose whether the calculator rounds half values up or to the nearest even number.

## Context

The calculator module multiplies and divides small amounts of money for the
invoices of the project. Today it truncates every result, which loses a cent
on roughly one invoice out of ten, and the accountant noticed it during the
last monthly closing. Two rounding modes are common: rounding half values up,
which people expect, and rounding half values to the nearest even number,
which banks use because it does not drift over many operations.

## Cited elements

- Nothing from the memory: the question comes from the accountant's remark.

## Where to look

- [the calculator](../../calc.py): check that every result goes through one function.

## Options

- Half up: small effort, low risk, reversible by changing one line.
- Half even: small effort, low risk of surprising people, reversible too.

## Consequences

If the human approves, I switch to half even. If they reject it, I switch to
half up. With no answer, nothing changes and truncation stays.

## Recommendation

Half even. Verified: the tests cover every operation. Assumed: the
accountant prefers no drift over intuition.

## Possible answers

- `approve` — half even.
- `reject` — half up.
- `insufficient-context` — the request goes back to the agent, who rewrites it.
"""


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
    env.update({"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)})
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


class TestVocabulaire(unittest.TestCase):
    def test_tout_mot_ecrit_revient_a_sa_cle_interne(self):
        self.assertEqual(langue.champ("status"), "statut")
        self.assertEqual(langue.champ("Statut"), "statut")
        self.assertEqual(langue.champ("superseded-by"), "remplacee-par")
        self.assertEqual(langue.statut("F", "measured"), "mesure")
        self.assertEqual(langue.statut("F", "Mesuré"), "mesure")
        self.assertEqual(langue.statut("B", "in progress"), "en-cours")
        self.assertEqual(langue.statut("B", "abandoned"), "abandonne")
        self.assertEqual(langue.statut("ADR", "abandoned"), "abandonnee")
        self.assertEqual(langue.reponse("approve"), "valider")
        self.assertEqual(langue.section("Where to look"), "ou-regarder")
        self.assertEqual(langue.entete("layer", "canonical"), ("couche", "canonique"))
        self.assertEqual(langue.entete("zone", "private"), ("zone", "privee"))
        self.assertEqual(langue.reference("file"), "fichier")
        self.assertEqual(langue.valeur("human"), "humain")

    def test_une_ligne_de_metadonnees_dans_chaque_langue(self):
        self.assertEqual(langue.meta("en", "F", statut="mesure", preuve="file:calc.py"),
                         "> status : measured · proof : file:calc.py")
        self.assertEqual(langue.meta("fr", "F", statut="mesure", preuve="fichier:calc.py"),
                         "> statut : mesuré · preuve : fichier:calc.py")

    def test_les_trailers_et_la_tautologie_voulue_en_anglais(self):
        message = "Add triple\n\nWaive-test: triple — called by the interface, tested end to end\nFixes: B-0001"
        self.assertEqual(set(langue.trailers(message)), {"dispense-test", "corrige"})
        from socle.checks_tests import VOULU
        self.assertTrue(VOULU.search("# socle: intended — double is deterministic"))

    def test_ce_que_le_moteur_ecrit_dans_chaque_langue(self):
        self.assertEqual(langue.entete_fichier("canonique", "publique", "en"),
                         "<!-- socle: layer=canonical zone=public -->")
        self.assertEqual(langue.entete_fichier("demandes", "privee", "fr"),
                         "<!-- socle: couche=demandes zone=privee -->")
        self.assertEqual(langue.mot(langue.REPONSES, "valider", "en"), "approve")
        self.assertEqual(langue.mot(langue.REPONSES, "valider", "de"), "valider")
        self.assertEqual(langue.ref_fichier("calc.py", "en"), "file:calc.py")
        self.assertEqual(langue.textes("titre-basculee"),
                         {"Entrée basculée dans la mémoire privée", "Entry moved to the private memory"})
        self.assertEqual(langue.trailer("Waive-doc"), "dispense-doc")
        self.assertEqual(memoire.parser_meta(["> status : open · origin : J-2026-10-11-A · for : human"]),
                         {"statut": "open", "origine": "J-2026-10-11-A", "pour": "human"})

    def test_la_politique_d_un_projet_neuf_dit_sa_langue(self):
        from socle.templates import gabarit

        texte = installeur.politique_langue(gabarit("policy.toml"), "en")
        self.assertIn('[memory]\nlanguage = "en"', texte)
        self.assertNotIn('# language = "fr"', texte)

    def test_le_format_documente_chaque_mot(self):
        format_ = (MOTEUR / "socle/FORMAT.md").read_text()
        tables = [langue.CHAMPS, *langue.STATUTS.values(), langue.VALEURS, langue.ENTETE, langue.COUCHES,
                  langue.ZONES, langue.REFERENCES, langue.SECTIONS, langue.REPONSES]
        for table in tables:
            for cle, mots in table.items():
                with self.subTest(cle=cle):
                    self.assertIn(f"`{cle}` | {mots['fr']} | {mots['en']} |", format_)

    def test_une_entree_anglaise_se_lit_comme_une_francaise(self):
        f = memoire.analyser("memory/canonical.md", "<!-- socle: layer=canonical zone=public -->\n# Canonical\n\n"
                             "## F-0001 — Double doubles\n\n> status : measured · proof : file:calc.py\n")
        self.assertEqual((f.couche, f.zone), ("canonique", "publique"))
        e = f.entrees[0]
        self.assertEqual(e.statut, "mesure")
        self.assertEqual(e.refs("preuve"), [("fichier", "calc.py")])


SUJET = "memory/backlog/B-0001-add-triple.md"


class ProjetAnglais(unittest.TestCase):
    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-langue-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            installeur.installer(self.racine, "python", "@essai", source=MOTEUR, langue_memoire="en")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "base", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        self.projet = config.Projet.charger(self.racine)

    def socle(self, *args) -> str:
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            cli.main(["--root", str(self.racine), *args])
        return sortie.getvalue()

    def lire(self, rel: str) -> str:
        return (self.racine / rel).read_text()

    def remplacer(self, rel: str, avant: str, apres: str):
        texte = self.lire(rel)
        self.assertIn(avant, texte)
        (self.racine / rel).write_text(texte.replace(avant, apres, 1))

    def erreurs(self) -> list[str]:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="agent", base=self.base)
        r = Rapport()
        for f in (controles_memoire.format_memoire, controles_memoire.references, controles_memoire.preuves,
                  controles_memoire.backlog, controles_memoire.lectures, controles_memoire.ajout_seul,
                  controles_memoire.contrat):
            f(ctx, r)
        return [c.message for c in r.erreurs()]


class TestCIAnglaise(unittest.TestCase):
    """Les workflows posés dans un projet anglais (B-0059)."""

    def installer(self, adaptateur: str, **options) -> str:
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
            self.assertEqual(installeur.installer(self.racine, adaptateur, "@essai", source=MOTEUR, **options), 0)
        return sortie.getvalue()

    def lire(self, rel: str) -> str:
        return (self.racine / rel).read_text(encoding="utf-8")

    def setUp(self):
        self.racine = Path(tempfile.mkdtemp(prefix="socle-ci-anglaise-"))
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        git(self.racine, "init", "-q", "-b", "main")
        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        self.installer("python", langue_memoire="en")

    def test_la_ci_posee_est_en_anglais(self):
        # Le nom du travail, celui des étapes et les commentaires.
        ci = self.lire(".github/workflows/socle.yml")
        self.assertIn("    name: Socle — verify, checks, self-test\n", ci)
        self.assertIn("- name: Private memory", ci)
        self.assertNotIn("Mémoire privée", ci)
        self.assertNotIn("Posé par l'installeur", ci)

    def test_une_mise_a_jour_garde_le_nom_du_travail_en_place(self):
        # Une protection de branche exige ce nom : la langue ne le change pas.
        chemin = self.racine / ".github/workflows/socle.yml"
        chemin.write_text(self.lire(".github/workflows/socle.yml").replace(
            "    name: Socle — verify, checks, self-test\n", "    name: Socle — verify, contrôles, auto-test\n"),
            encoding="utf-8")
        sortie = self.installer("python")
        ci = self.lire(".github/workflows/socle.yml")
        self.assertIn("    name: Socle — verify, contrôles, auto-test\n", ci)
        self.assertIn("- name: Private memory", ci)
        self.assertIn("CI job name kept: “Socle — verify, contrôles, auto-test”", sortie)

    def test_les_etapes_d_un_adaptateur_et_le_balayage_en_anglais(self):
        self.installer("python-pytest")
        self.assertIn("- name: pytest and mutmut", self.lire(".github/workflows/socle.yml"))
        balayage = self.lire(".github/workflows/socle-mutation.yml")
        self.assertIn("    name: Socle — mutation sweep\n", balayage)
        self.assertIn("- name: pytest and mutmut", balayage)
        self.assertNotIn("Balayage et verdict", balayage)

    def test_le_lanceur_parle_la_langue_du_projet(self):
        # Son message sous un Python trop ancien s'écrit avant le moteur.
        lanceur = self.lire(".socle/socle")
        self.assertIn('"the socle requires Python 3.11 or newer (tomllib); found: "', lanceur)
        self.assertNotIn(installeur.PYTHON_ANCIEN, lanceur)
        self.assertIn(installeur.PYTHON_ANCIEN, (MOTEUR / "socle/templates/launcher.py").read_text(encoding="utf-8"))

    def test_nom_du_travail_et_noms_d_etapes(self):
        self.assertEqual(outils.nom_du_travail("jobs:\n  socle:\n    name: 'Socle — x'\n"), "Socle — x")
        self.assertIsNone(outils.nom_du_travail("name: Socle\n"))
        etapes = "      - name: Dépendances\n        run: npm ci\n      - uses: actions/setup-go@v5\n"
        with messages.dans("en"):
            self.assertEqual(installeur.noms_d_etapes_traduits(etapes),
                             "      - name: Dependencies\n        run: npm ci\n      - uses: actions/setup-go@v5\n")
        self.assertEqual(installeur.noms_d_etapes_traduits(etapes), etapes)

    def test_un_projet_francais_garde_sa_ci_francaise(self):
        francais = Path(tempfile.mkdtemp(prefix="socle-ci-francaise-"))
        self.addCleanup(shutil.rmtree, francais, ignore_errors=True)
        git(francais, "init", "-q", "-b", "main")
        (francais / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            installeur.installer(francais, "python-pytest", "@essai", source=MOTEUR)
        self.assertIn("    name: Socle — verify, contrôles, auto-test\n",
                      (francais / ".github/workflows/socle.yml").read_text(encoding="utf-8"))
        self.assertIn("- name: pytest et mutmut",
                      (francais / ".github/workflows/socle-mutation.yml").read_text(encoding="utf-8"))


class TestProjetAnglais(ProjetAnglais):
    def test_l_installation_pose_tout_en_anglais(self):
        self.assertEqual(langue.du_projet(self.projet), "en")
        self.assertIn('[memory]\nlanguage = "en"', self.lire(".socle/policy.toml"))
        self.assertIn("## Socle: memory, documentation and tests", self.lire("AGENTS.md"))
        self.assertIn("layer=canonical zone=public", self.lire("memory/canonical.md"))
        self.assertIn("## Next steps", self.lire("memory/active.md"))
        self.assertIn("ref : file:.socle/engine.lock", next((self.racine / "memory/journal").glob("*.md")).read_text())
        self.assertEqual(self.erreurs(), [])

    def test_show_dit_le_statut_d_une_demande_en_anglais(self):
        # B-0059 : le statut affiché suit la langue ; la valeur comparée non.
        sortie = self.socle("new", "request", "Choose the cap")
        ident = sortie.split()[0]
        self.assertIn("\n--- pending ---", self.socle("show", ident))
        d = next(d for d in demandes.toutes(self.racine) if d.id == ident)
        self.assertEqual(d.statut, "en attente")
        d.reponse = {"reponse": "accept"}
        with messages.dans("en"):
            self.assertEqual(d.statut_affiche, "answered: accept")
        self.assertEqual(d.statut_affiche, "répondue : accept")

    def test_new_ecrit_dans_la_langue_du_projet(self):
        self.socle("new", "fact", "Double doubles")
        self.assertIn("> status : assumed · source :", self.lire("memory/canonical.md"))
        self.socle("new", "backlog", "Add triple")
        self.assertIn("> status : open · origin :", self.lire(SUJET))
        self.assertIn("read : backlog@", self.lire(SUJET))
        self.socle("new", "adr", "One constant only")
        adr = next((self.racine / "memory/decisions").glob("ADR-0001-*.md")).read_text()
        self.assertIn("layer=decisions zone=public", adr)
        self.assertIn("> status : proposed · date :", adr)
        self.assertIn("## Consequences", adr)
        self.socle("new", "request", "Choose the rounding mode")
        self.assertIn("## Where to look", next((self.racine / "memory/requests").glob("D-0001-*.md")).read_text())

    def test_une_memoire_anglaise_remplie_passe_les_controles(self):
        journal = next((self.racine / "memory/journal").glob("*.md"))
        ident = journal.read_text().split("## ", 2)[1].split(" ", 1)[0]
        self.socle("new", "fact", "Double doubles")
        self.remplacer("memory/canonical.md", "> status : assumed · source : <where this fact comes from>\n\n"
                       "<the fact, and what would prove it>", "> status : measured · proof : file:calc.py\n\nRead in the code.")
        self.socle("new", "backlog", "Add triple")
        self.remplacer(SUJET, "<J-… or commit:… where the topic came up>", ident)
        self.remplacer(SUJET, "<what to do, and why>", "For the invoices.")
        (self.racine / "memory/requests/D-0001-choose-the-rounding-mode.md").write_text(DEMANDE)
        self.assertEqual(self.erreurs(), [])
        d = next(x for x in demandes.toutes(self.racine) if x.id == "D-0001")
        self.assertEqual(demandes.linter(d, self.projet), [])
        demandes.ecrire_reponse(self.racine, d, "approve", "", "Théo", "2026-10-11", "conversation", "ok, half even")
        d = next(x for x in demandes.toutes(self.racine) if x.id == "D-0001")
        self.assertTrue(d.validee)
        self.assertEqual(demandes.verifier_reponse(d), [])

    def test_new_request_dit_le_contrat_en_anglais(self):
        """La relecture de B-0149 : le contrat d'une demande n'était vérifié
        qu'en français ; ici, les noms des paragraphes et les réponses de
        base sont ceux d'un projet en anglais, gabarit des questions compris."""
        with messages.dans("en"):
            sortie = self.socle("new", "request", "Choose the cap")
            questions = self.socle("new", "request", "--questions", "Frame the cap")
        self.assertIn("Its contract, which the lint judges", sortie)
        self.assertIn("**The project.**, **The work.**, **The question.**", sortie)
        self.assertIn("`approve`, `reject`, `insufficient-context`", sortie)
        self.assertIn("fingerprint lines set aside", sortie)
        self.assertNotIn("“Questions”", sortie)
        self.assertNotIn("contrat", sortie + questions)
        self.assertIn("“Questions” asks each open question", questions)
        self.assertIn("the template's free answer, `answers`", questions)
        self.assertIn("- `answers` —", next((self.racine / "memory/requests").glob("D-0002-*.md")).read_text())

    def test_un_fichier_protege_supprime_s_approuve_en_anglais(self):
        """B-0163 : `socle approve` écrit `deleted` dans un projet en anglais,
        et `protege.fichiers` ne cherchait que « supprimé » : la suppression
        approuvée restait refusée."""
        from socle import checks_ratchet as controles_cliquet, fingerprint as empreinte

        fichier = ".github/workflows/socle.yml"
        (self.racine / fichier).unlink()

        def erreurs():
            r = Rapport()
            controles_cliquet.proteges(contexte.Contexte(config.Projet.charger(self.racine), etage="agent",
                                                         base=self.base), r)
            return [c.message for c in r.erreurs("protege.fichiers")]

        self.assertTrue(any("`deleted`" in e for e in erreurs()))
        with unittest.mock.patch.dict(os.environ):
            os.environ.pop("CLAUDECODE", None)
            self.assertIn("written and approved", self.socle("approve", "--files", fichier, "--text", "Drop the workflow"))
        demande = next((self.racine / "memory/requests").glob("D-*.md")).read_text()
        self.assertIn(f"`{fichier}` — protected file changed by the human themselves; new fingerprint `deleted`",
                      demande)
        self.assertEqual(erreurs(), [])
        self.assertEqual((empreinte.supprime("en"), empreinte.supprime("fr"), empreinte.supprime("de")),
                         ("deleted", "supprimé", "supprimé"))
        self.assertEqual(demandes.FICHIER_SUPPRIME, tuple(empreinte.SUPPRIME.values()))

    def test_une_entree_francaise_se_lit_dans_un_projet_anglais(self):
        canon = self.racine / "memory/canonical.md"
        canon.write_text(canon.read_text() + "\n## F-0001 — Double double\n\n> statut : mesuré · preuve : fichier:calc.py\n")
        self.assertEqual(self.erreurs(), [])

    def test_le_recap_attendu_est_en_anglais(self):
        self.assertEqual(humain.recap_manquant(self.projet, "Done.\n\nFor you: nothing.\nNext: nothing."), [])
        self.assertEqual(humain.recap_manquant(self.projet, "Done."), ["For you:", "Next:"])

    def test_une_dispense_de_doc_en_anglais(self):
        from socle import checks_docs as controles_docs

        (self.racine / "calc.py").write_text("def double(x):\n    return 2 * x  # inchangé\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "Comment\n\nWaive-doc: a comment only, nothing to document", "--no-verify")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=self.base, tete="HEAD")
        self.assertEqual(controles_docs.dispenses(ctx), ["a comment only, nothing to document"])

    def test_une_bascule_en_anglais(self):
        pol = self.racine / ".socle/policy.toml"
        pol.write_text(pol.read_text() + '\n[private]\nmode = "chiffre"\n')
        (self.racine / "memory/backlog/B-0001-call-the-client.md").write_text(
            "<!-- socle: layer=backlog zone=public -->\n# B-0001 — Call the client\n\n> status : open · origin : "
            f"commit:{self.base[:7]}\n\nBefore November.\n")
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-qm", "sujet", "--no-verify")
        self.base = git(self.racine, "rev-parse", "HEAD").strip()
        self.socle("private", "move", "B-0001")
        self.assertIn("# B-0001 — Entry moved to the private memory\n\n> made-private : ",
                      self.lire("memory/backlog/B-0001-basculee.md"))
        copie = "memory/private/backlog/PB-0001-call-the-client.md"
        self.assertIn("from : B-0001", self.lire(copie))
        self.assertIn("layer=backlog zone=private", self.lire(copie))
        self.assertEqual(self.erreurs(), [])

if __name__ == "__main__":
    unittest.main()
