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

import re
from dataclasses import dataclass
from pathlib import Path

from socle import config, langue, memoire, outils
from socle.contexte import controle



def dossier(racine: Path, rev: str | None = None) -> str:
    """La zone privée du projet, sous le nom de son format."""
    return config.chemins(racine, rev).prive


def fichier_verrou(racine: Path, rev: str | None = None) -> str:
    return config.chemins(racine, rev).prive_lock


def fichier_termes(racine: Path, rev: str | None = None) -> str:
    return config.chemins(racine, rev).termes

MODES = ("compagnon", "chiffre")
# La liste des termes qui ne doivent jamais paraître en public (D-0007) :
# l'agent y ajoute librement, seul l'humain en retire.
ENTETE_TERMES = memoire.ENTETE_TERMES
# La relecture humaine avant publication (D-0006) : au choix de l'humain.
RELECTURES = ("aucune", "chaque-push", "lots")
# Les couches dont le contenu nouveau peut être privé par défaut (B-0029) ; le
# chantier actif, réécrit à la main, n'a pas d'entrée à placer.
COUCHES_PRIVABLES = ("canonique", "backlog", "decisions", "journal", "demandes")
# Les entrées qu'une bascule déplace : une demande se lit là où l'humain lit,
# elle se retire et se pose à nouveau en privé.
BASCULABLES = ("F", "B", "J", "ADR")


def mode(projet: config.Projet) -> str | None:
    m = projet.pol("private", "mode")
    return str(m) if m else None


est_prive = memoire.est_prive
lisible = memoire.lisible


def depot_compagnon(racine: Path) -> Path | None:
    p = racine / dossier(racine)
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

    texte = outils.lire_a(racine, rev, fichier_verrou(racine, rev))
    if not texte:
        return None
    try:
        return str(tomllib.loads(texte).get("commit", "")) or None
    except tomllib.TOMLDecodeError:
        return None


