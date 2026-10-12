"""Les hooks : accélérateurs, jamais garanties (principe 3).

Hooks de l'agent (Claude Code, déclarés dans `.claude/settings.json`) :
- `session-start` : l'état dérivé entre dans le contexte, au démarrage et
  après chaque compactage ;
- `pre-tool-use`  : refuse une action irréversible ou externe, l'écriture d'un
  fichier protégé, une référence inventée, une demande hors contrat ;
- `stop`          : refuse de conclure tant que les contrôles échouent.

Hooks git (`core.hooksPath = .socle/git-hooks`) :
- `git-pre-commit`        : contrôles rapides avant le commit ;
- `git-prepare-commit-msg`: ajoute à un commit d'agent la trace des hooks qui
  ont tiré pendant sa session (`Socle-Hooks:`), que la CI exige ;
- `git-pre-push`          : `verify --rapide`.

Chaque hook laisse une trace datée dans `.socle/trace/hooks.log` : un script
ne peut pas dire s'il a été CHARGÉ, il ne tourne que s'il l'a été. La trace
rend « les hooks tournent-ils ? » vérifiable (leçon de
`chess:tools/verify-hooks.sh`).
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import sys
from datetime import datetime
from pathlib import Path

from socle import commandes, config, demandes, memoire, outils, prive

OUTILS_ECRITURE = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
# Ce que le moteur refuse se juge sur chaque commande simple, découpée
# (`commandes.analyser`), pas sur le texte : voir `irreversible`. La
# politique peut AJOUTER des motifs (`[irreversible] bash`), appliqués à
# chaque commande simple ; elle ne retire rien à ceux du moteur (B-0044, L2).
IRREVERSIBLES_BASH: list[str] = []
IRREVERSIBLES_OUTILS = [
    r"mcp__github__(merge_pull_request|delete_file|create_repository|fork_repository|create_release|push_files"
    r"|create_or_update_file|enable_pr_auto_merge)",
]
# Les réglages de Claude Code commandent ses hooks : un réglage local peut
# les couper tous. Seul l'humain les modifie, où qu'ils soient.
REGLAGES_AGENT = re.compile(r"(^|/)\.claude/settings(\.local)?\.json$")
# Ce qui part hors du dépôt par le shell : un message de commit, un tag, une
# pull request ou un commentaire par `gh`. Ce qui vise le dépôt privé n'est
# pas une publication.
PUBLIE_BASH = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?(?:commit|tag)\b|\bgh\s+(?:pr|issue|release|api)\b")
PUSH_BASH = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?push\b")


def tracer(racine: Path, evenement: str, session: str = "", source: str = ""):
    try:
        p = config.chemin_trace(racine)
        p.parent.mkdir(parents=True, exist_ok=True)
        horodatage = datetime.now().astimezone().isoformat(timespec="seconds")
        with p.open("a", encoding="utf-8") as f:
            f.write(f"{horodatage}\t{evenement}\t{session}\t{source}\n")
    except OSError:
        pass  # une trace manquante se voit dans le trailer ; un hook qui casse bloquerait tout


def tracer_refus(racine: Path, etage: str, quoi: str, session: str = ""):
    """Un refus d'un hook, dans la trace : `Refus` et, en source, l'étage et
    ce qui a refusé. Le banc d'évaluation y lit quel étage attrape quoi."""
    tracer(racine, "Refus", session, f"{etage}:{' '.join(quoi.split())[:160]}")


def lire_entree() -> dict:
    try:
        brut = sys.stdin.read()
    except (OSError, ValueError):
        return {}
    try:
        return json.loads(brut) if brut.strip() else {}
    except json.JSONDecodeError:
        return {}


def installer_hooks_git(racine: Path) -> bool:
    """Pointe git vers `.socle/git-hooks` s'il ne pointe nulle part ailleurs.
    Rend vrai si la configuration est en place."""
    if not (racine / config.GIT_HOOKS).is_dir() or not outils.est_depot(racine):
        return False
    actuel = outils.git(racine, "config", "--get", "core.hooksPath", check=False).strip()
    if actuel == config.GIT_HOOKS:
        return True
    if actuel:
        return False  # un choix local existe : ne pas l'écraser
    outils.git_reussit(racine, "config", "core.hooksPath", config.GIT_HOOKS)
    return True


# --------------------------------------------------------------------------
# SessionStart
# --------------------------------------------------------------------------


def session_start(projet: config.Projet, entree: dict) -> int:
    from socle import etat

    tracer(projet.racine, "SessionStart", entree.get("session_id", ""), entree.get("source", ""))
    git_ok = installer_hooks_git(projet.racine)
    print(etat.calculer(projet))
    if not git_ok and (projet.racine / config.GIT_HOOKS).is_dir():
        print("\n!! hooks git non branchés : `git config core.hooksPath .socle/git-hooks`")
    return 0


# --------------------------------------------------------------------------
# PreToolUse
# --------------------------------------------------------------------------


def _refus(raison: str) -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": raison,
        }
    }, ensure_ascii=False))
    return 0


def _relatif(racine: Path, chemin: str) -> str | None:
    if not chemin:
        return None
    p = Path(chemin)
    if not p.is_absolute():
        p = racine / p
    try:
        return str(p.resolve().relative_to(racine.resolve())).replace(os.sep, "/")
    except ValueError:
        return None


