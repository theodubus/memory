"""La mémoire privée, dans ses deux modes, sur des dépôts fabriqués. Le
chiffrement est un filtre git réversible : le moteur ne connaît pas l'outil,
il ne voit que ce que git commite."""

import argparse
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from socle import cli, config, contexte, etat, hooks, liens, memoire, prive
from socle.demandes import ecrire_reponse
from socle.demandes import toutes as demandes_toutes
from socle.rapport import Rapport

P = "P"  # un identifiant privé en clair dans ce fichier public serait une fuite
ENTETE = "<!-- socle: couche=canonique zone=privee -->\n# Mémoire canonique privée\n"
FAIT_PRIVE = ENTETE + f"\n## {P}F-0001 — Le nom de code est Mistral\n\n> statut : supposé · source : fichier:memoire/actif.md\n"
CANONIQUE = "<!-- socle: couche=canonique zone=publique -->\n# Mémoire canonique\n"
ACTIF = "<!-- socle: couche=actif zone=publique -->\n# Chantier actif\n"

FILTRE = """import base64, sys
donnees = sys.stdin.buffer.read()
if sys.argv[1] == "clean":
    sys.stdout.buffer.write(donnees if donnees.startswith(b"ESSAI:") else b"ESSAI:" + base64.b64encode(donnees))
else:
    sys.stdout.buffer.write(base64.b64decode(donnees[6:]) if donnees.startswith(b"ESSAI:") else donnees)
"""


def git(cwd, *args):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


def verifier(racine: Path, fonction, tete=None) -> Rapport:
    ctx = contexte.Contexte(config.Projet.charger(racine), etage="agent", tete=tete)
    r = Rapport()
    fonction(ctx, r)
    return r


class Base(unittest.TestCase):
    mode = None

    def setUp(self):
        self.dossier = Path(tempfile.mkdtemp(prefix="socle-prive-"))
        self.racine = self.dossier / "public"
        (self.racine / ".socle").mkdir(parents=True)
        (self.racine / "memoire").mkdir()
        (self.racine / "memoire/canonique.md").write_text(CANONIQUE)
        (self.racine / "memoire/actif.md").write_text(ACTIF)
        if self.mode:
            (self.racine / ".socle/politique.toml").write_text(f'[private]\nmode = "{self.mode}"\n')
        git(self.racine, "init", "-q", "-b", "main")

    def tearDown(self):
        shutil.rmtree(self.dossier, ignore_errors=True)

    def commit(self, cwd=None, message="essai"):
        git(cwd or self.racine, "add", "-A")
        git(cwd or self.racine, "commit", "-qm", message)
        return git(cwd or self.racine, "rev-parse", "HEAD").strip()


class TestSansMode(Base):
    def test_rien_de_configure(self):
        projet = config.Projet.charger(self.racine)
        self.assertIsNone(prive.mode(projet))
        self.assertEqual(prive.ligne_etat(projet), "mémoire privée : non configurée (mode public seul)")
        self.commit()
        self.assertEqual(verifier(self.racine, prive.controle_acces).constats, [])

    def test_un_fichier_prive_commite_sans_mode_est_public(self):
        (self.racine / "memoire/prive").mkdir()
        (self.racine / "memoire/prive/canonique.md").write_text(FAIT_PRIVE)
        git(self.racine, "add", "-A")
        r = verifier(self.racine, prive.controle_acces)
        self.assertIn("sans mode de mémoire privée : ils sont publics", r.erreurs()[0].message)

    def test_zone_et_lisibilite(self):
        self.assertTrue(memoire.est_prive("memoire/prive/canonique.md"))
        self.assertFalse(memoire.est_prive("memoire/canonique.md"))
        self.assertTrue(memoire.lisible(FAIT_PRIVE))
        self.assertFalse(memoire.lisible("ESSAI:PCEtLSBzb2NsZQ=="))
        self.assertFalse(memoire.lisible(None))


class Compagnon(Base):
    mode = "compagnon"

    def setUp(self):
        super().setUp()
        (self.racine / ".gitignore").write_text("memoire/prive/\n")
        self.prive = self.racine / "memoire/prive"
        self.prive.mkdir()
        git(self.prive, "init", "-q", "-b", "main")
        (self.prive / "canonique.md").write_text(FAIT_PRIVE)
        self.sha = self.commit(self.prive, "fait privé")
        prive.ecrire_verrou(self.racine, self.sha)
        self.commit()


