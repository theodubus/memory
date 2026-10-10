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
import re
import sys
from datetime import datetime
from pathlib import Path

from socle import config, demandes, memoire, outils

OUTILS_ECRITURE = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
IRREVERSIBLES_BASH = [
    r"\bgit\s+push\b[^\n;&|]*\s(--force\b|-f\b|--force-with-lease\b|--mirror\b|--delete\b|-d\b|\+\S)",
    r"\bgit\s+push\b[^\n;&|]*\s(\S+:)?(main|master)\s*($|[;&|])",
    r"\bgit\s+push\b[^\n;&|]*\s--tags\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+filter-(branch|repo)\b",
    r"\b(npm|cargo|twine|gem|poetry|uv|pnpm|yarn)\s+publish\b",
    r"\bgh\s+(pr\s+merge|release\s+(create|delete)|repo\s+(delete|create|edit))\b",
    r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*\s+(/|~|\$HOME)(\s|$)",
]
IRREVERSIBLES_OUTILS = [
    r"mcp__github__(merge_pull_request|delete_file|create_repository|fork_repository|create_release|push_files)",
]
# Une INVOCATION de `answer` ou `approve`, par le lanceur ou par `-m socle` —
# pas un texte qui les nomme (un heredoc de documentation les cite souvent).
COMMANDES_HUMAINES = re.compile(
    r"(?:^|[;&|(]\s*|\s)(?:\S*/)?(?:python3?\s+)?\S*\.socle/socle(?:\s+--root\s+\S+)?\s+(answer|approve)\b"
    r"|-m\s+socle(?:\s+--root\s+\S+)?\s+(answer|approve)\b",
    re.M,
)


def tracer(racine: Path, evenement: str, session: str = "", source: str = ""):
    try:
        p = racine / config.TRACE
        p.parent.mkdir(parents=True, exist_ok=True)
        horodatage = datetime.now().astimezone().isoformat(timespec="seconds")
        with p.open("a", encoding="utf-8") as f:
            f.write(f"{horodatage}\t{evenement}\t{session}\t{source}\n")
    except OSError:
        pass  # une trace manquante se voit dans le trailer ; un hook qui casse bloquerait tout


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
    if memoire.couche_attendue(rel) not in (None, "inconnue"):
        mem.fichiers[rel] = memoire.analyser(rel, apres)
    defs = mem.definitions()
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


ECRIVAINS = {"rm", "mv", "truncate", "chmod", "touch", "install", "ln", "unlink", "shred"}


def cibles_ecrites(cmd: str) -> list[str]:
    """Les chemins qu'une commande shell écrit : cibles de `>`, `>>` et
    `tee`, arguments de `rm`, `mv`, `touch`…, destination de `cp`, fichiers
    d'un `sed -i` ou d'un `perl -i`. Exécuter ou lire un fichier n'est pas
    l'écrire. Heuristique : un `cd` dans la commande n'est pas suivi."""
    import shlex

    cibles = []
    for m in re.finditer(r"(?<![0-9&])>{1,2}\s*([^\s;&|<>()]+)", cmd):
        cibles.append(m.group(1))
    for simple in re.split(r"&&|\|\||[;|\n]", cmd):
        try:
            mots = shlex.split(simple, comments=True)
        except ValueError:
            mots = simple.split()
        while mots and re.fullmatch(r"\w+=\S*", mots[0]):
            mots.pop(0)  # affectations d'environnement
        if mots and mots[0] in ("sudo", "command", "exec"):
            mots.pop(0)
        if not mots:
            continue
        nom = mots[0].rsplit("/", 1)[-1]
        args = [a for a in mots[1:] if not a.startswith("-") and not re.match(r"^\d*>", a)]
        if nom in ECRIVAINS or nom == "tee":
            cibles += args
        elif nom == "cp" and args:
            cibles.append(args[-1])
        elif nom in ("sed", "perl") and any(re.match(r"^-[a-zA-Z]*i", a) for a in mots[1:]):
            cibles += args[1:]
        elif nom == "dd":
            cibles += [a[3:] for a in mots[1:] if a.startswith("of=")]
    return cibles


def ecriture_protegee(projet: config.Projet, cmd: str) -> str | None:
    """Le chemin protégé qu'une commande shell écrit, s'il y en a un."""
    motifs = projet.chemins_proteges()
    for jeton in cibles_ecrites(cmd):
        rel = _relatif(projet.racine, jeton.strip("'\""))
        if rel and outils.correspond(rel, motifs):
            return rel
    return None


