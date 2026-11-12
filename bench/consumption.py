"""La consommation d'une session qui orchestre (B-0173), lue dans ses transcriptions.

Les transcriptions de Claude Code sont des fichiers JSONL : une conversation
principale `<id>.jsonl`, et ses sous-agents sous `<id>/subagents/*.jsonl`.
Chaque réponse du modèle porte `message.usage` ; une réponse découpée en
plusieurs blocs répète le même `requestId` et le même usage : un appel se
compte une fois. L'outil n'imprime que des agrégats, jamais un texte de la
conversation.

Le coût pondéré ramène les catégories de jetons à de l'entrée non cachée.
Les poids sont une hypothèse, celle du tarif public : lecture de cache 0,1 ;
écriture de cache 1,25 sur cinq minutes, 2 sur une heure ; sortie 5 ;
entrée 1. Ce qu'en fait la limite d'usage n'est pas publié : `--point`
donne des relevés de la fenêtre de cinq heures, et l'outil en déduit ce
que vaut un point, et le poids de la lecture qui les explique le mieux.

    python3 bench/consumption.py ~/.claude/projects/<projet> --day 2026-11-12 \\
        --point 2026-11-12T18:07:03Z,0.00 --point 2026-11-12T18:07:25Z,0.39
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

CINQ_MINUTES = 300
UNE_HEURE = 3600
CINQ_HEURES = 5 * UNE_HEURE


@dataclass(frozen=True)
class Poids:
    """Le poids de chaque catégorie de jetons, en jetons d'entrée non cachée."""

    entree: float = 1.0
    ecriture_5m: float = 1.25
    ecriture_1h: float = 2.0
    lecture: float = 0.1
    sortie: float = 5.0


@dataclass
class Appel:
    horodatage: datetime
    modele: str
    entree: int
    ecriture_5m: int
    ecriture_1h: int
    lecture: int
    sortie: int

    @property
    def contexte(self) -> int:
        """Les jetons que l'appel a relus ou écrits : la taille de la conversation."""
        return self.entree + self.ecriture_5m + self.ecriture_1h + self.lecture


@dataclass
class Conversation:
    nom: str
    sous_agent: bool
    appels: list[Appel] = field(default_factory=list)
    # compactages : horodatage, déclencheur, jetons avant et après, durée, octets du résumé
    compactages: list[dict] = field(default_factory=list)
    # refus d'usage : horodatage, type de fenêtre, fin de la fenêtre
    limites: list[dict] = field(default_factory=list)
    # ce que le socle injecte : horodatage, nature (SessionStart:resume…, refus), octets
    injections: list[dict] = field(default_factory=list)


def _date(texte: str) -> datetime:
    return datetime.fromisoformat(texte.replace("Z", "+00:00"))


def _texte(contenu) -> str:
    if isinstance(contenu, str):
        return contenu
    if isinstance(contenu, list):
        return "".join(b.get("text", "") for b in contenu if isinstance(b, dict))
    return ""


def _commande_socle(outil: str | None, entree: dict) -> str | None:
    """La nature de ce qu'un appel d'outil rapporte du socle, ou None : une
    commande `socle <sous-commande>`, ou la relecture d'une sortie de hook que
    Claude Code a rangée dans un fichier parce qu'elle était trop longue."""
    if outil == "Bash":
        commande = str(entree.get("command") or "")
        if ".socle/socle " in commande:
            mots = commande.split(".socle/socle ", 1)[1].split()
            sous = mots[0] if mots and re.fullmatch(r"[a-z][a-z-]*", mots[0]) else "?"
            return f"commande socle {sous}"
    if outil == "Read" and "tool-results/hook-" in str(entree.get("file_path") or ""):
        return "sortie de hook relue"
    return None


