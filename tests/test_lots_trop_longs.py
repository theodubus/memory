"""Un lot ouvert qui attend plus de tâches qu'une session n'en mène :
l'état et le rappel de fin de tour l'en avertissent, sans rien refuser, au-
delà de `[batches] max_tasks` des garde-fous, 9 par défaut (B-0233,
T-0012)."""

import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

from socle import config, hooks, installer as installeur, memory as memoire, state as etat
from socle.checks_ratchet import assouplissements
from tests.test_ordre import memoire_de, sujet

MOTEUR = Path(__file__).resolve().parent.parent / "engine"


def lot(taches: int, statuts: dict[str, str] | None = None, statut_du_lot: str = "ouvert") -> memoire.Memoire:
    """Un lot qui attend `taches` tâches d'un même besoin ; `statuts` en
    clôt ou en commence certaines."""
    statuts = statuts or {}
    ids = [f"T-{n:04d}" for n in range(1, taches + 1)]
    return memoire_de(sujet("B-0001"), *(sujet(i, statuts.get(i, "ouvert"), besoin="B-0001") for i in ids),
                      sujet("L-0001", statut_du_lot, apres=", ".join(ids)))


class TestCompte(unittest.TestCase):
    def test_au_dela_du_seuil_une_ligne_nomme_le_lot_et_ses_taches(self):
        lignes = memoire.lots_trop_longs(lot(10), 9)
        self.assertEqual(len(lignes), 1)
        self.assertIn("L-0001 (10 tâches)", lignes[0])
        self.assertIn("plus de tâches qu'une session n'en mène", lignes[0])
        self.assertIn("seuil : 9", lignes[0])
        self.assertIn("`[batches] max_tasks`", lignes[0])

    def test_au_seuil_et_en_dessous_rien_ne_se_dit(self):
        self.assertEqual(memoire.lots_trop_longs(lot(9), 9), [])
        self.assertEqual(memoire.lots_trop_longs(lot(2), 9), [])

    def test_seules_comptent_les_taches_que_le_lot_attend_encore(self):
        # Douze tâches, dont trois closes et une en cours : il en attend neuf.
        statuts = {"T-0001": "fait", "T-0002": "abandonné", "T-0003": "fait", "T-0004": "en cours"}
        self.assertEqual(memoire.lots_trop_longs(lot(12, statuts), 9), [])
        self.assertIn("L-0001 (9 tâches)", memoire.lots_trop_longs(lot(12, statuts), 8)[0])

    def test_un_lot_en_cours_compte_et_un_lot_clos_non(self):
        self.assertTrue(memoire.lots_trop_longs(lot(3, statut_du_lot="en cours"), 2))
        clos = {f"T-{n:04d}": "fait" for n in range(1, 4)}
        self.assertEqual(memoire.lots_trop_longs(lot(3, clos, statut_du_lot="fait"), 2), [])

    def test_le_lot_d_avant_et_une_demande_attendus_ne_sont_pas_des_taches(self):
        mem = memoire_de(sujet("B-0001"), sujet("T-0001", besoin="B-0001"), sujet("T-0002", besoin="B-0001"),
                         sujet("L-0001", apres="T-0001"), sujet("L-0002", apres="L-0001, T-0002, D-0001"))
        self.assertEqual(memoire.lots_trop_longs(mem, 1), [])

    def test_plusieurs_lots_tiennent_sur_une_ligne(self):
        ids = [f"T-{n:04d}" for n in range(1, 5)]
        mem = memoire_de(sujet("B-0001"), *(sujet(i, besoin="B-0001") for i in ids),
                         sujet("L-0001", apres="T-0001, T-0002"), sujet("L-0002", apres="T-0003, T-0004"))
        lignes = memoire.lots_trop_longs(mem, 1)
        self.assertEqual(len(lignes), 1)
        self.assertIn("2 lot(s)", lignes[0])
        self.assertIn("L-0001 (2 tâches), L-0002 (2 tâches)", lignes[0])


