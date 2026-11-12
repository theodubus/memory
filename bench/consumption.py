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
donne des relevés de la fenêtre de cinq heures (et, après une barre, de la
semaine) ; l'outil en déduit ce que vaut un point, le poids de la lecture
qui les explique le mieux, et la fourchette que leur arrondi laisse.

    python3 bench/consumption.py ~/.claude/projects/<projet> --day 2026-11-12 \\
        --point 2026-11-12T18:07:03.8Z,0.00/0.53 --point 2026-11-12T18:07:25.6Z,0.39/0.59
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

CINQ_MINUTES = 300
UNE_HEURE = 3600
CINQ_HEURES = 5 * UNE_HEURE

# Ce que le socle met dans une conversation, reconnu à son texte : l'en-tête
# du dossier que `socle review` imprime, l'en-tête de la section que
# l'installeur pose dans AGENTS.md (en français et en anglais), et le chemin
# où Claude Code range la sortie d'un hook trop longue.
TETES_REVUE = ("# Revue adversariale d'un lot", "# Adversarial review of a batch")
SECTIONS_SOCLE = ("## Socle : mémoire, documentation et tests", "## Socle: memory, documentation and tests")
SORTIE_DE_HOOK = "tool-results/hook-"
AGENTS_SOCLE = "AGENTS.md, section du socle"


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
    # compactages : horodatage (sa fin), déclencheur, jetons avant et après, durée, octets du résumé
    compactages: list[dict] = field(default_factory=list)
    # refus d'usage : horodatage, type de fenêtre, fin de la fenêtre
    limites: list[dict] = field(default_factory=list)
    # ce que le socle injecte : horodatage, nature (SessionStart:resume…, refus…), octets reçus par l'agent
    injections: list[dict] = field(default_factory=list)


def _date(texte: str) -> datetime:
    """Un instant ISO 8601 ; sans fuseau, il vaut UTC."""
    h = datetime.fromisoformat(texte.strip().replace("Z", "+00:00"))
    return h if h.tzinfo else h.replace(tzinfo=timezone.utc)


def _texte(contenu) -> str:
    if isinstance(contenu, str):
        return contenu
    if isinstance(contenu, list):
        return "".join(b.get("text", "") for b in contenu if isinstance(b, dict))
    return ""


def _commande_socle(outil: str | None, entree: dict) -> str | None:
    """La nature de ce qu'un appel d'outil rapporte du socle, ou None : la
    relecture, par n'importe quel outil, d'une sortie de hook que Claude Code
    a rangée dans un fichier parce qu'elle était trop longue, ou une commande
    `socle <sous-commande>`."""
    if SORTIE_DE_HOOK in json.dumps(entree, ensure_ascii=False):
        return "sortie de hook relue"
    if outil == "Bash":
        commande = str(entree.get("command") or "")
        if ".socle/socle " in commande:
            mots = commande.split(".socle/socle ", 1)[1].split()
            sous = mots[0] if mots and re.fullmatch(r"[a-z][a-z-]*", mots[0]) else "?"
            return f"commande socle {sous}"
    return None


def _section_socle(texte: str) -> str:
    """La section du socle dans un AGENTS.md : de son en-tête à la section suivante."""
    for tete in SECTIONS_SOCLE:
        debut = texte.find(tete)
        if debut >= 0:
            section = texte[debut:]
            fin = section.find("\n## ", len(tete))
            return section if fin < 0 else section[:fin]
    return ""


def _est_dossier_de_revue(texte: str) -> bool:
    return any(tete in texte for tete in TETES_REVUE)


def lire_conversation(chemin: Path, sous_agent: bool = False) -> Conversation:
    """Lit une transcription : ses appels (un par `requestId`), ses compactages,
    ses refus d'usage et ce que le socle y a injecté."""
    conv = Conversation(nom=chemin.stem, sous_agent=sous_agent)
    vus: set[str] = set()
    outils: dict[str, str] = {}  # appel d'outil en cours -> nature de ce qu'il rapporte du socle

    def injecter(horo, nature, octets, **autres):
        conv.injections.append({"horodatage": _date(horo), "nature": nature, "octets": octets, **autres})

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
                    # l'agent reçoit `content` ; `stdout` est la sortie entière du hook
                    sortie = {"sortie_octets": len(str(a["stdout"] or "").encode())} if "stdout" in a else {}
                    injecter(horo, a.get("hookName"), len(str(a.get("content") or "").encode()), **sortie)
                elif a.get("type") in ("hook_blocking_error", "hook_system_message"):
                    injecter(horo, "refus Stop", len(json.dumps(a, ensure_ascii=False).encode()))
                elif a.get("type") == "instructions":
                    for fichier in a.get("files") or []:
                        section = _section_socle(str((fichier or {}).get("content") or ""))
                        if section:
                            injecter(horo, AGENTS_SOCLE, len(section.encode()))
            elif nature == "user":
                contenu = (o.get("message") or {}).get("content")
                blocs = contenu if isinstance(contenu, list) else [{"type": "text", "text": contenu}]
                for b in blocs:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "text" and _est_dossier_de_revue(str(b.get("text") or "")):
                        injecter(horo, "dossier de revue", len(str(b["text"]).encode()))
                    if b.get("type") != "tool_result":
                        continue
                    texte = _texte(b.get("content"))
                    nature_outil = outils.pop(b.get("tool_use_id"), None)
                    if b.get("is_error") and texte.startswith("PreToolUse:") and " hook " in texte[:40]:
                        injecter(horo, "refus PreToolUse", len(texte.encode()))
                    elif _est_dossier_de_revue(texte):
                        injecter(horo, "dossier de revue", len(texte.encode()))
                    elif nature_outil:
                        injecter(horo, nature_outil, len(texte.encode()))
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