def lire_conversation(chemin: Path, sous_agent: bool = False) -> Conversation:
    """Lit une transcription : ses appels (un par `requestId`), ses compactages,
    ses refus d'usage et ce que les hooks du socle y ont injecté."""
    conv = Conversation(nom=chemin.stem, sous_agent=sous_agent)
    vus: set[str] = set()
    outils: dict[str, str] = {}  # appel d'outil en cours -> nature de ce qu'il rapporte du socle
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            try:
                o = json.loads(ligne)
            except json.JSONDecodeError:
                continue
            nature = o.get("type")
            horo = o.get("timestamp")
            if nature == "assistant":
                if o.get("quotaLimits"):
                    q = o["quotaLimits"]
                    conv.limites.append({"horodatage": _date(horo), "type": q.get("rateLimitType"),
                                         "fin": datetime.fromtimestamp(q["resetsAt"], timezone.utc)
                                         if q.get("resetsAt") else None})
                    continue
                message = o.get("message") or {}
                usage = message.get("usage")
                cle = o.get("requestId") or o.get("uuid")
                if usage and cle not in vus and message.get("model") != "<synthetic>":
                    vus.add(cle)
                    cache = usage.get("cache_creation") or {}
                    total_ecrit = usage.get("cache_creation_input_tokens") or 0
                    e1h = cache.get("ephemeral_1h_input_tokens") or 0
                    e5m = cache.get("ephemeral_5m_input_tokens")
                    if e5m is None:
                        e5m = total_ecrit - e1h
                    conv.appels.append(Appel(_date(horo), message.get("model") or "?",
                                             usage.get("input_tokens") or 0, e5m, e1h,
                                             usage.get("cache_read_input_tokens") or 0, usage.get("output_tokens") or 0))
                # une réponse en plusieurs blocs : chaque enregistrement porte les siens
                if isinstance(message.get("content"), list):
                    for b in message["content"]:
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            nature_outil = _commande_socle(b.get("name"), b.get("input") or {})
                            if nature_outil:
                                outils[b.get("id")] = nature_outil
            elif nature == "system" and o.get("subtype") == "compact_boundary":
                m = o.get("compactMetadata") or {}
                conv.compactages.append({"horodatage": _date(horo), "declencheur": m.get("trigger"),
                                         "avant": m.get("preTokens") or 0, "apres": m.get("postTokens"),
                                         "duree_s": (m.get("durationMs") or 0) / 1000, "resume_octets": 0})
            elif nature == "user" and o.get("isCompactSummary") and conv.compactages:
                conv.compactages[-1]["resume_octets"] = len(_texte(o["message"].get("content")).encode())
            elif nature == "attachment":
                a = o.get("attachment") or {}
                if a.get("type") == "hook_success" and a.get("hookEvent") == "SessionStart":
                    conv.injections.append({"horodatage": _date(horo), "nature": a.get("hookName"),
                                            "octets": len(str(a.get("content") or "").encode())})
                elif a.get("type") in ("hook_blocking_error", "hook_system_message"):
                    conv.injections.append({"horodatage": _date(horo), "nature": "refus Stop",
                                            "octets": len(json.dumps(a, ensure_ascii=False).encode())})
            elif nature == "user" and isinstance((o.get("message") or {}).get("content"), list):
                for b in o["message"]["content"]:
                    if not (isinstance(b, dict) and b.get("type") == "tool_result"):
                        continue
                    texte = _texte(b.get("content"))
                    if b.get("is_error") and texte.startswith("PreToolUse:") and " hook " in texte[:40]:
                        conv.injections.append({"horodatage": _date(horo), "nature": "refus PreToolUse",
                                                "octets": len(texte.encode())})
                    elif b.get("tool_use_id") in outils:
                        conv.injections.append({"horodatage": _date(horo), "nature": outils.pop(b["tool_use_id"]),
                                                "octets": len(texte.encode())})
    conv.appels.sort(key=lambda a: a.horodatage)
    return conv


