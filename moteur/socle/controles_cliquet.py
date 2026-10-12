"""Rien ne s'affaiblit en silence (principe 5).

- `cliquet.garde-fous` : tout assouplissement des garde-fous (`.socle/guardrails.toml`)
  par rapport à la base exige une demande validée dans la plage, qui cite la
  clé assouplie. Durcir est libre.
- `protege.fichiers` : un fichier protégé par la politique ne change qu'avec
  une demande validée qui cite son empreinte nouvelle.
- `moteur.empreinte` : le moteur copié dans le projet est celui que l'installeur
  a posé.
- `hooks.configuration` et `hooks.trace` : les hooks de l'agent sont déclarés,
  et ils ont réellement tiré pendant la session qui a produit chaque commit.
"""

from __future__ import annotations

import json
import re

from socle import config, empreinte, memoire, outils
from socle.contexte import controle

ABSENT = object()

# (motif de clé, sens) — `bas` : plus petit est plus strict ; `vrai` : vrai
# est plus strict ; `faux` : faux ou absent est plus strict (un module « à
# mesurer » qui reçoit son plafond) ; `inclus` : une liste plus courte est
# plus stricte (des exclusions) ; `couvre` : une liste plus longue est plus
# stricte (une couverture).
REGLES = [
    (("budgets", "*", "max_bytes|max_lines"), "bas"),
    (("staleness", "active_days"), "bas"),
    (("mutation", "caps", "*", "max"), "bas"),
    (("mutation", "caps", "*", "reason"), "libre"),
    (("mutation", "caps", "*", "pending"), "faux"),
    (("nocopy", "min_chars"), "bas"),
    (("nocopy", "exclude"), "inclus"),
    (("references", "exclude"), "inclus"),
    (("references", "scan"), "couvre"),
    (("tooling", "paths"), "couvre"),
    (("memory", "code"), "couvre"),
    (("memory", "require_update_on_code_change"), "vrai"),
    (("requests", "internal_id_patterns"), "couvre"),
    (("tests", "spec_paths"), "inclus"),
    (("adoption", "warn_only"), "inclus"),
]


def _cle(chemin: tuple[str, ...]) -> str:
    morceaux = []
    for c in chemin:
        morceaux.append(c if re.fullmatch(r"[A-Za-z0-9_-]+", c) else json.dumps(c, ensure_ascii=False))
    return ".".join(morceaux)


def aplatir(d, prefixe=()) -> dict[tuple[str, ...], object]:
    res = {}
    for k, v in d.items():
        if k in ("docmap", "values") and not prefixe:
            continue  # comparés à part
        if isinstance(v, dict):
            res.update(aplatir(v, prefixe + (k,)))
        else:
            res[prefixe + (k,)] = v
    return res


def _regle(chemin: tuple[str, ...]) -> str | None:
    """Les règles se comparent composante par composante : une clé de budget
    est un motif de chemin, qui porte lui-même des points."""
    for motif, sens in REGLES:
        if len(motif) == len(chemin) and all(
            m == "*" or re.fullmatch(m, c) for m, c in zip(motif, chemin)
        ):
            return sens
    return None


def assouplissements(avant: dict, apres: dict, modules_existants: set[str] | None = None) -> list[tuple[str, str]]:
    """[(clé citable, explication)] des assouplissements de `avant` à `apres`."""
    res = []
    a, b = aplatir(avant), aplatir(apres)
    for chemin in sorted(set(a) | set(b)):
        va, vb = a.get(chemin, ABSENT), b.get(chemin, ABSENT)
        if va == vb:
            continue
        cle = _cle(chemin)
        sens = _regle(chemin)
        if sens == "libre":
            continue
        if va is ABSENT:
            if sens in ("bas", "vrai", "couvre", "faux") or (sens == "inclus" and not vb):
                continue  # un seuil ou une couverture qui apparaît durcit
            res.append((cle, f"clé ajoutée : {vb!r}"))
            continue
        if vb is ABSENT:
            if chemin[:2] == ("mutation", "caps") and modules_existants is not None and chemin[2] not in modules_existants:
                continue  # le module a disparu : son plafond avec lui
            if sens == "faux":
                continue  # « à mesurer » qui disparaît : le plafond mesuré le remplace
            res.append((cle, f"seuil retiré (valait {va!r})"))
            continue
        if sens == "bas" and isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            if vb > va:
                res.append((cle, f"{va} → {vb}"))
        elif sens == "vrai":
            if va and not vb:
                res.append((cle, f"{va} → {vb}"))
        elif sens == "faux":
            if vb and not va:
                res.append((cle, f"{va} → {vb}"))
        elif sens == "couvre":
            retires = set(va or []) - set(vb or [])
            if retires:
                res.append((cle, f"couverture retirée : {sorted(retires)}"))
        elif sens == "inclus":
            ajoutes = set(vb or []) - set(va or [])
            if ajoutes:
                res.append((cle, f"exclusion ajoutée : {sorted(ajoutes)}"))
        else:
            res.append((cle, f"changement non classé : {va!r} → {vb!r}"))

    code_avant = {g for l in avant.get("docmap", []) for g in l.get("code", [])}
    code_apres = {g for l in apres.get("docmap", []) for g in l.get("code", [])}
    for g in sorted(code_avant - code_apres):
        res.append((f"docmap {json.dumps(g, ensure_ascii=False)}", "correspondance code ↔ doc retirée"))
    vals_avant = {v.get("name"): v for v in avant.get("values", [])}
    vals_apres = {v.get("name"): v for v in apres.get("values", [])}
    for nom, decl in vals_avant.items():
        if nom not in vals_apres:
            res.append((f"values {json.dumps(nom, ensure_ascii=False)}", "valeur liée retirée"))
        elif vals_apres[nom] != decl:
            res.append((f"values {json.dumps(nom, ensure_ascii=False)}", "source de la valeur changée"))
    return res