def _duree_cache(conversation: Conversation) -> int:
    """La durée du cache d'une conversation, lue dans ce qu'elle écrit."""
    une_heure = sum(a.ecriture_1h for a in conversation.appels)
    return UNE_HEURE if une_heure > sum(a.ecriture_5m for a in conversation.appels) else CINQ_MINUTES


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
    """Chaque compactage, et une borne basse de son coût : l'appel qui résume
    n'est pas dans la transcription ; il relit au moins la conversation (au
    prix de la lecture, le cache étant chaud) et écrit le résumé (au prix de
    la sortie). Le seul compactage encadré par des relevés en a coûté plus du
    double (voir `etalonner`). S'y ajoute le premier appel d'après, qui
    réécrit le contexte neuf."""
    resultat = []
    for c in conversation.compactages:
        resume = c["resume_octets"] / octets_par_jeton
        borne = c["avant"] * poids.lecture + resume * poids.sortie
        suivant = next((a for a in conversation.appels if a.horodatage > c["horodatage"]), None)
        resultat.append({**c, "resume_jetons": resume, "borne_basse": borne,
                         "cout_appel_suivant": cout(suivant, poids) if suivant else 0.0})
    return resultat


def _centile(valeurs: list[float], q: float) -> float:
    """Le centile `q` (de 0 à 1) d'une liste, par la valeur de rang le plus proche en dessous."""
    valeurs = sorted(valeurs)
    return valeurs[int(q * (len(valeurs) - 1))]


def taille_contexte(conversation: Conversation, jours: set[str] | None = None) -> dict:
    """Par jour, la taille de la conversation relue à chaque appel : médiane,
    90e centile, maximum, et le nombre d'appels au-delà de 400 000 jetons."""
    par_jour: dict[str, list[int]] = defaultdict(list)
    for a in conversation.appels:
        if not jours or _jour(a.horodatage) in jours:
            par_jour[_jour(a.horodatage)].append(a.contexte)
    resultat = {}
    for jour, tailles in sorted(par_jour.items()):
        resultat[jour] = {"appels": len(tailles), "mediane": statistics.median(tailles),
                          "p90": _centile(tailles, 0.9), "maximum": max(tailles),
                          "au_dela_400k": sum(t > 400_000 for t in tailles)}
    return resultat


def appels_tiedes(conversation: Conversation) -> list[Appel]:
    """Les appels qui relisent un cache encore chaud : ni le premier de la
    conversation, ni le premier après un compactage, et à moins de la durée
    du cache de la conversation (une heure ou cinq minutes) du précédent."""
    duree = _duree_cache(conversation)
    coupures = [x["horodatage"] for x in conversation.compactages]
    return [apres for avant, apres in zip(conversation.appels, conversation.appels[1:])
            if (apres.horodatage - avant.horodatage).total_seconds() < duree
            and not any(avant.horodatage < h <= apres.horodatage for h in coupures)]


def cout_selon_contexte(conversations: list[Conversation], poids: Poids = Poids(),
                        centres: tuple[int, ...] = (100_000, 300_000, 520_000), demi_largeur: int = 40_000,
                        modele: str | None = None) -> list[dict]:
    """Ce que coûte un appel tiède selon la taille du contexte : pour chaque
    tranche (centre ± demi-largeur), le nombre d'appels, le coût médian
    complet (écriture, lecture et sortie), et la médiane de sa lecture."""
    tiedes = [a for c in conversations for a in appels_tiedes(c) if modele is None or a.modele == modele]
    resultat = []
    for centre in centres:
        tranche = [a for a in tiedes if centre - demi_largeur <= a.contexte < centre + demi_largeur]
        resultat.append({"centre": centre, "appels": len(tranche),
                         "cout": statistics.median(cout(a, poids) for a in tranche) if tranche else 0.0,
                         "lecture": statistics.median(a.lecture * poids.lecture for a in tranche) if tranche else 0.0})
    return resultat


def premiers_appels(conversations: list[Conversation], poids: Poids = Poids()) -> dict:
    """Ce que coûte un démarrage à neuf : le premier appel de chaque sous-agent
    (contexte et coût, en médiane et maximum), et ce même coût si le cache
    s'écrivait pour une heure, comme celui d'une conversation principale."""
    premiers = [c.appels[0] for c in conversations if c.sous_agent and c.appels]
    if not premiers:
        return {"nombre": 0, "contexte_median": 0, "cout_median": 0.0, "cout_median_1h": 0.0, "contexte_max": 0}
    sur_une_heure = replace(poids, ecriture_5m=poids.ecriture_1h)
    return {"nombre": len(premiers), "contexte_median": statistics.median(a.contexte for a in premiers),
            "cout_median": statistics.median(cout(a, poids) for a in premiers),
            "cout_median_1h": statistics.median(cout(a, sur_une_heure) for a in premiers),
            "contexte_max": max(a.contexte for a in premiers)}


