"""L'état dérivé : calculé à chaque démarrage de session et après chaque
compactage, jamais écrit à la main.

Tout ce qui est imprimé ici vient de git, de la mémoire ou de la trace des
hooks : rien n'est recopié, donc rien ne peut vieillir. Ce script ne doit
jamais empêcher une session de démarrer : un échec se traduit par une ligne
en moins, jamais par un code non nul.
"""

from __future__ import annotations

import re
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


def _gh_json(racine, chemin: str):
    """Une réponse de l'API de GitHub par `gh`, ou `None`."""
    import json

    try:
        p = subprocess.run(["gh", "api", chemin], cwd=racine, capture_output=True, text=True, timeout=5)
        return json.loads(p.stdout) if p.returncode == 0 else None
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return None


def nom_de_la_ci(projet: config.Projet) -> str:
    """Le nom du travail de la CI du socle, tel que GitHub l'exige."""
    texte = outils.lire_a(projet.racine, None, ".github/workflows/socle.yml") or ""
    m = re.search(r"(?m)^ {4}name:\s*(.+?)\s*$", texte)
    return m.group(1).strip("'\"") if m else "Socle"


def ci_exigee(projet: config.Projet) -> tuple[bool | None, str]:
    """La CI du socle est-elle exigée avant de fusionner sur la branche par
    défaut, par un ensemble de règles ou une protection de branche de
    GitHub ? Sans elle, une CI rouge n'empêche pas de fusionner : la
    garantie « seule la CI est incontournable » tombe (R1 de la passe de
    recul). `None` quand on ne peut pas le savoir, avec la raison ; sinon
    le nom de la branche, et si la revue des propriétaires du code est
    exigée aussi."""
    from socle import liens

    url = liens.url_depot(projet) or ""
    if not url.startswith("https://github.com/"):
        return None, "dépôt hors de GitHub"
    nom = (outils.branche_par_defaut(projet.racine) or "").removeprefix("origin/")
    if not nom:
        return None, "aucune branche par défaut connue"
    if not shutil.which("gh"):
        return None, "gh absent"
    depot = url.removeprefix("https://github.com/")
    regles = _gh_json(projet.racine, f"repos/{depot}/rules/branches/{nom}")
    branche = _gh_json(projet.racine, f"repos/{depot}/branches/{nom}")
    if not isinstance(regles, list) or not isinstance(branche, dict):
        return None, "gh non authentifié, ou réponse illisible"
    ci = nom_de_la_ci(projet)
    exigees = [c.get("context") for r in regles if r.get("type") == "required_status_checks"
               for c in (r.get("parameters") or {}).get("required_status_checks", [])]
    classique = ((branche.get("protection") or {}).get("required_status_checks") or {})
    if classique.get("enforcement_level", "off") != "off":
        exigees += classique.get("contexts", []) + [c.get("context") for c in classique.get("checks", [])]
    revue = any((r.get("parameters") or {}).get("require_code_owner_review") for r in regles
                if r.get("type") == "pull_request")
    return ci in exigees, nom + (" ; revue des propriétaires du code exigée" if revue else
                                 " ; revue des propriétaires du code non exigée")


def _balayage(projet: config.Projet, elements: list) -> list[str]:
    """La ligne du balayage de mutation planifié, quand l'adaptateur en
    déclare un ; endormi ou arrêté, le réveiller revient à l'humain."""
    from socle import humain, mutation

    niveau, message, _, page = mutation.etat_du_balayage(
        projet, outils.fichiers_courants(projet.racine), lambda f: outils.lire_a(projet.racine, None, f))
    if not message:
        return []
    if niveau == "erreur":
        elements.append(humain.Element("action", f"remettre en marche le balayage de mutation : {message}", page or ""))
    return [f"mutation : {message}"]