def contenu_apres(racine: Path, outil: str, args: dict, rel: str) -> tuple[str | None, str | None]:
    """(avant, après) d'une écriture, sans l'exécuter."""
    avant = outils.lire_a(racine, None, rel)
    if outil == "Write":
        return avant, args.get("content", "")
    if outil == "Edit":
        if avant is None:
            return None, None
        old, new = args.get("old_string", ""), args.get("new_string", "")
        if args.get("replace_all"):
            return avant, avant.replace(old, new)
        return avant, avant.replace(old, new, 1)
    if outil == "MultiEdit":
        if avant is None:
            return None, None
        t = avant
        for e in args.get("edits", []):
            old, new = e.get("old_string", ""), e.get("new_string", "")
            t = t.replace(old, new) if e.get("replace_all") else t.replace(old, new, 1)
        return avant, t
    return avant, None


def sha_fabrique(racine: Path, texte: str) -> str | None:
    """Un SHA de 40 caractères inconnu dont le préfixe de 7 est connu : la
    signature d'un SHA complété de tête (`chess:.claude/hooks/no-fabricated-sha.sh`)."""
    for sha in sorted(set(re.findall(r"\b[0-9a-f]{40}\b", texte))):
        if outils.git_reussit(racine, "cat-file", "-e", sha):
            continue
        if not outils.git_reussit(racine, "cat-file", "-e", sha[:7]):
            continue
        reel = outils.git(racine, "rev-parse", sha[:7], check=False).strip() or "<introuvable>"
        return (f"SHA fabriqué : {sha} n'est pas un objet de ce dépôt, alors que son préfixe {sha[:7]} en est un. "
                f"Le SHA complet de {sha[:7]} est {reel}. Ne jamais compléter un SHA de tête : `git rev-parse`.")
    return None


def references_inventees(projet: config.Projet, rel: str, avant: str | None, apres: str) -> list[str]:
    """Les références que cette écriture AJOUTE et qui ne mènent nulle part."""
    fautes = []
    mem = memoire.Memoire.charger(projet.racine)
    avant_defs = set(mem.definitions())
    index_avant = {i: {memoire.empreinte_index(mem, i)} for i in memoire.INDEX_TYPES}
    # Comme `memoire.lectures` : l'index lu au début du travail (à la base)
    # reste valable, même si l'agent y a ajouté depuis.
    base = outils.base_de_travail(projet.racine)
    if base:
        mem_base = memoire.Memoire.charger(projet.racine, base)
        for i in index_avant:
            index_avant[i].add(memoire.empreinte_index(mem_base, i))
    if memoire.couche_attendue(rel) not in (None, "inconnue"):
        mem.fichiers[rel] = memoire.analyser(rel, apres)
    defs = mem.definitions()
    # Lecture prouvée (ADR-0008) : une empreinte citée est celle de la version
    # actuelle. Le refus ne donne pas la bonne : elle s'obtient en relisant.
    deja = {(i, h) for i, h, _ in memoire.citations(avant or "")}
    for ident, h, ligne in memoire.citations(apres):
        if (ident, h) not in deja and ident in defs and memoire.empreinte_entree(defs[ident][0]) != h:
            fautes.append(f"`{ident}@{h}` (ligne {ligne}) n'est pas l'empreinte de la version actuelle de {ident} : "
                          f"la relire, `python3 .socle/socle show {ident}`")
    nouveaux = set(defs) - avant_defs
    deja_i = {(i, h) for i, h, _ in memoire.citations_index(avant or "")}
    for index, h, ligne in memoire.citations_index(apres):
        permises = index_avant[index] | {memoire.empreinte_index(mem, index, nouveaux)}
        if (index, h) not in deja_i and h not in permises:
            fautes.append(f"`{index}@{h}` (ligne {ligne}) n'est l'empreinte d'aucune version récente de l'index : "
                          f"le relire, `python3 .socle/socle show --index {index}`")
    deja = {i for i, _ in memoire.mentions(avant or "")}
    for ident, ligne in memoire.mentions(apres):
        if ident in deja or ident in defs or ident.startswith("P"):
            continue
        fautes.append(f"`{ident}` (ligne {ligne}) ne désigne aucune entrée de la mémoire — "
                      "créer l'entrée d'abord, ou corriger l'identifiant ; ne jamais en inventer un")
    refs_avant = set(memoire.references(avant or ""))
    for type_, cible in memoire.references(apres):
        if (type_, cible) in refs_avant:
            continue
        if type_ == "commit" and re.fullmatch(r"[0-9a-f]{7,40}", cible) and not outils.objet_existe(projet.racine, cible):
            fautes.append(f"`commit:{cible}` n'existe pas dans ce dépôt — lire le SHA avec `git rev-parse`, jamais de tête")
    return fautes


def statut_valide_ajoute(rel: str, avant: str | None, apres: str, projet) -> str | None:
    if memoire.couche_attendue(rel) != "canonique":
        return None
    av = {e.id: e for e in memoire.analyser(rel, avant or "").entrees}
    par_id = {d.id: d for d in demandes.toutes(projet.racine)}
    for e in memoire.analyser(rel, apres).entrees:
        if e.type != "F" or e.statut != "valide":
            continue
        if e.id in av and av[e.id].statut == "valide" and av[e.id].meta == e.meta:
            continue
        cites = [c for t, c in e.refs("validation") if t == "id"]
        if not any(par_id.get(c) and par_id[c].validee for c in cites):
            return (f"`{e.id}` passe à « validé » sans demande validée par l'humain : ce statut ne s'écrit "
                    "que par l'humain (politique, point 5). Émettre une demande `D-NNNN`.")
    return None


