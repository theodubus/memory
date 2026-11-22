"""Les notes de version du moteur (ADR-0078) : ce qu'une mise à jour change
pour un projet installé, donné par l'installeur quand il recopie le moteur.

Le pilote, passé au moteur nouveau, a vu changer toutes ses empreintes de
lecture sans qu'aucune note ne l'ait prévenu (B-0151)."""

import io
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from socle import config, installer as installeur, memory as memoire
from tests.test_installeur import MOTEUR, depot

PAQUET = MOTEUR / "socle"


def ids(texte: str) -> list[str]:
    return [i for i, _ in installeur.entrees_des_notes(texte)]


def source_du_moteur(garder: int | None = None) -> Path:
    """Une copie du moteur, à installer : sans notes de version (`garder`
    `None`), ou avec ses `garder` entrées les plus anciennes seulement, dans
    les deux langues."""
    source = Path(tempfile.mkdtemp(prefix="socle-source-"))
    shutil.copytree(PAQUET, source / "socle", ignore=shutil.ignore_patterns("__pycache__"))
    for f in (source / "socle").glob("CHANGES*.md"):
        if garder is None:
            f.unlink()
            continue
        tete, *entrees = re.split(r"(?m)^(?=## )", f.read_text(encoding="utf-8"))
        f.write_text(tete + "".join(entrees[-garder:]), encoding="utf-8")
    return source


def installer(racine: Path, source: Path, **options) -> str:
    with redirect_stdout(io.StringIO()) as flux, redirect_stderr(io.StringIO()):
        installeur.installer(racine, "python", "@essai", source=source, **options)
    return flux.getvalue()


class TestLesFichiers(unittest.TestCase):
    """Les deux fichiers, que le moteur porte."""

    def setUp(self):
        self.fr = (PAQUET / "CHANGES.md").read_text(encoding="utf-8")
        self.en = (PAQUET / "CHANGES.en.md").read_text(encoding="utf-8")

    def test_les_deux_fichiers_ont_les_memes_identifiants(self):
        self.assertTrue(ids(self.fr))
        self.assertEqual(ids(self.fr), ids(self.en))
        self.assertEqual(len(ids(self.fr)), len(set(ids(self.fr))))
        # Les plus récentes d'abord : la date, puis la lettre.
        self.assertEqual(ids(self.fr), sorted(ids(self.fr), reverse=True))

    def test_chaque_titre_de_niveau_2_est_une_entree(self):
        for texte in (self.fr, self.en):
            for ligne in texte.splitlines():
                if ligne.startswith("## "):
                    self.assertRegex(ligne, installeur.TITRE_DE_NOTE)

    def test_chaque_entree_dit_ce_que_l_agent_doit_faire(self):
        for texte, a_faire in ((self.fr, "\n\nÀ faire : "), (self.en, "\n\nTo do: ")):
            for ident, entree in installeur.entrees_des_notes(texte):
                self.assertIn(a_faire, entree, ident)

    def test_une_note_qui_ne_demande_rien_le_dit_dans_les_deux_langues(self):
        """B-0324 : l'installeur n'imprime d'une note qui ne demande rien que
        son titre ; un projet en anglais n'en perd pas plus qu'un autre."""
        fr, en = dict(installeur.entrees_des_notes(self.fr)), dict(installeur.entrees_des_notes(self.en))
        self.assertTrue(any(installeur.ne_demande_rien(t) for t in fr.values()))
        self.assertTrue(any(not installeur.ne_demande_rien(t) for t in fr.values()))
        for ident, texte in fr.items():
            self.assertEqual(installeur.ne_demande_rien(texte), installeur.ne_demande_rien(en[ident]), ident)

    def test_les_notes_ne_renvoient_pas_a_l_atelier(self):
        """Le produit parle sa propre voix (ADR-0033) : aucun identifiant de la
        mémoire de ce dépôt, ni sa documentation de fabrication."""
        for texte in (self.fr, self.en):
            self.assertEqual([m.group(0) for m in memoire.ID_RE.finditer(texte)], [])
            for mot in ("docs/fabrication", "chess", "Théo", "atelier", "workshop"):
                self.assertNotIn(mot, texte)


