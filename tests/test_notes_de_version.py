"""Les notes de version du moteur (ADR-0078) : ce qu'une mise à jour change
pour un projet installé, donné par l'installeur quand il recopie le moteur.

Le pilote, passé au moteur nouveau, a vu changer toutes ses empreintes de
lecture sans qu'aucune note ne l'ait prévenu (B-0151)."""

import io
import re
import shutil
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
