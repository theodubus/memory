"""B-0180 : l'adoption tolère les constats présents à l'installation, pas
ceux qui viennent après (ADR de B-0180)."""

import io
import re
import shutil
import subprocess
import tomllib
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from socle import config, context as contexte, installer as installeur, messages, state as etat
from socle.checks_docs import debut_de
from socle.checks_ratchet import assouplissements
from socle.report import AVERTISSEMENT, ERREUR, Constat

from tests.test_installeur import MOTEUR, depot

LISEZMOI = "Voir [la suite](absent.md).\nEt F-0099.\n"


def installer(racine: Path, adoption: bool) -> str:
    with redirect_stdout(io.StringIO()) as flux:
        installeur.installer(racine, "python", "@essai", adoption=adoption, source=MOTEUR)
    return flux.getvalue()


def references(racine: Path, etage: str = "ci") -> list[Constat]:
    projet = config.Projet.charger(racine)
    rapport = contexte.executer(contexte.Contexte(projet, etage=etage, base=None), ids=["memoire.references"])
    return rapport.constats


def git(racine: Path, *args):
    subprocess.run(["git", *args], cwd=racine, check=True, capture_output=True,
                   env={"HOME": str(racine), "PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1",
                        "GIT_AUTHOR_NAME": "e", "GIT_AUTHOR_EMAIL": "e@e", "GIT_COMMITTER_NAME": "e",
                        "GIT_COMMITTER_EMAIL": "e@e"})


class TestCleDeConstat(unittest.TestCase):
    def test_la_cle_ne_depend_pas_de_la_ligne(self):
        a = Constat("memoire.references", "lien mort : absent.md", "LISEZMOI.md", 1)
        b = Constat("memoire.references", "lien mort : absent.md", "LISEZMOI.md", 40)
        self.assertEqual(contexte.cle_de_constat(a), "LISEZMOI.md — lien mort : absent.md")
        self.assertEqual(contexte.cle_de_constat(a), contexte.cle_de_constat(b))
        c = Constat("x", "voir src/a.py:12 et la ligne 30,  puis\nla suite", None)
        d = Constat("x", "voir src/a.py:47:3 et la ligne 2, puis la suite", None)
        self.assertEqual(contexte.cle_de_constat(c), contexte.cle_de_constat(d))
        self.assertEqual(contexte.cle_de_constat(c), "voir src/a.py et la ligne …, puis la suite")

    def test_la_cle_est_le_fichier_et_l_objet_que_le_constat_cite(self):
        a = Constat("memoire.references", "lien mort : absent.md", "LISEZMOI.md", 1, ERREUR, "absent.md")
        b = Constat("memoire.references", "dead link: absent.md", "LISEZMOI.md", 9, ERREUR, "absent.md")
        self.assertEqual(contexte.cle_de_constat(a), "LISEZMOI.md — absent.md")
        self.assertEqual(contexte.cle_de_constat(a), contexte.cle_de_constat(b))  # reformulé, même objet

    def test_sans_objet_la_cle_garde_le_message_en_francais(self):
        with messages.dans("en"):
            m = messages.trad("lien mort : {cible}", cible="absent.md")
        self.assertEqual(m, "dead link: absent.md")
        self.assertEqual(messages.source(m), "lien mort : absent.md")
        self.assertEqual(contexte.cle_de_constat(Constat("x", m, "a.md", 3)), "a.md — lien mort : absent.md")

    def test_une_cle_suit_son_fichier_renomme(self):
        self.assertEqual(contexte.cle_renommee("a.md — F-0001", {"a.md": "b.md"}), "b.md — F-0001")
        self.assertEqual(contexte.cle_renommee("c.md — F-0001", {"a.md": "b.md"}), "c.md — F-0001")


