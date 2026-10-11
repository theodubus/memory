"""Les migrations du format des fichiers du projet (mémoire, politique,
garde-fous) d'une version du socle à la suivante.

Le verrou du moteur note le format (`format = N`). À la mise à jour,
l'installeur applique, dans l'ordre, chaque migration de N à la version
courante : un script, jamais un merge à la main. Une migration manquante
arrête la mise à jour au lieu de laisser un format qu'aucun contrôle ne lit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

# Version courante du format. Une migration `MIGRATIONS[n]` fait passer un
# projet du format n au format n + 1, et rend ce qu'elle a fait.
FORMAT = 1
MIGRATIONS: dict[int, Callable[[Path], list[str]]] = {}


def migrer(cible: Path, depuis: int, jusqua: int | None = None) -> list[str]:
    jusqua = FORMAT if jusqua is None else jusqua
    res = []
    for v in range(depuis, jusqua):
        f = MIGRATIONS.get(v)
        if f is None:
            raise RuntimeError(f"aucune migration du format {v} au format {v + 1} : mise à jour arrêtée")
        res += [f"format {v} → {v + 1} : {ligne}" for ligne in f(cible)] or [f"format {v} → {v + 1}"]
    return res