def concurrence(conversations: list[Conversation], inactivite_s: int = CINQ_MINUTES) -> dict[str, int]:
    """Par jour, le plus grand nombre de sous-agents actifs à la fois. Un
    sous-agent est actif d'un appel au suivant tant qu'ils sont à moins de
    `inactivite_s` l'un de l'autre : une attente plus longue (sa revue, une
    réponse) ne compte pas comme activité."""
    evenements: dict[str, list[tuple[datetime, int]]] = defaultdict(list)
    for c in conversations:
        if not c.sous_agent or not c.appels:
            continue
        debut = fin = c.appels[0].horodatage
        for a in c.appels[1:]:
            if (a.horodatage - fin).total_seconds() > inactivite_s:
                evenements[_jour(debut)] += [(debut, 1), (fin, -1)]
                debut = a.horodatage
            fin = a.horodatage
        evenements[_jour(debut)] += [(debut, 1), (fin, -1)]
    resultat = {}
    for jour, ev in evenements.items():
        courant = maximum = 0
        # à instant égal, un début passe avant une fin : un sous-agent d'un seul appel compte
        for _, delta in sorted(ev, key=lambda e: (e[0], -e[1])):
            courant += delta
            maximum = max(maximum, courant)
        resultat[jour] = maximum
    return resultat


def presence_socle(conversations: list[Conversation], poids: Poids = Poids(), octets_par_jeton: float = 3.5,
                   sous_agents: bool = False) -> dict:
    """Ce que coûtent, une fois dans le contexte, les octets que le socle a
    injectés, dans la conversation principale ou dans les sous-agents :
    chaque appel relit ce qui a été injecté depuis le dernier compactage.
    Par nature : `part_contexte`, la part moyenne du contexte relu qui en
    vient, `cout`, le coût pondéré qu'on lui attribue au prorata de
    l'entrée de l'appel (la sortie de l'appel n'en dépend pas), et
    `conversations`, le nombre de conversations qui l'ont reçue."""
    natures: dict = defaultdict(lambda: {"part_contexte": 0.0, "cout": 0.0, "conversations": 0})
    total = 0.0
    appels = 0
    for c in conversations:
        if c.sous_agent != sous_agents:
            continue
        coupures = sorted(x["horodatage"] for x in c.compactages)
        for n in {i["nature"] for i in c.injections if c.appels and i["horodatage"] <= c.appels[-1].horodatage}:
            natures[n]["conversations"] += 1
        for a in c.appels:
            appels += 1
            total += cout(a, poids)
            if not a.contexte:
                continue
            depuis = max([h for h in coupures if h <= a.horodatage], default=None)
            octets: dict[str, int] = defaultdict(int)
            for i in c.injections:
                if i["horodatage"] <= a.horodatage and (depuis is None or i["horodatage"] >= depuis):
                    octets[i["nature"]] += i["octets"]
            parts = {n: o / octets_par_jeton / a.contexte for n, o in octets.items()}
            echelle = min(1.0, 1 / sum(parts.values())) if sum(parts.values()) else 1.0
            entree = cout(a, poids) - a.sortie * poids.sortie
            for n, p in parts.items():
                natures[n]["part_contexte"] += p * echelle
                natures[n]["cout"] += p * echelle * entree
    for v in natures.values():
        v["part_contexte"] /= appels or 1  # moyenne sur tous les appels de la portée
    return {"appels": appels, "total": total, "natures": {n: dict(v) for n, v in natures.items()}}


def part_du_socle(presence: dict, exclure: tuple[str, ...] = ()) -> tuple[float, float]:
    """La part du contexte et la part du coût qui viennent du socle, sans les natures exclues."""
    gardees = [v for n, v in presence["natures"].items() if n not in exclure]
    contexte = sum(v["part_contexte"] for v in gardees)
    return contexte, (sum(v["cout"] for v in gardees) / presence["total"] if presence["total"] else 0.0)


def injections_socle(conversations: list[Conversation]) -> dict:
    """Ce que le socle injecte, par jour et par nature : le nombre, les octets
    reçus par l'agent, la plus grande injection, et, pour le hook de
    démarrage, la plus petite et la plus grande sortie entière."""
    par_jour: dict = defaultdict(lambda: defaultdict(lambda: {"nombre": 0, "octets": 0, "max": 0}))
    sorties = []
    for c in conversations:
        for i in c.injections:
            ligne = par_jour[_jour(i["horodatage"])][i["nature"]]
            ligne["nombre"] += 1
            ligne["octets"] += i["octets"]
            ligne["max"] = max(ligne["max"], i["octets"])
            if "sortie_octets" in i:
                sorties.append(i["sortie_octets"])
    return {"par_jour": {j: {n: dict(v) for n, v in natures.items()} for j, natures in par_jour.items()},
            "sorties_de_hook": (min(sorties), max(sorties)) if sorties else None}


def tailles(conversations: list[Conversation], nature: str, sous_agents: bool | None = None,
            par_conversation: bool = False) -> list[int]:
    """Les tailles, en octets, des injections d'une nature dans la portée
    choisie ; avec `par_conversation`, leur somme dans chaque conversation qui
    en a reçu (un dossier lu en plusieurs morceaux compte une fois)."""
    if not par_conversation:
        return sorted(i["octets"] for c in conversations if sous_agents is None or c.sous_agent == sous_agents
                      for i in c.injections if i["nature"] == nature)
    sommes = [sum(i["octets"] for i in c.injections if i["nature"] == nature) for c in conversations
              if sous_agents is None or c.sous_agent == sous_agents]
    return sorted(s for s in sommes if s)