ECRIVAINS = {"rm", "mv", "truncate", "chmod", "chown", "touch", "unlink", "shred", "tee"}


def ecrits(c: commandes.Commande) -> list[str]:
    """Les chemins qu'une commande simple écrit, rapportés au dossier de
    départ : ses redirections, les arguments de `rm`, `mv`, `touch`…, la
    destination de `cp`, les fichiers d'un `sed -i` ou d'un `perl -i`, et ce
    que `git rm`, `git mv`, `git restore` ou `git checkout -- …` réécrivent.
    Exécuter ou lire un fichier n'est pas l'écrire."""
    res = list(c.redirige)
    nom = c.programme
    options, args = commandes.options_et_arguments(c.argv[1:])
    if nom in ECRIVAINS:
        res += args
    elif nom in ("cp", "ln", "install", "rsync") and args:
        res.append(args[-1])
    elif nom in ("sed", "perl") and commandes.drapeau(options, "i", ("--in-place",)):
        res += args if any(o in ("-e", "-f", "--expression", "--file") for o in options) else args[1:]
    elif nom == "dd":
        res += [a[3:] for a in c.argv[1:] if a.startswith("of=")]
    elif nom == "git":
        sous, reste = commandes.git_sous_commande(c.argv)
        if sous in ("rm", "mv", "restore", "clean"):
            res += commandes.options_et_arguments(reste)[1]
        elif sous == "checkout" and "--" in reste:
            res += reste[reste.index("--") + 1:]
    return [c.chemin(x) for x in res if x]


def cibles_ecrites(cmd: str) -> list[str]:
    """Les chemins qu'une commande shell écrit, toutes commandes simples
    confondues."""
    return [x for c in commandes.analyser(cmd) for x in ecrits(c)]


def ecriture_protegee(projet: config.Projet, cmd: str) -> str | None:
    """Le chemin protégé qu'une commande shell écrit, s'il y en a un : un
    fichier protégé, ou un dossier qui en contient (`rm -rf .socle`)."""
    motifs = projet.chemins_proteges()
    suivis = None
    for jeton in cibles_ecrites(cmd):
        rel = _relatif(projet.racine, jeton.strip("'\""))
        if rel is None:
            continue
        if outils.correspond(rel, motifs):
            return rel
        if suivis is None:
            suivis = outils.fichiers_courants(projet.racine)
        prefixe = "" if rel in ("", ".") else rel.rstrip("/") + "/"
        touche = next((f for f in suivis if f.startswith(prefixe) and outils.correspond(f, motifs)), None)
        if touche:
            return f"{rel or '.'}/ (dont {touche})"
    return None


def _branches_protegees(racine: Path) -> set[str]:
    defaut = outils.branche_par_defaut(racine) or ""
    return {"main", "master", defaut.split("/", 1)[-1]} - {""}


def irreversible(racine: Path, c: commandes.Commande) -> str | None:
    """L'action irréversible ou externe qu'une commande simple lance
    (politique, point 4), dite en clair ; `None` sinon."""
    nom, argv = c.programme, c.argv
    if nom == "git":
        sous, reste = commandes.git_sous_commande(argv)
        options, args = commandes.options_et_arguments(reste)
        if sous == "push":
            if commandes.drapeau(options, "f", ("--force", "--force-with-lease", "--force-if-includes")):
                return "push forcé"
            if commandes.drapeau(options, "d", ("--delete", "--prune")):
                return "suppression d'une branche distante"
            if commandes.drapeau(options, "", ("--mirror", "--all", "--tags")):
                return "push de toutes les références"
            refs = args[1:]
            if any(r.startswith("+") for r in refs):
                return "push forcé (+)"
            if any(r.startswith(":") for r in refs):
                return "suppression d'une branche distante"
            cibles = [r.split(":", 1)[-1].removeprefix("refs/heads/") for r in refs] or \
                [outils.git(racine, "rev-parse", "--abbrev-ref", "HEAD", check=False).strip()]
            protegee = next((x for x in cibles if x in _branches_protegees(racine)), None)
            return f"push sur la branche par défaut ({protegee})" if protegee else None
        if sous == "reset" and "--hard" in options:
            return "git reset --hard"
        if sous in ("filter-branch", "filter-repo"):
            return f"git {sous}"
        return None
    if nom in ("npm", "cargo", "poetry", "uv", "pnpm", "yarn") and "publish" in argv[1:3]:
        return f"{nom} publish"
    if (nom, argv[1:2]) in (("twine", ["upload"]), ("gem", ["push"])):
        return f"{nom} {argv[1]}"
    if nom == "gh":
        sous = tuple(argv[1:3])
        if sous == ("pr", "merge") \
                or (sous[:1] == ("release",) and sous[1:] in (("create",), ("delete",), ("edit",))) \
                or (sous[:1] == ("repo",) and sous[1:] in (("create",), ("delete",), ("edit",), ("rename",),
                                                          ("archive",))) \
                or (sous[:1] == ("secret",) and sous[1:] in (("set",), ("delete",))):
            return "gh " + " ".join(sous)
        if sous[:1] == ("api",):
            for i, a in enumerate(argv):
                if a in ("-X", "--method") and i + 1 < len(argv):
                    methode = argv[i + 1]
                elif a.startswith("--method="):
                    methode = a.split("=", 1)[1]
                elif a.startswith("-X") and len(a) > 2:
                    methode = a[2:]
                else:
                    continue
                if methode.upper() in ("DELETE", "PUT", "PATCH"):
                    return f"gh api {methode.upper()}"
    if nom == "rm":
        options, args = commandes.options_et_arguments(argv[1:])
        if commandes.drapeau(options, "r", ("--recursive",)) or commandes.drapeau(options, "R"):
            for a in args:
                cible = c.chemin(a).rstrip("/")
                if a.rstrip("/*") in ("", "~", "$HOME") or cible == ".git" or cible.endswith("/.git"):
                    return f"rm -r {a}"
    return None