class TestSeuil(unittest.TestCase):
    def seuil(self, garde_fous: dict):
        return config.Projet(Path("."), garde_fous=garde_fous).taches_par_session()

    def test_le_seuil_des_garde_fous_et_sa_valeur_par_defaut(self):
        self.assertEqual(config.TACHES_PAR_SESSION, 9)
        self.assertEqual(self.seuil({}), 9)
        self.assertEqual(self.seuil({"batches": {"max_tasks": 4}}), 4)
        self.assertEqual(self.seuil({"batches": {"max_tasks": "beaucoup"}}), 9)
        self.assertEqual(self.seuil({"batches": {"max_tasks": float("nan")}}), 0)
        self.assertEqual(self.seuil({"batches": {"max_tasks": True}}), 1)

    def test_le_gabarit_pose_le_seuil_par_defaut_dans_les_deux_langues(self):
        for nom in ("guardrails.toml", "guardrails.en.toml"):
            gabarit = tomllib.loads((MOTEUR / "socle/templates" / nom).read_text())
            self.assertEqual(gabarit["batches"]["max_tasks"], config.TACHES_PAR_SESSION, nom)

    def test_le_cliquet_connait_la_cle(self):
        self.assertEqual(assouplissements({}, {"batches": {"max_tasks": 9}}), [])
        self.assertEqual(assouplissements({}, {"batches": {"max_tasks": 5}}), [])
        self.assertEqual(assouplissements({}, {"batches": {"max_tasks": 20}}), [("batches.max_tasks", "9 → 20")])


class TestEtatEtRappel(unittest.TestCase):
    """Dans un projet installé : l'état du démarrage et le rappel de fin de
    tour d'un dernier message sans récap."""

    @classmethod
    def setUpClass(cls):
        cls.racine = Path(tempfile.mkdtemp(prefix="socle-lots-"))
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=cls.racine, check=True)
        with contextlib.redirect_stdout(io.StringIO()):
            installeur.installer(cls.racine, "python", "@essai", source=MOTEUR)
        backlog = cls.racine / "memory/backlog"
        backlog.mkdir(parents=True, exist_ok=True)
        ids = [f"T-{n:04d}" for n in range(1, 4)]
        for ident, meta in (("B-0001", ""), *((i, " · besoin : B-0001") for i in ids),
                            ("L-0001", " · après : " + ", ".join(ids))):
            (backlog / f"{ident}-essai.md").write_text(
                f"<!-- socle: couche=backlog zone=publique -->\n# {ident} — Le sujet {ident}\n\n"
                f"> statut : ouvert · origine : fichier:calc.py{meta}\n\nPour l'essai.\n")
        cls.garde_fous = cls.racine / ".socle/guardrails.toml"
        cls.sains = cls.garde_fous.read_text()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.racine, ignore_errors=True)

    def avec_seuil(self, seuil: int) -> config.Projet:
        self.addCleanup(self.garde_fous.write_text, self.sains)
        self.garde_fous.write_text(self.sains.replace("max_tasks = 9", f"max_tasks = {seuil}"))
        return config.Projet.charger(self.racine)

    def rappel(self, projet: config.Projet) -> str:
        transcript = Path(tempfile.mkdtemp()) / "t.jsonl"
        self.addCleanup(shutil.rmtree, transcript.parent, ignore_errors=True)
        transcript.write_text(json.dumps({"type": "assistant", "message": {"content": "Fait."}}))
        (self.racine / ".socle/trace/derniere-fin-de-tour").unlink(missing_ok=True)
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            hooks.exiger_recap(projet, {"session_id": "l", "transcript_path": str(transcript)})
        return json.loads(sortie.getvalue())["reason"]

    def test_au_dela_du_seuil_l_etat_et_le_rappel_avertissent(self):
        projet = self.avec_seuil(2)
        for texte in (etat.calculer(projet), etat.calculer(projet, contenus=False), self.rappel(projet)):
            self.assertIn("!! 1 lot(s) attendent encore plus de tâches qu'une session n'en mène (seuil : 2", texte)
            self.assertIn("L-0001 (3 tâches)", texte)

    def test_au_seuil_ils_se_taisent(self):
        projet = self.avec_seuil(3)
        for texte in (etat.calculer(projet), self.rappel(projet)):
            self.assertIn("prochain lot : L-0001", texte)
            self.assertNotIn("qu'une session n'en mène", texte)

    def test_l_avertissement_se_dit_avec_ce_qui_demande_d_agir(self):
        lignes = etat.calculer(self.avec_seuil(2), contenus=False).splitlines()
        alerte = next(i for i, l in enumerate(lignes) if "qu'une session n'en mène" in l)
        self.assertLess(alerte, next(i for i, l in enumerate(lignes) if l.startswith("backlog  :")))


if __name__ == "__main__":
    unittest.main()
