"""Lance la suite de tests de l'atelier sur plusieurs cœurs (B-0257, T-0044).

`python3 -m unittest discover` lance les fichiers de tests l'un après
l'autre, sur un seul cœur : `verify --fast` y passait près de douze
minutes. Ce lanceur lance chaque fichier `tests/**/test_*.py` dans son
propre processus, `python3 -m unittest tests.<module> -q`, depuis la
racine et avec l'environnement hérité (`SOCLE_RAPIDE` compris, que pose
`verify --fast`), autant à la fois que de cœurs. Les plus gros fichiers
partent d'abord : la taille tient lieu de durée attendue.

Il imprime la sortie de chaque module en échec, puis une ligne de bilan :
modules, échecs, tests, durée au mur et les plus longs. Il rend 1 si un
module échoue ou ne se lance pas, ou s'il ne trouve aucun fichier de
tests ; 0 sinon. Bibliothèque standard seule (ADR-0001).

    python3 tests/parallele.py            # depuis la racine du dépôt
    python3 tests/parallele.py -j 2       # deux modules à la fois
"""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = "tests"
MOTIF = "test_*.py"
# Les plus longs que nomme le bilan.
PLUS_LONGS = 5


@dataclass
class Resultat:
    module: str
    code: int
    duree: float
    sortie: str

    @property
    def echoue(self) -> bool:
        return self.code != 0


def modules(racine: Path) -> list[str]:
    """Les modules de tests sous `racine/tests`, à la manière de `tests.<module>`,
    les plus gros fichiers d'abord, puis par nom : l'ordre est stable."""
    dossier = racine / DOSSIER
    fichiers = [f for f in dossier.rglob(MOTIF) if f.is_file()]
    fichiers.sort(key=lambda f: (-f.stat().st_size, f.as_posix()))
    return [".".join(f.relative_to(racine).with_suffix("").parts) for f in fichiers]


def lancer(racine: Path, module: str) -> Resultat:
    """Un module de tests dans son propre processus, depuis la racine, avec
    l'environnement hérité. Un processus qui ne démarre pas compte en échec."""
    debut = time.monotonic()
    try:
        p = subprocess.run([sys.executable, "-m", "unittest", module, "-q"], cwd=racine,
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, encoding="utf-8", errors="replace")
        code, sortie = p.returncode, p.stdout
    except OSError as e:
        code, sortie = -1, f"le module ne se lance pas : {e}"
    return Resultat(module, code, time.monotonic() - debut, sortie)


def executer(racine: Path, fils: int) -> tuple[list[Resultat], float]:
    """Tous les modules, `fils` à la fois ; les résultats dans l'ordre des
    noms, et la durée au mur."""
    noms = modules(racine)
    debut = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=fils) as pool:
        resultats = list(pool.map(lambda m: lancer(racine, m), noms))
    return sorted(resultats, key=lambda r: r.module), time.monotonic() - debut


def _court(r: Resultat) -> str:
    return r.module.rsplit(".", 1)[-1]


def _compte(sortie: str) -> tuple[int, int]:
    """Les tests lancés et sautés que dit le résumé de `unittest`, ses
    dernières lignes : ce qu'un test imprime avant ne compte pas."""
    lances = re.findall(r"^Ran (\d+) tests? in ", sortie, re.M)
    fin = re.findall(r"^(?:OK|FAILED)\b.*$", sortie, re.M)
    sautes = re.search(r"\bskipped=(\d+)", fin[-1]) if fin else None
    return (int(lances[-1]) if lances else 0), (int(sautes.group(1)) if sautes else 0)


def bilan(resultats: list[Resultat], mur: float, fils: int) -> str:
    """La ligne de bilan : modules, ceux en échec, tests lancés et sautés,
    durée au mur, et les plus longs."""
    echecs = [_court(r) for r in resultats if r.echoue]
    comptes = [_compte(r.sortie) for r in resultats]
    longs = sorted(resultats, key=lambda r: -r.duree)[:PLUS_LONGS]
    texte = (f"modules : {len(resultats)} · en échec : {len(echecs)}"
             + (f" ({', '.join(echecs)})" if echecs else "")
             + f" · tests : {sum(c[0] for c in comptes)} (sautés : {sum(c[1] for c in comptes)})"
             + f" · mur : {mur:.0f} s sur {fils} fils")
    if longs:
        texte += " · les plus longs : " + ", ".join(f"{_court(r)} {r.duree:.0f} s" for r in longs)
    return texte


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lance chaque fichier de tests dans son processus, "
                                                 "autant à la fois que de cœurs.")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 1,
                        help="modules lancés à la fois (par défaut : le nombre de cœurs)")
    parser.add_argument("--root", type=Path, default=RACINE,
                        help="la racine qui contient le dossier `tests` (par défaut : celle de ce dépôt)")
    args = parser.parse_args(argv)
    if args.jobs < 1:
        parser.error(f"-j attend un entier positif, pas {args.jobs}")
    racine = args.root.resolve()
    if not modules(racine):
        print(f"aucun fichier {DOSSIER}/**/{MOTIF} sous {racine} : rien à lancer", file=sys.stderr)
        return 1
    resultats, mur = executer(racine, args.jobs)
    for r in resultats:
        if r.echoue:
            print(f"=== {r.module} : échec (code {r.code}, {r.duree:.0f} s) ===")
            print(r.sortie.rstrip())
            print()
    print(bilan(resultats, mur, args.jobs))
    return 1 if any(r.echoue for r in resultats) else 0


if __name__ == "__main__":
    sys.exit(main())
