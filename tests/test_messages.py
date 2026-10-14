"""B-0038 : les messages du moteur dans la langue du projet (ADR-0028). Le
texte français, enveloppé par `trad`, est la clé du catalogue anglais ; il ne
doit en manquer aucun, et une traduction garde les variables de sa clé."""

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from socle import config, hooks, human as humain, messages, utils as outils
from socle.messages_en import MESSAGES
from socle.report import Rapport, en_echec_dans

RACINE = Path(__file__).resolve().parent.parent
MOTEUR = RACINE / "engine" / "socle"
VARIABLE = re.compile(r"\{(\w+)\}")


def enveloppes() -> list[tuple[str, int, ast.Call]]:
    """Chaque appel à `trad` ou `a_traduire` du moteur : (module, ligne, appel)."""
    res = []
    for chemin in sorted(MOTEUR.glob("*.py")):
        if chemin.name == "messages.py":
            continue
        for n in ast.walk(ast.parse(chemin.read_text(encoding="utf-8"))):
            if isinstance(n, ast.Call):
                f = n.func
                nom = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
                if nom in ("trad", "a_traduire"):
                    res.append((chemin.name, n.lineno, n))
    return res


def resumes_des_controles() -> set[str]:
    """La première phrase de la docstring de chaque contrôle du registre, que
    `socle checks` affiche traduite."""
    from socle import context as contexte

    res = set()
    for chemin in sorted(MOTEUR.glob("*.py")):
        for n in ast.walk(ast.parse(chemin.read_text(encoding="utf-8"))):
            if isinstance(n, ast.FunctionDef) and any(
                    isinstance(d, ast.Call) and getattr(d.func, "id", "") == "controle" for d in n.decorator_list):
                doc = ast.get_docstring(n)
                if doc:
                    res.add(contexte.resume(doc))
    return res


# Là où le moteur émet un message : le constat d'un contrôle (son second
# argument), une impression, une exception, le refus d'un hook (le premier).
PUITS_CONSTAT = {"erreur", "avertir", "indisponible"}
PUITS = {"print", "_refus", "refus", "SystemExit", "RuntimeError", "ValueError"}


def prose(n: ast.AST) -> str | None:
    """Le texte d'une chaîne écrite en dur, s'il est de la prose : au moins
    deux mots hors des accents graves (une commande, un chemin) et des
    variables d'une f-string."""
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        texte = n.value
    elif isinstance(n, ast.JoinedStr):
        texte = " ".join(v.value for v in n.values if isinstance(v, ast.Constant))
    elif isinstance(n, ast.BinOp):
        return prose(n.left) or prose(n.right)
    elif isinstance(n, ast.IfExp):
        return prose(n.body) or prose(n.orelse)
    else:
        return None
    texte = re.sub(r"`[^`]*`", " ", texte)
    return texte if len(re.findall(r"[A-Za-zÀ-ÿ]{2,}", texte)) >= 2 else None


class Traduction(unittest.TestCase):
    def tearDown(self):
        messages.choisir(messages.FRANCAIS)

    def test_trad_en_francais_remplit_les_variables(self):
        self.assertEqual(messages.trad("le fichier {chemin} manque", chemin="a.py"), "le fichier a.py manque")

    def test_trad_laisse_une_accolade_sans_valeur(self):
        self.assertEqual(messages.trad('{"cle": 1} pour {nom}', nom="x"), '{"cle": 1} pour x')

    def test_trad_une_variable_nommee_texte(self):
        self.assertEqual(messages.trad("« {texte} »", texte="t"), "« t »")

    def test_trad_en_anglais_lit_le_catalogue(self):
        cle, valeur = next(iter(MESSAGES.items()))
        with messages.dans("en"):
            self.assertEqual(messages.trad(cle), valeur)
        self.assertEqual(messages.trad(cle), cle)

    def test_un_message_absent_du_catalogue_sort_en_francais(self):
        with messages.dans("en"):
            self.assertEqual(messages.trad("absent du catalogue, {x}", x=1), "absent du catalogue, 1")

    def test_choisir_rend_la_precedente_et_une_langue_inconnue_retombe_sur_le_francais(self):
        self.assertEqual(messages.choisir("en"), "fr")
        self.assertEqual(messages.langue(), "en")
        self.assertEqual(messages.choisir("xx"), "en")
        self.assertEqual(messages.langue(), "fr")

    def test_dans_rend_la_langue_meme_sur_une_exception(self):
        with self.assertRaises(ValueError), messages.dans("en"):
            raise ValueError
        self.assertEqual(messages.langue(), "fr")

    def test_a_traduire_rend_le_texte_tel_quel(self):
        self.assertEqual(messages.a_traduire("un texte"), "un texte")

    def test_remplir_sans_valeur_rend_le_texte_tel_quel(self):
        self.assertEqual(messages.remplir("{x} et {y}", {}), "{x} et {y}")
        self.assertEqual(messages.remplir("{x} et {y}", {"y": 2}), "{x} et 2")

    def test_un_autre_fil_part_du_francais(self):
        vu = []
        with messages.dans("en"):
            fil = threading.Thread(target=lambda: vu.append(messages.langue()))
            fil.start()
            fil.join()
        self.assertEqual(vu, ["fr"])

    def test_le_genre_d_un_element_dans_la_langue_du_projet(self):
        e = humain.Element("décision", "D-0001 — choisir")
        self.assertEqual(humain.genre(e), "décision")
        with messages.dans("en"):
            self.assertEqual(humain.genre(e), "decision")
            self.assertEqual(humain.texte([e])[0], "what falls to the human: 1")