def lire_dossier(dossier: Path, session: str | None = None) -> list[Conversation]:
    """Les conversations d'un dossier de transcriptions : chaque `<id>.jsonl`
    est une conversation principale, ses sous-agents dans `<id>/subagents/`."""
    conversations = []
    for principal in sorted(Path(dossier).glob("*.jsonl")):
        if session and not principal.stem.startswith(session):
            continue
        conversations.append(lire_conversation(principal))
        for sous in sorted((principal.parent / principal.stem / "subagents").glob("*.jsonl")):
            conversations.append(lire_conversation(sous, sous_agent=True))
    return conversations


def tronquer(conversations: list[Conversation], jusqu_a: datetime) -> list[Conversation]:
    """Les conversations sans ce qui suit `jusqu_a` : une mesure se fige à un
    instant, même si la session (et l'outil qui la mesure) continue."""
    resultat = []
    for c in conversations:
        avant = lambda xs: [x for x in xs if (x.horodatage if isinstance(x, Appel) else x["horodatage"]) <= jusqu_a]
        resultat.append(Conversation(c.nom, c.sous_agent, avant(c.appels), avant(c.compactages), avant(c.limites),
                                     avant(c.injections)))
    return [c for c in resultat if c.appels or not c.sous_agent]


def cout(appel: Appel, poids: Poids = Poids()) -> float:
    """Le coût pondéré d'un appel, en jetons d'entrée non cachée."""
    return (appel.entree * poids.entree + appel.ecriture_5m * poids.ecriture_5m
            + appel.ecriture_1h * poids.ecriture_1h + appel.lecture * poids.lecture
            + appel.sortie * poids.sortie)


def _jour(h: datetime) -> str:
    return h.astimezone(timezone.utc).date().isoformat()


CATEGORIES = ("entree", "ecriture_5m", "ecriture_1h", "lecture", "sortie")


def resume_par_jour(conversations: list[Conversation], poids: Poids = Poids()) -> dict:
    """Par jour, par modèle et par portée (principale, sous-agents) : le nombre
    d'appels et de conversations, les jetons par catégorie, le coût pondéré, et,
    pour les sous-agents, la médiane et le maximum du coût d'un sous-agent."""
    table: dict = {}
    for conv in conversations:
        portee = "sous-agents" if conv.sous_agent else "principale"
        for a in conv.appels:
            cle = (_jour(a.horodatage), a.modele, portee)
            ligne = table.setdefault(cle, {"appels": 0, "cout": 0.0, "par_conversation": defaultdict(float),
                                           **{c: 0 for c in CATEGORIES}})
            ligne["appels"] += 1
            ligne["cout"] += cout(a, poids)
            ligne["par_conversation"][conv.nom] += cout(a, poids)
            for c in CATEGORIES:
                ligne[c] += getattr(a, c)
    for ligne in table.values():
        couts = list(ligne.pop("par_conversation").values())
        ligne["conversations"] = len(couts)
        ligne["mediane"] = statistics.median(couts)
        ligne["maximum"] = max(couts)
    return table


def pauses(conversation: Conversation, poids: Poids = Poids(), seuil_s: int = CINQ_MINUTES) -> list[dict]:
    """Les reprises après un silence de plus de `seuil_s` secondes entre deux
    appels : l'écart, le coût du premier appel après, et son rapport à l'appel
    médian de la conversation."""
    if len(conversation.appels) < 2:
        return []
    mediane = statistics.median(cout(a, poids) for a in conversation.appels) or 1.0
    resultat = []
    for avant, apres in zip(conversation.appels, conversation.appels[1:]):
        ecart = (apres.horodatage - avant.horodatage).total_seconds()
        if ecart > seuil_s:
            c = cout(apres, poids)
            resultat.append({"horodatage": apres.horodatage, "ecart_s": ecart, "cout": c,
                             "rapport": c / mediane, "contexte": apres.contexte})
    return resultat


