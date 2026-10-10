"""L'état dérivé : calculé à chaque démarrage de session et après chaque
compactage, jamais écrit à la main.

Tout ce qui est imprimé ici vient de git, de la mémoire ou de la trace des
hooks : rien n'est recopié, donc rien ne peut vieillir. Ce script ne doit
jamais empêcher une session de démarrer : un échec se traduit par une ligne
en moins, jamais par un code non nul.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from collections import Counter

from socle import config, demandes, memoire, outils


def _ligne_ci(racine, branche) -> str:
    """L'état de la CI, si `gh` est là et authentifié. Sinon on le dit : le
    moteur n'exige aucun service externe."""
    if not shutil.which("gh"):
        return "non disponible localement (gh absent) — voir la pull request"
    try:
        p = subprocess.run(
            ["gh", "run", "list", "--branch", branche, "--limit", "1",
             "--json", "status,conclusion,workflowName,headSha"],
            cwd=racine, capture_output=True, text=True, timeout=8,
        )
    except (subprocess.TimeoutExpired, OSError):
        return "non disponible (gh ne répond pas)"
    if p.returncode != 0 or not p.stdout.strip() or p.stdout.strip() == "[]":
        return "non disponible (gh non authentifié ou aucune exécution)"
    import json

    try:
        r = json.loads(p.stdout)[0]
    except (ValueError, IndexError):
        return "non disponible (réponse illisible)"
    return f"{r.get('workflowName')} : {r.get('conclusion') or r.get('status')} sur {r.get('headSha', '')[:7]}"


def calculer(projet: config.Projet, contenus: bool = True) -> str:
    racine = projet.racine
    lignes = []
    nom = racine.name
    lignes.append(f"== {nom} — état dérivé par `socle state`, rien de recopié ==")
    try:
        lignes += _git(racine, projet)
    except outils.ErreurGit as e:
        lignes.append(f"git : indisponible ({e})")
    try:
        mem = memoire.Memoire.charger(racine)
        lignes += _memoire(mem, projet)
    except Exception as e:  # l'état ne bloque jamais le démarrage
        lignes.append(f"mémoire : illisible ({type(e).__name__}: {e}) — lancer `python3 .socle/socle check`")
    try:
        lignes += _demandes(racine)
    except Exception as e:
        lignes.append(f"demandes : illisibles ({type(e).__name__}: {e})")
    lignes += _hooks(racine)
    lignes.append("mémoire privée : non configurée (mode public seul)" if not projet.pol("private", "mode")
                  else _prive(racine, projet))
    lignes.append("vérifier : `python3 .socle/socle verify --rapide` (tout : sans `--rapide`)")
    if contenus:
        for chemin in ("memoire/actif.md", "memoire/canonique.md"):
            texte = outils.lire_a(racine, None, chemin)
            if texte is not None:
                lignes.append("")
                lignes.append(f"--- {chemin} ---")
                lignes.append(texte.rstrip())
    return "\n".join(lignes)


def _git(racine, projet) -> list[str]:
    if not outils.est_depot(racine) or not outils.a_des_commits(racine):
        return ["commit   : aucun (dépôt neuf)"]
    res = []
    court = outils.git(racine, "rev-parse", "--short", "HEAD").strip()
    branche = outils.git(racine, "rev-parse", "--abbrev-ref", "HEAD").strip()
    sales = [l for l in outils.git(racine, "status", "--porcelain").splitlines() if l.strip()]
    propre = "arbre propre" if not sales else f"ATTENTION, {len(sales)} fichier(s) non commité(s)"
    res.append(f"commit   : {court} sur {branche} ({propre})")
    defaut = outils.branche_par_defaut(racine)
    if defaut:
        non = outils.git(racine, "log", "--oneline", f"{defaut}..HEAD", check=False).splitlines()
        res.append(f"base     : {defaut} — non fusionné : {len(non)} commit(s)")
        res += [f"  {l}" for l in non[:10]]
        if len(non) > 10:
            res.append(f"  … et {len(non) - 10} autre(s)")
        base = outils.base_de_travail(racine)
        if base:
            changes = outils.fichiers_changes(racine, base)
            code = outils.filtrer(changes, projet.chemins_code())
            docs = [c for c in changes if c.endswith(".md")]
            mem = [c for c in changes if c.startswith(config.MEMOIRE + "/")]
            res.append(f"depuis la base : {len(code)} fichier(s) de code, {len(docs)} de doc, {len(mem)} de mémoire")
            if code and not mem:
                res.append("  ^ du code a changé et la mémoire non : la fin de tour le refusera")
    else:
        res.append("base     : aucune branche par défaut connue")
    res.append(f"CI       : {_ligne_ci(racine, branche)}")
    return res