class RefusDesHooks(unittest.TestCase):
    """Deux refus du hook de l'agent, lus dans les deux langues : le texte
    français ne change pas, l'anglais vient du catalogue."""

    def tearDown(self):
        messages.choisir(messages.FRANCAIS)

    def test_sha_fabrique(self):
        vrai = outils.git(RACINE, "rev-parse", "HEAD").strip()
        faux = vrai[:7] + ("0" if vrai[7] != "0" else "1") * 33
        self.assertIn("SHA fabriqué : " + faux, hooks.sha_fabrique(RACINE, f"commit {faux}"))
        with messages.dans("en"):
            self.assertIn("Fabricated SHA: " + faux, hooks.sha_fabrique(RACINE, f"commit {faux}"))
        self.assertIsNone(hooks.sha_fabrique(RACINE, f"commit {vrai}"))

    def test_statut_valide_ajoute(self):
        projet = config.Projet.charger(RACINE)
        apres = "## F-9999 — un fait\n\n> statut : validé · validation : D-9999\n"
        faute = hooks.statut_valide_ajoute("memory/canonical.md", "", apres, projet)
        self.assertIn("passe à « validé » sans demande validée", faute)
        with messages.dans("en"):
            faute = hooks.statut_valide_ajoute("memory/canonical.md", "", apres, projet)
        self.assertIn("becomes “validated” without a request approved by the human", faute)
        self.assertIsNone(hooks.statut_valide_ajoute("memory/active.md", "", apres, projet))


class Contexte:
    """Un contexte de contrôle réduit à ce que lisent les trois contrôles
    ci-dessous : les fichiers, leurs textes et la configuration de ce dépôt."""

    def __init__(self, textes: dict[str, str]):
        self.textes = textes
        self.fichiers = sorted(textes)
        self.projet = config.Projet.charger(RACINE)
        self.racine = RACINE

    def lire(self, chemin):
        return self.textes.get(chemin)

    def documents(self):
        return {c: t for c, t in self.textes.items() if c.endswith(".md")}


class ConstatsDansLesDeuxLangues(unittest.TestCase):
    def tearDown(self):
        messages.choisir(messages.FRANCAIS)

    def constats(self, controle, ctx) -> list[str]:
        r = Rapport()
        controle(ctx, r)
        return [c.message for c in r.constats]

    def test_outillage(self):
        from socle import checks_docs as controles_docs

        ctx = Contexte({".github/workflows/autre.yml": "", "README.md": "rien"})
        self.assertIn("dispositif qu'aucun document ne nomme : `autre.yml`",
                      self.constats(controles_docs.outillage, ctx)[0])
        with messages.dans("en"):
            self.assertIn("a device no document names: `autre.yml`", self.constats(controles_docs.outillage, ctx)[0])

    def test_valeur_source(self):
        from socle import checks_docs as controles_docs

        ctx = Contexte({})
        self.assertEqual(controles_docs.valeur_source(ctx, {"file": "absent.txt", "regex": "x"}),
                         (None, "source absente : absent.txt"))
        with messages.dans("en"):
            self.assertEqual(controles_docs.valeur_source(ctx, {}), (None, "declaration without `regex`"))
        self.assertEqual(controles_docs.valeur_source(Contexte({"v.txt": "N = 4"}), {"file": "v.txt", "regex": r"N = (\d+)"}),
                         ("4", None))

    def test_configuration(self):
        from socle import checks_ratchet as controles_cliquet

        self.assertIn("`.claude/settings.json` absent", self.constats(controles_cliquet.configuration, Contexte({}))[0])
        with messages.dans("en"):
            self.assertIn("unreadable JSON",
                          self.constats(controles_cliquet.configuration, Contexte({".claude/settings.json": "{"}))[0])
            self.assertIn("no SessionStart hook calls `.socle/socle hook`",
                          self.constats(controles_cliquet.configuration, Contexte({".claude/settings.json": "{}"}))[0])