class TestNotesNouvelles(unittest.TestCase):
    """La comparaison, par identifiants, entre deux copies du moteur."""

    def setUp(self):
        self.ancien = Path(tempfile.mkdtemp(prefix="socle-notes-"))
        self.addCleanup(shutil.rmtree, self.ancien, ignore_errors=True)
        self.tous = ids((PAQUET / "CHANGES.md").read_text(encoding="utf-8"))

    def test_une_copie_sans_notes_les_recoit_toutes(self):
        deja = installeur.identifiants_des_notes(self.ancien)
        self.assertEqual(deja, set())
        self.assertEqual([i for i, _ in installeur.notes_nouvelles(deja, PAQUET)], self.tous)

    def test_une_copie_qui_en_a_une_partie_recoit_les_autres(self):
        (self.ancien / "CHANGES.md").write_text(
            "# Notes\n\n" + "".join(f"## {i} — titre\n\nÀ faire : rien.\n\n" for i in self.tous[-2:]),
            encoding="utf-8")
        deja = installeur.identifiants_des_notes(self.ancien)
        self.assertEqual(deja, set(self.tous[-2:]))
        self.assertEqual([i for i, _ in installeur.notes_nouvelles(deja, PAQUET)], self.tous[:-2])

    def test_l_anglais_donne_le_fichier_anglais(self):
        notes = installeur.notes_nouvelles(set(), PAQUET, "en")
        self.assertIn("\n\nTo do: ", notes[0][1])
        self.assertEqual(installeur.fichier_des_notes(PAQUET, "en").name, "CHANGES.en.md")
        self.assertEqual(installeur.fichier_des_notes(PAQUET, "fr").name, "CHANGES.md")
        # Une langue sans version retombe sur le français.
        self.assertEqual(installeur.fichier_des_notes(PAQUET, "de").name, "CHANGES.md")

    def test_le_texte_dit_quoi_en_faire(self):
        notes = installeur.notes_nouvelles(set(), PAQUET)
        texte = installeur.texte_des_notes(notes[:1], ".socle/engine/socle/CHANGES.md", toutes=False)
        self.assertIn("1 entrée(s) que la copie du moteur remplacée n'avait pas", texte)
        self.assertIn("faire ce que chacune demande", texte)
        self.assertTrue(texte.endswith(notes[0][1]))
        toutes = installeur.texte_des_notes(notes, ".socle/engine/socle/CHANGES.md", toutes=True)
        self.assertIn("la copie du moteur remplacée n'en avait pas", toutes)
        self.assertIn("leur date le dit", toutes)


def note(ident: str, a_faire: str | None, titre: str = "titre") -> tuple[str, str]:
    """Une entrée des notes de version, son paragraphe « À faire » (ou « To
    do ») tel quel, ou sans paragraphe (`None`)."""
    corps = f"## {ident} — {titre}\n\nCe que le changement fait au projet."
    return ident, corps + (f"\n\n{a_faire}" if a_faire is not None else "")