def commande_humaine(c: commandes.Commande) -> tuple[str, list[str]] | None:
    """Une commande du socle réservée à l'humain (`answer`, `approve`,
    `relu`, `prive installer`), quel que soit le chemin du lanceur (entre
    guillemets, après un `cd`, par `python3 -m socle`) : son nom et ses
    arguments ; `None` sinon."""
    argv = c.argv
    if not argv:
        return None

    def lanceur(chemin: str) -> bool:
        return posixpath.normpath(c.chemin(chemin)).endswith(".socle/socle") or chemin.endswith(".socle/socle")

    if re.fullmatch(r"python[\d.]*", c.programme):
        reste = argv[1:]
        while reste and reste[0].startswith("-"):
            reste = reste[1:]
        if not reste or not lanceur(reste[0]):
            return None
        reste = reste[1:]
    elif c.programme == "socle" or lanceur(argv[0]):
        reste = argv[1:]
    else:
        return None
    while reste and (reste[0] == "--root" or reste[0].startswith("--root=")):
        reste = reste[2:] if reste[0] == "--root" else reste[1:]
    if reste[:2] == ["prive", "installer"]:
        return "prive installer", reste
    if reste and reste[0] in ("answer", "approve", "relu"):
        return reste[0], reste
    return None


class _Repere:
    """L'interface d'une expression régulière (`search`), gardée pour les
    appelants d'avant le découpage des commandes : elle trouve une
    INVOCATION, pas un texte qui la nomme."""

    def __init__(self, noms: tuple[str, ...]):
        self.noms = noms

    def search(self, cmd: str):
        for c in commandes.analyser(cmd):
            h = commande_humaine(c)
            if h and h[0] in self.noms:
                return _Trouve(h[0])
        return None


class _Trouve:
    def __init__(self, nom: str):
        self.nom = nom

    def group(self, *_):
        return self.nom


COMMANDES_HUMAINES = _Repere(("answer", "approve", "relu"))
INSTALLER_PRIVE = _Repere(("prive installer",))