class LigneDEchec(unittest.TestCase):
    def test_en_echec_dans_lit_les_deux_langues(self):
        self.assertEqual(en_echec_dans("x\nECHEC — 2 contrôle(s) : a.b, c\n"), ["a.b", "c"])
        self.assertEqual(en_echec_dans("x\nFAILED — 2 check(s): a.b, c\n"), ["a.b", "c"])
        self.assertEqual(en_echec_dans("TOUT PASSE\n"), [])

    def test_un_rapport_anglais_se_relit(self):
        r = Rapport()
        r.erreur("memoire.format", "x")
        with messages.dans("en"):
            texte = r.texte()
        self.assertIn("FAILED — 1 check(s): memoire.format", texte)
        self.assertEqual(en_echec_dans(texte), ["memoire.format"])


class Catalogue(unittest.TestCase):
    def test_un_message_enveloppe_n_est_pas_compose_avant_sa_traduction(self):
        # Un texte littéral, ou un nom qui en porte un marqué `a_traduire` ;
        # jamais une f-string ni une concaténation, que le catalogue ne
        # saurait pas trouver.
        fautes = [f"{m}:{l}" for m, l, n in enveloppes()
                  if not n.args or isinstance(n.args[0], (ast.JoinedStr, ast.BinOp))
                  or (isinstance(n.args[0], ast.Constant) and not isinstance(n.args[0].value, str))]
        self.assertEqual(fautes, [], "le premier argument de `trad` est un texte littéral, pas une f-string")

    def test_chaque_message_enveloppe_est_au_catalogue_anglais(self):
        manquants = sorted({f"{m}:{l} {n.args[0].value!r}" for m, l, n in enveloppes()
                            if n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value not in MESSAGES})
        self.assertEqual(manquants, [])

    def test_le_catalogue_n_a_pas_d_entree_que_rien_n_emploie(self):
        employes = {n.args[0].value for _, _, n in enveloppes() if n.args and isinstance(n.args[0], ast.Constant)}
        self.assertEqual(sorted(set(MESSAGES) - employes - resumes_des_controles()), [])

    def test_aucun_message_en_dur_la_ou_le_moteur_en_emet(self):
        fautes = []
        for chemin in sorted(MOTEUR.glob("*.py")):
            for n in ast.walk(ast.parse(chemin.read_text(encoding="utf-8"))):
                if not isinstance(n, ast.Call):
                    continue
                f = n.func
                nom = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
                args = ([n.args[1]] if nom in PUITS_CONSTAT and len(n.args) >= 2 else []) + (
                    [n.args[0]] if nom in PUITS and n.args else [])
                fautes += [f"{chemin.name}:{n.lineno} {nom}" for a in args if prose(a)]
        self.assertEqual(fautes, [], "un message s'écrit `trad(\"…\")`, et sa traduction va au catalogue")

    def test_prose_reconnait_un_message_et_laisse_une_commande(self):
        self.assertIsNotNone(prose(ast.parse('f"le fichier {x} manque"').body[0].value))
        self.assertIsNone(prose(ast.parse('"`git config core.hooksPath .socle/git-hooks`"').body[0].value))
        self.assertIsNone(prose(ast.parse('f"  - {ligne}"').body[0].value))

    def test_chaque_controle_a_son_resume_au_catalogue(self):
        self.assertEqual(sorted(resumes_des_controles() - set(MESSAGES)), [])

    def test_le_resume_d_un_controle_est_sa_premiere_phrase(self):
        from socle import context as contexte

        self.assertEqual(contexte.resume("Une phrase sur\n    deux lignes. Une autre.\n\nSuite."),
                         "Une phrase sur deux lignes.")
        self.assertEqual(contexte.resume("Sans point final"), "Sans point final")
        self.assertEqual(contexte.resume("`memoire.format` reste entier."), "`memoire.format` reste entier.")

    def test_une_traduction_garde_les_variables_de_sa_cle(self):
        fautes = [(fr, en) for fr, en in MESSAGES.items()
                  if sorted(VARIABLE.findall(fr)) != sorted(VARIABLE.findall(en)) or not en.strip()]
        self.assertEqual(fautes, [])

    def test_chaque_valeur_donnee_a_trad_a_sa_variable_dans_le_texte(self):
        fautes = []
        for m, l, n in enveloppes():
            if not (n.args and isinstance(n.args[0], ast.Constant)):
                continue
            noms = set(VARIABLE.findall(n.args[0].value))
            fautes += [f"{m}:{l} {k.arg}" for k in n.keywords if k.arg and k.arg not in noms]
        self.assertEqual(fautes, [])