class TestCeQuiNeDemandeRien(unittest.TestCase):
    """B-0324 : seule une note dont « À faire » est « rien. » en entier, ou commence par
    « rien ; » ne demande rien ; dans le doute, elle demande quelque chose."""

    def test_la_forme_de_ce_qui_ne_demande_rien(self):
        for a_faire in ("À faire : rien.", "À faire : rien ; le skill est une copie protégée.",
                        "À faire : rien; sans espace.", "To do: nothing.", "To do: nothing; a detail.",
                        "To do: nothing ; a detail."):
            self.assertTrue(installeur.ne_demande_rien(note("2026-11-22-z", a_faire)[1]), a_faire)
        for a_faire in ("À faire : rien, sauf si le hook refuse.", "À faire : rien dans le projet.",
                        "À faire : rien d'obligatoire.", "À faire : rien de plus que de suivre le skill.",
                        "À faire : rien", "À faire : relire le backlog.", "À faire : Rien.",
                        "To do: nothing, unless the hook refuses.", "To do: nothing in the project.",
                        "To do: review the backlog.", None):
            self.assertFalse(installeur.ne_demande_rien(note("2026-11-22-z", a_faire)[1]), a_faire)

    def test_rien_suivi_d_une_consigne_demande_quelque_chose(self):
        """Revue de L-0021 : « rien. » n'est la forme qui ne demande rien que
        s'il est le paragraphe entier ; suivi d'une consigne (« ne pas la
        lancer vers le projet »), la note s'imprime en entier."""
        for a_faire in ("À faire : rien. Ne pas lancer `find … | xargs rm` vers le projet.",
                        "À faire : rien.\nPour la lancer, écrire son chemin absolu.",
                        "To do: nothing. Do not run it against the project."):
            self.assertFalse(installeur.ne_demande_rien(note("2026-11-22-z", a_faire)[1]), a_faire)
        self.assertTrue(installeur.ne_demande_rien(note("2026-11-22-z", "À faire : rien.\n")[1]))

    def test_les_notes_reelles_qui_demandent_quelque_chose_s_impriment_en_entier(self):
        """Revue de L-0021 : des notes du moteur dont « À faire » commence par
        « rien. » ou « rien ; » donnent une consigne ; la règle les imprime en
        entier, dans les deux langues."""
        for nom in ("CHANGES.md", "CHANGES.en.md"):
            entrees = dict(installeur.entrees_des_notes((PAQUET / nom).read_text(encoding="utf-8")))
            for ident in ("2026-11-20-d", "2026-11-16-a", "2026-11-15-e", "2026-11-15-d", "2026-11-14-g",
                          "2026-11-10-a"):
                with self.subTest(nom=nom, note=ident):
                    self.assertFalse(installeur.ne_demande_rien(entrees[ident]))

    def test_seul_le_premier_paragraphe_a_faire_compte(self):
        _, texte = note("2026-11-22-z", "À faire : relire le backlog.")
        self.assertFalse(installeur.ne_demande_rien(texte + "\n\nÀ faire : rien."))
        # « À faire » au fil d'une phrase n'est pas le paragraphe.
        self.assertFalse(installeur.ne_demande_rien("## 2026-11-22-z — t\n\nSon « À faire : rien. » change."))