class TestCompagnon(Compagnon):
    def test_disponible_et_au_verrou(self):
        projet = config.Projet.charger(self.racine)
        self.assertEqual(prive.depot_compagnon(self.racine), self.prive)
        self.assertEqual(prive.commit_compagnon(self.racine), self.sha)
        self.assertEqual(prive.lire_verrou(self.racine), self.sha)
        self.assertEqual(prive.compagnon_modifie(self.racine), [])
        self.assertTrue(prive.acces(projet).disponible)
        self.assertIn("disponible, au commit", prive.ligne_etat(projet))
        self.assertIn("mémoire privée : disponible, au commit", etat.calculer(projet, contenus=False))
        self.assertEqual(memoire.fichiers_compagnon(self.racine), ["memoire/prive/canonique.md"])
        self.assertIn(f"{P}F-0001", memoire.Memoire.charger(self.racine).definitions())
        self.assertEqual(verifier(self.racine, prive.controle_verrou).erreurs(), [])

    def test_verrou_perime(self):
        (self.prive / "canonique.md").write_text(FAIT_PRIVE + "\nUne précision.\n")
        self.commit(self.prive, "précision")
        erreurs = verifier(self.racine, prive.controle_verrou).erreurs()
        self.assertEqual(len(erreurs), 1)
        self.assertIn("le verrou désigne", erreurs[0].message)

    def test_changement_prive_hors_commit(self):
        (self.prive / "canonique.md").write_text(FAIT_PRIVE + "\nPas commité.\n")
        self.assertEqual(prive.compagnon_modifie(self.racine), ["canonique.md"])
        self.assertIn("hors de tout commit", verifier(self.racine, prive.controle_verrou).erreurs()[0].message)

    def test_fichier_prive_force_dans_le_depot_public(self):
        # Tant que le clone est là, git refuse en silence d'y prendre un
        # fichier ; sans lui, `add -f` passe outre le `.gitignore`.
        shutil.rmtree(self.prive / ".git")
        git(self.racine, "add", "-f", "memoire/prive/canonique.md")
        self.assertIn("fichier privé commité dans le dépôt public",
                      verifier(self.racine, prive.controle_verrou).erreurs()[0].message)

    def test_clone_absent_est_indisponible(self):
        shutil.rmtree(self.prive)
        projet = config.Projet.charger(self.racine)
        self.assertFalse(prive.acces(projet).disponible)
        self.assertIn("INDISPONIBLE", prive.ligne_etat(projet))
        r = verifier(self.racine, prive.controle_acces)
        self.assertEqual(r.erreurs(), [])
        self.assertIn("indisponible", r.constats[0].message)

    def test_commande_verrouiller_puis_extraire(self):
        (self.prive / "canonique.md").write_text(FAIT_PRIVE + "\nUne précision.\n")
        nouveau = self.commit(self.prive, "précision")
        flux = io.StringIO()
        with contextlib.redirect_stdout(flux), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.cmd_prive(argparse.Namespace(root=str(self.racine), action="verrouiller")), 0)
        self.assertEqual(prive.lire_verrou(self.racine), nouveau)
        prive.ecrire_verrou(self.racine, self.sha)
        with contextlib.redirect_stdout(flux), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.cmd_prive(argparse.Namespace(root=str(self.racine), action="extraire")), 0)
        self.assertEqual(prive.commit_compagnon(self.racine), self.sha)

    def test_le_contenu_nouveau_est_prive_par_defaut(self):
        flux = io.StringIO()
        with contextlib.redirect_stdout(flux):
            cli.cmd_new(argparse.Namespace(root=str(self.racine), type="fact", title="Une idée", private=False, public=False))
        self.assertIn(f"## {P}F-0002 — Une idée", (self.prive / "canonique.md").read_text())
        with contextlib.redirect_stdout(flux):
            cli.cmd_new(argparse.Namespace(root=str(self.racine), type="fact", title="Un résultat", private=False, public=True))
        self.assertIn("## F-0001 — Un résultat", (self.racine / "memoire/canonique.md").read_text())

    def test_en_ci_un_constat_prive_est_masque(self):
        (self.prive / "canonique.md").write_text(FAIT_PRIVE.replace("supposé", "inventé"))
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage="ci")
        r = contexte.executer(ctx, ["memoire.format"])
        self.assertTrue(r.erreurs())
        texte = r.texte()
        self.assertNotIn("inventé", texte)
        self.assertNotIn("canonique.md", texte)
        self.assertIn("constat masqué : zone privée", texte)