def ecrire_verrou(racine: Path, sha: str):
    (racine / fichier_verrou(racine)).write_text(
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
        print(f"mémoire privée : pas de verrou ({fichier_verrou(racine)})")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        fichier = Path(tmp) / "cle"
        fichier.write_text(cle.strip() + "\n", encoding="utf-8")
        fichier.chmod(0o600)
        env = {**os.environ, "GIT_SSH_COMMAND": f"ssh -i {fichier} -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"}
        cible = racine / dossier(racine)
        for args in (["clone", "-q", "--no-checkout", depot, str(cible)], ["-C", str(cible), "checkout", "-q", verrou]):
            if subprocess.run(["git", *args], cwd=racine, env=env, capture_output=True).returncode != 0:
                print(f"mémoire privée : récupération impossible (étape `git {args[0] if args[0] != '-C' else 'checkout'}`)")
                return 1
    print(f"mémoire privée : récupérée au verrou {verrou[:10]}")
    return 0


def lire_prive(projet: config.Projet, rev: str | None, chemin: str) -> str | None:
    """Le texte en clair d'un fichier privé, tel qu'il était à une révision du
    dépôt public (`None` : l'arbre de travail). En mode compagnon, la
    révision publique désigne, par son verrou, un commit du dépôt privé ; en
    mode chiffré, git applique le filtre de déchiffrement s'il le peut."""
    import subprocess

    racine = projet.racine
    m = mode(projet)
    if rev is None or m not in MODES:
        return outils.lire_a(racine, None, chemin) if m in MODES else None
    if m == "compagnon":
        depot, verrou = depot_compagnon(racine), lire_verrou(racine, rev)
        if depot is None or not verrou:
            return None
        r = subprocess.run(["git", "show", f"{verrou}:{memoire.hors_zone_privee(chemin)}"], cwd=depot, capture_output=True)
    else:
        r = subprocess.run(["git", "cat-file", "--filters", f"{rev}:{chemin}"], cwd=racine, capture_output=True)
    return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else None


@dataclass
class Termes:
    liste: list[str]
    disponible: bool
    texte: str = ""


def termes(projet: config.Projet, rev: str | None = None) -> Termes:
    """La liste des termes privés : un par ligne, `#` pour un commentaire,
    `re:` devant une expression régulière. Illisible ici (chiffrée, ou le
    dépôt privé absent), elle est indisponible, jamais vide en silence."""
    m = mode(projet)
    if m is None:
        return Termes([], True)
    texte = lire_prive(projet, rev, fichier_termes(projet.racine, rev))
    if texte is None:
        dispo = (depot_compagnon(projet.racine) is not None) if m == "compagnon" else (
            rev is not None or not (projet.racine / fichier_termes(projet.racine)).is_file())
        return Termes([], dispo)
    if not texte.lstrip().startswith(ENTETE_TERMES):
        return Termes([], False)
    liste = [l.strip() for l in texte.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    return Termes(liste, True, texte)


def ajouter_terme(projet: config.Projet, terme: str) -> bool:
    """Ajoute un terme à la liste (libre : cela durcit le contrôle). Faux
    s'il y était déjà. Une liste illisible ici (chiffrée sans la clé, dépôt
    privé absent) n'est pas réécrite : elle serait écrasée (B-0044, L3)."""
    p = projet.racine / fichier_termes(projet.racine)
    actuels = termes(projet)
    if not actuels.disponible or (p.is_file() and not actuels.texte):
        raise RuntimeError(f"liste des termes privés illisible ici (`{fichier_termes(projet.racine)}`) : "
                           "le terme n'est pas ajouté, la liste serait écrasée. "
                           + acces(projet).raison)
    if terme.strip() in actuels.liste:
        return False
    texte = actuels.texte or f"{ENTETE_TERMES} — un par ligne, `re:` pour une expression régulière.\n"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texte.rstrip("\n") + "\n" + terme.strip() + "\n", encoding="utf-8")
    return True


def fuites(texte: str, liste: list[str], identifiants: bool = True) -> list[str]:
    """Ce qu'un texte public laisse fuir du privé. Le terme trouvé n'est
    jamais réécrit : la réponse ne donne que son rang dans la liste."""
    res = []
    if identifiants:
        vus = []
        for m in memoire.ID_RE.finditer(texte):
            if m["prive"] and memoire.id_valide(m["type"], m["num"]) and m.group(0) not in vus:
                vus.append(m.group(0))
        res += [f"identifiant privé `{i}`" for i in vus]
    norme = outils.sans_accents(texte).lower()
    for i, terme in enumerate(liste, 1):
        if terme.startswith("re:"):
            try:
                trouve = re.search(terme[3:], texte, re.I)
            except re.error:
                res.append(f"terme privé n°{i} : expression régulière invalide")
                continue
        else:
            t = outils.sans_accents(terme).lower()
            trouve = re.search(rf"(?<!\w){re.escape(t)}(?!\w)", norme)
        if trouve:
            res.append(f"terme privé n°{i} de la liste")
    return res


def relecture(projet: config.Projet) -> str | None:
    """Le mode de relecture avant publication choisi par l'humain, ou `None`
    s'il n'en a pas choisi."""
    r = projet.pol("private", "review")
    return str(r) if r else None


def fichier_relectures(racine: Path) -> Path:
    """Les publications relues, dans le répertoire git commun : un état
    local, comme la trace des hooks."""
    return config.chemin_trace(racine).parent / "relectures.log"


def relue(racine: Path, sha: str) -> bool:
    p = fichier_relectures(racine)
    if not p.is_file():
        return False
    return any(l.split("\t", 1)[0] == sha for l in p.read_text(encoding="utf-8").splitlines())


def noter_relecture(racine: Path, sha: str, par: str, canal: str, citation: str):
    import json
    from datetime import datetime

    p = fichier_relectures(racine)
    p.parent.mkdir(parents=True, exist_ok=True)
    quand = datetime.now().astimezone().isoformat(timespec="seconds")
    with p.open("a", encoding="utf-8") as f:
        f.write(f"{sha}\t{quand}\t{par}\t{canal}\t{json.dumps(citation, ensure_ascii=False)}\n")


def publication_refusee(projet: config.Projet, shas: list[str]) -> str | None:
    """Pourquoi pousser ces commits vers le dépôt public attend une
    relecture humaine, ou `None`."""
    r = relecture(projet)
    if mode(projet) is None or r in (None, "aucune"):
        return None
    manquants = [s for s in shas if s and not set(s) <= {"0"} and not relue(projet.racine, s)]
    if not manquants:
        return None
    return (f"relecture avant publication (politique : {r}) : {manquants[0][:10]} n'a pas été relu. Montrer à "
            "l'humain ce qui part (diff, messages de commit), puis consigner son accord avec son texte exact : "
            "`socle relu --relayed --by <nom> --quote-file <fichier>`. "
            + ("Une relecture à chaque push." if r == "chaque-push" else "Une relecture par lot de commits."))


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
            return Acces(False, f"le dépôt privé n'est pas cloné dans `{dossier(racine)}/`")
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


def memoire_privee(ctx) -> memoire.Memoire | None:
    """La mémoire privée telle qu'elle est à la tête jugée : l'arbre de
    travail, ou, à une révision, le dépôt privé au commit du verrou (mode
    compagnon) et les fichiers déchiffrés par le filtre (mode chiffré).
    `None` : elle ne se lit pas ici."""
    projet, racine = ctx.projet, ctx.racine
    if ctx.tete is None:
        return ctx.memoire if acces(projet, ctx.memoire.illisibles).disponible else None
    m = mode(projet)
    if m == "compagnon":
        depot, verrou = depot_compagnon(racine), lire_verrou(racine, ctx.tete)
        if depot is None or not verrou:
            return None
        noms = outils.git(depot, "ls-tree", "-r", "--name-only", verrou, check=False).splitlines()
        chemins = [f"{dossier(racine, ctx.tete)}/{n}" for n in noms]
    elif m == "chiffre":
        chemins = [c for c in ctx.fichiers if est_prive(c)]
    else:
        return None
    res = memoire.Memoire(racine=racine, rev=ctx.tete)
    for c in chemins:
        if memoire.couche_attendue(c) is None:
            continue
        texte = lire_prive(projet, ctx.tete, c)
        if texte is None or not lisible(texte):
            return None
        res.fichiers[c] = memoire.analyser(c, texte)
    return res


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
            r.erreur("prive.acces", f"{len(commites)} fichier(s) sous `{dossier(ctx.racine)}/` commité(s) sans mode de mémoire "
                     "privée : ils sont publics. Choisir un mode (`[private] mode` de la politique) ou les déplacer",
                     commites[0])
        return
    if m not in MODES:
        r.erreur("prive.acces", f"mode de mémoire privée « {m} » inconnu (attendu : {', '.join(MODES)})", ctx.projet.chemins.politique)
        return
    a = acces(ctx.projet, ctx.memoire.illisibles if ctx.tete is None else None)
    if not a.disponible:
        r.indisponible("prive.acces", f"mémoire privée indisponible : {a.raison}")
    rel = relecture(ctx.projet)
    if rel is None:
        r.avertir("prive.acces", "relecture avant publication non choisie (`[private] review` : "
                  f"{', '.join(RELECTURES)}) : aucune n'est exigée", ctx.projet.chemins.politique)
    elif rel not in RELECTURES:
        r.erreur("prive.acces", f"relecture « {rel} » inconnue (attendu : {', '.join(RELECTURES)})", ctx.projet.chemins.politique)


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
                     f"que `{dossier(ctx.racine)}/` clone (le retirer de l'index)", c)
    # Le verrou de la tête jugée ; en fin de tour, celui de l'arbre de
    # travail, qui sera commité.
    verrou = lire_verrou(ctx.racine, ctx.tete)
    if verrou is None:
        if commit_compagnon(ctx.racine) is None:
            # Rien n'est encore en place : c'est à l'humain (B-0034, P5).
            r.erreur("prive.verrou", "mode compagnon sans dépôt privé ni verrou : sa mise en place revient à "
                     "l'humain, `prive installer --depot <adresse du dépôt privé>`", fichier_verrou(ctx.racine))
        else:
            r.erreur("prive.verrou", "mode compagnon sans verrou : `socle prive verrouiller`",
                     fichier_verrou(ctx.racine))
        return
    sha = commit_compagnon(ctx.racine)
    if sha is None:
        r.indisponible("prive.verrou", "dépôt privé non cloné : verrou non vérifiable")
        return
    modifies = compagnon_modifie(ctx.racine)
    if modifies and ctx.etage != "ci":
        r.erreur("prive.verrou", f"{len(modifies)} changement(s) de la mémoire privée hors de tout commit du dépôt "
                 "privé : les y commiter, puis `socle prive verrouiller`", dossier(ctx.racine))
    if sha != verrou:
        r.erreur("prive.verrou", f"le verrou désigne {verrou[:10]}, le dépôt privé est à {sha[:10]} : "
                 "`socle prive verrouiller` pour l'avancer, ou `socle prive extraire` pour y revenir", fichier_verrou(ctx.racine))


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
        attribut = outils.git(ctx.racine, "check-attr", "filter", "--", ctx.projet.chemins.dans_prive(ctx.projet.chemins.canonique), check=False)
        if attribut.strip().endswith(": unspecified") or not attribut.strip():
            zone = dossier(ctx.racine)
            r.erreur("prive.chiffre", f"aucun filtre de chiffrement ne couvre `{zone}/` "
                     f"(`.gitattributes` : `{zone}/** filter=…`)", ".gitattributes")