def page_protection(projet: config.Projet) -> str | None:
    """La page des réglages de GitHub où l'humain pose ses ensembles de
    règles (rulesets)."""
    from socle import liens

    url = liens.url_depot(projet) or ""
    return f"{url}/settings/rules" if url.startswith("https://github.com/") else None


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
    try:
        from socle import humain

        elements = humain.a_faire(projet)
        exigee, detail = ci_exigee(projet)
        nom = detail.split(" ; ")[0]
        if exigee is False:
            elements.append(humain.Element(
                "action", f"protéger la branche `{nom}` : y exiger la CI « {nom_de_la_ci(projet)} » avant toute "
                "fusion, et la revue des propriétaires du code (CODEOWNERS)", page_protection(projet) or ""))
        lignes += _balayage(projet, elements)
        if exigee:
            lignes.append(f"branche  : {detail.replace(' ; ', ' — CI du socle exigée avant fusion ; ', 1)}")
        elif exigee is False:
            lignes.append(f"branche  : {nom} — CI du socle NON exigée : une CI rouge n'empêche pas de fusionner")
        else:
            lignes.append(f"branche  : protection inconnue ({detail})")
        lignes += humain.texte(elements)
    except Exception as e:
        lignes.append(f"ce qui revient à l'humain : incalculable ({type(e).__name__}: {e})")
    try:
        from socle import humain

        faits = humain.fait_par_l_humain(projet)
        if faits:
            lignes.append(f"écrit par l'humain lui-même depuis le dernier commit de l'agent : {len(faits)} "
                          "— à lui citer, avec le lien")
            for e in faits:
                lignes.append(f"  {e.genre} : {e.quoi}")
                lignes.append(f"    {e.lien}")
    except Exception as e:
        lignes.append(f"ce que l'humain a écrit lui-même : incalculable ({type(e).__name__}: {e})")
    lignes += _hooks(racine)
    from socle import prive

    lignes.append(prive.ligne_etat(projet))
    lignes.append("vérifier : `python3 .socle/socle verify --rapide` (tout : sans `--rapide`)")
    if contenus:
        # Le chantier actif et les faits, publics puis privés (B-0029) : une
        # mémoire privée lisible ici en fait partie, illisible elle est
        # signalée plus haut.
        ch = projet.chemins
        for chemin in (ch.actif, ch.canonique, ch.dans_prive(ch.actif), ch.dans_prive(ch.canonique)):
            texte = outils.lire_a(racine, None, chemin)
            if texte is not None and memoire.est_prive(chemin) and not memoire.lisible(texte):
                continue
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
            mem = [c for c in changes if memoire.est_memoire(c)]
            res.append(f"depuis la base : {len(code)} fichier(s) de code, {len(docs)} de doc, {len(mem)} de mémoire")
            if code and not mem:
                res.append("  ^ du code a changé et la mémoire non : la fin de tour le refusera")
    else:
        res.append("base     : aucune branche par défaut connue")
    res.append(f"CI       : {_ligne_ci(racine, branche)}")
    return res


def _memoire(mem: memoire.Memoire, projet) -> list[str]:
    faits = Counter(e.statut or "?" for e in mem.entrees("F") if not e.archivee)
    libelles = {"mesure": "mesuré(s)", "suppose": "supposé(s)", "refute": "réfuté(s)", "valide": "validé(s)"}
    detail = ", ".join(f"{n} {libelles.get(s, s)}" for s, n in sorted(faits.items()))
    adrs = list(mem.entrees("ADR"))
    journal = sorted((e.id for e in mem.entrees("J")), key=lambda i: i.lstrip("P"))
    res = [
        f"mémoire  : {sum(faits.values())} fait(s) ({detail or 'aucun'}) · {len(adrs)} décision(s) · "
        f"journal : {len(journal)} entrée(s), dernière {journal[-1] if journal else '—'}"
    ]
    # L'index des décisions, que le cadrage prévoit : une ligne par décision
    # en vigueur, à lire en entier (`socle show ADR-NNNN`) avant d'en rouvrir une.
    # Toutes, rejetées et remplacées comprises : on ne rouvre pas non plus une
    # décision écartée. L'empreinte de l'index se cite dans une décision
    # nouvelle (`lu : decisions@…`, ADR-0008).
    lignes_index = memoire.lignes_index(mem, "decisions")
    if lignes_index:
        res.append(f"décisions, index decisions@{memoire.empreinte_index(mem, 'decisions')} "
                   "(une en entier : `python3 .socle/socle show ADR-NNNN`) :")
        res += [f"  {l}" for l in lignes_index]
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
    t = outils.git(mem.racine, "log", "-1", "--format=%ct", "--", config.chemins(mem.racine).actif, check=False).strip() \
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
    lignes = config.lire_trace(racine)
    if not lignes:
        return ["hooks    : aucune trace — ils n'ont encore jamais tiré dans ce clone"]
    dernier = " ".join(lignes[-1].split("\t")[:2])
    return [f"hooks    : {len(lignes)} déclenchement(s) tracé(s), dernier : {dernier}"]

