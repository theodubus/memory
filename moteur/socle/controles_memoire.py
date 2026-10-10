"""Contrôles de la mémoire et des demandes humaines.

Chaque fonction est un contrôle déterministe : elle ajoute des constats au
rapport, et un constat de gravité « erreur » fait échouer le passage.
"""

from __future__ import annotations

import re
import subprocess
import time
from functools import lru_cache

from socle import config, demandes, memoire, outils
from socle.contexte import controle

FICHIERS_REQUIS = ("memoire/canonique.md", "memoire/actif.md", "memoire/backlog.md")
TYPE_DE_COUCHE = {v: k for k, v in memoire.TYPES.items()}
TRANSITIONS_ADR = {
    ("proposee", "acceptee"), ("proposee", "rejetee"), ("proposee", "abandonnee"),
    ("acceptee", "remplacee"), ("acceptee", "abandonnee"),
}


def est_prive(chemin: str) -> bool:
    return chemin.startswith(config.MEMOIRE + "/prive/")


# --------------------------------------------------------------------------
# Format
# --------------------------------------------------------------------------


@controle("memoire.format")
def format_memoire(ctx, r):
    """En-têtes, couches, identifiants, statuts : la mémoire se lit par script."""
    for requis in FICHIERS_REQUIS:
        if requis not in ctx.fichiers:
            r.erreur("memoire.format", "fichier de mémoire requis absent", requis)
    for chemin, f in sorted(ctx.memoire.fichiers.items()):
        attendue = memoire.couche_attendue(chemin)
        if attendue == "inconnue":
            r.erreur("memoire.format", "fichier hors des couches connues de la mémoire", chemin)
            continue
        if f.couche is None:
            r.erreur("memoire.format", "en-tête `<!-- socle: couche=… zone=… -->` absent", chemin, 1)
            continue
        if f.couche != attendue:
            r.erreur("memoire.format", f"couche déclarée « {f.couche} », l'emplacement impose « {attendue} »", chemin, 1)
        zone_lieu = "privee" if est_prive(chemin) else "publique"
        if f.zone not in memoire.ZONES:
            r.erreur("memoire.format", "zone non déclarée (`zone=publique` ou `zone=privee`)", chemin, 1)
        elif f.zone != zone_lieu:
            r.erreur("memoire.format", f"zone déclarée « {f.zone} » dans un emplacement « {zone_lieu} »", chemin, 1)
        _format_entrees(r, chemin, f, attendue, zone_lieu == "privee")

    for ident, defs in ctx.memoire.definitions().items():
        if len(defs) > 1:
            lieux = ", ".join(f"{d.fichier}:{d.ligne}" for d in defs)
            r.erreur("memoire.format", f"`{ident}` est défini {len(defs)} fois ({lieux})", defs[0].fichier, defs[0].ligne)


def _format_entrees(r, chemin, f, couche, prive):
    nom = chemin.rsplit("/", 1)[-1]
    if couche == "actif":
        for e in f.entrees:
            r.erreur("memoire.format", f"`{e.id}` défini dans le chantier actif, qui est réécrit : "
                     "un identifiant stable vit dans une couche durable", chemin, e.ligne)
        return
    attendu = TYPE_DE_COUCHE[couche]
    if couche == "journal" and not re.match(r"^\d{4}-\d{2}\.md$", nom):
        r.erreur("memoire.format", "un fichier de journal se nomme `AAAA-MM.md`", chemin)
    premiers = [e for e in f.entrees if e.parent is None]
    if couche in ("decisions", "demandes"):
        if len(premiers) != 1:
            r.erreur("memoire.format", f"un fichier de {couche} porte exactement une entrée ({len(premiers)} trouvée(s))", chemin)
        elif not nom.startswith(premiers[0].id):
            r.erreur("memoire.format", f"le nom du fichier doit commencer par {premiers[0].id}", chemin)
    for e in f.entrees:
        if e.prive != prive:
            r.erreur("memoire.format", f"`{e.id}` : un identifiant {'privé commence par P' if prive else 'public ne commence pas par P'}", chemin, e.ligne)
        if e.parent is not None:
            if couche != "journal" or e.type not in ("F", "B"):
                r.erreur("memoire.format", f"`{e.id}` imbriqué hors d'une archive de journal", chemin, e.ligne)
            continue
        if e.type != attendu:
            r.erreur("memoire.format", f"`{e.id}` n'a pas sa place dans la couche « {couche} »", chemin, e.ligne)
            continue
        if couche == "journal":
            date = e.id.lstrip("P")[2:12]
            if not nom.startswith(date[:7]):
                r.erreur("memoire.format", f"`{e.id}` est daté hors du mois de son fichier", chemin, e.ligne)
        statuts = memoire.STATUTS.get(e.type)
        if statuts is not None:
            if not e.statut:
                r.erreur("memoire.format", f"`{e.id}` sans `statut` (attendu : {', '.join(sorted(statuts))})", chemin, e.ligne)
            elif e.statut not in statuts:
                r.erreur("memoire.format", f"`{e.id}` : statut « {e.statut} » inconnu (attendu : {', '.join(sorted(statuts))})", chemin, e.ligne)
        if e.barre and e.type == "F" and e.statut != "refute":
            r.erreur("memoire.format", f"`{e.id}` est barré sans être « réfuté »", chemin, e.ligne)