class Chiffre(Base):
    mode = "chiffre"

    def setUp(self):
        super().setUp()
        filtre = self.dossier / "filtre.py"
        filtre.write_text(FILTRE)
        git(self.racine, "config", "filter.essai.clean", f"{sys.executable} {filtre} clean")
        git(self.racine, "config", "filter.essai.smudge", f"{sys.executable} {filtre} smudge")
        (self.racine / ".gitattributes").write_text("memoire/prive/** filter=essai\n")
        (self.racine / "memoire/prive").mkdir()
        (self.racine / "memoire/prive/canonique.md").write_text(FAIT_PRIVE)
        self.commit()


class TestChiffre(Chiffre):
    def test_commite_chiffre_lu_en_clair(self):
        brut = git(self.racine, "show", "HEAD:memoire/prive/canonique.md")
        self.assertTrue(brut.startswith("ESSAI:"))
        projet = config.Projet.charger(self.racine)
        self.assertTrue(prive.acces(projet).disponible)
        self.assertIn(f"{P}F-0001", memoire.Memoire.charger(self.racine).definitions())
        self.assertEqual(verifier(self.racine, prive.controle_chiffre).erreurs(), [])
        self.assertEqual(prive.arbre_commite(contexte.Contexte(projet, tete="HEAD")), "HEAD")

    def test_sans_la_cle_la_memoire_est_indisponible(self):
        (self.racine / "memoire/prive/canonique.md").write_text(git(self.racine, "show", "HEAD:memoire/prive/canonique.md"))
        projet = config.Projet.charger(self.racine)
        mem = memoire.Memoire.charger(self.racine)
        self.assertEqual(mem.illisibles, ["memoire/prive/canonique.md"])
        self.assertFalse(prive.acces(projet, mem.illisibles).disponible)
        ctx = contexte.Contexte(projet, etage="agent")
        self.assertIsNone(ctx.lire("memoire/prive/canonique.md"))
        self.assertIn("memoire/prive/canonique.md", ctx.fichiers)

    def test_commite_en_clair_sans_filtre(self):
        (self.racine / ".gitattributes").write_text("")
        (self.racine / "memoire/prive/journal").mkdir()
        (self.racine / "memoire/prive/journal/2026-10.md").write_text(
            "<!-- socle: couche=journal zone=privee -->\n# Journal privé\n")
        git(self.racine, "add", "-A")
        messages = [c.message for c in verifier(self.racine, prive.controle_chiffre).erreurs()]
        self.assertTrue(any("EN CLAIR" in m for m in messages), messages)
        self.assertTrue(any("aucun filtre de chiffrement" in m for m in messages), messages)


if __name__ == "__main__":
    unittest.main()


class TestRecuperation(Base):
    """En CI : le dépôt privé, au commit du verrou, ou indisponible sans clé."""

    mode = "compagnon"

    def setUp(self):
        super().setUp()
        self.depot = self.dossier / "prive-origine"
        self.depot.mkdir()
        git(self.depot, "init", "-q", "-b", "main")
        (self.depot / "canonique.md").write_text(FAIT_PRIVE)
        self.sha = self.commit(self.depot, "un")
        (self.depot / "canonique.md").write_text(FAIT_PRIVE + "\nDeux.\n")
        self.commit(self.depot, "deux")
        prive.ecrire_verrou(self.racine, self.sha)

    def recuperer(self, **env) -> tuple[int, str]:
        flux = io.StringIO()
        avant = {k: os.environ.pop(k, None) for k in ("SOCLE_PRIVE_DEPOT", "SOCLE_PRIVE_CLE")}
        os.environ.update(env)
        try:
            with contextlib.redirect_stdout(flux):
                code = prive.recuperer(config.Projet.charger(self.racine))
        finally:
            for k, v in avant.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v
        return code, flux.getvalue()

    def test_sans_cle_indisponible(self):
        code, sortie = self.recuperer()
        self.assertEqual(code, 0)
        self.assertIn("indisponible ici", sortie)
        self.assertIsNone(prive.commit_compagnon(self.racine))

    def test_avec_cle_au_verrou_sans_rien_reveler(self):
        code, sortie = self.recuperer(SOCLE_PRIVE_DEPOT=str(self.depot), SOCLE_PRIVE_CLE="cle-factice")
        self.assertEqual(code, 0, sortie)
        self.assertEqual(prive.commit_compagnon(self.racine), self.sha)
        self.assertNotIn(str(self.depot), sortie)
        code, sortie = self.recuperer(SOCLE_PRIVE_DEPOT=str(self.dossier / "absent"), SOCLE_PRIVE_CLE="x")
        self.assertEqual(code, 1)
        self.assertNotIn("absent", sortie)