# --- L'étalonnage sur les relevés de la fenêtre ----------------------------

def _evenements(conversations: list[Conversation]) -> list[tuple[datetime, Appel | None]]:
    """Les appels de toutes les conversations et leurs compactages, dans
    l'ordre de leur fin : chacun porte un relevé dans l'en-tête de sa réponse.
    Un compactage est un appel que la transcription ne chiffre pas (None)."""
    ev: list[tuple[datetime, Appel | None]] = [(a.horodatage, a) for c in conversations for a in c.appels]
    ev += [(x["horodatage"], None) for c in conversations for x in c.compactages]
    ev.sort(key=lambda e: e[0])
    return ev


def _tranches(conversations: list[Conversation], points: list[tuple], decalage: bool = True) -> list[list]:
    """Les événements entre deux relevés consécutifs. Avec `decalage`, un
    relevé lu à l'instant T reflète les appels finis avant celui dont la
    réponse le porte (le dernier fini à T) : l'en-tête d'une réponse dit
    l'usage d'avant sa requête."""
    ev = _evenements(conversations)
    instants = [h for h, _ in ev]

    def borne(t: datetime) -> int:
        n = sum(1 for h in instants if h <= t)
        return max(0, n - 1) if decalage else n

    bornes = [borne(p[0]) for p in points]
    return [ev[i0:i1] for i0, i1 in zip(bornes, bornes[1:])]


def etalonner(conversations: list[Conversation], points: list[tuple], poids: Poids = Poids(),
              decalage: bool = True, groupes: list[list] | None = None) -> list[dict]:
    """Ce que vaut un point de fenêtre, entre deux relevés consécutifs (instant,
    part de la fenêtre, …). Un intervalle qui contient un compactage n'a pas
    de valeur du point : l'appel qui compacte n'est pas chiffré."""
    groupes = _tranches(conversations, points, decalage) if groupes is None else groupes
    resultat = []
    for r0, r1, groupe in zip(points, points[1:], groupes):
        appels = [a for _, a in groupe if a is not None]
        c = sum(cout(a, poids) for a in appels)
        delta = round((r1[1] - r0[1]) * 100, 6)
        modeles: dict[str, float] = defaultdict(float)
        for a in appels:
            modeles[a.modele] += cout(a, poids)
        resultat.append({"debut": r0[0], "fin": r1[0], "appels": len(appels), "compactages": len(groupe) - len(appels),
                         "cout": c, "points": delta,
                         "par_point": c / delta if delta > 0 and len(appels) == len(groupe) and c > 0 else None,
                         "lecture": sum(a.lecture for a in appels),
                         "ecriture": sum(a.ecriture_5m + a.ecriture_1h for a in appels), "modeles": dict(modeles)})
    return resultat


def _utilisables(tranches: list[dict]) -> list[dict]:
    """Les intervalles qui servent à l'ajustement : un point au moins, aucun compactage."""
    return [t for t in tranches if t["points"] >= 1 and not t["compactages"]]


def _segments(points: list[tuple], groupes: list[list], poids: Poids) -> list[list[tuple[float, float]]]:
    """Les relevés en suites que rien ne coupe, chacun en (points relevés,
    coût cumulé depuis le début de sa suite). Un compactage, que la
    transcription ne chiffre pas, ou une fenêtre qui repart à zéro, coupe."""
    segments, courant, cumul = [], [(points[0][1] * 100, 0.0)], 0.0
    for r0, r1, groupe in zip(points, points[1:], groupes):
        if any(a is None for _, a in groupe) or r1[1] < r0[1]:
            segments.append(courant)
            courant, cumul = [(r1[1] * 100, 0.0)], 0.0
            continue
        cumul += sum(cout(a, poids) for _, a in groupe)
        courant.append((r1[1] * 100, cumul))
    segments.append(courant)
    return segments


def ajuster_lecture(conversations: list[Conversation], points: list[tuple], poids: Poids = Poids(),
                    decalage: bool = True) -> tuple[float, float] | None:
    """Le poids de la lecture de cache qui explique le mieux les relevés (les
    autres poids fixés), et ce que vaut alors un point. L'arrondi porte sur
    chaque relevé : pour chaque poids, les relevés d'une même suite se
    régressent sur le coût cumulé (une pente commune, l'origine propre à
    chaque suite), et l'on garde le poids qui laisse le moins d'écart
    quadratique. None quand rien ne s'y prête : aucun coût entre deux
    relevés d'une même suite, ou des relevés qui n'avancent pas."""
    groupes = _tranches(conversations, points, decalage)
    meilleur = None
    for k in range(1, 301):
        essai = replace(poids, lecture=k / 1000)
        segments = [s for s in _segments(points, groupes, essai) if len(s) > 1]
        moyennes = [(sum(p for p, _ in s) / len(s), sum(c for _, c in s) / len(s)) for s in segments]
        sxx = sum((c - mc) ** 2 for s, (_, mc) in zip(segments, moyennes) for _, c in s)
        sxy = sum((c - mc) * (p - mp) for s, (mp, mc) in zip(segments, moyennes) for p, c in s)
        if sxx <= 0 or sxy <= 0:
            return None
        pente = sxy / sxx
        ecart = sum((p - mp - pente * (c - mc)) ** 2 for s, (mp, mc) in zip(segments, moyennes) for p, c in s)
        if meilleur is None or ecart < meilleur[1]:
            meilleur = (essai.lecture, ecart, 1 / pente)
    return (meilleur[0], meilleur[2]) if meilleur else None


