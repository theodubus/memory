"""B-0038 : les messages du moteur dans la langue du projet (ADR-0028). Le
texte français, enveloppé par `trad`, est la clé du catalogue anglais ; il ne
doit en manquer aucun, et une traduction garde les variables de sa clé."""

import ast
import re
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
        self.assertEqual(sorted(set(MESSAGES) - employes), [])

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


if __name__ == "__main__":
    unittest.main()