def pre_tool_use(projet: config.Projet, entree: dict) -> int:
    racine = projet.racine
    outil = entree.get("tool_name", "")
    args = entree.get("tool_input") or {}
    tracer(racine, "PreToolUse", entree.get("session_id", ""), outil)

    def refus(raison: str) -> int:
        tracer_refus(racine, "PreToolUse", f"{outil} — {raison}", entree.get("session_id", ""))
        return _refus(raison)

    motifs_outils = projet.pol("irreversible", "tools", defaut=IRREVERSIBLES_OUTILS)
    for m in motifs_outils:
        if re.fullmatch(m, outil):
            return refus(f"action externe ou irréversible ({outil}) : validation humaine requise "
                         "(politique, point 4). Émettre une demande, travailler sur autre chose en attendant.")

    if outil == "Bash":
        cmd = args.get("command", "")
        # Chaque commande simple, découpée : ce qu'elle lance, pas le texte
        # qu'elle cite (un heredoc, un message de commit).
        simples = commandes.analyser(cmd)
        en_plus = projet.pol("irreversible", "bash", defaut=IRREVERSIBLES_BASH) or []
        for c in simples:
            action = irreversible(racine, c) or next(
                (" ".join(c.argv)[:120] for m in en_plus if re.search(m, " ".join(c.argv))), None)
            if action:
                return refus(f"commande irréversible ou externe ({action}) : « {cmd.strip()[:200]} » — validation "
                             "humaine requise (politique, point 4). Si c'est une décision, émettre une demande "
                             "`D-NNNN` ; si c'est une action que l'humain doit faire lui-même, l'inscrire au backlog "
                             "avec `pour : humain`. Puis continuer sur autre chose.")
            h = commande_humaine(c)
            if h and h[0] == "prive installer":
                return refus("`socle prive installer` est réservé à l'humain : il pousse vers le dépôt privé et "
                             "crée une clé de déploiement (politique, point 4). L'inscrire au backlog avec "
                             "`pour : humain`.")
            if h and h[0] == "approve":
                return refus("`socle approve` est réservé à l'humain : il valide ses propres changements protégés.")
            # Les drapeaux du relais se cherchent dans la commande elle-même,
            # pas ailleurs dans le texte.
            relais = "--relayed" in h[1] and any(x.split("=", 1)[0] in ("--quote", "--quote-file") for x in h[1]) \
                if h else True
            if not relais:
                return refus("l'agent ne répond jamais à la place de l'humain. Il ne peut que relayer une réponse "
                             "donnée dans la conversation : `socle answer D-NNNN <réponse> --relayed --by <nom> "
                             "--quote-file <texte exact>` (ADR-0006), ou `socle relu --relayed --by <nom> "
                             "--quote-file <texte exact>` pour une relecture avant publication.")
        faute = _fuite_bash(projet, cmd)
        if faute:
            return refus(faute)
        reglage = next((x for c in simples for x in ecrits(c) if REGLAGES_AGENT.search(x)), None)
        if reglage:
            return refus(f"`{reglage}` : les réglages de Claude Code commandent ses hooks, seul l'humain les "
                         "modifie (un réglage local peut les couper tous).")
        cible = ecriture_protegee(projet, cmd)
        if cible:
            return refus(f"écriture d'un fichier protégé ({cible}) par le shell : seul l'humain modifie "
                         "la politique, les hooks, la CI et le moteur (relance de l'installeur).")

    faute = _fuite_outil(projet, outil, args)
    if faute:
        return refus(faute)

    if outil in OUTILS_ECRITURE:
        chemin = args.get("file_path") or args.get("notebook_path") or ""
        if REGLAGES_AGENT.search(chemin.replace(os.sep, "/")):
            return refus(f"`{chemin}` : les réglages de Claude Code commandent ses hooks, seul l'humain les "
                         "modifie (un réglage local peut les couper tous).")
        rel = _relatif(racine, chemin)
        if rel and outils.correspond(rel, projet.chemins_proteges()):
            return refus(f"`{rel}` est protégé par la politique : seul l'humain le modifie (CODEOWNERS), "
                         "ou l'installeur pour les hooks, la CI et le moteur. Proposer le changement par une demande.")
        if rel and rel.endswith(".md"):
            avant, apres = contenu_apres(racine, outil, args, rel)
            if apres is not None:
                fautes = references_inventees(projet, rel, avant, apres)
                if fautes:
                    return refus("référence inventée — " + " ; ".join(fautes[:5]))
                faute = statut_valide_ajoute(rel, avant, apres, projet)
                if faute:
                    return refus(faute)
                if memoire.couche_attendue(rel) == "demandes":
                    d = demandes.charger(racine, None, rel, apres)
                    if d.reponse is None:
                        fautes = demandes.linter(d, projet)
                        if fautes:
                            return refus("demande hors contrat (elle doit se lire sans le projet en tête) — "
                                          + " ; ".join(fautes[:8]))

    faute = sha_fabrique(racine, json.dumps(args, ensure_ascii=False))
    if faute:
        return refus(faute)
    return 0


# --------------------------------------------------------------------------
# Fuites de la mémoire privée (D-0008) : le hook de l'agent voit, avant
# qu'elles partent, les écritures et les publications que ni les hooks git ni
# la CI ne voient à temps (une description de pull request, un commentaire).
# --------------------------------------------------------------------------


def _vers_le_prive(racine: Path, cmd: str) -> bool:
    zones = "|".join(re.escape(d) for d in memoire.DOSSIERS_PRIVES)
    return bool(re.search(r"(?:-C|cd)\s+(?:\S*/)?(?:" + zones + ")", cmd))


def _fuites_dans(projet: config.Projet, texte: str) -> str | None:
    t = prive.termes(projet)
    trouve = prive.fuites(texte, t.liste)
    if not trouve:
        return None
    return ("fuite de la mémoire privée : " + ", ".join(trouve[:5]) + ". Une écriture publique ne cite ni "
            "identifiant privé ni terme de la liste privée : reformuler sans eux (politique, mémoire privée).")


def _fuite_bash(projet: config.Projet, cmd: str) -> str | None:
    if prive.mode(projet) is None or _vers_le_prive(projet.racine, cmd):
        return None
    if PUSH_BASH.search(cmd):
        tete = outils.git(projet.racine, "rev-parse", "HEAD", check=False).strip()
        refus = prive.publication_refusee(projet, [tete])
        if refus:
            return refus
    if PUBLIE_BASH.search(cmd):
        return _fuites_dans(projet, cmd)
    return None


def _fuite_outil(projet: config.Projet, outil: str, args: dict) -> str | None:
    if prive.mode(projet) is None:
        return None
    if outil.startswith("mcp__"):
        return _fuites_dans(projet, json.dumps(args, ensure_ascii=False))
    if outil in OUTILS_ECRITURE:
        rel = _relatif(projet.racine, args.get("file_path") or args.get("notebook_path") or "")
        if not rel or prive.est_prive(rel):
            return None
        avant, apres = contenu_apres(projet.racine, outil, args, rel)
        if apres is None:
            return None
        # Seul ce qui s'ajoute compte : une fuite plus ancienne ne bloque pas
        # chaque écriture suivante du même fichier.
        anciennes = set((avant or "").splitlines())
        ajout = "\n".join(l for l in apres.splitlines() if l not in anciennes)
        return _fuites_dans(projet, ajout)
    return None


# --------------------------------------------------------------------------
# Stop
# --------------------------------------------------------------------------