def fourchette(conversations: list[Conversation], points: list[tuple], poids: Poids = Poids(),
               decalage: bool = True, arrondi: float = 1.0) -> dict | None:
    """Les poids de lecture, et ce que vaut alors un point, que les relevés
    admettent à leur arrondi près. Chaque relevé est arrondi au centième :
    un poids est admis s'il existe une valeur du point qui place chaque relevé
    à moins d'un demi-point de la droite que tracent les coûts cumulés, soit
    au plus `arrondi` point d'écart entre deux relevés d'une même suite.
    None quand aucun poids n'est admis."""
    groupes = _tranches(conversations, points, decalage)
    admis = []
    for k in range(1, 301):
        essai = replace(poids, lecture=k / 1000)
        segments = _segments(points, groupes, essai)
        bas, haut, possible = 0.0, math.inf, True
        for seg in segments:
            for i, (pi, ci) in enumerate(seg):
                for pj, cj in seg[:i]:
                    if ci - cj > 0:
                        bas = max(bas, (pi - pj - arrondi) / (ci - cj))
                        haut = min(haut, (pi - pj + arrondi) / (ci - cj))
                    elif abs(pi - pj) > arrondi:
                        possible = False
        if possible and bas <= haut and 0 < haut < math.inf:
            admis.append((essai.lecture, 1 / haut, 1 / bas if bas > 0 else math.inf))
    if not admis:
        return None
    return {"lecture": (min(a[0] for a in admis), max(a[0] for a in admis)),
            "par_point": (min(a[1] for a in admis), max(a[2] for a in admis))}


def points_de_semaine(points: list[tuple], arrondi: float = 1.0) -> dict | None:
    """Ce que vaut un point de la semaine en points de la fenêtre, entre le
    premier et le dernier relevé qui portent la semaine, et la fourchette que
    l'arrondi des deux relevés laisse. None si la fenêtre repart à zéro entre
    eux ou si la semaine n'avance pas."""
    avec = [p for p in points if len(p) > 2 and p[2] is not None]
    if len(avec) < 2 or any(b[1] < a[1] for a, b in zip(avec, avec[1:])):
        return None
    fenetre = round((avec[-1][1] - avec[0][1]) * 100, 6)
    semaine = round((avec[-1][2] - avec[0][2]) * 100, 6)
    if semaine <= 0 or fenetre <= 0:
        return None
    return {"fenetre": fenetre, "semaine": semaine, "rapport": fenetre / semaine,
            "bas": (fenetre - arrondi) / (semaine + arrondi),
            "haut": (fenetre + arrondi) / (semaine - arrondi) if semaine > arrondi else math.inf}


def modele_etalonne(tranches: list[dict]) -> str | None:
    """Le modèle qui porte l'essentiel du coût des intervalles qui servent à l'ajustement."""
    couts: dict[str, float] = defaultdict(float)
    for t in _utilisables(tranches):
        for m, c in t["modeles"].items():
            couts[m] += c
    return max(couts, key=couts.get) if couts else None


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


def valeur_du_point_des_autres(fenetres: list[dict], modele: str, par_point: float) -> list[dict]:
    """Pour chaque fenêtre close par un refus : les points qu'y a pris
    `modele` (étalonné à `par_point`), et ce que vaut un point pour les autres
    modèles, sur les points qui restent. None quand les autres n'y ont rien
    fait, ou quand `modele` seul dépasse la fenêtre."""
    resultat = []
    for f in fenetres:
        connus = f["par_modele"].get(modele, 0.0) / par_point
        autres = f["cout"] - f["par_modele"].get(modele, 0.0)
        reste = 100 - connus
        resultat.append({**f, "points_du_modele": connus,
                         "autres_par_point": autres / reste if autres > 1e-6 * f["cout"] and reste > 0 else None})
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
    return f"{100 * x:.1f} %".replace(".", ",")


def _v(x: float, chiffres: int = 1) -> str:
    return f"{x:.{chiffres}f}".replace(".", ",")


def _instant(h: datetime) -> str:
    return f"{h:%H:%M:%S}.{h.microsecond // 1000:03d}"


def lire_point(texte: str) -> tuple[datetime, float, float | None]:
    """Un relevé `--point` : `2026-11-12T18:07:25.6Z,0.39/0.59` : l'instant
    (UTC s'il n'a pas de fuseau), la part de la fenêtre de cinq heures, et,
    après une barre, celle de la semaine. Les parts s'écrivent avec un point
    décimal : une virgule se confondrait avec le séparateur, elle est refusée."""
    morceaux = texte.split(",")
    if len(morceaux) != 2:
        raise ValueError(f"relevé illisible : {texte!r} ; attendu INSTANT,PART[/SEMAINE], "
                         "avec un point décimal (0.39, pas 0,39)")
    instant, parts = morceaux
    fenetre, _, semaine = parts.replace(" ", "").partition("/")
    return _date(instant), float(fenetre), (float(semaine) if semaine else None)


