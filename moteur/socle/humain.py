"""Ce qui revient à l'humain : les décisions qu'il doit prendre et les actions
que lui seul peut faire.

Trois sources, toutes dérivées, rien de recopié :
- les demandes en attente de réponse (décisions) ;
- les entrées du backlog marquées `pour : humain` (actions déclarées : un
  réglage de GitHub, un fichier à fournir, une action que le hook refuse à
  l'agent) ;
- ce qui se calcule : les branches distantes que la branche par défaut
  contient en entier, donc supprimables sans rien perdre — une action
  distante que le hook refuse à l'agent (repris de `chess:tools/etat.sh`).

La liste sert deux fois : dans l'état dérivé au démarrage, et dans le récap
que le hook de fin de tour exige quand l'agent a agi (ADR-0007).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from socle import config, demandes, memoire, outils

MARQUEUR_RECAP = r"(?im)^[\W_]*pour toi\s*:"


@dataclass
class Element:
    genre: str  # « décision » ou « action »
    quoi: str


def branches_a_supprimer(projet: config.Projet) -> list[str]:
    """Les branches distantes que la branche par défaut contient en entier :
    jamais la branche par défaut, ni la branche de travail, ni celles que la
    politique garde (`[human] keep_branches`). Calculé sur le dernier fetch."""
    racine = projet.racine
    defaut = outils.branche_par_defaut(racine)
    if not defaut or not defaut.startswith("origin/"):
        return []
    courante = outils.git(racine, "rev-parse", "--abbrev-ref", "HEAD", check=False).strip()
    garder = projet.pol("human", "keep_branches", defaut=[]) or []
    res = []
    refs = outils.git(racine, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin", check=False)
    for ref in refs.split():
        nom = ref.removeprefix("origin/")
        if ref in ("origin", "origin/HEAD", defaut) or nom == courante or outils.correspond(nom, garder):
            continue
        absents = outils.git(racine, "rev-list", "--count", f"{defaut}..{ref}", check=False).strip()
        if absents == "0":
            res.append(nom)
    return sorted(res)


def a_faire(projet: config.Projet) -> list[Element]:
    res = []
    for d in demandes.toutes(projet.racine):
        if d.reponse is None and d.statut == "en attente" and d.entree:
            res.append(Element("décision", f"{d.id} — {d.entree.titre}"))
    mem = memoire.Memoire.charger(projet.racine)
    for e in mem.entrees("B"):
        if e.archivee or e.statut in memoire.BACKLOG_CLOS:
            continue
        if outils.cle(memoire.nettoyer(e.meta.get("pour", ""))) == "humain":
            res.append(Element("action", f"{e.id} — {e.titre}"))
    for b in branches_a_supprimer(projet):
        res.append(Element("action", f"supprimer la branche distante `{b}`, déjà contenue dans la branche par défaut"))
    return res


def texte(elements: list[Element]) -> list[str]:
    if not elements:
        return ["ce qui revient à l'humain : rien"]
    lignes = [f"ce qui revient à l'humain : {len(elements)}"]
    for e in elements:
        lignes.append(f"  {e.genre} : {e.quoi}")
    return lignes


def dernier_message(transcript: Path) -> str | None:
    """Le texte du dernier message de l'agent, lu dans le transcript JSONL de
    Claude Code. `None` si illisible : le format appartient à l'agent, le
    moteur ne fait que le lire."""
    try:
        lignes = transcript.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for ligne in reversed(lignes):
        try:
            obj = json.loads(ligne)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "assistant":
            continue
        contenu = (obj.get("message") or {}).get("content")
        if isinstance(contenu, str) and contenu.strip():
            return contenu
        if isinstance(contenu, list):
            textes = [b.get("text", "") for b in contenu if isinstance(b, dict) and b.get("type") == "text"]
            if any(t.strip() for t in textes):
                return "\n".join(textes)
    return None


def a_un_recap(projet: config.Projet, message: str) -> bool:
    motif = projet.pol("human", "recap_marker", defaut=MARQUEUR_RECAP)
    return bool(re.search(motif, message))