class TestCeQueLeTexteImprime(unittest.TestCase):
    """Ce que `texte_des_notes` imprime de chaque note : entière si elle
    demande quelque chose, d'abord ; son titre seul sinon (B-0324)."""

    FICHIER = ".socle/engine/socle/CHANGES.md"

    def setUp(self):
        self.notes = [note("2026-11-22-d", "À faire : rien.", "rien"),
                      note("2026-11-22-c", "À faire : relire le backlog.", "action"),
                      note("2026-11-22-b", "À faire : rien ; une précision.", "précision"),
                      note("2026-11-22-a", "À faire : rien, sauf si le hook refuse.", "sauf si"),
                      note("2026-11-21-a", None, "sans paragraphe")]

    def test_une_note_qui_demande_une_action_s_imprime_en_entier_d_abord(self):
        for toutes in (False, True):
            texte = installeur.texte_des_notes(self.notes, self.FICHIER, toutes)
            entieres = [t for i, t in self.notes if i in ("2026-11-22-c", "2026-11-22-a", "2026-11-21-a")]
            for t in entieres:
                self.assertIn(t, texte)
            # Dans leur ordre, avant les titres de celles qui ne demandent rien.
            positions = [texte.index(t) for t in entieres]
            self.assertEqual(positions, sorted(positions))
            self.assertLess(positions[-1], texte.index("2 entrée(s) ne demandent rien"))

    def test_une_note_qui_ne_demande_rien_n_imprime_que_son_titre(self):
        for toutes in (False, True):
            texte = installeur.texte_des_notes(self.notes, self.FICHIER, toutes)
            self.assertTrue(texte.endswith(
                "\n\n2 entrée(s) ne demandent rien (« À faire : rien ») : leur titre seul, et leur texte dans "
                "`.socle/engine/socle/CHANGES.md`, à lire au besoin :\n"
                "## 2026-11-22-d — rien\n## 2026-11-22-b — précision"), texte)
            self.assertNotIn("À faire : rien.", texte)
            self.assertNotIn("une précision", texte)
            self.assertEqual(texte.count("Ce que le changement fait au projet."), 3)

    def test_sans_note_qui_ne_demande_rien_pas_de_ligne_de_plus(self):
        texte = installeur.texte_des_notes(self.notes[1:2], self.FICHIER, False)
        self.assertNotIn("ne demandent rien", texte)
        self.assertTrue(texte.endswith(self.notes[1][1]))

    def test_en_anglais(self):
        from socle import messages

        notes = [note("2026-11-22-b", "To do: nothing; a detail.", "nothing"),
                 note("2026-11-22-a", "To do: review the backlog.", "action")]
        with messages.dans("en"):
            texte = installeur.texte_des_notes(notes, ".socle/engine/socle/CHANGES.en.md", False)
        self.assertIn(notes[1][1], texte)
        self.assertTrue(texte.endswith(
            "\n\n1 entry(ies) ask nothing (“To do: nothing”): their title only, and their text in "
            "`.socle/engine/socle/CHANGES.en.md`, to read when needed:\n## 2026-11-22-b — nothing"), texte)
        self.assertNotIn("a detail", texte)


