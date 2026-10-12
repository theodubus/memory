"""Outils communs : git, motifs de chemins, texte.

Tout passe par git plutôt que par le système de fichiers quand une question
porte sur l'historique : l'état dérivé et les contrôles « ajout seul » n'ont
de sens que comparés à une révision, jamais à un souvenir.
"""

from __future__ import annotations

import codecs
import hashlib
import os
import re
import subprocess
import unicodedata
from functools import lru_cache
from pathlib import Path

# L'arbre vide de git : sert de base quand il n'y en a pas (premier commit,
# dépôt neuf), pour que « tout est ajouté » se calcule comme un diff ordinaire.
ARBRE_VIDE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


class ErreurGit(RuntimeError):
    pass


def git(racine: Path, *args: str, check: bool = True, entree: str | None = None) -> str:
    r = subprocess.run(
        ["git", *args],
        cwd=racine,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        input=entree,
    )
    if check and r.returncode != 0:
        raise ErreurGit(f"git {' '.join(args)} : {r.stderr.strip() or r.stdout.strip()}")
    return r.stdout


def git_reussit(racine: Path, *args: str) -> bool:
    r = subprocess.run(["git", *args], cwd=racine, capture_output=True)
    return r.returncode == 0


def trouver_racine(depart: Path | None = None) -> Path:
    """La racine du projet : celle du dépôt git, sinon le premier parent qui
    porte un `.socle/`."""
    depart = (depart or Path.cwd()).resolve()
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=depart, capture_output=True, text=True
    )
    if r.returncode == 0 and r.stdout.strip():
        return Path(r.stdout.strip())
    for p in [depart, *depart.parents]:
        if (p / ".socle").is_dir():
            return p
    return depart


def est_depot(racine: Path) -> bool:
    return git_reussit(racine, "rev-parse", "--git-dir")


def a_des_commits(racine: Path) -> bool:
    return git_reussit(racine, "rev-parse", "--verify", "--quiet", "HEAD^{commit}")


def rev_existe(racine: Path, rev: str) -> bool:
    return git_reussit(racine, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")


def objet_existe(racine: Path, sha: str) -> bool:
    return git_reussit(racine, "cat-file", "-e", f"{sha}^{{commit}}")


def resoudre(racine: Path, rev: str) -> str:
    return git(racine, "rev-parse", f"{rev}^{{commit}}").strip()


def fichiers_courants(racine: Path) -> list[str]:
    """Fichiers suivis et non suivis non ignorés, tels qu'ils sont sur disque."""
    if not est_depot(racine):
        return sorted(
            str(p.relative_to(racine)).replace(os.sep, "/")
            for p in racine.rglob("*")
            if p.is_file() and ".git" not in p.parts
        )
    sortie = git(racine, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    vus = []
    for nom in sortie.split("\0"):
        if nom and (racine / nom).is_file():
            vus.append(nom)
    return sorted(set(vus))


def fichiers_a(racine: Path, rev: str | None) -> list[str]:
    if rev is None or rev == ARBRE_VIDE:
        return []
    sortie = git(racine, "ls-tree", "-r", "-z", "--name-only", rev)
    return [n for n in sortie.split("\0") if n]


def lire_a(racine: Path, rev: str | None, chemin: str) -> str | None:
    """Le contenu d'un fichier à une révision ; `None` s'il n'y existe pas.
    `rev=None` veut dire « l'arbre de travail »."""
    if rev is None:
        p = racine / chemin
        if not p.is_file():
            return None
        return p.read_text(encoding="utf-8", errors="replace")
    if rev == ARBRE_VIDE:
        return None
    r = subprocess.run(
        ["git", "show", f"{rev}:{chemin}"], cwd=racine, capture_output=True
    )
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", errors="replace")


def fichiers_changes(racine: Path, base: str | None, tete: str | None = None) -> list[str]:
    """Chemins changés entre `base` et `tete`. `tete=None` : l'arbre de
    travail, non suivis compris."""
    base = base or ARBRE_VIDE
    if tete is None:
        if a_des_commits(racine):
            sortie = git(racine, "diff", "--name-only", "--no-renames", "-z", base)
        else:
            sortie = ""
        noms = {n for n in sortie.split("\0") if n}
        autres = git(racine, "ls-files", "-z", "--others", "--exclude-standard")
        noms |= {n for n in autres.split("\0") if n}
        if not a_des_commits(racine):
            indexes = git(racine, "ls-files", "-z", "--cached")
            noms |= {n for n in indexes.split("\0") if n}
        return sorted(noms)
    sortie = git(racine, "diff", "--name-only", "--no-renames", "-z", base, tete)
    return sorted(n for n in sortie.split("\0") if n)


HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", re.M)


def lignes_changees(racine: Path, base: str | None, tete: str | None, chemin: str) -> set[int] | None:
    """Les lignes de `chemin`, dans la tête, ajoutées ou modifiées depuis
    `base` ; une suppression marque la ligne qui la suit. `None` : le fichier
    n'existait pas dans la base, tout y est nouveau."""
    if not base or lire_a(racine, base, chemin) is None:
        return None
    args = ["diff", "-U0", "--no-color", "--no-ext-diff", base] + ([tete] if tete else []) + ["--", chemin]
    res = set()
    for m in HUNK.finditer(git(racine, *args, check=False)):
        debut, n = int(m.group(1)), int(m.group(2) or 1)
        res |= set(range(debut, debut + n)) if n else {debut + 1}
    return res


def branche_par_defaut(racine: Path) -> str | None:
    """`origin/main`, `origin/master`, ou ce que pointe `origin/HEAD`."""
    r = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"],
        cwd=racine, capture_output=True, text=True,
    )
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip().removeprefix("refs/remotes/")
    for nom in ("origin/main", "origin/master", "main", "master"):
        if rev_existe(racine, nom):
            return nom
    # Un dépôt neuf n'a parfois encore que sa branche de travail : ce qui est
    # déjà poussé sert alors de base, plutôt que pas de base du tout.
    r = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
        cwd=racine, capture_output=True, text=True,
    )
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    return None