DEMANDE_RETRAIT = """<!-- socle: couche=demandes zone=publique -->
# D-0001 — Retirer un terme de la liste privée

> date : 2026-10-10

## Décision demandée

Valider la liste `memoire/prive/termes.txt` dans la version `{cite}`.

## Réponses possibles

- `valider` — le terme sort de la liste.
- `contexte-insuffisant` — la demande revient à l'agent.
"""


class TestTermes(Compagnon):
    """La liste des termes privés (D-0007) : l'agent ajoute, seul l'humain
    retire ; un terme trouvé n'est jamais réécrit."""

    def setUp(self):
        super().setUp()
        projet = config.Projet.charger(self.racine)
        self.assertTrue(prive.ajouter_terme(projet, "Mistral"))
        self.assertFalse(prive.ajouter_terme(projet, "Mistral"))
        prive.ajouter_terme(projet, "re:zephyr-\\d+")
        sha = self.commit(self.prive, "termes")
        prive.ecrire_verrou(self.racine, sha)
        self.base = self.commit()

    def rapport(self, fonction, etage="agent", tete=None) -> Rapport:
        ctx = contexte.Contexte(config.Projet.charger(self.racine), etage=etage, base=self.base, tete=tete)
        r = Rapport()
        fonction(ctx, r)
        return r

    def test_liste_et_recherche(self):
        projet = config.Projet.charger(self.racine)
        t = prive.termes(projet)
        self.assertEqual((t.liste, t.disponible), (["Mistral", "re:zephyr-\\d+"], True))
        self.assertEqual(prive.termes(projet, self.base).liste, t.liste)
        self.assertEqual(prive.lire_prive(projet, self.base, prive.TERMES), t.texte)
        self.assertEqual(prive.fuites("Le projet MISTRAL avance, zephyr-12 aussi.", t.liste, identifiants=False),
                         ["terme privé n°1 de la liste", "terme privé n°2 de la liste"])
        self.assertEqual(prive.fuites("Un mistralien n'est pas un terme.", t.liste, identifiants=False), [])

    def test_fuite_dans_un_fichier_public_et_un_message(self):
        (self.racine / "notes.md").write_text("Le projet Mistral.\n")
        self.commit(message=f"Note sur {P}F-0001")
        erreurs = [c.message for c in self.rapport(prive.controle_fuites).erreurs()]
        self.assertEqual(len(erreurs), 2, erreurs)
        self.assertTrue(all("Mistral" not in m for m in erreurs))
        self.assertIn("terme privé n°1", erreurs[0])
        self.assertIn(f"identifiant privé `{P}F-0001`", erreurs[1])

    def test_retirer_un_terme_exige_l_humain(self):
        texte = (self.prive / "termes.txt").read_text().replace("Mistral\n", "")
        (self.prive / "termes.txt").write_text(texte)
        sha = self.commit(self.prive, "retrait")
        prive.ecrire_verrou(self.racine, sha)
        cite = "sha256:" + prive.outils.sha256(texte)[:16]
        erreurs = self.rapport(prive.controle_termes).erreurs()
        self.assertIn(cite, erreurs[0].message)
        self.assertNotIn("Mistral", erreurs[0].message)
        demande = self.racine / "memoire/demandes/D-0001-retrait.md"
        demande.parent.mkdir(parents=True)
        demande.write_text(DEMANDE_RETRAIT.format(cite=cite))
        d = [x for x in demandes_toutes(self.racine) if x.id == "D-0001"][0]
        ecrire_reponse(self.racine, d, "valider", "", "Théo", "2026-10-10", canal="conversation", citation="ok")
        r = self.rapport(prive.controle_termes)
        self.assertEqual(r.erreurs(), [])
        self.assertIn("validé par D-0001", r.constats[0].message)

    def test_hook_de_l_agent_et_message_de_commit(self):
        projet = config.Projet.charger(self.racine)
        entree = {"session_id": "t", "tool_name": "Write",
                  "tool_input": {"file_path": str(self.racine / "notes.md"), "content": "Le projet Mistral.\n"}}
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            hooks.pre_tool_use(projet, entree)
        self.assertIn("fuite de la mémoire privée", sortie.getvalue())
        self.assertNotIn("Mistral", sortie.getvalue().replace("Le projet Mistral", ""))
        message = self.dossier / "COMMIT_EDITMSG"
        message.write_text("Avancer sur Mistral\n# Mistral en commentaire ne compte pas\n")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.cmd_hook(argparse.Namespace(root=str(self.racine), event="git-commit-msg",
                                                             rest=[str(message)])), 1)
            message.write_text("Avancer\n# Mistral en commentaire ne compte pas\n")
            self.assertEqual(hooks.git_commit_msg(projet, str(message)), 0)