def _valide_par(ctx, *citations: str):
    for d in ctx.validations:
        if all(c in d.texte for c in citations):
            return d
    return None


@controle("cliquet.garde-fous", base=True)
def cliquet(ctx, r):
    """Durcir un garde-fou est libre ; l'assouplir exige une demande validée
    qui cite la clé (politique, point 1)."""
    avant = ctx.projet_base.garde_fous if ctx.projet_base else {}
    if not avant:
        return  # installation : rien à comparer
    if ctx.migre:  # une migration de format renomme les chemins, elle n'assouplit rien
        avant = traduire_profond(avant, ctx.projet.chemins.format)
    for cle, pourquoi in assouplissements(avant, ctx.projet.garde_fous, set(ctx.fichiers)):
        d = _valide_par(ctx, cle)
        if d:
            r.avertir("cliquet.garde-fous", f"assouplissement validé par {d.id} : {cle} — {pourquoi}",
                      ctx.projet.chemins.garde_fous)
        else:
            r.erreur("cliquet.garde-fous", f"assouplissement sans validation humaine : {cle} — {pourquoi}. "
                     f"Émettre une demande qui cite `{cle}` ; elle couvrira ce changement une fois validée",
                     ctx.projet.chemins.garde_fous)



def traduire_profond(valeur, vers: int):
    """Les garde-fous d'un format dans l'autre : chaque chemin, clé ou
    valeur, sous son nom du format `vers`."""
    if isinstance(valeur, dict):
        return {traduire_profond(k, vers): traduire_profond(v, vers) for k, v in valeur.items()}
    if isinstance(valeur, list):
        return [traduire_profond(v, vers) for v in valeur]
    if isinstance(valeur, str):
        return config.traduire(valeur, vers=vers)
    return valeur

@controle("protege.fichiers", base=True)
def proteges(ctx, r):
    """Un fichier protégé ne change qu'avec une demande validée qui cite son
    empreinte nouvelle (hooks, CI, politique, adaptateur, moteur)."""
    if not ctx.projet_base or not ctx.projet_base.installe:
        installes = outils.filtrer(ctx.changes, ctx.projet.chemins_proteges())
        if installes:
            r.avertir("protege.fichiers", f"installation du socle : {len(installes)} fichier(s) protégé(s) posé(s) — "
                      "la politique par défaut est celle du cadrage")
        return
    motifs = set(ctx.projet.chemins_proteges()) | set(ctx.projet_base.chemins_proteges())
    for c in outils.filtrer(ctx.changes, sorted(motifs)):
        if memoire.est_reponse(c):
            continue  # les réponses sont le mécanisme de validation lui-même
        if ctx.projet.mode == config.MODE_AMONT and c.startswith(ctx.projet.dossier_moteur + "/socle/"):
            continue
        present = (ctx.racine / c).is_file() if ctx.tete is None else ctx.lire(c) is not None
        if present and ctx.tete is None:
            cite = empreinte.courte(empreinte.fichier(ctx.racine / c))
        elif present:
            cite = "sha256:" + outils.sha256(ctx.lire(c))[:16]
        else:
            cite = "supprimé"
        d = _valide_par(ctx, c, cite)
        if d:
            r.avertir("protege.fichiers", f"modification validée par {d.id}", c)
        else:
            r.erreur("protege.fichiers", f"fichier protégé modifié sans validation humaine. Une demande validée "
                     f"doit citer `{c}` et `{cite}`", c)