def _rapport_etalonnage(conversations, poids, points) -> tuple[list[str], dict]:
    """La section de l'étalonnage, et ce qu'elle établit (poids, valeur du point, modèle)."""
    lignes = ["## Étalonnage sur les relevés de la fenêtre", "",
              "| de | à | appels | lecture | écriture | coût pondéré | points | jetons par point |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    tranches = etalonner(conversations, points, poids)
    for t in tranches:
        pp = _k(t["par_point"]) if t["par_point"] else ("compactage" if t["compactages"] else "—")
        appels = f"{t['appels']} + compactage" if t["compactages"] else str(t["appels"])
        lignes.append(f"| {_instant(t['debut'])} | {_instant(t['fin'])} | {appels} | {_k(t['lecture'])} "
                      f"| {_k(t['ecriture'])} | {_k(t['cout'])} | {t['points']:.0f} | {pp} |")
    ajuste = ajuster_lecture(conversations, points, poids)
    if ajuste is None:
        lignes += ["", "Étalonnage impossible : entre deux relevés que rien ne coupe, aucun point pris, ou aucun "
                   "appel chiffré.", ""]
        return lignes, {}
    lecture, par_point = ajuste
    retenu = replace(poids, lecture=lecture)
    valeurs = [t["par_point"] for t in _utilisables(etalonner(conversations, points, retenu)) if t["par_point"]]
    lignes += ["", f"Poids de lecture qui explique le mieux les relevés (hors compactage) : {lecture:.3f} ; "
               f"un point vaut alors {_v(par_point / 1000)} k jetons pondérés, soit {_k(par_point / poids.ecriture_1h)} "
               f"jetons écrits pour une heure ou {_k(par_point / lecture)} jetons lus"
               + (f" ; de {_k(min(valeurs))} à {_k(max(valeurs))} selon l'intervalle (un relevé est arrondi "
                  "au point près)." if valeurs else ".")]
    marge = fourchette(conversations, points, poids)
    if marge:
        (l0, l1), (p0, p1) = marge["lecture"], marge["par_point"]
        lignes.append(f"À l'arrondi des relevés près : lecture de {l0:.3f} à {l1:.3f}, un point de {_v(p0 / 1000)} k "
                      f"à {_v(p1 / 1000)} k jetons pondérés.")
    else:
        lignes.append("À l'arrondi des relevés près, aucun poids de lecture n'explique tous les relevés.")
    for t in etalonner(conversations, points, retenu):
        if t["compactages"]:
            reste = t["points"] - t["cout"] / par_point
            lignes.append(f"Compactage entre {_instant(t['debut'])} et {_instant(t['fin'])} : {t['points']:.0f} points "
                          f"relevés, dont {_v(reste)} que les appels chiffrés n'expliquent pas (à un point près).")
    semaine = points_de_semaine(points)
    if semaine:
        lignes.append(f"Un point de la semaine vaut {_v(semaine['rapport'])} points de la fenêtre "
                      f"({semaine['fenetre']:.0f} contre {semaine['semaine']:.0f} ; de {_v(semaine['bas'])} "
                      f"à {_v(semaine['haut'])} à l'arrondi près).")
    if abs(poids.lecture - lecture) > 0.0005:
        lignes.append(f"Les colonnes en points de ce rapport supposent `--weight-read {lecture:.3f}`.")
    lignes.append("")
    return lignes, {"lecture": lecture, "par_point": par_point, "modele": modele_etalonne(tranches)}


def predire(conversations: list[Conversation], debut: tuple, fin: tuple, poids: Poids,
            valeurs: dict[str, float], defaut: float) -> dict:
    """Les points qu'un intervalle entre deux relevés devrait prendre : le
    coût de chaque modèle divisé par ce que vaut son point (`valeurs`, sinon
    `defaut`), et les points relevés. Un compactage, non chiffré, l'empêche."""
    (t,) = etalonner(conversations, [debut, fin], poids)
    par_modele = {m: c / valeurs.get(m, defaut) for m, c in t["modeles"].items()}
    return {"predits": None if t["compactages"] else sum(par_modele.values()), "releves": t["points"],
            "par_modele": par_modele}


def rapport(conversations: list[Conversation], poids: Poids = Poids(), jours: set[str] | None = None,
            points: list[tuple] | None = None, octets_par_jeton: float = 3.5,
            controles: list[tuple] | None = None) -> str:
    """Le rapport en Markdown : des tableaux d'agrégats, rien de la conversation."""
    lignes = [f"Poids (hypothèse) : entrée {poids.entree}, écriture 5 min {poids.ecriture_5m}, "
              f"écriture 1 h {poids.ecriture_1h}, lecture {poids.lecture}, sortie {poids.sortie}.", ""]
    garder = (lambda j: True) if not jours else (lambda j: j in jours)
    etalonnage, etalon = ([], {})
    if points and len(points) > 1:
        etalonnage, etalon = _rapport_etalonnage(conversations, poids, points)
    par_point = etalon.get("par_point")
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
        lignes.append(f"| {jour} | {modele} | {portee} | {l['conversations']} | {l['appels']} | {_k(l['entree'])} "
                      f"| {_k(l['ecriture_5m'])} | {_k(l['ecriture_1h'])} | {_k(l['lecture'])} | {_k(l['sortie'])} "
                      f"| {_k(l['cout'])} | {_k(l['mediane'])} | {_k(l['maximum'])} |")
    ensemble = totaux["principale"] + totaux["sous-agents"]
    lignes += ["", f"Total pondéré : {_k(ensemble)} ; principale {_pc(totaux['principale'] / ensemble if ensemble else 0)}, "
               f"sous-agents {_pc(totaux['sous-agents'] / ensemble if ensemble else 0)}.", ""]
    lignes += ["## Sous-agents à la fois (maximum du jour, coupé à cinq minutes d'inactivité)", ""]
    lignes += [f"- {j} : {n}" for j, n in sorted(concurrence(conversations).items()) if garder(j)]
    neuf = premiers_appels(conversations, poids)
    lignes += ["", f"Premier appel d'un sous-agent, sur toute la période lue ({neuf['nombre']}) : contexte médian "
               f"{_k(neuf['contexte_median'])}, maximum {_k(neuf['contexte_max'])}, coût médian "
               f"{_k(neuf['cout_median'])} ; {_k(neuf['cout_median_1h'])} si le cache s'écrivait pour une heure."]
    lignes += ["", "## Coût d'un appel tiède selon le contexte (période lue)", "",
               "| modèle | contexte | appels | coût médian | dont lecture | en points |",
               "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for modele in sorted({a.modele for c in conversations for a in c.appels}):
        for t in cout_selon_contexte(conversations, poids, modele=modele):
            if t["appels"]:
                en_points = (f"{_v(t['cout'] / par_point, 2)} (lecture {_v(t['lecture'] / par_point, 2)})"
                             if par_point and modele == etalon.get("modele") else "—")
                lignes.append(f"| {modele} | {_k(t['centre'] - 40_000)} à {_k(t['centre'] + 40_000)} | {t['appels']} "
                              f"| {_k(t['cout'])} | {_k(t['lecture'])} | {en_points} |")
    lignes += ["", "## Reprises après une pause", "",
               "| portée | pause de plus de | reprises | conv. | coût des premiers appels | part du total "
               "| premier appel / appel médian |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for r in resume_pauses(conversations, poids, jours):
        lignes.append(f"| {r['portee']} | {r['seuil_s'] // 60} min | {r['reprises']} | {r['conversations']} "
                      f"| {_k(r['cout'])} | {_pc(r['part'])} | × {r['rapport_median']:.0f} |")
    lignes += ["", "## Compactages", "",
               "| instant | déclencheur | avant | après | résumé | borne basse (modèle) | appel suivant |",
               "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for c in conversations:
        for x in compactages(c, poids, octets_par_jeton):
            if garder(_jour(x["horodatage"])):
                lignes.append(f"| {x['horodatage']:%Y-%m-%d %H:%M} | {x['declencheur']} | {_k(x['avant'])} "
                              f"| {_k(x['apres'] or 0)} | {_k(x['resume_jetons'])} | {_k(x['borne_basse'])} "
                              f"| {_k(x['cout_appel_suivant'])} |")
    lignes += ["", "## Taille de la conversation principale (jetons relus par appel)", "",
               "| jour | appels | médiane | 90e centile | maximum | appels > 400 k |",
               "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for c in conversations:
        if not c.sous_agent:
            for j, t in taille_contexte(c, jours).items():
                lignes.append(f"| {j} | {t['appels']} | {_k(t['mediane'])} | {_k(t['p90'])} | {_k(t['maximum'])} "
                              f"| {t['au_dela_400k']} |")
    inj = injections_socle(conversations)
    lignes += ["", "## Ce que le socle injecte", "", "| jour | nature | nombre | octets | plus grande |",
               "| --- | --- | ---: | ---: | ---: |"]
    for j, natures in sorted(inj["par_jour"].items()):
        if garder(j):
            for n, v in sorted(natures.items()):
                lignes.append(f"| {j} | {n} | {v['nombre']} | {v['octets']} | {v['max']} |")
    if inj["sorties_de_hook"]:
        lignes += ["", f"Sortie entière du hook de démarrage, sur toute la période lue : de {inj['sorties_de_hook'][0]} "
                   f"à {inj['sorties_de_hook'][1]} octets ; l'agent n'en reçoit que la colonne « octets »."]
    revues = tailles(conversations, "dossier de revue", sous_agents=True, par_conversation=True)
    if revues:
        lignes += ["", f"Dossier de revue reçu par un sous-agent (somme de ses lectures) : {len(revues)} sous-agents, "
                   f"de {revues[0]} à {revues[-1]} octets, médiane {statistics.median(revues):.0f}."]
    lignes += ["", "### Ce qu'ils pèsent une fois dans le contexte (toute la période lue)", "",
               f"À {octets_par_jeton} octets par jeton ; chaque appel relit ce qui a été injecté depuis le dernier "
               "compactage.", "", "| portée | nature | conv. | part du contexte | coût pondéré |",
               "| --- | --- | ---: | ---: | ---: |"]
    for portee, sous in (("principale", False), ("sous-agents", True)):
        presence = presence_socle(conversations, poids, octets_par_jeton, sous_agents=sous)
        for n, v in sorted(presence["natures"].items(), key=lambda x: -x[1]["cout"]):
            lignes.append(f"| {portee} | {n} | {v['conversations']} | {_pc(v['part_contexte'])} | {_k(v['cout'])} |")
        sans, avec = part_du_socle(presence, exclure=(AGENTS_SOCLE,)), part_du_socle(presence)
        lignes.append(f"| {portee} | **total** sans AGENTS.md / avec | | {_pc(sans[0])} / {_pc(avec[0])} "
                      f"| {_pc(sans[1])} / {_pc(avec[1])} du coût |")
    lignes.append("")
    limitees = [f for f in fenetres_limitees(conversations, poids) if garder(_jour(f["refus"]))]
    if limitees:
        modele = etalon.get("modele")
        if par_point and modele:
            limitees = valeur_du_point_des_autres(limitees, modele, par_point)
        lignes += ["## Fenêtres de cinq heures closes par un refus", "",
                   "| ouverture | refus | appels | coût pondéré | dont sous-agents | par modèle "
                   f"| points de {modele or 'l’étalonné'} | un point des autres |",
                   "| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |"]
        for f in limitees:
            modeles = ", ".join(f"{m} {_k(v)}" for m, v in sorted(f["par_modele"].items()))
            connus = _v(f["points_du_modele"], 0) if "points_du_modele" in f else "—"
            autres = _k(f["autres_par_point"]) if f.get("autres_par_point") else "—"
            lignes.append(f"| {f['debut']:%m-%d %H:%M} | {f['refus']:%m-%d %H:%M} | {f['appels']} | {_k(f['cout'])} "
                          f"| {_k(f['cout_sous_agents'])} | {modeles} | {connus} | {autres} |")
        valeurs = sorted(f["autres_par_point"] for f in limitees if f.get("autres_par_point"))
        if valeurs:
            lignes += ["", f"Un point des autres modèles : médiane {_k(statistics.median(valeurs))}, de {_k(valeurs[0])} "
                       f"à {_k(valeurs[-1])} ({len(valeurs)} fenêtres sur {len(limitees)})."]
        lignes.append("")
    if controles and par_point:
        # la valeur du point des autres modèles se prend sur toutes les fenêtres closes, pas sur les jours gardés
        autres = [f["autres_par_point"] for f in valeur_du_point_des_autres(fenetres_limitees(conversations, poids),
                                                                            etalon["modele"], par_point)
                  if f.get("autres_par_point")]
        defaut = statistics.median(autres) if autres else par_point
        for c in controles:
            p = predire(conversations, points[-1], c, poids, {etalon["modele"]: par_point}, defaut)
            if p["predits"] is None:
                etalonnage.append(f"Contrôle jusqu'à {_instant(c[0])} : un compactage s'y trouve, pas de prédiction.")
                continue
            detail = ", ".join(f"{m} {_v(v)}" for m, v in sorted(p["par_modele"].items()))
            etalonnage.append(f"Contrôle hors échantillon, de {_instant(points[-1][0])} à {_instant(c[0])} : "
                              f"{_v(p['predits'])} points prédits ({detail} ; les autres modèles à {_k(defaut)} "
                              f"par point), {p['releves']:.0f} relevés.")
        etalonnage.append("")
    return "\n".join(lignes + etalonnage)


def main(argv: list[str] | None = None) -> int:
    """La ligne de commande : le dossier des transcriptions en argument."""
    p = argparse.ArgumentParser(description="La consommation d'une session, lue dans ses transcriptions (B-0173).")
    p.add_argument("folder", type=Path, help="le dossier des transcriptions (les <id>.jsonl et leurs sous-agents)")
    p.add_argument("--session", help="le début de l'identifiant d'une conversation principale")
    p.add_argument("--day", action="append", help="un jour UTC à garder (AAAA-MM-JJ), répétable")
    p.add_argument("--until", help="ignorer ce qui suit cet instant (AAAA-MM-JJTHH:MM:SSZ ; UTC sans fuseau)")
    p.add_argument("--point", action="append", default=[],
                   help="un relevé de la fenêtre de cinq heures : INSTANT,PART[/SEMAINE], point décimal (répétable)")
    p.add_argument("--control", action="append", default=[],
                   help="un relevé hors échantillon, prédit depuis le dernier --point (même forme, répétable)")
    p.add_argument("--weight-input", type=float, default=Poids.entree)
    p.add_argument("--weight-write-5m", type=float, default=Poids.ecriture_5m)
    p.add_argument("--weight-write-1h", type=float, default=Poids.ecriture_1h)
    p.add_argument("--weight-read", type=float, default=Poids.lecture)
    p.add_argument("--weight-output", type=float, default=Poids.sortie)
    p.add_argument("--bytes-per-token", type=float, default=3.5,
                   help="pour estimer en jetons ce que le socle injecte (hypothèse : 3,5 pour un texte français)")
    args = p.parse_args(argv)
    try:
        jusqu_a = _date(args.until) if args.until else None
        points = sorted(lire_point(x) for x in args.point)
        controles = sorted(lire_point(x) for x in args.control)
    except ValueError as erreur:
        p.error(str(erreur))
    poids = Poids(args.weight_input, args.weight_write_5m, args.weight_write_1h, args.weight_read, args.weight_output)
    conversations = lire_dossier(args.folder, args.session)
    if jusqu_a:
        conversations = tronquer(conversations, jusqu_a)
    if not conversations:
        print(f"aucune transcription dans {args.folder}", file=sys.stderr)
        return 1
    print(rapport(conversations, poids, set(args.day) if args.day else None, points, args.bytes_per_token, controles))
    return 0


if __name__ == "__main__":
    sys.exit(main())