@controle("prive.fuites")
def controle_fuites(ctx, r):
    """Aucun terme de la liste privée dans un fichier public modifié, et ni
    terme ni identifiant privé dans un message de commit. Le terme trouvé
    n'est jamais écrit : le journal de la CI est public."""
    if mode(ctx.projet) is None:
        return
    lt = termes(ctx.projet, ctx.tete)
    if not lt.disponible:
        r.indisponible("prive.fuites", "liste des termes privés illisible ici : seuls les identifiants privés "
                       "sont cherchés")
    moteur = ctx.projet.dossier_moteur.rstrip("/") + "/"
    presents = set(ctx.fichiers)
    for c in ctx.changes:
        if c not in presents or est_prive(c) or c.startswith((moteur, ctx.projet.chemins.archives + "/")):
            continue
        texte = ctx.lire(c)
        if texte is None or "\0" in texte[:4096]:
            continue
        for f in fuites(texte, lt.liste, identifiants=False):
            r.erreur("prive.fuites", f"fuite de la mémoire privée : {f}", c)
    for commit in ctx.commits:
        for f in fuites(commit["message"], lt.liste):
            r.erreur("prive.fuites", f"fuite de la mémoire privée dans le message du commit {commit['sha'][:10]} : {f}")


@controle("prive.termes", base=True)
def controle_termes(ctx, r):
    """Ajouter un terme à la liste privée est libre ; en retirer un exige une
    demande validée qui cite la liste et son empreinte nouvelle (D-0007)."""
    if mode(ctx.projet) is None:
        return
    avant, apres = termes(ctx.projet, ctx.base), termes(ctx.projet, ctx.tete)
    if not (avant.disponible and apres.disponible):
        r.indisponible("prive.termes", "liste des termes privés illisible ici : retraits non vérifiables")
        return
    retires = [x for x in avant.liste if x not in apres.liste]
    if not retires:
        return
    from socle.controles_cliquet import _valide_par

    cite = "sha256:" + outils.sha256(apres.texte)[:16]
    termes_ici = fichier_termes(ctx.racine)
    d = _valide_par(ctx, termes_ici, cite)
    if d:
        r.avertir("prive.termes", f"{len(retires)} terme(s) retiré(s), validé par {d.id}", termes_ici)
    else:
        r.erreur("prive.termes", f"{len(retires)} terme(s) retiré(s) de la liste privée sans validation humaine : "
                 f"une demande validée doit citer `{termes_ici}` et `{cite}`", termes_ici)



