"""La mémoire privée (jalon 7) : des notes du projet qui ne doivent pas être
publiques, rangées sous `memoire/prive/` avec le même format que le reste.

Deux modes, au choix de l'humain dans la politique (`[private] mode`) :

- **compagnon** : `memoire/prive/` est le clone d'un dépôt privé, ignoré par
  le dépôt public ; un verrou commité (`.socle/prive.lock`) dit à quel commit
  du dépôt privé correspond chaque commit public ;
- **chiffre** : les fichiers privés sont commités chiffrés dans le dépôt
  public, par un filtre git (git-crypt ou équivalent). Le moteur ne connaît
  pas l'outil : il vérifie que ce qui est commité n'est pas en clair, et que
  la mémoire est lisible là où on la lit.

Sans accès (nouveau clone, CI d'un fork, clé absente), la mémoire privée est
« indisponible » : les contrôles qui en dépendent le disent, ils ne passent
pas en silence.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from socle import config, memoire, outils
from socle.contexte import controle

DOSSIER = memoire.DOSSIER_PRIVE
VERROU = f"{config.DOSSIER}/prive.lock"
MODES = ("compagnon", "chiffre")


def mode(projet: config.Projet) -> str | None:
    m = projet.pol("private", "mode")
    return str(m) if m else None


est_prive = memoire.est_prive
lisible = memoire.lisible


def depot_compagnon(racine: Path) -> Path | None:
    p = racine / DOSSIER
    return p if (p / ".git").exists() else None


def commit_compagnon(racine: Path) -> str | None:
    p = depot_compagnon(racine)
    if p is None or not outils.a_des_commits(p):
        return None
    return outils.git(p, "rev-parse", "HEAD").strip()


def compagnon_modifie(racine: Path) -> list[str]:
    p = depot_compagnon(racine)
    if p is None:
        return []
    return [l[3:] for l in outils.git(p, "status", "--porcelain", check=False).splitlines() if l.strip()]


def lire_verrou(racine: Path, rev: str | None = None) -> str | None:
    import tomllib

    texte = outils.lire_a(racine, rev, VERROU)
    if not texte:
        return None
    try:
        return str(tomllib.loads(texte).get("commit", "")) or None
    except tomllib.TOMLDecodeError:
        return None


def ecrire_verrou(racine: Path, sha: str):
    (racine / VERROU).write_text(
        "# Le commit du dépôt privé qui correspond à ce commit public (mode compagnon).\n"
        "# Écrit par `socle prive verrouiller`, jamais à la main.\n"
        f'commit = "{sha}"\n', encoding="utf-8")


def recuperer(projet: config.Projet) -> int:
    """En CI : cloner le dépôt privé au commit du verrou, avec la clé de
    déploiement que donnent les secrets `SOCLE_PRIVE_DEPOT` et
    `SOCLE_PRIVE_CLE`. Sans eux (pull request d'un fork), la mémoire privée
    reste indisponible, et les contrôles le disent. Le journal de la CI est
    public : ni l'adresse ni la sortie de git n'y sont écrites."""
    import os
    import subprocess
    import tempfile

    racine = projet.racine
    depot, cle = os.environ.get("SOCLE_PRIVE_DEPOT", ""), os.environ.get("SOCLE_PRIVE_CLE", "")
    verrou = lire_verrou(racine)
    if not depot or not cle:
        print("mémoire privée : indisponible ici, sans clé de déploiement (pull request d'un fork ?)")
        return 0
    if verrou is None:
        print(f"mémoire privée : pas de verrou ({VERROU})")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        fichier = Path(tmp) / "cle"
        fichier.write_text(cle.strip() + "\n", encoding="utf-8")
        fichier.chmod(0o600)
        env = {**os.environ, "GIT_SSH_COMMAND": f"ssh -i {fichier} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"}
        cible = racine / DOSSIER
        for args in (["clone", "-q", "--no-checkout", depot, str(cible)], ["-C", str(cible), "checkout", "-q", verrou]):
            if subprocess.run(["git", *args], cwd=racine, env=env, capture_output=True).returncode != 0:
                print(f"mémoire privée : récupération impossible (étape `git {args[0] if args[0] != '-C' else 'checkout'}`)")
                return 1
    print(f"mémoire privée : récupérée au verrou {verrou[:10]}")
    return 0


@dataclass
class Acces:
    disponible: bool
    raison: str


def acces(projet: config.Projet, illisibles: list[str] | None = None) -> Acces:
    """La mémoire privée est-elle là, et lisible ?"""
    m = mode(projet)
    racine = projet.racine
    if m == "compagnon":
        sha = commit_compagnon(racine)
        if sha is None:
            return Acces(False, f"le dépôt privé n'est pas cloné dans `{DOSSIER}/`")
        verrou = lire_verrou(racine)
        if verrou and verrou != sha:
            return Acces(True, f"disponible, mais au commit {sha[:10]} et non au verrou {verrou[:10]} "
                         "(`socle prive extraire` pour revenir au verrou, `socle prive verrouiller` pour l'avancer)")
        return Acces(True, f"disponible, au commit {sha[:10]}")
    if m == "chiffre":
        if illisibles is None:
            illisibles = [c for c in outils.fichiers_courants(racine)
                          if est_prive(c) and not lisible(outils.lire_a(racine, None, c))]
        if illisibles:
            return Acces(False, f"{len(illisibles)} fichier(s) privé(s) illisible(s) : chiffrés, la clé manque ici")
        return Acces(True, "disponible, déchiffrée")
    return Acces(False, "aucun mode de mémoire privée dans la politique")


def ligne_etat(projet: config.Projet) -> str:
    m = mode(projet)
    if m is None:
        return "mémoire privée : non configurée (mode public seul)"
    if m not in MODES:
        return f"mémoire privée : mode « {m} » inconnu (attendu : {', '.join(MODES)})"
    a = acces(projet)
    if a.disponible:
        return f"mémoire privée : {a.raison} (mode {m})"
    return (f"mémoire privée : INDISPONIBLE (mode {m}) — {a.raison} ; les contrôles qui l'exigent le "
            "signalent ; ne pas conclure sur ce qui en dépend")


def arbre_commite(ctx) -> str | None:
    """Ce qui est, ou sera, commité : la tête jugée, ou l'index."""
    if ctx.tete:
        return ctx.tete
    if not outils.est_depot(ctx.racine):
        return None
    return outils.git(ctx.racine, "write-tree", check=False).strip() or None


# --------------------------------------------------------------------------
# Contrôles
# --------------------------------------------------------------------------


@controle("prive.acces")
def controle_acces(ctx, r):
    """La mémoire privée configurée est accessible, sinon c'est dit ; des
    fichiers privés sans mode configuré sont publics, donc refusés."""
    m = mode(ctx.projet)
    if m is None:
        commites = [c for c in outils.fichiers_a(ctx.racine, arbre_commite(ctx)) if est_prive(c)]
        if commites:
            r.erreur("prive.acces", f"{len(commites)} fichier(s) sous `{DOSSIER}/` commité(s) sans mode de mémoire "
                     "privée : ils sont publics. Choisir un mode (`[private] mode` de la politique) ou les déplacer",
                     commites[0])
        return
    if m not in MODES:
        r.erreur("prive.acces", f"mode de mémoire privée « {m} » inconnu (attendu : {', '.join(MODES)})", config.POLITIQUE)
        return
    a = acces(ctx.projet, ctx.memoire.illisibles if ctx.tete is None else None)
    if not a.disponible:
        r.indisponible("prive.acces", f"mémoire privée indisponible : {a.raison}")


@controle("prive.verrou")
def controle_verrou(ctx, r):
    """Mode compagnon : rien de privé n'est commité dans le dépôt public, et
    le verrou désigne le commit du dépôt privé qui va avec ce commit."""
    if mode(ctx.projet) != "compagnon":
        return
    arbre = arbre_commite(ctx)
    for c in outils.fichiers_a(ctx.racine, arbre):
        if est_prive(c):
            r.erreur("prive.verrou", f"fichier privé commité dans le dépôt public : il appartient au dépôt privé, "
                     f"que `{DOSSIER}/` clone (le retirer de l'index)", c)
    # Le verrou de la tête jugée ; en fin de tour, celui de l'arbre de
    # travail, qui sera commité.
    verrou = lire_verrou(ctx.racine, ctx.tete)
    if verrou is None:
        r.erreur("prive.verrou", "mode compagnon sans verrou : `socle prive verrouiller`", VERROU)
        return
    sha = commit_compagnon(ctx.racine)
    if sha is None:
        r.indisponible("prive.verrou", "dépôt privé non cloné : verrou non vérifiable")
        return
    modifies = compagnon_modifie(ctx.racine)
    if modifies and ctx.etage != "ci":
        r.erreur("prive.verrou", f"{len(modifies)} changement(s) de la mémoire privée hors de tout commit du dépôt "
                 "privé : les y commiter, puis `socle prive verrouiller`", DOSSIER)
    if sha != verrou:
        r.erreur("prive.verrou", f"le verrou désigne {verrou[:10]}, le dépôt privé est à {sha[:10]} : "
                 "`socle prive verrouiller` pour l'avancer, ou `socle prive extraire` pour y revenir", VERROU)


@controle("prive.chiffre")
def controle_chiffre(ctx, r):
    """Mode chiffré : aucun fichier privé n'est commité en clair, et un
    filtre de chiffrement couvre la zone privée."""
    if mode(ctx.projet) != "chiffre":
        return
    arbre = arbre_commite(ctx)
    for c in outils.fichiers_a(ctx.racine, arbre):
        if est_prive(c) and lisible(outils.lire_a(ctx.racine, arbre, c)):
            r.erreur("prive.chiffre", "fichier privé commité EN CLAIR : le filtre de chiffrement n'a pas tourné. "
                     "Retirer le commit avant tout push ; si c'est poussé, l'historique public l'a gardé", c)
    if outils.est_depot(ctx.racine):
        attribut = outils.git(ctx.racine, "check-attr", "filter", "--", f"{DOSSIER}/canonique.md", check=False)
        if attribut.strip().endswith(": unspecified") or not attribut.strip():
            r.erreur("prive.chiffre", f"aucun filtre de chiffrement ne couvre `{DOSSIER}/` "
                     f"(`.gitattributes` : `{DOSSIER}/** filter=…`)", ".gitattributes")
