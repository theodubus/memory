"""Les migrations du format des fichiers du projet (mémoire, politique,
garde-fous) d'une version du socle à la suivante.

Le verrou du moteur note le format (`format = N`). À la mise à jour,
l'installeur applique, dans l'ordre, chaque migration de N à la version
courante : un script, jamais un merge à la main. Une migration manquante
arrête la mise à jour au lieu de laisser un format qu'aucun contrôle ne lit.
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Callable

from socle import config, outils

# Un chemin du format 1 dans un texte : la mémoire, ou un fichier de `.socle/`
# renommé. Ce qui suit le chemin (guillemet, espace, parenthèse…) le termine.
CHEMIN_1 = re.compile(r"(?<![\w./-])(?P<pre>(?:\.\./)+|/)?(?P<chemin>memoire/[^\s\"'`)\]>,;]*|"
                      r"\.socle/(?:moteur\.lock|politique\.toml|garde-fous\.toml|"
                      r"adaptateur\.toml|prive\.lock|moteur(?=/|[\s\"'`)\]>,;]|$))[^\s\"'`)\]>,;]*)")


def traduire_texte(texte: str) -> str:
    """Les chemins du format 1 d'un texte, sous leurs noms du format 2 ; un
    lien relatif (`../memoire/…`) ou un motif ancré (`/memoire/prive/`) aussi."""
    return CHEMIN_1.sub(lambda m: (m["pre"] or "") + config.traduire(m["chemin"], vers=2), texte)


def _vers_format_2(cible: Path) -> list[str]:
    """B-0032 : les chemins passent en anglais (`memory/`, `canonical.md`,
    `requests/`, `policy.toml`, `guardrails.toml`…). Les fichiers sont
    renommés (`git mv`, l'historique les suit) ; les chemins sont traduits
    dans la configuration et dans la documentation hors mémoire. La mémoire
    n'est pas réécrite : le journal est en ajout seul, une demande répondue
    est gelée, et les anciens chemins qu'elles citent restent valides par
    alias."""
    res = []
    # Les fichiers suivis par git, et eux seuls : un fichier pas encore
    # commité se déplace à la main, sans quoi `git mv` le laisserait derrière.
    suivis = set(outils.git(cible, "ls-files", "-z", check=False).split("\0")) - {""} \
        if outils.est_depot(cible) else set()

    def deplacer(de: str, vers: str):
        a, b = cible / de, cible / vers
        if not a.exists() and not a.is_symlink():
            return
        if b.exists():
            raise RuntimeError(f"migration arrêtée : {vers} existe déjà, {de} n'y est pas déplacé — "
                               "fusionner les deux à la main, puis relancer")
        b.parent.mkdir(parents=True, exist_ok=True)
        if de in suivis:
            outils.git(cible, "mv", de, vers)
        else:
            shutil.move(str(a), str(b))

    # 1. La configuration du socle.
    for de, vers in ((".socle/moteur.lock", ".socle/engine.lock"), (".socle/politique.toml", ".socle/policy.toml"),
                     (".socle/garde-fous.toml", ".socle/guardrails.toml"),
                     (".socle/adaptateur.toml", ".socle/adapter.toml"), (".socle/prive.lock", ".socle/private.lock")):
        if (cible / de).exists():
            deplacer(de, vers)
            res.append(f"{de} → {vers}")
    if (cible / ".socle/moteur").is_dir():
        if (cible / ".socle/engine").exists():
            shutil.rmtree(cible / ".socle/engine")
        for f in sorted(x for x in suivis if x.startswith(".socle/moteur/")):
            deplacer(f, config.traduire(f, vers=2))
        if (cible / ".socle/moteur").exists():
            shutil.rmtree(cible / ".socle/moteur")
        res.append(".socle/moteur/ → .socle/engine/")

    # 2. La mémoire, fichier par fichier. Le clone du dépôt privé (mode
    # compagnon) se déplace en bloc, puis ses fichiers se renomment dedans :
    # à commiter dans le dépôt privé, puis `socle prive verrouiller`.
    memoire_1 = cible / "memoire"
    if memoire_1.is_dir():
        prive_1 = memoire_1 / "prive"
        compagnon = (prive_1 / ".git").exists()
        if compagnon:
            (cible / "memory").mkdir(exist_ok=True)
            shutil.move(str(prive_1), str(cible / "memory/private"))
            prive_2 = cible / "memory/private"
            for dossier, sous, noms in os.walk(prive_2):
                sous[:] = [s for s in sous if s != ".git"]
                for n in noms:
                    rel = str((Path(dossier) / n).relative_to(prive_2)).replace(os.sep, "/")
                    neuf = config.traduire("memoire/prive/" + rel, vers=2)[len("memory/private/"):]
                    if neuf != rel:
                        (prive_2 / neuf).parent.mkdir(parents=True, exist_ok=True)
                        outils.git(prive_2, "mv", "-k", rel, neuf)
            res.append("le dépôt privé, cloné dans memory/private/ : ses fichiers sont renommés, à commiter "
                       "dans le dépôt privé, puis `socle prive verrouiller`")
        for dossier, sous, noms in os.walk(memoire_1):
            for n in noms:
                rel = str((Path(dossier) / n).relative_to(cible)).replace(os.sep, "/")
                deplacer(rel, config.traduire(rel, vers=2))
        # L'ancien dossier ne se supprime que vide : un fichier resté là est
        # une perte, pas un reste.
        restes = [str(Path(d, n).relative_to(cible)) for d, _, noms in os.walk(memoire_1) for n in noms]
        if restes:
            raise RuntimeError("migration arrêtée : des fichiers restent dans memoire/ — " + ", ".join(restes[:5]))
        shutil.rmtree(memoire_1)
        res.append("memoire/ → memory/ (canonical.md, active.md, requests/, private/, *.answer.toml)")

    # 3. Les chemins cités par la configuration et la documentation ; ni la
    # mémoire, ni le moteur (son format décrit les deux).
    reecrits = []
    moteur = config.lire_toml(outils.lire_a(cible, None, config.FORMAT_2.lock) or "").get("engine_dir", "")
    hors = tuple(x for x in ("memory/", ".socle/engine/", moteur.rstrip("/") + "/" if moteur else "") if x)
    for f in sorted(set(outils.fichiers_courants(cible)) if outils.est_depot(cible) else []):
        if not (f in (".gitignore", ".gitattributes", ".github/CODEOWNERS") or f.startswith(".socle/")
                and f.endswith((".toml", ".lock")) or f.endswith(".md") and not f.startswith(hors)):
            continue
        p = cible / f
        if not p.is_file():
            continue
        avant = p.read_text(encoding="utf-8")
        apres = traduire_texte(avant)
        if apres != avant:
            p.write_text(apres, encoding="utf-8")
            reecrits.append(f)
    if reecrits:
        res.append(f"chemins traduits dans {len(reecrits)} fichier(s) : {', '.join(reecrits[:8])}"
                   + (" …" if len(reecrits) > 8 else ""))
    config.oublier_formats()
    return res


# Version courante du format. Une migration `MIGRATIONS[n]` fait passer un
# projet du format n au format n + 1, et rend ce qu'elle a fait.
FORMAT = 2
MIGRATIONS: dict[int, Callable[[Path], list[str]]] = {1: _vers_format_2}


def migrer(cible: Path, depuis: int, jusqua: int | None = None) -> list[str]:
    jusqua = FORMAT if jusqua is None else jusqua
    res = []
    for v in range(depuis, jusqua):
        f = MIGRATIONS.get(v)
        if f is None:
            raise RuntimeError(f"aucune migration du format {v} au format {v + 1} : mise à jour arrêtée")
        res += [f"format {v} → {v + 1} : {ligne}" for ligne in f(cible)] or [f"format {v} → {v + 1}"]
    return res