# --------------------------------------------------------------------------
# Couche par couche, entrée par entrée (B-0029)
# --------------------------------------------------------------------------


def couches_privees(projet: config.Projet) -> set[str]:
    """Les couches dont le contenu nouveau est privé par défaut : celles que
    la politique nomme (`[private] layers`) ; à défaut, toutes sauf les
    demandes, que `[private] requests` rend privées. Aucune sans mémoire
    privée."""
    if mode(projet) is None:
        return set()
    choix = projet.pol("private", "layers")
    if choix is None:
        return set(COUCHES_PRIVABLES[:-1]) | ({"demandes"} if projet.pol("private", "requests", defaut=False) else set())
    return {outils.cle(c) for c in choix} & set(COUCHES_PRIVABLES)


def couches_inconnues(projet: config.Projet) -> list[str]:
    """Les noms de `[private] layers` qui ne désignent aucune couche."""
    return [c for c in projet.pol("private", "layers", defaut=[]) or [] if outils.cle(c) not in COUCHES_PRIVABLES]


def basculer(projet: config.Projet, ident: str, jour: str) -> list[str]:
    """Bascule une entrée publique dans la mémoire privée : une copie privée,
    sous un identifiant privé, en reprend le titre et le texte et cite
    `depuis : <identifiant>` ; l'entrée publique garde son identifiant, pour
    que les renvois restent valides, et perd son titre et son texte. Refuse
    ce qu'elle ne sait pas déplacer sans casser un renvoi. Rend ce qu'il faut
    dire à l'humain."""
    racine, ch = projet.racine, projet.chemins
    if mode(projet) is None:
        raise ValueError("aucune mémoire privée dans la politique (`[private] mode`) : rien où basculer")
    a = acces(projet)
    if not a.disponible:
        raise ValueError(f"mémoire privée indisponible : {a.raison}")
    mem = memoire.Memoire.charger(racine)
    e = mem.entree(ident)
    if e is None:
        raise ValueError(f"`{ident}` ne désigne aucune entrée de la mémoire")
    if e.prive or e.basculee:
        raise ValueError(f"`{ident}` est déjà privée")
    if e.type == "D":
        raise ValueError("une demande se lit là où l'humain lit : la retirer (`retirée : <raison>` dans ses "
                         "métadonnées) et en poser une privée (`socle new request \"…\" --private`)")
    if e.type not in BASCULABLES:
        raise ValueError(f"`{ident}` : seuls un fait, un sujet, une entrée de journal ou une décision se basculent")
    if e.archivee:
        raise ValueError(f"`{ident}` est archivée dans `{e.parent}` : c'est cette entrée de journal qui se bascule")
    enfants = [x.id for x in mem.entrees() if x.parent == ident]
    if enfants:
        raise ValueError(f"`{ident}` archive {', '.join(enfants)}, que d'autres entrées citent peut-être : "
                         "leurs renvois publics ne survivraient pas à la bascule")
    nouvel = mem.prochain_id(e.type, prive=True, date=e.id[2:12] if e.type == "J" else None)
    lg = langue.du_projet(projet)
    copie = _copie_privee(e, nouvel, lg)
    fichier = mem.fichiers[e.fichier]
    if e.type == "ADR":
        nom = e.fichier.rsplit("/", 1)[-1]
        prive_rel = ch.dans_prive(f"{ch.decisions}/{nouvel}{nom[len(ident):]}")
        _ecrire(racine / prive_rel, f"{langue.entete_fichier('decisions', 'privee', lg)}\n{copie}\n")
        public_rel = f"{ch.decisions}/{ident}-basculee.md"
        _ecrire(racine / public_rel, f"{langue.entete_fichier('decisions', 'publique', lg)}\n{_pierre(e, jour, lg)}\n")
        (racine / e.fichier).unlink()
    else:
        prive_rel = ch.dans_prive(e.fichier)
        cible = racine / prive_rel
        if not cible.is_file():
            titre = fichier.texte.split("\n# ", 1)[1].split("\n", 1)[0] if "\n# " in fichier.texte else fichier.couche
            _ecrire(cible, f"{langue.entete_fichier(fichier.couche, 'privee', lg)}\n# {titre}\n")
        cible.write_text(cible.read_text(encoding="utf-8").rstrip("\n") + "\n\n" + copie + "\n", encoding="utf-8")
        public_rel = e.fichier
        texte = (racine / e.fichier).read_text(encoding="utf-8")
        if e.texte not in texte:
            raise ValueError(f"`{ident}` : son texte ne se retrouve pas tel quel dans {e.fichier}")
        (racine / e.fichier).write_text(texte.replace(e.texte, _pierre(e, jour, lg), 1), encoding="utf-8")
    res = [f"{ident} → {nouvel} : son titre et son texte sont dans {prive_rel}",
           f"en public, {public_rel} ne garde de {ident} que l'identifiant : les renvois restent valides",
           "l'historique public garde l'ancien texte : seule une réécriture de l'historique, publiée en "
           "écrasant la branche, l'efface ; c'est à l'humain de la faire : le lui dire",
           "un nom qui doit rester privé partout s'ajoute à la liste des termes : `socle prive terme <terme>`"]
    if mode(projet) == "compagnon":
        res.append("mode compagnon : commiter la copie dans le dépôt privé, puis `socle prive verrouiller`")
    return res