def _memoire(mem: memoire.Memoire, projet) -> list[str]:
    faits = Counter(e.statut or "?" for e in mem.entrees("F") if not e.archivee)
    detail = ", ".join(f"{n} {s}" for s, n in sorted(faits.items()))
    adrs = list(mem.entrees("ADR"))
    journal = sorted((e.id for e in mem.entrees("J")), key=lambda i: i.lstrip("P"))
    res = [
        f"mémoire  : {sum(faits.values())} fait(s) ({detail or 'aucun'}) · {len(adrs)} décision(s) · "
        f"journal : {len(journal)} entrée(s), dernière {journal[-1] if journal else '—'}"
    ]
    backlog = [e for e in mem.entrees("B") if not e.archivee]
    par = Counter(e.statut for e in backlog)
    res.append(
        f"backlog  : {par.get('ouvert', 0)} ouvert(s), {par.get('en-cours', 0)} en cours, "
        f"{par.get('bloque', 0)} bloqué(s), {par.get('fait', 0) + par.get('abandonne', 0)} clos à archiver"
    )
    for statut, libelle in (("en-cours", "en cours"), ("bloque", "bloqué")):
        for e in [e for e in backlog if e.statut == statut][:8]:
            res.append(f"  {libelle} : {e.id} — {e.titre}")
    jours = projet.gf("staleness", "active_days", defaut=7)
    t = outils.git(mem.racine, "log", "-1", "--format=%ct", "--", "memoire/actif.md", check=False).strip() \
        if outils.a_des_commits(mem.racine) else ""
    if t:
        age = (time.time() - float(t)) / 86400
        if age > jours:
            res.append(f"péremption : chantier actif inchangé depuis {age:.0f} jours (seuil {jours})")
    return res


def _demandes(racine) -> list[str]:
    toutes = demandes.toutes(racine)
    attente = [d for d in toutes if d.reponse is None and d.statut == "en attente"]
    res = [f"demandes humaines en attente : {len(attente)}"]
    for d in attente:
        date = d.entree.meta.get("date", "") if d.entree else ""
        res.append(f"  {d.id} — {d.entree.titre if d.entree else d.chemin}{f' (du {date})' if date else ''}")
    renvoyees = [d for d in toutes if d.statut == "renvoyée"]
    for d in renvoyees:
        res.append(f"  RENVOYÉE (contexte insuffisant) : {d.id} — à réécrire en une demande qui la remplace")
    return res


def _hooks(racine) -> list[str]:
    trace = racine / config.TRACE
    if not trace.is_file() or not trace.read_text(encoding="utf-8", errors="replace").strip():
        return ["hooks    : aucune trace — ils n'ont encore jamais tiré dans ce clone"]
    lignes = trace.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    dernier = " ".join(lignes[-1].split("\t")[:2])
    return [f"hooks    : {len(lignes)} déclenchement(s) tracé(s), dernier : {dernier}"]


def _prive(racine, projet) -> str:
    mode = projet.pol("private", "mode")
    if (racine / config.MEMOIRE / "prive").is_dir():
        return f"mémoire privée : disponible (mode {mode})"
    return (f"mémoire privée : INDISPONIBLE (mode {mode}) — les contrôles qui l'exigent le signalent ; "
            "ne pas conclure sur ce qui en dépend")