class TestRelecture(Compagnon):
    """La relecture avant publication (D-0006) : au choix de l'humain."""

    def regler(self, valeur):
        (self.racine / ".socle/politique.toml").write_text(f'[private]\nmode = "compagnon"\nreview = "{valeur}"\n')

    def test_sans_reglage_rien_n_est_exige_mais_c_est_dit(self):
        projet = config.Projet.charger(self.racine)
        self.assertIsNone(prive.relecture(projet))
        self.assertIsNone(prive.publication_refusee(projet, ["abc"]))
        self.assertIn("relecture avant publication non choisie", verifier(self.racine, prive.controle_acces).texte())

    def test_par_lots_un_push_attend_la_relecture(self):
        self.regler("lots")
        projet = config.Projet.charger(self.racine)
        tete = git(self.racine, "rev-parse", "HEAD").strip()
        self.assertIn("politique : lots", prive.publication_refusee(projet, [tete]))
        entree = {"session_id": "t", "tool_name": "Bash", "tool_input": {"command": "git push origin travail"}}
        sortie = io.StringIO()
        with contextlib.redirect_stdout(sortie):
            hooks.pre_tool_use(projet, entree)
        self.assertIn("relecture avant publication", sortie.getvalue())
        avant = sys.stdin
        sys.stdin = io.StringIO(f"refs/heads/travail {tete} refs/heads/travail {'0' * 40}\n")
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(hooks.git_pre_push(projet), 1)
        finally:
            sys.stdin = avant
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.cmd_relu(argparse.Namespace(root=str(self.racine), rev="HEAD", by="Théo",
                                                             relayed=True, quote="ok tu peux publier", quote_file=None)), 0)
        self.assertTrue(prive.relue(self.racine, tete))
        self.assertTrue(prive.fichier_relectures(self.racine).is_file())
        self.assertIsNone(prive.publication_refusee(projet, [tete]))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.cmd_relu(argparse.Namespace(root=str(self.racine), rev="HEAD", by="Théo",
                                                             relayed=True, quote="", quote_file=None)), 2)

    def test_aucune(self):
        self.regler("aucune")
        self.assertIsNone(prive.publication_refusee(config.Projet.charger(self.racine), ["abc"]))
        prive.noter_relecture(self.racine, "abc", "Théo", "terminal", "")
        self.assertTrue(prive.relue(self.racine, "abc"))


class TestDemandesPrivees(Compagnon):
    """Les demandes et leurs réponses deviennent privées sur décision de
    l'humain (`[private] requests`)."""

    def test_privees_sur_decision(self):
        (self.racine / ".socle/politique.toml").write_text(
            '[private]\nmode = "compagnon"\nrequests = true\n\n[protected]\npaths = ["memoire/demandes/*.reponse.toml"]\n')
        projet = config.Projet.charger(self.racine)
        self.assertIn("memoire/prive/demandes/*.reponse.toml", projet.chemins_proteges())
        with contextlib.redirect_stdout(io.StringIO()):
            cli.cmd_new(argparse.Namespace(root=str(self.racine), type="request", title="Une question privée",
                                           private=False, public=False))
        ids = [d.id for d in demandes_toutes(self.racine)]
        self.assertEqual(ids, [f"{P}D-0001"])

    def test_publiques_par_defaut(self):
        with contextlib.redirect_stdout(io.StringIO()):
            cli.cmd_new(argparse.Namespace(root=str(self.racine), type="request", title="Une question",
                                           private=False, public=False))
        self.assertEqual([d.id for d in demandes_toutes(self.racine)], ["D-0001"])


class TestLienPrive(Chiffre):
    def test_un_fichier_chiffre_n_a_pas_de_lien(self):
        (self.racine / ".socle/politique.toml").write_text(
            '[private]\nmode = "chiffre"\n\n[human]\nrepo_url = "https://github.com/essai/public"\n')
        url, raison = liens.lien(config.Projet.charger(self.racine), "memoire/prive/canonique.md")
        self.assertIsNone(url)
        self.assertIn("chiffré sur GitHub", raison)