def _copie_privee(e: memoire.Entree, nouvel: str, lg: str) -> str:
    """L'entrée sous son identifiant privé, qui cite celle qu'elle reprend."""
    lignes = e.texte.splitlines()
    lignes[0] = lignes[0].replace(e.id, nouvel, 1)
    j = 1
    while j < len(lignes) and not lignes[j].strip():
        j += 1
    if j < len(lignes) and lignes[j].lstrip().startswith(">"):
        while j + 1 < len(lignes) and lignes[j + 1].lstrip().startswith(">"):
            j += 1
        lignes[j] = lignes[j].rstrip() + " · " + langue.meta(lg, depuis=e.id)[2:]
    else:
        lignes[1:1] = ["", langue.meta(lg, depuis=e.id)]
    return "\n".join(lignes)


def _pierre(e: memoire.Entree, jour: str, lg: str) -> str:
    """Ce qui reste en public d'une entrée basculée."""
    return (f"{'#' * e.niveau} {e.id} — {langue.mot(langue.TEXTES, 'titre-basculee', lg)}\n\n"
            f"{langue.meta(lg, basculee=jour)}\n\n{langue.mot(langue.TEXTES, 'texte-basculee', lg)}")


def _ecrire(p: Path, texte: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texte, encoding="utf-8")