def _empreinte_arbre(racine: Path) -> str:
    """Ce que la dernière vérification réussie a vu : HEAD et le diff courant."""
    tete = outils.git(racine, "rev-parse", "HEAD", check=False).strip()
    diff = outils.git(racine, "diff", "HEAD", check=False)
    autres = outils.git(racine, "ls-files", "--others", "--exclude-standard", check=False)
    return outils.sha256(tete + diff + autres)


def stop(projet: config.Projet, entree: dict) -> int:
    from socle import contexte, verification

    racine = projet.racine
    tracer(racine, "Stop", entree.get("session_id", ""))
    compteur = racine / config.COMPTEUR_STOP
    base = outils.base_de_travail(racine)
    ctx = contexte.Contexte(projet, etage="agent", base=base, tete=None, rapide=True)
    rapport = contexte.executer(ctx)

    # Les capacités rapides de l'adaptateur, seulement si l'arbre a bougé
    # depuis la dernière vérification réussie : inutile de payer une
    # compilation pour un tour qui n'a touché que de la documentation.
    deja = racine / ".socle/trace/derniere-verification"
    marque = _empreinte_arbre(racine) if outils.a_des_commits(racine) else ""
    code = outils.filtrer(ctx.changes, projet.chemins_code())
    if code and (not deja.is_file() or deja.read_text().strip() != marque):
        verification.executer_etapes(projet, True, rapport)
        if rapport.reussi and marque:
            deja.parent.mkdir(parents=True, exist_ok=True)
            deja.write_text(marque)

    if rapport.reussi:
        compteur.unlink(missing_ok=True)
        return exiger_recap(projet, entree)
    essais = int(compteur.read_text().strip() or 0) + 1 if compteur.is_file() else 1
    compteur.parent.mkdir(parents=True, exist_ok=True)
    compteur.write_text(str(essais))
    texte = rapport.texte("contrôles de fin de tour (`socle check --stage agent`)")
    if essais >= projet.maximum_tentatives():
        compteur.unlink(missing_ok=True)
        print(json.dumps({"systemMessage": (
            f"Les contrôles échouent encore après {essais} tentatives : ARRÊT ET ESCALADE (politique, point 7). "
            "Écrire une demande `D-NNNN` qui résume l'échec, ce qui a été tenté et ce qui est supposé, "
            "puis s'arrêter.\n\n" + texte)}, ensure_ascii=False))
        return 0
    tracer_refus(racine, "Stop", ",".join(rapport.controles_en_echec()), entree.get("session_id", ""))
    print(json.dumps({"decision": "block", "reason": (
        f"Les contrôles échouent (tentative {essais}/{projet.maximum_tentatives()}) : corriger avant de conclure.\n\n" + texte
    )}, ensure_ascii=False))
    return 0


def _appels_externes(racine: Path, session: str) -> bool:
    """Un outil externe (`mcp__…` : pull request, commentaire…) a-t-il été
    appelé depuis la fin de tour précédente de cette session ?"""
    if not session:
        return False
    lignes = [l.split("\t") for l in config.lire_trace(racine)]
    siennes = [l for l in lignes if len(l) >= 4 and l[2] == session]
    stops = [i for i, l in enumerate(siennes) if l[1] == "Stop"]
    debut = stops[-2] + 1 if len(stops) >= 2 else 0
    return any(l[1] == "PreToolUse" and l[3].startswith("mcp__") for l in siennes[debut:])


def exiger_recap(projet: config.Projet, entree: dict) -> int:
    """Un tour où l'agent a agi se termine par un récap et deux lignes,
    `Pour toi :` et `Ensuite :` (ADR-0007, ADR-0009). Tout dernier message,
    qu'il ait agi ou non, ne donne que des liens que l'humain peut suivre
    (ADR-0010)."""
    from socle import humain, liens

    racine = projet.racine
    fichier = racine / ".socle/trace/derniere-fin-de-tour"
    marque = _empreinte_arbre(racine) if outils.a_des_commits(racine) else ""
    a_agi = (not fichier.is_file() or fichier.read_text().strip() != marque
             or _appels_externes(racine, entree.get("session_id", "")))

    def retenir():
        fichier.parent.mkdir(parents=True, exist_ok=True)
        fichier.write_text(marque)

    chemin = entree.get("transcript_path")
    message = humain.dernier_message(Path(chemin)) if chemin else None
    if message is None:
        if a_agi:
            retenir()
            print(json.dumps({"systemMessage": "récap de fin d'intervention non vérifiable : transcript illisible"},
                             ensure_ascii=False))
        return 0
    manque = humain.recap_manquant(projet, message) if a_agi else []
    morts, sans_lien = liens.problemes(projet, message)
    if not (manque or morts or sans_lien):
        if a_agi:
            retenir()
        return 0
    if entree.get("stop_hook_active"):
        if a_agi:
            retenir()
        defauts = ([f"sans {' ni '.join(manque)}"] if manque else []) + (
            [f"{len(morts) + len(sans_lien)} lien(s) que l'humain ne pourra pas suivre"] if morts or sans_lien else [])
        print(json.dumps({"systemMessage": f"fin d'intervention {', '.join(defauts)}, malgré un rappel"},
                         ensure_ascii=False))
        return 0
    raisons = []
    if manque:
        liste = "\n".join(humain.texte(humain.a_faire(projet)))
        suite = humain.prochaines_etapes(projet) or "(le chantier actif n'a pas de section « Prochaines étapes »)"
        raisons.append(
            f"Tu as agi pendant ce tour, et ton dernier message n'a pas {' ni '.join(manque)}. Termine par un récap "
            "de ce qui a été fait, puis :\n"
            "- « Pour toi : » ce qui revient à l'humain — décisions, actions qu'il est seul à pouvoir faire — ou « rien » ;\n"
            "- « Ensuite : » la suite proposée (prochain jalon, ce qu'il reste à faire avant), et ce que tu attends, "
            "s'il y a lieu (une CI, un match : quoi, et jusqu'à quand).\n\n"
            "Ce qui revient à l'humain, calculé maintenant :\n" + liste
            + "\n\nProchaines étapes, selon le chantier actif :\n" + suite)
    if morts:
        raisons.append(
            "Ton dernier message contient des liens que l'humain ne pourra pas suivre : il lit dans la conversation "
            "ou sur GitHub, pas dans ton conteneur.\n" + "\n".join(f"- {m}" for m in morts)
            + "\nDonne un fichier par son permalien (`socle url <chemin|ID>`, après le push) ; n'écris entre accents "
            "graves que des chemins qui existent dans ce dépôt, et ceux d'un autre dépôt sous la forme `depot:chemin`.")
    if sans_lien:
        raisons.append(
            f"Ton dernier message cite {', '.join(sans_lien)}, en attente de l'humain, sans son lien : "
            "il doit pouvoir l'ouvrir d'un clic. Ajoute la sortie de `socle url "
            + " ".join(sans_lien) + "`.")
    tracer_refus(racine, "Stop", ",".join(x for x, oui in (("recap", manque), ("liens", morts), ("lien-de-demande", sans_lien))
                                         if oui), entree.get("session_id", ""))
    print(json.dumps({"decision": "block", "reason": "\n\n".join(raisons)}, ensure_ascii=False))
    return 0