def resume_pauses(conversations: list[Conversation], poids: Poids = Poids(), jours: set[str] | None = None,
                  seuils: tuple[int, ...] = (CINQ_MINUTES, UNE_HEURE)) -> list[dict]:
    """Pour chaque portée et chaque seuil : le nombre de reprises, leur coût
    (le premier appel après la pause), leur part du coût total, et le rapport
    médian de ce premier appel à l'appel médian."""
    lignes = []
    for portee in ("principale", "sous-agents"):
        convs = [c for c in conversations if c.sous_agent == (portee == "sous-agents")]
        total = sum(cout(a, poids) for c in convs for a in c.appels if not jours or _jour(a.horodatage) in jours)
        for seuil in seuils:
            reprises = [p for c in convs for p in pauses(c, poids, seuil)
                        if not jours or _jour(p["horodatage"]) in jours]
            somme = sum(p["cout"] for p in reprises)
            lignes.append({"portee": portee, "seuil_s": seuil, "reprises": len(reprises), "cout": somme,
                           "part": somme / total if total else 0.0,
                           "rapport_median": statistics.median(p["rapport"] for p in reprises) if reprises else 0.0,
                           "conversations": len({id(c) for c in convs for p in pauses(c, poids, seuil)
                                                 if not jours or _jour(p["horodatage"]) in jours})})
    return lignes


def compactages(conversation: Conversation, poids: Poids = Poids(), octets_par_jeton: float = 3.5) -> list[dict]:
    """Chaque compactage, et son coût estimé : l'appel qui résume n'est pas
    dans la transcription ; il relit la conversation (au prix de la lecture,
    le cache étant chaud) et écrit le résumé (au prix de la sortie). S'y
    ajoute le premier appel d'après, qui réécrit le contexte neuf."""
    resultat = []
    for c in conversation.compactages:
        resume = c["resume_octets"] / octets_par_jeton
        estime = c["avant"] * poids.lecture + resume * poids.sortie
        suivant = next((a for a in conversation.appels if a.horodatage > c["horodatage"]), None)
        resultat.append({**c, "resume_jetons": resume, "cout_estime": estime,
                         "cout_appel_suivant": cout(suivant, poids) if suivant else 0.0})
    return resultat


def taille_contexte(conversation: Conversation, jours: set[str] | None = None) -> dict:
    """Par jour, la taille de la conversation relue à chaque appel : médiane,
    90e centile, maximum, et le nombre d'appels au-delà de 400 000 jetons."""
    par_jour: dict[str, list[int]] = defaultdict(list)
    for a in conversation.appels:
        if not jours or _jour(a.horodatage) in jours:
            par_jour[_jour(a.horodatage)].append(a.contexte)
    resultat = {}
    for jour, tailles in sorted(par_jour.items()):
        tailles.sort()
        resultat[jour] = {"appels": len(tailles), "mediane": statistics.median(tailles),
                          "p90": tailles[int(0.9 * (len(tailles) - 1))], "maximum": tailles[-1],
                          "au_dela_400k": sum(t > 400_000 for t in tailles)}
    return resultat


def premiers_appels(conversations: list[Conversation], poids: Poids = Poids()) -> dict:
    """Ce que coûte un démarrage à neuf : le premier appel de chaque sous-agent
    (contexte et coût, en médiane et maximum), à comparer à une relecture à froid."""
    premiers = [c.appels[0] for c in conversations if c.sous_agent and c.appels]
    if not premiers:
        return {"nombre": 0, "contexte_median": 0, "cout_median": 0.0, "contexte_max": 0}
    return {"nombre": len(premiers), "contexte_median": statistics.median(a.contexte for a in premiers),
            "cout_median": statistics.median(cout(a, poids) for a in premiers),
            "contexte_max": max(a.contexte for a in premiers)}