def adresse_ssh(adresse: str) -> str:
    """L'adresse SSH d'un dépôt, que la CI clone avec la clé de déploiement :
    `https://hote/o/r` devient `git@hote:o/r.git` ; une autre forme reste."""
    m = re.match(r"^https?://(?P<hote>[\w.-]+)/(?P<o>[\w.-]+)/(?P<r>[\w.-]+?)(?:\.git)?/?$", adresse)
    return f"git@{m['hote']}:{m['o']}/{m['r']}.git" if m else adresse


def installer_compagnon(projet: config.Projet, adresse: str) -> tuple[int, list[str]]:
    """Le mode compagnon mis en place d'un geste (B-0034, P5) : le dépôt privé
    cloné, son premier commit poussé s'il est vide, le verrou écrit, une clé
    de déploiement créée ; puis ce qui reste à faire sur GitHub, avec les
    liens. Réservé à l'humain : il pousse vers le dépôt privé et crée une clé."""
    import shutil
    import subprocess

    from socle import liens

    racine = projet.racine
    if mode(projet) != "compagnon":
        return 1, ["refus : la politique ne choisit pas le mode compagnon — relancer l'installation avec "
                   "`--private compagnon`, qui l'écrit"]
    rel = dossier(racine)
    zone = racine / rel
    res = []
    if depot_compagnon(racine) is None:
        if zone.exists() and any(zone.iterdir()):
            return 1, [f"refus : {rel}/ existe et n'est pas un clone : le déplacer, puis relancer"]
        r = subprocess.run(["git", "clone", "-q", adresse, str(zone)], cwd=racine, capture_output=True, text=True)
        if r.returncode != 0:
            return 1, [f"refus : clone impossible ({r.stderr.strip()[-300:] or 'git clone a échoué'})"]
        res.append(f"dépôt privé cloné dans {rel}/")
    else:
        res.append(f"dépôt privé déjà cloné dans {rel}/")
    p = racine / ".gitignore"
    texte = p.read_text(encoding="utf-8") if p.is_file() else ""
    if f"{rel}/" not in texte.splitlines():
        p.write_text(texte.rstrip("\n") + f"\n# Le clone du dépôt privé (mémoire privée)\n{rel}/\n", encoding="utf-8")
        res.append(f"{rel}/ ignoré par le dépôt public (.gitignore)")
    if not outils.a_des_commits(zone):
        (zone / "README.md").write_text(
            f"# Mémoire privée de {racine.name}\n\nLe socle y range la mémoire privée du projet, au même format que "
            "la mémoire publique. Ce dépôt reste privé.\n", encoding="utf-8")
        for args in (["add", "README.md"], ["commit", "-q", "-m", "Mémoire privée : premier commit"]):
            r = subprocess.run(["git", *args], cwd=zone, capture_output=True, text=True)
            if r.returncode != 0:
                return 1, res + [f"refus : premier commit du dépôt privé impossible ({r.stderr.strip()[-300:]})"]
        res.append("premier commit du dépôt privé")
    sha = commit_compagnon(racine)
    # La CI clone le dépôt privé au commit du verrou : il doit y être poussé.
    r = subprocess.run(["git", "push", "-q", "-u", "origin", "HEAD"], cwd=zone, capture_output=True, text=True)
    if r.returncode != 0:
        res.append(f"!! dépôt privé non poussé ({r.stderr.strip()[-200:]}) : le pousser, sans quoi la CI ne "
                   "trouvera pas le commit du verrou")
    else:
        res.append("dépôt privé poussé")
    ecrire_verrou(racine, sha)
    res.append(f"verrou : {sha[:10]} ({fichier_verrou(racine)})")

    cle = config.chemin_trace(racine).parent / "prive-deploiement"
    if not cle.is_file():
        cle.parent.mkdir(parents=True, exist_ok=True)
        if shutil.which("ssh-keygen"):
            r = subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", f"socle CI {racine.name}",
                                "-f", str(cle)], capture_output=True, text=True)
            if r.returncode != 0:
                res.append(f"!! clé de déploiement non créée ({r.stderr.strip()[-200:]})")
        else:
            res.append(f"!! ssh-keygen absent : créer la clé à la main, `ssh-keygen -t ed25519 -N \"\" -f {cle}`")
    if cle.is_file():
        res.append(f"clé de déploiement : {cle} (hors du dépôt, jamais commitée)")

    res += [""] + gestes_github(adresse, liens.url_depot(projet), cle)
    res += ["", "Ensuite :",
            f"  - effacer la clé privée une fois le secret posé : rm {cle}",
            f"  - commiter puis pousser : git add {fichier_verrou(racine)} .gitignore && "
            "git commit -m \"Mémoire privée : le dépôt compagnon\" && git push"]
    return 0, res


