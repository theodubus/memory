"""Le contrat `verify` : les capacités de l'adaptateur, puis les contrôles du
socle, un seul code de sortie.

Toutes les étapes s'exécutent même après un échec. Une étape qui échoue
rapporte sa sortie — la fin, pas un extrait choisi : c'est le moment où on en
a besoin, et la tronquer oblige à relancer.
"""

from __future__ import annotations

import os
import subprocess

from socle import config
from socle.rapport import Rapport

ORDRE = ("format", "lint", "build", "tests")
LIGNES_SORTIE = 120


def etapes(projet: config.Projet, rapide: bool) -> list[tuple[str, dict]]:
    caps = projet.adaptateur.get("capabilities", {})
    res = []
    for nom in ORDRE:
        c = caps.get(nom)
        if c is None:
            continue
        res.append((nom, c))
    for extra in projet.adaptateur.get("steps", []) or []:
        res.append((extra.get("name", "étape"), extra))
    if rapide:
        res = [(n, c) for n, c in res if c.get("fast", False) or "command" not in c]
    return res


def executer_etapes(projet: config.Projet, rapide: bool, rapport: Rapport, flux=None):
    env = dict(os.environ)
    env.setdefault("LC_ALL", "C.UTF-8")
    for nom, c in etapes(projet, rapide):
        ident = f"verify.{nom}"
        rapport.execute(ident)
        if "command" not in c:
            rapport.indisponible(ident, f"capacité absente : {c.get('absent', '?')} — remplacement : {c.get('replacement', '?')}")
            continue
        if flux:
            print(f"  … {ident} : {c['command']}", file=flux, flush=True)
        try:
            p = subprocess.run(c["command"], shell=True, cwd=projet.racine, capture_output=True,
                               text=True, encoding="utf-8", errors="replace", env=env,
                               timeout=c.get("timeout", 3600))
        except subprocess.TimeoutExpired:
            rapport.erreur(ident, f"délai dépassé : {c['command']}")
            continue
        if p.returncode != 0:
            sortie = (p.stdout + p.stderr).rstrip().splitlines()
            queue = "\n        ".join(sortie[-LIGNES_SORTIE:])
            rapport.erreur(ident, f"`{c['command']}` a rendu {p.returncode}\n        {queue}")