def concurrence(conversations: list[Conversation]) -> dict[str, int]:
    """Par jour, le plus grand nombre de sous-agents actifs à la fois (entre
    leur premier et leur dernier appel du jour)."""
    evenements: dict[str, list[tuple[datetime, int]]] = defaultdict(list)
    for c in conversations:
        if not c.sous_agent:
            continue
        par_jour: dict[str, list[datetime]] = defaultdict(list)
        for a in c.appels:
            par_jour[_jour(a.horodatage)].append(a.horodatage)
        for jour, h in par_jour.items():
            evenements[jour] += [(min(h), 1), (max(h), -1)]
    resultat = {}
    for jour, ev in evenements.items():
        courant = maximum = 0
        for _, delta in sorted(ev, key=lambda e: (e[0], -e[1])):
            courant += delta
            maximum = max(maximum, courant)
        resultat[jour] = maximum
    return resultat


def injections_socle(conversations: list[Conversation], poids: Poids = Poids(),
                     octets_par_jeton: float = 3.5) -> dict:
    """Ce que le socle injecte, par jour et par nature : le nombre et les
    octets. Et ce que ces octets coûtent une fois dans la conversation
    principale : chaque appel relit ce qui a été injecté depuis le dernier
    compactage ; `part_contexte` est la part moyenne du contexte qui en vient,
    `cout` le coût pondéré qu'on lui attribue au prorata."""
    par_jour: dict = defaultdict(lambda: defaultdict(lambda: {"nombre": 0, "octets": 0}))
    for c in conversations:
        for i in c.injections:
            ligne = par_jour[_jour(i["horodatage"])][i["nature"]]
            ligne["nombre"] += 1
            ligne["octets"] += i["octets"]
    present = {"cout": 0.0, "total": 0.0, "parts": []}
    for c in conversations:
        if c.sous_agent:
            continue
        coupures = sorted([x["horodatage"] for x in c.compactages])
        for a in c.appels:
            depuis = max([h for h in coupures if h <= a.horodatage], default=None)
            octets = sum(i["octets"] for i in c.injections
                         if i["horodatage"] <= a.horodatage and (depuis is None or i["horodatage"] >= depuis))
            part = min(1.0, octets / octets_par_jeton / a.contexte) if a.contexte else 0.0
            present["parts"].append(part)
            present["cout"] += part * (cout(a, poids) - a.sortie * poids.sortie)
            present["total"] += cout(a, poids)
    parts = present.pop("parts")
    present["part_contexte"] = statistics.mean(parts) if parts else 0.0
    present["part_cout"] = present["cout"] / present["total"] if present["total"] else 0.0
    return {"par_jour": {j: dict(v) for j, v in par_jour.items()}, "presence": present}


def etalonner(conversations: list[Conversation], points: list[tuple[datetime, float]], poids: Poids = Poids(),
              decalage: bool = True) -> list[dict]:
    """Ce que vaut un point de fenêtre, entre deux relevés consécutifs.

    Avec `decalage`, un relevé lu à l'instant T reflète les appels finis avant
    celui dont la réponse le porte (le dernier appel fini à T) : l'en-tête
    d'une réponse dit l'usage d'avant sa requête."""
    appels = [a for c in conversations for a in c.appels]
    # l'appel qui compacte n'est pas dans la transcription : il compte ici pour
    # son estimation (il relit la conversation et écrit le résumé)
    for c in conversations:
        for x in compactages(c, poids):
            appels.append(Appel(x["horodatage"], "compactage", 0, 0, 0, x["avant"], int(x["resume_jetons"])))
    appels.sort(key=lambda a: a.horodatage)

    def borne(t: datetime) -> int:
        n = sum(1 for a in appels if a.horodatage <= t)
        return max(0, n - 1) if decalage else n

    resultat = []
    for (t0, p0), (t1, p1) in zip(points, points[1:]):
        i0, i1 = borne(t0), borne(t1)
        tranche = appels[i0:i1]
        c = sum(cout(a, poids) for a in tranche)
        delta = round((p1 - p0) * 100, 6)
        resultat.append({"debut": t0, "fin": t1, "appels": len(tranche), "cout": c, "points": delta,
                         "par_point": c / delta if delta > 0 else None,
                         "lecture": sum(a.lecture for a in tranche),
                         "ecriture": sum(a.ecriture_5m + a.ecriture_1h for a in tranche)})
    return resultat