# --------------------------------------------------------------------------
# Hooks git
# --------------------------------------------------------------------------


def git_pre_commit(projet: config.Projet) -> int:
    from socle import contexte

    tracer(projet.racine, "git-pre-commit")
    base = outils.base_de_travail(projet.racine)
    # On juge ce qui sera commité : l'index, figé en arbre par `write-tree`,
    # et non les fichiers sur disque, qui peuvent cacher un défaut indexé ou
    # en montrer un qui ne sera pas commité (B-0007).
    index = outils.git(projet.racine, "write-tree", check=False).strip() or None
    ctx = contexte.Contexte(projet, etage="git", base=base, tete=index, rapide=True)
    rapport = contexte.executer(ctx)
    if not rapport.reussi:
        tracer_refus(projet.racine, "git-pre-commit", ",".join(rapport.controles_en_echec()))
        rapport.afficher("socle — contrôles avant commit", flux=sys.stderr, court=True)
        if "protege.fichiers" in rapport.controles_en_echec():
            print("\nFichiers protégés : si c'est l'humain qui les a changés (une mise à jour du socle, sa "
                  "politique), `python3 .socle/socle approve --text \"<raison>\"` les liste et les approuve — réservé à l'humain ; "
                  "l'agent, lui, ouvre une demande.", file=sys.stderr)
        print("\nCommit refusé. `git commit --no-verify` contourne ce hook, jamais la CI.", file=sys.stderr)
        return 1
    return 0


def compter_session(racine: Path, session: str | None = None) -> str:
    """`SessionStart=1 PreToolUse=12 Stop=3` pour la session donnée, ou à
    défaut la plus récente de la trace ; `aucun` sans trace. Le commit d'une
    session dont les hooks sont coupés compte ainsi zéro, au lieu d'emprunter
    la trace d'une session plus ancienne (B-0044, L2)."""
    lignes = [l.split("\t") for l in config.lire_trace(racine)]
    agent = [l for l in lignes if len(l) >= 3 and l[1] in ("SessionStart", "PreToolUse", "Stop")]
    if not agent and not session:
        return "aucun"
    session = session or next((l[2] for l in reversed(agent) if l[2]), "")
    de_la_session = [l for l in agent if l[2] == session]
    compte = {e: sum(1 for l in de_la_session if l[1] == e) for e in ("SessionStart", "PreToolUse", "Stop")}
    if compte["SessionStart"] == 0:
        # Le socle a-t-il été installé PENDANT cette session ? Alors son
        # SessionStart a eu lieu avant que le hook n'existe.
        premier = next((i for i, l in enumerate(lignes) if len(l) >= 3 and l[2] == session), None)
        if premier is not None and premier > 0 and lignes[premier - 1][1] == "Install":
            return f"SessionStart=installation PreToolUse={compte['PreToolUse']} Stop={compte['Stop']}"
    return " ".join(f"{k}={v}" for k, v in compte.items())