class TestALaMiseAJour(unittest.TestCase):
    """L'installeur, de bout en bout : ce qu'il imprime, et le message de
    commit qu'il propose."""

    def setUp(self):
        self.racine = depot({"app.py": "print('ok')\n"})
        self.addCleanup(shutil.rmtree, self.racine, ignore_errors=True)
        self.tous = ids((PAQUET / "CHANGES.md").read_text(encoding="utf-8"))

    def source(self, garder: int | None = None) -> Path:
        s = source_du_moteur(garder)
        self.addCleanup(shutil.rmtree, s, ignore_errors=True)
        return s

    def test_une_copie_ancienne_sans_notes_les_recoit_toutes(self):
        premiere = installer(self.racine, self.source(), adoption=False)
        # Une première installation n'a rien à apprendre d'une mise à jour.
        self.assertNotIn("Notes de version", premiere)
        sortie = installer(self.racine, MOTEUR)
        self.assertIn(f"Notes de version : la copie du moteur remplacée n'en avait pas ; voici toutes leurs "
                      f"entrées ({len(self.tous)}), dans `.socle/engine/socle/CHANGES.md`", sortie)
        for ident in self.tous:
            self.assertIn(f"\n## {ident} — ", sortie)
        # Les notes avant l'audit, et le message de commit qui les nomme.
        self.assertLess(sortie.index("Notes de version"), sortie.index("\nAudit :"))
        apres = sortie.split("Et maintenant :", 1)[1]
        self.assertIn(f'git commit -m "Mettre à jour le socle {installeur.VERSION}" -m "Notes de version du socle : '
                      f'{", ".join(self.tous)}, dans .socle/engine/socle/CHANGES.md" && git push', apres)
        self.assertIn("lui dire de lire ses notes de version", apres)

    def test_une_copie_qui_en_a_une_partie_ne_recoit_que_les_autres(self):
        installer(self.racine, self.source(garder=3), adoption=False)
        sortie = installer(self.racine, MOTEUR)
        nouvelles = self.tous[:-3]
        self.assertIn(f"{len(nouvelles)} entrée(s) que la copie du moteur remplacée n'avait pas", sortie)
        for ident in nouvelles:
            self.assertIn(f"\n## {ident} — ", sortie)
        for ident in self.tous[-3:]:
            self.assertNotIn(f"## {ident} — ", sortie)
            self.assertNotIn(ident, sortie.split("Et maintenant :", 1)[1])
        # Relancée, la mise à jour n'a plus rien à dire : la copie a toutes les notes.
        relance = installer(self.racine, MOTEUR)
        self.assertNotIn("Notes de version", relance)
        self.assertNotIn("-m \"Notes de version", relance)

    def commit(self):
        env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "SOCLE_HOOKS_OFF": "1"}
        subprocess.run(["git", "add", "-A"], cwd=self.racine, check=True, env=env)
        subprocess.run(["git", "-c", "user.name=essai", "-c", "user.email=essai@exemple.org", "-c",
                        "core.hooksPath=/dev/null", "commit", "-q", "-m", "essai"], cwd=self.racine, check=True,
                       env=env)

    def test_relancee_avant_son_commit_elle_nomme_les_memes_notes(self):
        """B-0225 : relancé avant le commit de la mise à jour, l'installeur
        trouvait déjà la copie nouvelle dans l'arbre, et ne nommait plus
        rien ; il lit les notes de la copie du dernier commit."""
        installer(self.racine, self.source(garder=3), adoption=False)
        self.commit()
        premiere = installer(self.racine, MOTEUR)
        relance = installer(self.racine, MOTEUR)
        nouvelles = self.tous[:-3]
        commande = (f'git commit -m "Mettre à jour le socle {installeur.VERSION}" -m "Notes de version du socle : '
                    f'{", ".join(nouvelles)}, dans .socle/engine/socle/CHANGES.md" && git push')
        for sortie in (premiere, relance):
            self.assertIn(f"{len(nouvelles)} entrée(s) que la copie du moteur remplacée n'avait pas", sortie)
            apres = sortie.split("Et maintenant :", 1)[1]
            self.assertIn(commande, apres)
            self.assertIn(f"lui dire de lire ses notes de version ({', '.join(nouvelles)}, dans "
                          "`.socle/engine/socle/CHANGES.md`)", apres)
        # Commitée, la mise à jour n'a plus de notes à donner.
        self.commit()
        self.assertNotIn("Notes de version", installer(self.racine, MOTEUR))

    def test_une_copie_commitee_sans_notes_les_recoit_toutes_meme_relancee(self):
        """Le dernier commit a une copie du moteur sans notes, d'avant
        ADR-0078 : relancée, la mise à jour les donne encore toutes, et ne
        se replie pas sur l'arbre, qui a déjà la copie nouvelle."""
        installer(self.racine, self.source(), adoption=False)
        self.commit()
        installer(self.racine, MOTEUR)
        relance = installer(self.racine, MOTEUR)
        self.assertIn(f"voici toutes leurs entrées ({len(self.tous)})", relance)

    def test_notes_deja_lues_dans_le_dernier_commit_sinon_dans_l_arbre(self):
        installer(self.racine, self.source(garder=3), adoption=False)
        # Sans commit, l'arbre.
        self.assertEqual(installeur.notes_deja_lues(self.racine, ".socle/engine"), set(self.tous[-3:]))
        self.commit()
        installer(self.racine, MOTEUR)
        self.assertEqual(installeur.notes_deja_lues(self.racine, ".socle/engine"), set(self.tous[-3:]))
        # Un dernier commit sans copie du moteur à cet endroit : l'arbre.
        self.assertEqual(installeur.notes_deja_lues(self.racine, "ailleurs"), set())

    def test_rien_quand_le_moteur_n_est_pas_recopie(self):
        """Lancé depuis le projet, l'installeur garde le moteur (ADR-0077) :
        la copie en place est celle que les notes décriraient."""
        installer(self.racine, self.source(), adoption=False)
        sortie = installer(self.racine, self.racine / ".socle/engine")
        self.assertIn("moteur déjà en place", sortie)
        self.assertNotIn("Notes de version", sortie)

    def test_rien_en_mode_amont(self):
        """En amont, le moteur est la source : rien n'est recopié."""
        shutil.copytree(self.source(), self.racine / "engine")
        installer(self.racine, self.racine / "engine", adoption=False, mode=config.MODE_AMONT)
        sortie = installer(self.racine, self.racine / "engine", mode=config.MODE_AMONT)
        self.assertIn("mise à jour : moteur amont", sortie)
        self.assertNotIn("Notes de version", sortie)

    def test_un_projet_en_anglais_les_recoit_en_anglais(self):
        installer(self.racine, self.source(), adoption=False, langue_memoire="en")
        sortie = installer(self.racine, MOTEUR)
        self.assertIn("Release notes: the replaced engine copy had none", sortie)
        self.assertIn("`.socle/engine/socle/CHANGES.en.md`", sortie)
        self.assertIn("## 2026-11-09-a — The reading fingerprint no longer covers the metadata", sortie)
        self.assertNotIn("À faire : ", sortie)
        self.assertIn(f'-m "Socle release notes: {", ".join(self.tous)}, in .socle/engine/socle/CHANGES.en.md"',
                      sortie)

    def verifier_ce_qui_s_imprime(self, sortie: str, notes: list[tuple[str, str]], fichier: str, tete: str):
        """Dans `sortie`, chacune des `notes` : entière si elle demande
        quelque chose, avant la ligne `tete` qui compte les autres ; de
        celles-ci, le titre seul (B-0324)."""
        rien = [t for _, t in notes if installeur.ne_demande_rien(t)]
        self.assertTrue(rien)
        self.assertIn(tete.format(n=len(rien), fichier=fichier), sortie)
        fin_des_entieres = sortie.index(tete.format(n=len(rien), fichier=fichier))
        for ident, texte in notes:
            titre, corps = texte.split("\n", 1)
            if installeur.ne_demande_rien(texte):
                self.assertIn(f"\n{titre}\n", sortie, ident)
                self.assertNotIn(corps.strip(), sortie, ident)
            else:
                self.assertLess(sortie.index(texte), fin_des_entieres, ident)

    def test_a_la_mise_a_jour_une_note_qui_ne_demande_rien_n_a_que_son_titre(self):
        installer(self.racine, self.source(garder=3), adoption=False)
        sortie = installer(self.racine, MOTEUR)
        self.verifier_ce_qui_s_imprime(
            sortie, installeur.notes_nouvelles(set(), PAQUET)[:-3], ".socle/engine/socle/CHANGES.md",
            "{n} entrée(s) ne demandent rien (« À faire : rien ») : leur titre seul, et leur texte dans "
            "`{fichier}`, à lire au besoin :")

    def test_en_anglais_une_note_qui_ne_demande_rien_n_a_que_son_titre(self):
        installer(self.racine, self.source(), adoption=False, langue_memoire="en")
        sortie = installer(self.racine, MOTEUR)
        self.verifier_ce_qui_s_imprime(
            sortie, installeur.notes_nouvelles(set(), PAQUET, "en"), ".socle/engine/socle/CHANGES.en.md",
            "{n} entry(ies) ask nothing (“To do: nothing”): their title only, and their text in `{fichier}`, "
            "to read when needed:")

    def test_sans_notes_le_message_de_commit_ne_change_pas(self):
        installer(self.racine, MOTEUR, adoption=False)
        commit = next(e for e in installeur.et_maintenant(self.racine, True, []) if "git commit" in e)
        self.assertIn(f'git commit -m "Mettre à jour le socle {installeur.VERSION}" && git push', commit)
        etapes = installeur.et_maintenant(self.racine, True, [], ["2026-11-14-c"])
        commit = next(e for e in etapes if "git commit" in e)
        self.assertIn('-m "Notes de version du socle : 2026-11-14-c, dans .socle/engine/socle/CHANGES.md"', commit)
        # Une première installation n'en porte jamais.
        commit = next(e for e in installeur.et_maintenant(self.racine, False, [], ["2026-11-14-c"])
                      if "git commit" in e)
        self.assertNotIn("Notes de version", commit)


if __name__ == "__main__":
    unittest.main()