@controle("moteur.empreinte")
def moteur(ctx, r):
    """Le moteur du projet est celui que l'installeur a posé."""
    if not ctx.projet.installe:
        r.erreur("moteur.empreinte", f"socle non installé : `{ctx.projet.chemins.lock}` absent (commité ? un "
                 ".gitignore du projet peut l'écarter)")
        return
    if ctx.projet.mode == config.MODE_AMONT:
        r.indisponible("moteur.empreinte", "mode amont : ce dépôt fabrique le moteur, son empreinte n'est pas figée")
        return
    attendue = ctx.projet.lock.get("fingerprint")
    calculee, n = empreinte.calculer(ctx.racine, ctx.projet.dossier_moteur)
    if n == 0:
        r.erreur("moteur.empreinte", f"moteur introuvable dans {ctx.projet.dossier_moteur}")
    elif calculee != attendue:
        r.erreur("moteur.empreinte", f"moteur altéré : empreinte {empreinte.courte(calculee)}, "
                 f"le verrou attend {empreinte.courte(str(attendue))}. Relancer l'installeur, jamais réparer à la main",
                 ctx.projet.chemins.lock)


HOOKS_REQUIS = ("SessionStart", "PreToolUse", "Stop")


@controle("hooks.configuration")
def configuration(ctx, r):
    """Les hooks de l'agent sont déclarés et appellent le moteur."""
    if not ctx.projet.pol("agents", "claude_code", defaut=True):
        return
    texte = ctx.lire(".claude/settings.json")
    if texte is None:
        r.erreur("hooks.configuration", "`.claude/settings.json` absent : les hooks de Claude Code ne sont pas déclarés")
        return
    try:
        conf = json.loads(texte)
    except json.JSONDecodeError as e:
        r.erreur("hooks.configuration", f"JSON illisible : {e}", ".claude/settings.json")
        return
    for evt in HOOKS_REQUIS:
        commandes = [h.get("command", "") for bloc in conf.get("hooks", {}).get(evt, []) for h in bloc.get("hooks", [])]
        if not any(".socle/socle" in c and "hook" in c for c in commandes):
            r.erreur("hooks.configuration", f"aucun hook {evt} n'appelle `.socle/socle hook`", ".claude/settings.json")


def lire_trailer_hooks(valeur: str) -> dict[str, str]:
    res = {}
    for morceau in valeur.replace(",", " ").split():
        if "=" in morceau:
            k, v = morceau.split("=", 1)
            res[k] = v
    return res


def est_agent(projet, message: str) -> bool:
    marqueurs = projet.pol("agents", "markers", defaut=[r"(?im)^co-authored-by:.*\bclaude\b", r"(?im)^socle-agent:"])
    return any(re.search(m, message) for m in marqueurs)


@controle("hooks.trace", etages=("ci",), base=True)
def trace(ctx, r):
    """Chaque commit d'agent porte la trace des hooks qui ont tiré pendant sa
    session (`Socle-Hooks:`, ajouté par le hook git). Absente, ou sans
    PreToolUse : les hooks n'ont jamais été chargés."""
    for c in ctx.commits:
        if len(c["parents"]) != 1 or not est_agent(ctx.projet, c["message"]):
            continue
        if all(outils.lire_a(ctx.racine, c["parents"][0], f.lock) is None for f in config.FORMATS.values()):
            continue  # le socle n'était pas encore installé
        sujet = c["message"].strip().splitlines()[0]
        valeurs = outils.trailers(c["message"]).get("socle-hooks")
        if not valeurs:
            r.erreur("hooks.trace", f"{c['sha'][:10]} « {sujet} » : commit d'agent sans trailer `Socle-Hooks` — "
                     "les hooks git n'ont pas tourné (`git config core.hooksPath .socle/git-hooks`)")
            continue
        t = lire_trailer_hooks(valeurs[-1])
        if not t.get("PreToolUse", "0").isdigit() or int(t.get("PreToolUse", "0")) < 1:
            r.erreur("hooks.trace", f"{c['sha'][:10]} « {sujet} » : aucun PreToolUse n'a tiré pendant la session — "
                     "les hooks de l'agent n'étaient pas chargés")
        if t.get("SessionStart") == "0":
            r.erreur("hooks.trace", f"{c['sha'][:10]} « {sujet} » : le hook SessionStart n'a jamais tiré pendant la session")