class TestAdoption(unittest.TestCase):
    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n", "LISEZMOI.md": LISEZMOI})
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        self.sortie = installer(self.racine, adoption=True)
        self.gf = self.racine / ".socle/guardrails.toml"

    def tolerees(self) -> dict:
        return tomllib.loads(self.gf.read_text())["adoption"].get("tolerated")

    def test_l_adoption_consigne_les_constats_presents(self):
        self.assertEqual(sorted(self.tolerees()["memoire.references"]),
                         ["LISEZMOI.md — F-0099", "LISEZMOI.md — absent.md"])
        self.assertIn("memoire.references — 2 constat(s) d'avant l'installation encore toléré(s)", self.sortie)
        constats = references(self.racine)
        self.assertEqual([k.gravite for k in constats], [AVERTISSEMENT, AVERTISSEMENT])

    def test_les_controles_d_adoption_citent_leur_objet(self):
        (self.racine / "tests").mkdir(exist_ok=True)
        (self.racine / "tests/test_x.py").write_text("import unittest\n\n\nclass T(unittest.TestCase):\n"
                                                    "    def test_rien(self):\n        pass\n")
        paragraphe = "Un long paragraphe recopié tel quel dans deux fichiers du projet, " * 4 + "\n"
        (self.racine / "a.md").write_text(paragraphe)
        (self.racine / "b.md").write_text(paragraphe)
        projet = config.Projet.charger(self.racine)
        rapport = contexte.executer(contexte.Contexte(projet, etage="ci", base=None),
                                    ids=["tests.creux", "docs.copie"], adoption=False)
        objets = {k.controle: k.objet for k in rapport.erreurs()}
        self.assertEqual(objets, {"tests.creux": "sans assertion test_rien",
                                  "docs.copie": "copie en b.md : Un long paragraphe recopié tel quel dans deux"})

    def test_la_liste_tolere_toujours_dans_une_autre_langue(self):
        with messages.dans("en"):
            constats = references(self.racine)
        self.assertEqual([k.gravite for k in constats], [AVERTISSEMENT, AVERTISSEMENT], constats)

    def test_hors_de_la_ci_aucun_constat_n_est_dit_resorbe(self):
        # Aux étages agent et git, un contrôle peut ne juger que les fichiers
        # changés : un constat toléré non vu n'y est pas résorbé.
        (self.racine / "LISEZMOI.md").write_text("Rien.\n")
        for etage in ("agent", "git"):
            self.assertFalse([k for k in references(self.racine, etage) if "résorbé" in k.message], etage)

    def test_un_constat_neuf_sous_l_adoption_fait_echouer_le_controle(self):
        # Une ligne de plus en tête : les constats anciens changent de ligne
        # et restent tolérés ; la référence inventée après, non.
        (self.racine / "LISEZMOI.md").write_text("Titre.\n" + LISEZMOI + "Et F-0098.\n")
        constats = references(self.racine)
        erreurs = [k for k in constats if k.gravite == ERREUR]
        self.assertEqual(len(erreurs), 1, constats)
        self.assertIn("F-0098", erreurs[0].message)
        self.assertEqual(len([k for k in constats if k.gravite == AVERTISSEMENT]), 2)

    def test_deux_constats_de_meme_cle_se_comptent(self):
        (self.racine / "LISEZMOI.md").write_text(LISEZMOI + "Voir [la suite](absent.md).\n")
        erreurs = [k for k in references(self.racine) if k.gravite == ERREUR]
        self.assertEqual([k.message for k in erreurs], ["lien mort : absent.md"])

    def test_un_constat_resorbe_le_dit_et_a_zero_le_controle_peut_sortir(self):
        (self.racine / "LISEZMOI.md").write_text("Rien.\n")
        messages = [k.message for k in references(self.racine)]
        self.assertEqual(len([m for m in messages if "résorbé" in m]), 2, messages)
        texte = self.gf.read_text()
        texte = re.sub(r'(?ms)^"memoire\.references" = \[.*?^\]', '"memoire.references" = []', texte)
        self.gf.write_text(texte)
        bilan = contexte.bilan_adoption(config.Projet.charger(self.racine))
        self.assertEqual(len(bilan), 1)
        self.assertIn("peut sortir de `[adoption] warn_only`", bilan[0])
        self.assertIn(bilan[0], etat.calculer(config.Projet.charger(self.racine), contenus=False))

    def test_un_projet_adopte_sans_liste_la_recoit_a_sa_mise_a_jour(self):
        # Une adoption d'avant B-0180 : `warn_only` sans liste.
        self.gf.write_text(installeur._TABLE_TOLERES.sub("", self.gf.read_text()))
        projet = config.Projet.charger(self.racine)
        self.assertEqual(contexte.tolerances(projet), {"memoire.references": None})
        self.assertIn("désarmé en entier", contexte.bilan_adoption(projet)[0])
        self.assertIn("désarmé en entier", etat.calculer(projet, contenus=False))
        (self.racine / "LISEZMOI.md").write_text(LISEZMOI + "Et F-0098.\n")
        constats = references(self.racine)
        self.assertFalse([k for k in constats if k.gravite == ERREUR])  # l'ancienne règle, et elle le dit
        self.assertTrue(any("désarmé en entier" in k.message for k in constats))
        sortie = installer(self.racine, adoption=False)
        self.assertIn("mise à jour : memoire.references était désarmé en entier", sortie)
        self.assertEqual(len(self.tolerees()["memoire.references"]), 3)
        self.assertFalse([k for k in references(self.racine) if k.gravite == ERREUR])
        (self.racine / "LISEZMOI.md").write_text(LISEZMOI + "Et F-0098.\nEt F-0097.\n")
        self.assertEqual(len([k for k in references(self.racine) if k.gravite == ERREUR]), 1)

    def test_a_la_mise_a_jour_seuls_les_constats_de_la_base_sont_toleres(self):
        self.gf.write_text(installeur._TABLE_TOLERES.sub("", self.gf.read_text()))
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-q", "--no-verify", "-m", "base")
        git(self.racine, "update-ref", "refs/remotes/origin/main", "HEAD")
        git(self.racine, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        (self.racine / "LISEZMOI.md").write_text(LISEZMOI + "Et F-0098.\n")  # né sur la branche
        sortie = installer(self.racine, adoption=False)
        self.assertEqual(sorted(self.tolerees()["memoire.references"]),
                         ["LISEZMOI.md — F-0099", "LISEZMOI.md — absent.md"])
        self.assertIn("1 constat(s) né(s) sur la branche", sortie)
        self.assertIn("LISEZMOI.md — F-0098", sortie)
        erreurs = [k for k in references(self.racine) if k.gravite == ERREUR]
        self.assertEqual([k.objet for k in erreurs], ["F-0098"])

    def test_sans_base_la_mise_a_jour_le_dit(self):
        self.gf.write_text(installeur._TABLE_TOLERES.sub("", self.gf.read_text()))
        self.assertIn("aucune base lisible", installer(self.racine, adoption=False))

    def test_consigner_n_etend_jamais_une_liste_deja_la(self):
        avant = self.tolerees()
        (self.racine / "LISEZMOI.md").write_text(LISEZMOI + "Et F-0098.\n")
        projet = config.Projet.charger(self.racine)
        self.assertIn("LISEZMOI.md — F-0098",
                      contexte.constats_presents(projet, ["memoire.references"])["memoire.references"])
        lignes = installeur.consigner_tolerances(self.racine, mise_a_jour=True)
        self.assertEqual(self.tolerees(), avant)
        self.assertEqual(len(lignes), 1)


class TestClesDistinctes(unittest.TestCase):
    """B-0190 : deux paragraphes recopiés entre les deux mêmes fichiers ont
    deux clés ; l'un toléré, l'autre neuf, le neuf fait échouer le contrôle."""

    P1 = "Un premier paragraphe recopié tel quel entre les deux fichiers du projet, " * 4
    P2 = "Un second paragraphe, tout autre, lui aussi recopié entre les deux mêmes fichiers, " * 4

    def adopter(self, fichiers: dict[str, str]) -> Path:
        racine = depot({"app.py": "print('ok')\n", **fichiers})
        self.addCleanup(shutil.rmtree, racine, ignore_errors=True)
        installer(racine, adoption=True)
        return racine

    def juger(self, racine: Path, controle: str) -> list[Constat]:
        projet = config.Projet.charger(racine)
        return contexte.executer(contexte.Contexte(projet, etage="ci", base=None), ids=[controle]).constats

    def test_le_debut_d_un_paragraphe_est_ses_huit_premiers_mots(self):
        self.assertEqual(debut_de("un  deux\ttrois\nquatre cinq six sept huit neuf"),
                         "un deux trois quatre cinq six sept huit")
        self.assertEqual(debut_de("Trois mots seulement"), "Trois mots seulement")
        self.assertEqual(debut_de("x" * 500), "x" * 80)  # sans blanc, la clé reste bornée

    def test_deux_paragraphes_recopies_entre_deux_fichiers_ont_deux_cles(self):
        racine = self.adopter({"a.md": self.P1 + "\n\n" + self.P2 + "\n", "b.md": self.P1 + "\n"})
        toleres = tomllib.loads((racine / ".socle/guardrails.toml").read_text())["adoption"]["tolerated"]
        self.assertEqual(toleres["docs.copie"],
                         ["a.md — copie en b.md : Un premier paragraphe recopié tel quel entre les"])
        (racine / "b.md").write_text(self.P2 + "\n")
        erreurs = [k for k in self.juger(racine, "docs.copie") if k.gravite == ERREUR]
        self.assertEqual([k.objet for k in erreurs],
                         ["copie en b.md : Un second paragraphe, tout autre, lui aussi recopié"])


class TestCliquetDesToleres(unittest.TestCase):
    AVANT = {"adoption": {"warn_only": ["memoire.references"],
                          "tolerated": {"memoire.references": ["a — x", "a — x", "b — y"]}}}

    def apres(self, liste, warn=("memoire.references",)):
        d = {"adoption": {"warn_only": list(warn)}}
        if liste is not None:
            d["adoption"]["tolerated"] = {"memoire.references": liste}
        return d

    def test_retirer_un_constat_est_libre(self):
        self.assertEqual(assouplissements(self.AVANT, self.apres(["a — x"])), [])
        self.assertEqual(assouplissements(self.AVANT, self.apres(None, warn=())), [])

    def test_en_ajouter_un_assouplit(self):
        (cle, pourquoi), = assouplissements(self.AVANT, self.apres(["a — x", "a — x", "a — x", "b — y"]))
        self.assertEqual(cle, 'adoption.tolerated."memoire.references" "a — x"')
        self.assertIn("1", pourquoi)

    def test_chaque_constat_ajoute_se_cite_a_part(self):
        cles = [c for c, _ in assouplissements(self.AVANT, self.apres(["a — x", "a — x", "b — y", "c — z",
                                                                        "d — w"]))]
        self.assertEqual(cles, ['adoption.tolerated."memoire.references" "c — z"',
                                'adoption.tolerated."memoire.references" "d — w"'])

    def test_un_fichier_renomme_garde_ses_constats_toleres(self):
        renomme = self.apres(["n — x", "n — x", "b — y"])
        self.assertEqual(assouplissements(self.AVANT, renomme, renommes={"a": "n"}), [])
        self.assertTrue(assouplissements(self.AVANT, renomme))

    def test_retirer_la_liste_sous_l_adoption_desarme(self):
        (cle, pourquoi), = assouplissements(self.AVANT, self.apres(None))
        self.assertIn("désarmé", pourquoi)

    def test_une_liste_qui_apparait_durcit(self):
        avant = {"adoption": {"warn_only": ["memoire.references"]}}
        self.assertEqual(assouplissements(avant, self.apres(["a — x"])), [])


class TestSecondeRevue(unittest.TestCase):
    """B-0189 : la seconde revue de B-0180."""

    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n", "LISEZMOI.md": LISEZMOI})
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        installer(self.racine, adoption=True)
        self.gf = self.racine / ".socle/guardrails.toml"

    def commit(self, message: str) -> str:
        git(self.racine, "add", "-A")
        git(self.racine, "commit", "-q", "--no-verify", "-m", message)
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.racine, capture_output=True,
                              text=True, check=True).stdout.strip()

    def juger(self, base: str, ids: list[str]) -> list[Constat]:
        projet = config.Projet.charger(self.racine)
        return contexte.executer(contexte.Contexte(projet, etage="ci", base=base), ids=ids).constats

    def test_une_cle_dont_le_chemin_contient_un_tiret_long_est_suivie(self):
        self.assertEqual(contexte.cle_renommee("docs/a — b.md — F-0001", {"docs/a — b.md": "c.md"}),
                         "c.md — F-0001")

    def test_le_renommage_se_regle_dans_la_pull_request_qui_renomme(self):
        base = self.commit("base")
        git(self.racine, "mv", "LISEZMOI.md", "LIRE.md")
        self.commit("renomme")
        erreurs = [k for k in self.juger(base, ["memoire.references"]) if k.gravite == ERREUR]
        self.assertEqual(len(erreurs), 2, erreurs)
        self.assertTrue(any("renommer sa clé dans `[adoption.tolerated]` de « LISEZMOI.md — absent.md » à "
                            "« LIRE.md — absent.md »" in k.message for k in erreurs), erreurs)
        # La liste corrigée dans la même plage : le cliquet la laisse passer,
        # et la CI est verte.
        self.gf.write_text(self.gf.read_text().replace('"LISEZMOI.md — ', '"LIRE.md — '))
        self.commit("liste corrigée")
        constats = self.juger(base, ["memoire.references", "cliquet.garde-fous"])
        self.assertFalse([k for k in constats if k.gravite == ERREUR], constats)
        self.assertFalse([k for k in constats if "résorbé" in k.message], constats)

    def test_la_liste_corrigee_dans_un_push_suivant_passe(self):
        # Le renommage est parti dans un push antérieur : la plage du push
        # suivant ne le contient plus, les renommages se lisent depuis la
        # branche par défaut.
        self.commit("base")
        git(self.racine, "update-ref", "refs/remotes/origin/main", "HEAD")
        git(self.racine, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        git(self.racine, "mv", "LISEZMOI.md", "LIRE.md")
        pousse = self.commit("renomme")
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci", base=pousse)
        self.assertEqual(ctx.renommes, {})
        self.assertEqual(ctx.renommes_adoption, {"LISEZMOI.md": "LIRE.md"})
        erreurs = [k for k in self.juger(pousse, ["memoire.references"]) if k.gravite == ERREUR]
        self.assertEqual(len(erreurs), 2, erreurs)
        self.assertTrue(all("renommer sa clé" in k.message for k in erreurs), erreurs)
        self.gf.write_text(self.gf.read_text().replace('"LISEZMOI.md — ', '"LIRE.md — '))
        self.commit("liste corrigée")
        constats = self.juger(pousse, ["memoire.references", "cliquet.garde-fous"])
        self.assertFalse([k for k in constats if k.gravite == ERREUR], constats)

    def test_le_resorbe_cite_la_cle_telle_qu_elle_est_dans_la_liste(self):
        base = self.commit("base")
        git(self.racine, "mv", "LISEZMOI.md", "LIRE.md")
        self.commit("renomme")
        (self.racine / "LIRE.md").write_text("Et F-0099.\n")
        self.commit("lien retiré")
        resorbes = [k.message for k in self.juger(base, ["memoire.references"]) if "résorbé" in k.message]
        self.assertEqual(len(resorbes), 1, resorbes)
        self.assertIn("LISEZMOI.md — absent.md", resorbes[0])

    def test_la_mise_a_jour_suit_les_renommages_de_la_branche(self):
        self.gf.write_text(installeur._TABLE_TOLERES.sub("", self.gf.read_text()))
        self.commit("base")
        git(self.racine, "update-ref", "refs/remotes/origin/main", "HEAD")
        git(self.racine, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
        git(self.racine, "mv", "LISEZMOI.md", "LIRE.md")
        self.commit("renomme sur la branche")
        sortie = installer(self.racine, adoption=False)
        tolerees = tomllib.loads(self.gf.read_text())["adoption"]["tolerated"]["memoire.references"]
        self.assertEqual(sorted(tolerees), ["LIRE.md — F-0099", "LIRE.md — absent.md"])
        self.assertNotIn("né(s) sur la branche", sortie)
        self.assertIn("2 constat(s) d'un fichier renommé sur la branche, consigné(s) sous son nouveau nom", sortie)

    def test_un_chemin_cite_n_a_pas_la_cle_du_lien_mort(self):
        # Le lien toléré corrigé en un chemin cité, inexistant, vers la même
        # cible : une faute d'un autre genre, qui n'est pas tolérée.
        (self.racine / "LISEZMOI.md").write_text(LISEZMOI.replace("[la suite](absent.md)", "`memory/absent.md`"))
        self.gf.write_text(self.gf.read_text().replace('"LISEZMOI.md — absent.md"', '"LISEZMOI.md — memory/absent.md"'))
        erreurs = [k for k in references(self.racine) if k.gravite == ERREUR]
        self.assertEqual([k.objet for k in erreurs], ["chemin:memory/absent.md"])
        self.assertEqual(contexte.cle_de_constat(erreurs[0]), "LISEZMOI.md — chemin:memory/absent.md")

    def test_docs_valeurs_garde_sa_source_francaise(self):
        self.gf.write_text(self.gf.read_text() + '\n[[values]]\nname = "v"\n')
        projet = config.Projet.charger(self.racine)
        with messages.dans("en"):
            rapport = contexte.executer(contexte.Contexte(projet, etage="ci", base=None), ids=["docs.valeurs"])
        erreur, = rapport.erreurs()
        self.assertEqual(messages.source(erreur.message), "`v` : déclaration sans `regex`")

    def test_tests_attendus_garde_sa_source_francaise(self):
        (self.racine / "tests").mkdir(exist_ok=True)
        (self.racine / "tests/test_x.py").write_text("import unittest\n\n\nclass T(unittest.TestCase):\n"
                                                    "    def test_un(self):\n        self.assertEqual(1 + 1, 2)\n")
        base = self.commit("base")
        (self.racine / "tests/test_x.py").write_text("import unittest\n\n\nclass T(unittest.TestCase):\n"
                                                    "    def test_un(self):\n        self.assertEqual(1 + 1, 3)\n")
        projet = config.Projet.charger(self.racine)
        with messages.dans("en"):
            rapport = contexte.executer(contexte.Contexte(projet, etage="ci", base=base), ids=["tests.attendus"])
        erreurs = rapport.erreurs()
        self.assertTrue(erreurs, rapport.constats)
        self.assertTrue(all(messages.source(k.message).startswith("assertion changée") for k in erreurs),
                        [messages.source(k.message) for k in erreurs])


if __name__ == "__main__":
    unittest.main()