def git_prepare_commit_msg(projet: config.Projet, fichier: str, source: str = "") -> int:
    """Sur un commit fait dans une session d'agent (`CLAUDECODE` dans
    l'environnement), ajoute `Socle-Agent` et `Socle-Hooks`."""
    tracer(projet.racine, "git-prepare-commit-msg")
    if not os.environ.get("CLAUDECODE") or source in ("merge", "squash"):
        return 0
    p = Path(fichier)
    message = p.read_text(encoding="utf-8")
    if re.search(r"(?im)^socle-hooks:", message):
        return 0
    corps = message.rstrip("\n")
    lignes = [
        "Socle-Agent: claude-code",
        f"Socle-Hooks: {compter_session(projet.racine, os.environ.get('CLAUDE_CODE_SESSION_ID'))}",
    ]
    # Les trailers vont dans le dernier paragraphe, avant les commentaires.
    contenu, commentaires = [], []
    for l in corps.splitlines():
        (commentaires if l.startswith("#") else contenu).append(l)
    texte = "\n".join(contenu).rstrip()
    sep = "\n" if outils.trailers(texte) else "\n\n"
    nouveau = texte + sep + "\n".join(lignes) + "\n"
    if commentaires:
        nouveau += "\n" + "\n".join(commentaires) + "\n"
    p.write_text(nouveau, encoding="utf-8")
    return 0


def git_commit_msg(projet: config.Projet, fichier: str = "") -> int:
    """Le message d'un commit public ne cite ni identifiant privé ni terme de
    la liste privée : le seul étage, hors de l'agent, qui le voit avant le
    commit (D-0008). Il avertit aussi d'une fonction que la CI refusera faute
    de test ou de dispense (B-0034, P9)."""
    tracer(projet.racine, "git-commit-msg")
    if not fichier:
        return 0
    try:
        brut = Path(fichier).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    message = "\n".join(l for l in brut.splitlines() if not l.startswith("#"))
    faute = _fuites_dans(projet, message) if prive.mode(projet) is not None else None
    if faute:
        tracer_refus(projet.racine, "git-commit-msg", "fuite")
        print(f"socle — commit refusé : {faute}", file=sys.stderr)
        return 1
    avertissement = code_sans_test(projet, message)
    if avertissement:
        print(avertissement, file=sys.stderr)
    return 0


def code_sans_test(projet: config.Projet, message: str) -> str | None:
    """Une fonction publique que ni un test ni une dispense ne nomme : la CI
    refusera le commit (`tests.code-teste`). Le hook commit-msg, le premier
    étage qui voit le message et ses dispenses, le dit sans refuser : un
    humain qui commite son code l'apprend ici, pas en CI (B-0034, P9)."""
    from socle import contexte, controles_tests
    from socle.rapport import Rapport

    base = outils.base_de_travail(projet.racine)
    index = outils.git(projet.racine, "write-tree", check=False).strip() or None
    ctx = contexte.Contexte(projet, etage="git", base=base, tete=index, rapide=True, message=message)
    r = Rapport()
    try:
        controles_tests.code_teste(ctx, r)
    except Exception:  # un avertissement ne bloque jamais un commit
        return None
    erreurs = r.erreurs("tests.code-teste")
    if not erreurs:
        return None
    return ("socle — avertissement : la CI refusera ce commit (`tests.code-teste`) :\n"
            + "\n".join(f"  ! {c.en_ligne()}" for c in erreurs)
            + "\nLe commit passe ici. Écrire le test dans un commit suivant, ou amender ce message "
            "(`git commit --amend`) avec la dispense.")


def plage_poussee(projet: config.Projet, lignes: list[str]):
    """Les contrôles qui comparent à une base, sur la plage qui part : du
    commit distant au commit local de chaque référence déjà présente en
    face. C'est la plage que la CI d'un push jugera ; contre la branche par
    défaut, une dispense ou une validation plus anciennes de la branche
    couvraient ce qu'elle refusera (B-0043)."""
    from socle import contexte
    from socle.rapport import Rapport

    rapport = Rapport()
    contexte.charger_controles()
    ids = [c.id for c in contexte.selectionner("ci", rapide=True) if c.base]
    for l in lignes:
        morceaux = l.split()
        if len(morceaux) < 4:
            continue
        local, distant = morceaux[1], morceaux[3]
        if set(local) == {"0"} or set(distant) == {"0"} or not outils.rev_existe(projet.racine, distant):
            continue  # une branche neuve, une suppression, ou un distant qu'on n'a pas : rien à comparer
        ctx = contexte.Contexte(projet, etage="ci", base=distant, tete=local, rapide=True)
        rapport.fusionner(contexte.executer(ctx, ids))
    return rapport


def git_pre_push(projet: config.Projet) -> int:
    from socle import contexte, verification

    tracer(projet.racine, "git-pre-push")
    # Les commits qui partent : `<réf locale> <sha local> <réf distante> <sha distant>` par ligne.
    lignes = [] if sys.stdin is None or sys.stdin.isatty() else sys.stdin.read().splitlines()
    refus = prive.publication_refusee(projet, [l.split()[1] for l in lignes if len(l.split()) >= 2])
    if refus:
        tracer_refus(projet.racine, "git-pre-push", "relecture")
        print(f"socle — push refusé : {refus}", file=sys.stderr)
        return 1
    base = outils.base_de_travail(projet.racine)
    ctx = contexte.Contexte(projet, etage="git", base=base, tete=None, rapide=True)
    rapport = contexte.executer(ctx)
    for constat in plage_poussee(projet, lignes).constats:
        if constat not in rapport.constats:
            rapport.constats.append(constat)
    verification.executer_etapes(projet, True, rapport)
    if not rapport.reussi:
        tracer_refus(projet.racine, "git-pre-push", ",".join(rapport.controles_en_echec()))
        rapport.afficher("socle — vérification avant push", flux=sys.stderr, court=True)
        return 1
    return 0