def ajuster_lecture(conversations: list[Conversation], points: list[tuple[datetime, float]],
                    poids: Poids = Poids(), decalage: bool = True) -> tuple[float, float]:
    """Le poids de la lecture de cache qui rend les relevés le plus cohérents
    (les autres poids fixés), et ce que vaut alors un point : on cherche le
    poids qui minimise la dispersion relative des jetons par point, pondérée
    par les points de chaque intervalle."""
    meilleur = (poids.lecture, float("inf"), 0.0)
    for k in range(1, 301):
        essai = Poids(poids.entree, poids.ecriture_5m, poids.ecriture_1h, k / 1000, poids.sortie)
        tranches = [t for t in etalonner(conversations, points, essai, decalage) if t["points"] >= 1]
        if not tranches:
            break
        total_points = sum(t["points"] for t in tranches)
        moyen = sum(t["cout"] for t in tranches) / total_points
        ecart = sum(t["points"] * (t["cout"] / t["points"] / moyen - 1) ** 2 for t in tranches) / total_points
        if ecart < meilleur[1]:
            meilleur = (essai.lecture, ecart, moyen)
    return meilleur[0], meilleur[2]


def fenetres_limitees(conversations: list[Conversation], poids: Poids = Poids()) -> list[dict]:
    """Chaque fenêtre de cinq heures qui s'est terminée sur un refus : le coût
    pondéré de toutes les conversations entre son ouverture et le premier
    refus, qui vaut donc la fenêtre entière (si rien d'autre ne l'a consommée)."""
    premiers: dict[datetime, datetime] = {}
    for c in conversations:
        for lim in c.limites:
            if lim["type"] == "five_hour" and lim["fin"]:
                premiers[lim["fin"]] = min(premiers.get(lim["fin"], lim["horodatage"]), lim["horodatage"])
    resultat = []
    for fin, refus in sorted(premiers.items()):
        debut = fin - timedelta(seconds=CINQ_HEURES)
        tranche = [(c, a) for c in conversations for a in c.appels if debut <= a.horodatage <= refus]
        par_modele: dict[str, float] = defaultdict(float)
        for _, a in tranche:
            par_modele[a.modele] += cout(a, poids)
        resultat.append({"debut": debut, "refus": refus, "appels": len(tranche),
                         "cout": sum(cout(a, poids) for _, a in tranche),
                         "cout_sous_agents": sum(cout(a, poids) for c, a in tranche if c.sous_agent),
                         "par_modele": dict(par_modele)})
    return resultat


# --- Le rapport ---------------------------------------------------------