def base_de_travail(racine: Path) -> str | None:
    """La base contre laquelle l'agent et les hooks git comparent : le point
    de divergence avec la branche par défaut. `None` si rien ne s'y prête."""
    if not a_des_commits(racine):
        return None
    defaut = branche_par_defaut(racine)
    if defaut is None:
        return None
    r = subprocess.run(
        ["git", "merge-base", "HEAD", defaut], cwd=racine, capture_output=True, text=True
    )
    if r.returncode != 0 or not r.stdout.strip():
        return None
    # Égale à HEAD (branche neuve, ou tout est déjà poussé), elle reste la
    # bonne base : le travail en cours est dans l'arbre, comparé à elle.
    return r.stdout.strip()


def commits(racine: Path, base: str | None, tete: str = "HEAD") -> list[dict]:
    """Les commits de `base..tete`, du plus ancien au plus récent."""
    plage = tete if base in (None, ARBRE_VIDE) else f"{base}..{tete}"
    sortie = git(racine, "log", "--reverse", "--format=%H%x00%P%x00%B%x1e", plage)
    res = []
    for bloc in sortie.split("\x1e"):
        bloc = bloc.strip("\n")
        if not bloc:
            continue
        sha, parents, message = bloc.split("\0", 2)
        res.append({"sha": sha, "parents": parents.split(), "message": message})
    return res


TRAILER = re.compile(r"^([A-Za-z][A-Za-z0-9-]*)\s*:\s*(.*\S)\s*$")


def trailers(message: str) -> dict[str, list[str]]:
    """Les trailers du dernier paragraphe d'un message de commit, clés en
    minuscules."""
    paragraphes = [p for p in re.split(r"\n\s*\n", message.strip()) if p.strip()]
    if len(paragraphes) < 2:
        return {}
    res: dict[str, list[str]] = {}
    for ligne in paragraphes[-1].splitlines():
        m = TRAILER.match(ligne)
        if m:
            res.setdefault(m.group(1).lower(), []).append(m.group(2))
    return res


@lru_cache(maxsize=512)
def motif_vers_regex(motif: str) -> re.Pattern:
    """Motif de chemin à la gitignore, relatif à la racine : `*` ne traverse pas
    `/`, `**/` traverse zéro ou plusieurs répertoires, `**` final prend tout."""
    i, n, res = 0, len(motif), []
    while i < n:
        c = motif[i]
        if motif.startswith("**/", i):
            res.append("(?:.*/)?")
            i += 3
        elif motif.startswith("**", i):
            res.append(".*")
            i += 2
        elif c == "*":
            res.append("[^/]*")
            i += 1
        elif c == "?":
            res.append("[^/]")
            i += 1
        else:
            res.append(re.escape(c))
            i += 1
    return re.compile("^" + "".join(res) + "$")


def correspond(chemin: str, motifs) -> bool:
    if isinstance(motifs, str):
        motifs = [motifs]
    return any(motif_vers_regex(m).match(chemin) for m in motifs)


def filtrer(chemins, motifs, exclus=()) -> list[str]:
    return [c for c in chemins if correspond(c, motifs) and not correspond(c, exclus)]


def sans_accents(texte: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", texte) if unicodedata.category(c) != "Mn"
    )


def cle(texte: str) -> str:
    """Forme canonique d'un mot-clé : minuscules, sans accents, espaces en tirets."""
    return re.sub(r"\s+", "-", sans_accents(texte).strip().lower())


def sha256(donnees: bytes | str) -> str:
    if isinstance(donnees, str):
        donnees = donnees.encode("utf-8")
    return hashlib.sha256(donnees).hexdigest()


def empreinte_fichier(chemin: Path) -> str:
    return sha256(chemin.read_bytes())


def est_texte(chemin: Path, limite: int = 2_000_000) -> bool:
    try:
        if chemin.stat().st_size > limite:
            return False
        with chemin.open("rb") as f:
            debut = f.read(4096)
        if b"\0" in debut:
            return False
        # Décodeur incrémental : 4096 octets peuvent couper un caractère en
        # deux, ce qui n'en fait pas un fichier binaire.
        codecs.getincrementaldecoder("utf-8")().decode(debut, final=False)
        return True
    except (OSError, UnicodeDecodeError):
        return False