# --------------------------------------------------------------------------
# Références
# --------------------------------------------------------------------------

LIEN_RE = re.compile(r"!?\[[^\]\n]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
CODE_EN_LIGNE = re.compile(r"`([^`\n]+)`")
INTERDITS_CHEMIN = set("*?[]{}<>$|~\"' =,;()")


def slug(titre: str) -> str:
    """L'ancre que GitHub donne à un titre."""
    t = re.sub(r"`|\*\*|__", "", titre.strip().lower())
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def ancres(texte: str) -> set[str]:
    res, vus = set(), {}
    for _, ligne, code in memoire.lignes_hors_code(texte):
        if code:
            continue
        m = memoire.TITRE_RE.match(ligne)
        if m:
            s = slug(m["reste"])
            n = vus.get(s, 0)
            res.add(s if n == 0 else f"{s}-{n}")
            vus[s] = n + 1
    return res


def _existe(ctx, chemin: str) -> bool:
    chemin = chemin.strip("/")
    if chemin in ctx._cache.setdefault("ensemble", set(ctx.fichiers)) or chemin == "":
        return True
    dossiers = ctx._cache.get("dossiers")
    if dossiers is None:
        dossiers = set()
        for f in ctx.fichiers:
            parts = f.split("/")
            for i in range(1, len(parts)):
                dossiers.add("/".join(parts[:i]))
        ctx._cache["dossiers"] = dossiers
    return chemin in dossiers


@lru_cache(maxsize=4096)
def _ignore(racine, chemin: str) -> bool:
    r = subprocess.run(["git", "check-ignore", "-q", "--no-index", chemin], cwd=racine, capture_output=True)
    return r.returncode == 0


def _racines(ctx) -> set[str]:
    if "racines" not in ctx._cache:
        ctx._cache["racines"] = {f.split("/", 1)[0] for f in ctx.fichiers}
    return ctx._cache["racines"]


def _normaliser_chemin(base_dir: str, cible: str) -> str:
    parts = [] if cible.startswith("/") else [p for p in base_dir.split("/") if p]
    for p in cible.split("/"):
        if p in ("", "."):
            continue
        if p == "..":
            if parts:
                parts.pop()
            continue
        parts.append(p)
    return "/".join(parts)


def textes_scannes(ctx) -> dict[str, str]:
    motifs = ctx.projet.gf("references", "scan", defaut=["**/*.md"])
    res = ctx.textes(motifs, ctx.projet.exclusions_docs())
    for chemin, f in ctx.memoire.fichiers.items():
        res.setdefault(chemin, f.texte)
    return res


@controle("memoire.references")
def references(ctx, r):
    """Tout identifiant, commit, fichier, lien ou chemin cité existe."""
    defs = ctx.memoire.definitions()
    prive_dispo = any(est_prive(c) for c in ctx.memoire.fichiers)
    for chemin, texte in sorted(textes_scannes(ctx).items()):
        dossier = chemin.rsplit("/", 1)[0] if "/" in chemin else ""
        for ident, ligne in memoire.mentions(texte):
            if ident.startswith("P"):
                if not est_prive(chemin) or not prive_dispo:
                    continue  # fuite : `memoire.prive` ; indisponible : signalé à part
            if ident not in defs:
                r.erreur("memoire.references", f"`{ident}` ne désigne aucune entrée de la mémoire", chemin, ligne)
        for i, ligne, code in memoire.lignes_hors_code(texte):
            if code:
                continue
            for type_, cible in memoire.references(ligne):
                if type_ == "id":
                    continue
                faute = verifier_ref(ctx, type_, cible)
                if faute:
                    r.erreur("memoire.references", faute, chemin, i)
            for m in LIEN_RE.finditer(ligne):
                faute = _verifier_lien(ctx, chemin, dossier, m.group(1))
                if faute:
                    r.erreur("memoire.references", faute, chemin, i)
            sans_refs = memoire.REF_RE.sub(" ", ligne)
            for m in CODE_EN_LIGNE.finditer(sans_refs):
                faute = _verifier_chemin_cite(ctx, m.group(1))
                if faute:
                    r.erreur("memoire.references", faute, chemin, i)


def verifier_ref(ctx, type_: str, cible: str) -> str | None:
    if re.search(r"[<>…]", cible):
        return None  # un gabarit (`commit:<sha>`), pas une référence
    if type_ == "commit":
        if not re.fullmatch(r"[0-9a-f]{7,40}", cible):
            return f"`commit:{cible}` n'est pas un SHA"
        if not outils.objet_existe(ctx.racine, cible):
            return f"`commit:{cible}` n'existe pas dans ce dépôt (historique complet ? `fetch-depth: 0`)"
    elif type_ == "fichier":
        chemin = re.split(r"[#]|:(?=\d)", cible, maxsplit=1)[0]
        if not _existe(ctx, chemin) and not _ignore(ctx.racine, chemin):
            return f"`fichier:{cible}` : {chemin} n'existe pas"
    elif type_ == "cmd":
        premier = cible.split()[0] if cible.split() else ""
        if "/" in premier and not _existe(ctx, premier.removeprefix("./")):
            return f"`cmd:{cible}` : {premier} n'existe pas"
    return None


def _verifier_lien(ctx, chemin_doc: str, dossier: str, cible: str) -> str | None:
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", cible) or cible.startswith("//"):
        return None  # URL : jamais suivie, aucun service externe
    chemin, _, ancre = cible.partition("#")
    if chemin:
        cible_n = _normaliser_chemin(dossier, chemin)
        if not _existe(ctx, cible_n) and not _ignore(ctx.racine, cible_n):
            return f"lien mort : {cible}"
    else:
        cible_n = chemin_doc
    if ancre and cible_n.endswith(".md"):
        texte = ctx.lire(cible_n)
        if texte is not None and ancre not in ancres(texte):
            return f"ancre morte : {cible}"
    return None


def _verifier_chemin_cite(ctx, jeton: str) -> str | None:
    """Un chemin du dépôt cité entre accents graves. Ne juge que ce qui en a
    clairement la forme et commence par une racine du dépôt."""
    j = jeton.strip()
    if "/" not in j or any(c in INTERDITS_CHEMIN for c in j):
        return None
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", j) or j.startswith(("/", "../")):
        return None
    j = j.removeprefix("./")
    j = re.sub(r"(:\d+)+$", "", j).split("#", 1)[0]
    dossier = j.endswith("/")
    j = j.rstrip("/")
    if not j or j.split("/", 1)[0] not in _racines(ctx):
        return None
    # Un répertoire ignoré (`/tools/arbiters/`) ne se reconnaît qu'avec sa
    # barre finale : sans elle, git ne sait pas que c'est un répertoire.
    if _existe(ctx, j) or _ignore(ctx.racine, j + "/" if dossier else j):
        return None
    return f"chemin cité inexistant : `{jeton}`"


@controle("memoire.prive")
def prive(ctx, r):
    """Aucun identifiant privé dans un fichier public : le public ne référence
    jamais le privé."""
    moteur = ctx.projet.dossier_moteur.rstrip("/") + "/"
    for chemin in ctx.fichiers:
        if est_prive(chemin) or chemin.startswith((config.ARCHIVES + "/", moteur)):
            continue
        texte = ctx.lire(chemin)
        if texte is None or "\0" in texte[:4096] or len(texte) > 2_000_000:
            continue
        for ident, ligne in memoire.mentions(texte):
            if ident.startswith("P"):
                r.erreur("memoire.prive", f"identifiant privé `{ident}` dans un fichier public", chemin, ligne)


# --------------------------------------------------------------------------
# Lecture prouvée (ADR-0008)
# --------------------------------------------------------------------------


def _entree_englobante(mem: memoire.Memoire, chemin: str, ligne: int) -> memoire.Entree | None:
    f = mem.fichiers.get(chemin)
    if f is None:
        return None
    dedans = [e for e in f.entrees if e.ligne <= ligne <= e.ligne + e.texte.count("\n")]
    return max(dedans, key=lambda e: e.ligne) if dedans else None


@controle("memoire.lectures", base=True)
def lectures(ctx, r):
    """Une citation `ID@empreinte` ajoutée désigne la version actuelle de
    l'entrée ; une décision, une demande ou un sujet de backlog nouveaux
    prouvent ce qu'ils ont lu avant d'être écrits."""
    mem, base = ctx.memoire, ctx.memoire_base
    defs = mem.definitions()
    nouveaux = set(defs) - set(base.definitions())
    for chemin, texte in sorted(textes_scannes(ctx).items()):
        avant = ctx.lire_base(chemin) or ""
        deja = {(i, h) for i, h, _ in memoire.citations(avant)}
        for ident, h, ligne in memoire.citations(texte):
            if (ident, h) in deja or ident not in defs:
                continue
            if memoire.empreinte_entree(defs[ident][0]) != h:
                r.erreur("memoire.lectures", f"`{ident}@{h}` ne correspond pas à la version actuelle de {ident} "
                         f"(lue avant un changement, ou inventée) : la relire, `python3 .socle/socle show {ident}`, "
                         "et citer l'empreinte affichée", chemin, ligne)
        deja_i = {(i, h) for i, h, _ in memoire.citations_index(avant)}
        for index, h, ligne in memoire.citations_index(texte):
            if (index, h) in deja_i:
                continue
            soi = _entree_englobante(mem, chemin, ligne)
            sauf = {soi.id} if soi else set()
            # Les entrées du même index ajoutées après celle qui cite : elle
            # ne pouvait pas les lire, et elles ne périment pas sa lecture.
            apres = {n for n in nouveaux if soi and defs[n][0].type == soi.type and n > soi.id}
            permises = {
                memoire.empreinte_index(mem, index, sauf),
                memoire.empreinte_index(mem, index, sauf | apres),
                memoire.empreinte_index(mem, index, sauf | nouveaux),
                memoire.empreinte_index(base, index),
            }
            if h not in permises:
                r.erreur("memoire.lectures", f"`{index}@{h}` ne correspond à aucune version récente de l'index : "
                         f"le relire, `python3 .socle/socle show --index {index}`, et citer l'empreinte affichée",
                         chemin, ligne)

    # Ce que les entrées nouvelles doivent prouver avoir lu.
    for ident in sorted(nouveaux):
        e = defs[ident][0]
        if e.archivee:
            continue
        if e.type == "ADR" and not any(i == "decisions" for i, _, _ in memoire.citations_index(e.texte)):
            r.erreur("memoire.lectures", f"décision nouvelle `{ident}` sans `lu : decisions@…` : consulter l'index "
                     "des décisions avant d'en ajouter une (`socle show --index decisions`)", e.fichier, e.ligne)
        if e.type == "B" and not any(i == "backlog" for i, _, _ in memoire.citations_index(e.texte)):
            r.erreur("memoire.lectures", f"sujet nouveau `{ident}` sans `lu : backlog@…` : consulter le backlog avant "
                     "d'y ajouter, pour ne pas dupliquer (`socle show --index backlog`)", e.fichier, e.ligne)
        if e.type in ("ADR", "D"):
            prouves = {i for i, _, _ in memoire.citations(e.texte)}
            for cite in sorted({i for i, _ in memoire.mentions(e.texte)} - prouves - {ident}):
                r.erreur("memoire.lectures", f"`{ident}` s'appuie sur `{cite}` sans montrer l'avoir lu : citer "
                         f"`{cite}@<empreinte>`, l'empreinte que donne `socle show {cite}`", e.fichier, e.ligne)


# --------------------------------------------------------------------------
# Preuves, backlog
# --------------------------------------------------------------------------

TYPES_PREUVE = {"commit", "fichier", "cmd", "id"}


@controle("memoire.preuves")
def preuves(ctx, r):
    """Un fait mesuré pointe vers sa preuve ; un fait réfuté garde sa trace ; un
    fait validé cite la demande que l'humain a validée."""
    par_id = {d.id: d for d in ctx.demandes if d.id}
    for e in ctx.memoire.entrees("F"):
        if e.statut == "mesure":
            if not {t for t, _ in e.refs("preuve")} & TYPES_PREUVE:
                r.erreur("memoire.preuves", f"`{e.id}` est « mesuré » sans `preuve` (commit:, fichier:, cmd: ou identifiant)", e.fichier, e.ligne)
        elif e.statut == "refute":
            if not e.barre:
                r.erreur("memoire.preuves", f"`{e.id}` réfuté : son titre se barre (`~~…~~`), il ne s'efface pas", e.fichier, e.ligne)
            if not {t for t, _ in e.refs("refutation", "preuve")} & TYPES_PREUVE:
                r.erreur("memoire.preuves", f"`{e.id}` réfuté sans `refutation` qui pointe vers la mesure", e.fichier, e.ligne)
        elif e.statut == "valide":
            cites = [c for t, c in e.refs("validation") if t == "id" and c.lstrip("P").startswith("D-")]
            if not cites:
                r.erreur("memoire.preuves", f"`{e.id}` « validé » sans `validation : D-NNNN` — ce statut ne s'écrit que par l'humain, via une demande", e.fichier, e.ligne)
            for c in cites:
                d = par_id.get(c)
                if d is None or not d.validee:
                    r.erreur("memoire.preuves", f"`{e.id}` cite `{c}`, qui n'a pas de réponse « valider »", e.fichier, e.ligne)


@controle("memoire.backlog")
def backlog(ctx, r):
    """Chaque sujet a une origine ; un sujet clos a une référence."""
    for e in ctx.memoire.entrees("B"):
        if not e.refs("origine"):
            r.erreur("memoire.backlog", f"`{e.id}` sans `origine` (entrée de journal, commit ou demande)", e.fichier, e.ligne)
        if e.statut in memoire.BACKLOG_CLOS and not e.refs("ref"):
            r.erreur("memoire.backlog", f"`{e.id}` est clos (« {e.statut} ») sans `ref` vers ce qui l'a clos", e.fichier, e.ligne)


# --------------------------------------------------------------------------
# Budgets, péremption, retard
# --------------------------------------------------------------------------


@controle("memoire.budgets")
def budgets(ctx, r):
    """Chaque couche et le fichier d'instructions ont un plafond de taille."""
    budgets = ctx.projet.gf("budgets", defaut={}) or {}
    couverts = set()
    for motif, b in budgets.items():
        for chemin in outils.filtrer(ctx.fichiers, [motif]):
            couverts.add(chemin)
            texte = ctx.lire(chemin) or ""
            octets = len(texte.encode("utf-8"))
            lignes = texte.count("\n") + (0 if texte.endswith("\n") or not texte else 1)
            if "max_bytes" in b and octets > b["max_bytes"]:
                r.erreur("memoire.budgets", f"{octets} octets pour un budget de {b['max_bytes']} ({motif}) : archiver dans le journal", chemin)
            if "max_lines" in b and lignes > b["max_lines"]:
                r.erreur("memoire.budgets", f"{lignes} lignes pour un budget de {b['max_lines']} ({motif}) : archiver dans le journal", chemin)
    # Le fichier d'instructions est AGENTS.md ; tant qu'une adoption garde
    # CLAUDE.md comme source (renommage en attente), c'est lui qui est relu.
    instructions = [config.INSTRUCTIONS]
    if (ctx.lire("CLAUDE.md") or "").strip() not in ("", "@AGENTS.md"):
        instructions.append("CLAUDE.md")
    for chemin in list(ctx.memoire.fichiers) + instructions:
        if chemin in ctx.fichiers and chemin not in couverts:
            r.erreur("memoire.budgets", "aucun budget ne couvre ce fichier (`[budgets]` des garde-fous)", chemin)


def date_derniere_modif(ctx, chemin: str) -> float | None:
    if ctx.tete is None and chemin in ctx._cache.setdefault("sales", _sales(ctx)):
        return time.time()
    rev = ctx.rev_commit
    if not outils.a_des_commits(ctx.racine):
        return time.time()
    sortie = outils.git(ctx.racine, "log", "-1", "--format=%ct", rev, "--", chemin, check=False).strip()
    return float(sortie) if sortie else None


def _sales(ctx) -> set[str]:
    if not outils.a_des_commits(ctx.racine):
        return set(ctx.fichiers)
    sortie = outils.git(ctx.racine, "status", "--porcelain", "-z", check=False)
    return {e[3:] for e in sortie.split("\0") if len(e) > 3}


@controle("memoire.peremption")
def peremption(ctx, r):
    """Un chantier actif qui ne bouge plus est signalé — un avertissement, pas un échec."""
    jours = ctx.projet.gf("staleness", "active_days", defaut=7)
    chemin = "memoire/actif.md"
    if chemin not in ctx.fichiers:
        return
    t = date_derniere_modif(ctx, chemin)
    if t is None:
        return
    age = (time.time() - t) / 86400
    if age > jours:
        r.avertir("memoire.peremption", f"chantier actif inchangé depuis {age:.0f} jours (seuil : {jours})", chemin)


@controle("memoire.retard", etages=("agent",), base=True)
def retard(ctx, r):
    """Du code a changé et la mémoire non : la fin de tour attend sa mise à jour."""
    if not ctx.projet.gf("memory", "require_update_on_code_change", defaut=True):
        return
    code = outils.filtrer(ctx.changes, ctx.projet.chemins_code())
    if code and not any(c.startswith(config.MEMOIRE + "/") for c in ctx.changes):
        r.erreur("memoire.retard", f"{len(code)} fichier(s) de code changé(s) depuis la base et aucun de `memoire/` : "
                 "mettre à jour le chantier actif ou le journal avant de conclure")


# --------------------------------------------------------------------------
# Ajout seul : comparé à la base
# --------------------------------------------------------------------------


def _corps_sans_meta(e: memoire.Entree) -> str:
    lignes = e.texte.splitlines()[1:]
    return "\n".join(l for l in lignes if not l.lstrip().startswith(">")).strip()


def _norm(t: str) -> str:
    return "\n".join(l.rstrip() for l in t.strip().splitlines())


@controle("memoire.ajout-seul", base=True)
def ajout_seul(ctx, r):
    """Journal et décisions en ajout seul ; un fait ne disparaît pas, ne change
    qu'avec une nouvelle preuve, et se barre quand il est réfuté."""
    avant = ctx.memoire_base.definitions()
    apres = ctx.memoire.definitions()
    for ident, defs in avant.items():
        a = defs[0]
        b = apres.get(ident, [None])[0]
        if a.type == "J":
            if b is None:
                r.erreur("memoire.ajout-seul", f"entrée de journal `{ident}` supprimée (le journal est en ajout seul)", a.fichier, a.ligne)
            elif _norm(a.texte) != _norm(b.texte) and not _seulement_ajouts(a.texte, b.texte):
                r.erreur("memoire.ajout-seul", f"entrée de journal `{ident}` modifiée (le journal est en ajout seul)", b.fichier, b.ligne)
        elif a.type == "ADR":
            if b is None:
                r.erreur("memoire.ajout-seul", f"décision `{ident}` supprimée (une décision se remplace, elle ne s'efface pas)", a.fichier, a.ligne)
                continue
            if _norm(_corps_sans_meta(a)) != _norm(_corps_sans_meta(b)) or a.titre != b.titre:
                r.erreur("memoire.ajout-seul", f"décision `{ident}` réécrite : seul son statut peut changer, une décision nouvelle la remplace", b.fichier, b.ligne)
            if a.statut != b.statut and (a.statut, b.statut) not in TRANSITIONS_ADR:
                r.erreur("memoire.ajout-seul", f"décision `{ident}` : passage « {a.statut} » → « {b.statut} » interdit", b.fichier, b.ligne)
            if b.statut == "remplacee" and not [c for t, c in b.refs("remplacee-par") if t == "id"]:
                r.erreur("memoire.ajout-seul", f"décision `{ident}` remplacée sans `remplacée-par : ADR-NNNN`", b.fichier, b.ligne)
        elif a.type == "F":
            if b is None:
                r.erreur("memoire.ajout-seul", f"fait `{ident}` effacé : un fait se barre (réfuté) ou s'archive dans le journal, jamais ne disparaît", a.fichier, a.ligne)
                continue
            if b.archivee:
                continue
            if _norm(a.texte) == _norm(b.texte):
                continue
            nouvelles = set(b.refs("preuve", "refutation", "validation")) - set(a.refs("preuve", "refutation", "validation"))
            if not nouvelles:
                r.erreur("memoire.ajout-seul", f"fait `{ident}` modifié sans référence de preuve nouvelle", b.fichier, b.ligne)
            if b.statut == "refute" and a.statut != "refute":
                if _norm(a.corps) and _norm(a.corps) not in _norm(b.corps):
                    r.erreur("memoire.ajout-seul", f"fait `{ident}` réfuté : son texte se garde, barré ; il ne se réécrit pas", b.fichier, b.ligne)
        elif a.type == "B":
            if b is None:
                r.erreur("memoire.ajout-seul", f"sujet `{ident}` disparu du backlog sans archive dans le journal", a.fichier, a.ligne)
            elif b.archivee and b.statut not in memoire.BACKLOG_CLOS:
                r.erreur("memoire.ajout-seul", f"sujet `{ident}` archivé sans être clos", b.fichier, b.ligne)
        elif a.type == "D":
            if b is None:
                r.erreur("memoire.ajout-seul", f"demande `{ident}` supprimée (la retirer : `retirée : <raison>` dans ses métadonnées)", a.fichier, a.ligne)

    reponses_base = {c for c in ctx.fichiers_base if c.endswith(".reponse.toml")}
    for c in sorted(reponses_base):
        if ctx.lire(c) != ctx.lire_base(c):
            r.erreur("memoire.ajout-seul", "réponse humaine modifiée ou supprimée : elle est définitive", c)


def _seulement_ajouts(avant: str, apres: str) -> bool:
    """Une entrée de journal qui reçoit une archive imbriquée à la suite de son
    texte reste en ajout seul."""
    return _norm(apres).startswith(_norm(avant))


# --------------------------------------------------------------------------
# Demandes
# --------------------------------------------------------------------------


@controle("demandes.contrat")
def contrat(ctx, r):
    """Toute demande en attente est autonome : sept champs, aucun identifiant nu."""
    for d in ctx.demandes:
        if d.reponse is not None:
            continue  # gelée : elle a été lintée quand elle a été écrite
        for faute in demandes.linter(d, ctx.projet):
            r.erreur("demandes.contrat", faute, d.chemin)


@controle("demandes.reponses")
def reponses(ctx, r):
    """Une réponse porte sur le texte exact de sa demande et en est une réponse possible."""
    for d in ctx.demandes:
        for faute in demandes.verifier_reponse(d):
            r.erreur("demandes.reponses", faute, d.chemin_reponse or d.chemin)
    for c in ctx.fichiers:
        if c.endswith(".reponse.toml") and c.startswith(config.MEMOIRE + "/"):
            if c[: -len(".reponse.toml")] + ".md" not in ctx.fichiers:
                r.erreur("demandes.reponses", "réponse sans demande", c)


@controle("instructions.source-unique")
def source_unique(ctx, r):
    """`AGENTS.md` fait foi ; `CLAUDE.md` l'importe en une ligne."""
    if config.INSTRUCTIONS not in ctx.fichiers:
        r.erreur("instructions.source-unique", "AGENTS.md absent : c'est le fichier d'instructions qui fait foi")
    if "CLAUDE.md" in ctx.fichiers:
        texte = (ctx.lire("CLAUDE.md") or "").strip()
        if texte != "@AGENTS.md":
            r.erreur("instructions.source-unique", "CLAUDE.md doit contenir la seule ligne `@AGENTS.md` (aucune copie à synchroniser)", "CLAUDE.md")