# Ce qui reste en français dans un projet anglais, et pourquoi : le nom du
# travail de CI, que la protection de la branche exige tel quel, et les
# textes `absent` des adaptateurs, écrits dans leurs fichiers.
RESTES_FRANCAIS = ("Socle — verify, contrôles, auto-test", "capability absent:")
ACCENTS = re.compile(r"[éèàùçêâîôûœÉÈÀ«»]")


class ProjetAnglais(unittest.TestCase):
    """Un projet installé avec `--language en` lit le moteur en anglais : ce
    que l'humain lit (installation, aide, état) comme ce que lit l'agent
    (refus des hooks, contrôles)."""

    @classmethod
    def setUpClass(cls):
        cls.dossier = Path(tempfile.mkdtemp())
        cls.racine = cls.dossier / "projet"
        cls.racine.mkdir()
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t"}
        env.pop("CLAUDECODE", None)
        cls.env = env
        for args in (["init", "-q", "-b", "main"],):
            subprocess.run(["git", *args], cwd=cls.racine, check=True, env=env)
        (cls.racine / "calc.py").write_text("def double(x):\n    return 2 * x\n")
        (cls.racine / "tests").mkdir()
        (cls.racine / "tests/test_calc.py").write_text(
            "import unittest\nfrom calc import double\n\n\nclass T(unittest.TestCase):\n"
            "    def test_double(self):\n        self.assertEqual(double(2), 4)\n")
        subprocess.run(["git", "add", "-A"], cwd=cls.racine, check=True, env=env)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=cls.racine, check=True, env=env)
        cls.installation = cls.socle(["install", "--target", ".", "--adapter", "auto", "--owner", "@moi",
                                      "--language", "en"], par_le_moteur=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dossier, ignore_errors=True)

    @classmethod
    def socle(cls, args, entree=None, par_le_moteur=False):
        lanceur = ([sys.executable, "-m", "socle"] if par_le_moteur
                   else [sys.executable, str(cls.racine / ".socle/socle")])
        env = {**cls.env, "PYTHONPATH": str(RACINE / "engine")} if par_le_moteur else cls.env
        r = subprocess.run([*lanceur, *args], cwd=cls.racine, capture_output=True, text=True, input=entree, env=env)
        return r.stdout + r.stderr

    def sans_francais(self, sortie: str):
        restes = [l for l in sortie.splitlines() if ACCENTS.search(l) and not any(x in l for x in RESTES_FRANCAIS)]
        self.assertEqual(restes, [], sortie[-3000:])

    def test_l_installation_parle_anglais(self):
        self.assertIn("What now:", self.installation)
        self.sans_francais(self.installation)

    def test_l_aide_l_etat_et_les_controles_parlent_anglais(self):
        for args in (["state"], ["check", "--stage", "ci"], ["checks"], ["help"], [], ["--help"],
                     ["show", "--index", "decisions"]):
            sortie = self.socle(args)
            self.sans_francais(sortie)
        self.assertIn("what falls to the human: nothing", self.socle(["state"]))
        self.assertIn("for the human:", self.socle([]))

    def test_un_refus_du_hook_parle_anglais(self):
        entree = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push --force origin main"}})
        sortie = self.socle(["hook", "pre-tool-use"], entree=entree)
        raison = json.loads(sortie)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("irreversible or external command (force push)", raison)
        self.sans_francais(raison)

    def test_un_constat_parle_anglais(self):
        actif = self.racine / "memory/active.md"
        avant = actif.read_text()
        actif.write_text("pas d'en-tête\n")
        try:
            sortie = self.socle(["check", "--stage", "ci", "--only", "memoire.format"])
        finally:
            actif.write_text(avant)
        self.assertIn("FAILED — 1 check(s): memoire.format", sortie)
        self.assertIn("header `<!-- socle: layer=… zone=… -->` missing", sortie)

    def test_la_politique_d_un_projet_anglais_ne_differe_pas_du_gabarit(self):
        from socle import installer as installeur

        self.assertEqual(installeur.diff_politique(self.racine), [])


if __name__ == "__main__":
    unittest.main()