def pre_tool_use(projet: config.Projet, entree: dict) -> int:
    racine = projet.racine
    outil = entree.get("tool_name", "")
    args = entree.get("tool_input") or {}
    tracer(racine, "PreToolUse", entree.get("session_id", ""), outil)

    motifs_outils = projet.pol("irreversible", "tools", defaut=IRREVERSIBLES_OUTILS)
    for m in motifs_outils:
        if re.fullmatch(m, outil):
            return _refus(f"action externe ou irréversible ({outil}) : validation humaine requise "
                          "(politique, point 4). Émettre une demande, travailler sur autre chose en attendant.")

    if outil == "Bash":
        cmd = args.get("command", "")
        for m in projet.pol("irreversible", "bash", defaut=IRREVERSIBLES_BASH):
            if re.search(m, cmd):
                return _refus(f"commande irréversible ou externe : « {cmd.strip()[:200]} » — validation humaine "
                              "requise (politique, point 4). Émettre une demande `D-NNNN` et continuer sur autre chose.")
        if COMMANDES_HUMAINES.search(cmd):
            return _refus("`socle answer` et `socle approve` sont réservés à l'humain : une réponse écrite "
                          "par l'agent ne validerait rien (politique, points 5 et 8).")
        cible = ecriture_protegee(projet, cmd)
        if cible:
            return _refus(f"écriture d'un fichier protégé ({cible}) par le shell : seul l'humain modifie "
                          "la politique, les hooks, la CI et le moteur (relance de l'installeur).")

    if outil in OUTILS_ECRITURE:
        rel = _relatif(racine, args.get("file_path") or args.get("notebook_path") or "")
        if rel and outils.correspond(rel, projet.chemins_proteges()):
            return _refus(f"`{rel}` est protégé par la politique : seul l'humain le modifie (CODEOWNERS), "
                          "ou l'installeur pour les hooks, la CI et le moteur. Proposer le changement par une demande.")
        if rel and rel.endswith(".md"):
            avant, apres = contenu_apres(racine, outil, args, rel)
            if apres is not None:
                fautes = references_inventees(projet, rel, avant, apres)
                if fautes:
                    return _refus("référence inventée — " + " ; ".join(fautes[:5]))
                faute = statut_valide_ajoute(rel, avant, apres, projet)
                if faute:
                    return _refus(faute)
                if memoire.couche_attendue(rel) == "demandes":
                    d = demandes.charger(racine, None, rel, apres)
                    if d.reponse is None:
                        fautes = demandes.linter(d, projet)
                        if fautes:
                            return _refus("demande hors contrat (elle doit se lire sans le projet en tête) — "
                                          + " ; ".join(fautes[:8]))

    faute = sha_fabrique(racine, json.dumps(args, ensure_ascii=False))
    if faute:
        return _refus(faute)
    return 0


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
        return 0
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
    print(json.dumps({"decision": "block", "reason": (
        f"Les contrôles échouent (tentative {essais}/{projet.maximum_tentatives()}) : corriger avant de conclure.\n\n" + texte
    )}, ensure_ascii=False))
    return 0


# --------------------------------------------------------------------------
# Hooks git
# --------------------------------------------------------------------------


def git_pre_commit(projet: config.Projet) -> int:
    from socle import contexte

    tracer(projet.racine, "git-pre-commit")
    base = outils.base_de_travail(projet.racine)
    ctx = contexte.Contexte(projet, etage="git", base=base, tete=None, rapide=True)
    rapport = contexte.executer(ctx)
    if not rapport.reussi:
        rapport.afficher("socle — contrôles avant commit", flux=sys.stderr)
        print("\nCommit refusé. `git commit --no-verify` contourne ce hook, jamais la CI.", file=sys.stderr)
        return 1
    return 0


def compter_session(racine: Path) -> str:
    """`SessionStart=1 PreToolUse=12 Stop=3` pour la session la plus récente
    de la trace ; `aucun` sans trace."""
    trace = racine / config.TRACE
    if not trace.is_file():
        return "aucun"
    lignes = [l.split("\t") for l in trace.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    agent = [l for l in lignes if len(l) >= 3 and l[1] in ("SessionStart", "PreToolUse", "Stop")]
    if not agent:
        return "aucun"
    session = next((l[2] for l in reversed(agent) if l[2]), "")
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
        f"Socle-Hooks: {compter_session(projet.racine)}",
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


def git_pre_push(projet: config.Projet) -> int:
    from socle import contexte, verification

    tracer(projet.racine, "git-pre-push")
    base = outils.base_de_travail(projet.racine)
    ctx = contexte.Contexte(projet, etage="git", base=base, tete=None, rapide=True)
    rapport = contexte.executer(ctx)
    verification.executer_etapes(projet, True, rapport)
    if not rapport.reussi:
        rapport.afficher("socle — vérification avant push", flux=sys.stderr)
        return 1
    return 0