def gestes_github(adresse: str, web_public: str | None, cle: Path) -> list[str]:
    """Les deux gestes qui restent à l'humain sur GitHub, avec les liens des
    pages où les faire quand les dépôts y sont, et les commandes `gh`."""
    from socle import liens

    ssh = adresse_ssh(adresse)
    web_prive = liens.depuis_distant(adresse)
    github = (web_prive or "").startswith("https://github.com/")
    res = ["Sur GitHub, deux gestes :",
           "  1. la clé publique en clé de déploiement du dépôt privé, en lecture seule"
           + (f" : {web_prive}/settings/keys/new" if github else ""),
           f"     (le contenu de {cle}.pub)",
           "  2. deux secrets du dépôt public" + (f" : {web_public}/settings/secrets/actions/new"
                                                  if web_public and github else ""),
           f"     SOCLE_PRIVE_DEPOT = {ssh}",
           f"     SOCLE_PRIVE_CLE   = le contenu de {cle}"]
    if github:
        depot = web_prive.removeprefix("https://github.com/")
        res += ["  Ou, avec gh :",
                f"     gh repo deploy-key add {cle}.pub --repo {depot} --title \"socle CI\"",
                f"     gh secret set SOCLE_PRIVE_DEPOT --body \"{ssh}\"",
                f"     gh secret set SOCLE_PRIVE_CLE < {cle}"]
    return res