def _k(n: float) -> str:
    """Un nombre de jetons en milliers ou millions, lisible dans un tableau."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f} M".replace(".", ",")
    if n >= 1_000:
        return f"{n / 1_000:.0f} k"
    return f"{n:.0f}"


def _pc(x: float) -> str:
    return f"{100 * x:.0f} %"


def lire_point(texte: str) -> tuple[datetime, float]:
    """Un relevé `--point` : `2026-11-12T18:07:03Z,0.39` (instant UTC, part de la fenêtre)."""
    instant, part = texte.split(",")[:2]
    return _date(instant), float(part.replace(" ", ""))


def rapport(conversations: list[Conversation], poids: Poids = Poids(), jours: set[str] | None = None,
            points: list[tuple[datetime, float]] | None = None, octets_par_jeton: float = 3.5) -> str:
    """Le rapport en Markdown : des tableaux d'agrégats, rien de la conversation."""
    lignes = [f"Poids (hypothèse) : entrée {poids.entree}, écriture 5 min {poids.ecriture_5m}, "
              f"écriture 1 h {poids.ecriture_1h}, lecture {poids.lecture}, sortie {poids.sortie}.", ""]
    garder = (lambda j: True) if not jours else (lambda j: j in jours)
    table = resume_par_jour(conversations, poids)
    lignes += ["## Par jour, par modèle", "",
               "| jour | modèle | portée | conv. | appels | entrée | écr. 5 min | écr. 1 h | lecture | sortie "
               "| coût pondéré | médiane / conv. | max / conv. |",
               "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    totaux: dict = defaultdict(float)
    for (jour, modele, portee), l in sorted(table.items()):
        if not garder(jour):
            continue
        totaux[portee] += l["cout"]
        totaux[(jour, portee)] += l["cout"]
        lignes.append(f"| {jour} | {modele} | {portee} | {l['conversations']} | {l['appels']} | {_k(l['entree'])} "
                      f"| {_k(l['ecriture_5m'])} | {_k(l['ecriture_1h'])} | {_k(l['lecture'])} | {_k(l['sortie'])} "
                      f"| {_k(l['cout'])} | {_k(l['mediane'])} | {_k(l['maximum'])} |")
    ensemble = totaux["principale"] + totaux["sous-agents"]
    lignes += ["", f"Total pondéré : {_k(ensemble)} ; principale {_pc(totaux['principale'] / ensemble if ensemble else 0)}, "
               f"sous-agents {_pc(totaux['sous-agents'] / ensemble if ensemble else 0)}.", ""]
    lignes += ["## Sous-agents à la fois (maximum du jour)", ""]
    lignes += [f"- {j} : {n}" for j, n in sorted(concurrence(conversations).items()) if garder(j)]
    neuf = premiers_appels(conversations, poids)
    lignes += ["", f"Premier appel d'un sous-agent, sur toute la période lue ({neuf['nombre']}) : contexte médian {_k(neuf['contexte_median'])}, "
               f"maximum {_k(neuf['contexte_max'])}, coût médian {_k(neuf['cout_median'])}."]
    lignes += ["", "## Reprises après une pause", "",
               "| portée | pause de plus de | reprises | conv. | coût des premiers appels | part du total "
               "| premier appel / appel médian |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for r in resume_pauses(conversations, poids, jours):
        lignes.append(f"| {r['portee']} | {r['seuil_s'] // 60} min | {r['reprises']} | {r['conversations']} "
                      f"| {_k(r['cout'])} | {_pc(r['part'])} | × {r['rapport_median']:.0f} |")
    lignes += ["", "## Compactages", "",
               "| instant | déclencheur | avant | résumé | coût estimé | appel suivant |",
               "| --- | --- | ---: | ---: | ---: | ---: |"]
    for c in conversations:
        for x in compactages(c, poids, octets_par_jeton):
            if garder(_jour(x["horodatage"])):
                lignes.append(f"| {x['horodatage']:%Y-%m-%d %H:%M} | {x['declencheur']} | {_k(x['avant'])} "
                              f"| {_k(x['resume_jetons'])} | {_k(x['cout_estime'])} | {_k(x['cout_appel_suivant'])} |")
    lignes += ["", "## Taille de la conversation principale (jetons relus par appel)", "",
               "| jour | appels | médiane | 90e centile | maximum | appels > 400 k |",
               "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for c in conversations:
        if not c.sous_agent:
            for j, t in taille_contexte(c, jours).items():
                lignes.append(f"| {j} | {t['appels']} | {_k(t['mediane'])} | {_k(t['p90'])} | {_k(t['maximum'])} "
                              f"| {t['au_dela_400k']} |")
    inj = injections_socle(conversations, poids, octets_par_jeton)
    lignes += ["", "## Ce que le socle injecte", "", "| jour | nature | nombre | octets |", "| --- | --- | ---: | ---: |"]
    for j, natures in sorted(inj["par_jour"].items()):
        if garder(j):
            for n, v in sorted(natures.items()):
                lignes.append(f"| {j} | {n} | {v['nombre']} | {v['octets']} |")
    p = inj["presence"]
    lignes += ["", f"Sur toute la période lue, dans la conversation principale, ce qui a été injecté depuis le dernier compactage fait en "
               f"moyenne {_pc(p['part_contexte'])} du contexte relu, soit {_k(p['cout'])} du coût pondéré "
               f"({_pc(p['part_cout'])}), à {octets_par_jeton} octets par jeton.", ""]
    limitees = [f for f in fenetres_limitees(conversations, poids) if garder(_jour(f["refus"]))]
    if limitees:
        lignes += ["## Fenêtres de cinq heures closes par un refus", "",
                   "| ouverture | refus | appels | coût pondéré | dont sous-agents | par modèle |",
                   "| --- | --- | ---: | ---: | ---: | --- |"]
        for f in limitees:
            modeles = ", ".join(f"{m} {_k(v)}" for m, v in sorted(f["par_modele"].items()))
            lignes.append(f"| {f['debut']:%m-%d %H:%M} | {f['refus']:%m-%d %H:%M} | {f['appels']} | {_k(f['cout'])} "
                          f"| {_k(f['cout_sous_agents'])} | {modeles} |")
        lignes.append("")
    if points and len(points) > 1:
        lignes += ["## Étalonnage sur les relevés de la fenêtre", "",
                   "| de | à | appels | lecture | écriture | coût pondéré | points | jetons par point |",
                   "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for t in etalonner(conversations, points, poids):
            pp = _k(t["par_point"]) if t["par_point"] else "—"
            lignes.append(f"| {t['debut']:%H:%M:%S} | {t['fin']:%H:%M:%S} | {t['appels']} | {_k(t['lecture'])} "
                          f"| {_k(t['ecriture'])} | {_k(t['cout'])} | {t['points']:.0f} | {pp} |")
        lecture, par_point = ajuster_lecture(conversations, points, poids)
        lignes += ["", f"Poids de lecture qui explique le mieux les relevés : {lecture:.3f} ; "
                   f"un point vaut alors {_k(par_point)} jetons pondérés.", ""]
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    """La ligne de commande : le dossier des transcriptions en argument."""
    p = argparse.ArgumentParser(description="La consommation d'une session, lue dans ses transcriptions (B-0173).")
    p.add_argument("folder", type=Path, help="le dossier des transcriptions (les <id>.jsonl et leurs sous-agents)")
    p.add_argument("--session", help="le début de l'identifiant d'une conversation principale")
    p.add_argument("--day", action="append", help="un jour UTC à garder (AAAA-MM-JJ), répétable")
    p.add_argument("--until", help="ignorer ce qui suit cet instant UTC (AAAA-MM-JJTHH:MM:SSZ)")
    p.add_argument("--point", action="append", default=[],
                   help="un relevé de la fenêtre de cinq heures : INSTANT_UTC,PART (répétable)")
    p.add_argument("--weight-input", type=float, default=Poids.entree)
    p.add_argument("--weight-write-5m", type=float, default=Poids.ecriture_5m)
    p.add_argument("--weight-write-1h", type=float, default=Poids.ecriture_1h)
    p.add_argument("--weight-read", type=float, default=Poids.lecture)
    p.add_argument("--weight-output", type=float, default=Poids.sortie)
    p.add_argument("--bytes-per-token", type=float, default=3.5,
                   help="pour estimer en jetons ce que le socle injecte (hypothèse : 3,5 pour un texte français)")
    args = p.parse_args(argv)
    poids = Poids(args.weight_input, args.weight_write_5m, args.weight_write_1h, args.weight_read, args.weight_output)
    conversations = lire_dossier(args.folder, args.session)
    if args.until:
        conversations = tronquer(conversations, _date(args.until))
    if not conversations:
        print(f"aucune transcription dans {args.folder}", file=sys.stderr)
        return 1
    points = sorted(lire_point(x) for x in args.point)
    print(rapport(conversations, poids, set(args.day) if args.day else None, points, args.bytes_per_token))
    return 0


if __name__ == "__main__":
    sys.exit(main())
