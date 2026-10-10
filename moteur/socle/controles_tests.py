"""Garde-fous de tests : un test ne prouve rien tant qu'un contrôle n'a pas
montré qu'il peut échouer.

- `tests.creux`      : test sans assertion, assertion tautologique, test
                       désactivé sans raison écrite ;
- `tests.attendus`   : test supprimé ou valeur attendue changée sans
                       changement de spécification ni validation humaine ;
- `tests.regression` : tout correctif livre un test qui échoue sur le commit
                       parent et passe sur le correctif ;
- `mutation.couverture` : tout module qui porte du code a un plafond de
                       mutants survivants ;
- `adaptateur.capacites` : chaque capacité est déclarée, ou absente avec sa
                       raison et son contrôle de remplacement.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from socle import outils, tests_lecture
from socle.contexte import controle

CAPACITES = ("format", "lint", "build", "tests", "mutation", "coverage", "regression")
# `f(x) == f(x)` est creux… sauf dans un test de déterminisme, qui appelle
# deux fois pour comparer. La raison s'écrit, comme pour un test désactivé.
VOULU = re.compile(r"socle\s*:\s*voulu\s*[—–:-]\s*\S.{2,}", re.I)
FIX_DEFAUT = r"(?i)^(fix|corrige|correctif|correction)\b"


def cfg_tests(projet) -> dict | None:
    t = projet.adaptateur.get("tests")
    if not t or "function" not in t:
        return None
    return t


def fonctions(ctx, chemins, rev_tete=True) -> list[tests_lecture.Fonction]:
    cfg = cfg_tests(ctx.projet)
    res = []
    for c in chemins:
        texte = ctx.lire(c) if rev_tete else ctx.lire_base(c)
        if texte is not None:
            res += tests_lecture.extraire(texte, c, cfg)
    return res


def fichiers_tests(ctx, liste) -> list[str]:
    cfg = cfg_tests(ctx.projet)
    return outils.filtrer(liste, cfg.get("paths", []), cfg.get("exclude", []))


@controle("adaptateur.capacites")
def capacites(ctx, r):
    """Aucune capacité n'est omise en silence : déclarée, ou absente avec sa
    raison et son contrôle de remplacement."""
    if not ctx.projet.adaptateur:
        r.erreur("adaptateur.capacites", "aucun adaptateur (`.socle/adaptateur.toml`)")
        return
    caps = ctx.projet.adaptateur.get("capabilities", {})
    for nom in CAPACITES:
        c = caps.get(nom)
        if c is None:
            r.erreur("adaptateur.capacites", f"capacité « {nom} » non déclarée : une commande, ou `absent` + `replacement`", ".socle/adaptateur.toml")
        elif "command" not in c and not ("absent" in c and "replacement" in c):
            r.erreur("adaptateur.capacites", f"capacité « {nom} » : ni `command`, ni `absent` avec `replacement`", ".socle/adaptateur.toml")
    if cfg_tests(ctx.projet) is None:
        r.erreur("adaptateur.capacites", "section `[tests]` sans `function` : les tests creux ne peuvent pas être détectés", ".socle/adaptateur.toml")


@controle("tests.creux")
def creux(ctx, r):
    """Pas de test sans assertion, d'assertion tautologique, ni de test
    désactivé sans raison écrite. Sur le diff aux étages agent et git ; partout en CI."""
    cfg = cfg_tests(ctx.projet)
    if cfg is None:
        r.indisponible("tests.creux", "adaptateur sans `[tests]` : détection impossible")
        return
    tous = fichiers_tests(ctx, ctx.fichiers)
    cibles = tous if ctx.etage == "ci" or not ctx.base else fichiers_tests(ctx, ctx.changes)
    cibles = [c for c in cibles if c in set(ctx.fichiers)]
    # Les aides se cherchent dans TOUS les fichiers de test et de source : une
    # aide qui affirme peut vivre ailleurs que le test qui l'appelle.
    sources = outils.filtrer(ctx.fichiers, ctx.projet.adaptateur.get("sources", []))
    toutes = fonctions(ctx, sorted(set(tous) | set(sources)))
    assertion = re.compile(cfg.get("assertion", r"assert"))
    aides = tests_lecture.aides_qui_affirment(toutes, assertion)
    ignore = re.compile(cfg["ignore"]) if cfg.get("ignore") else None
    raison = re.compile(cfg["ignore_reason"]) if cfg.get("ignore_reason") else None
    tautos = [re.compile(t) for t in cfg.get("tautology", [])]
    for f in [f for f in toutes if f.fichier in cibles and f.est_test]:
        desactive = ignore and any(ignore.search(a) for a in f.attributs)
        if desactive and not (raison and any(raison.search(a) for a in f.attributs)):
            r.erreur("tests.creux", f"test `{f.nom}` désactivé sans raison écrite", f.fichier, f.ligne)
        if not tests_lecture.affirme(f, assertion, aides):
            r.erreur("tests.creux", f"test `{f.nom}` sans assertion : il passe sans rien mesurer", f.fichier, f.ligne)
        for k, ligne in enumerate(f.lignes_corps):
            precedente = f.lignes_corps[k - 1] if k else ""
            if VOULU.search(ligne) or VOULU.search(precedente):
                continue  # une tautologie voulue, raison écrite (un test de déterminisme)
            for t in tautos:
                if t.search(ligne):
                    r.erreur("tests.creux", f"assertion tautologique dans `{f.nom}` : « {ligne.strip()} » — "
                             "si elle est voulue (déterminisme), l'écrire : commentaire `socle: voulu — <raison>`",
                             f.fichier, f.ligne + k + 1)


def _justifie(ctx, nom: str) -> str | None:
    """Une validation humaine ou un changement de spécification qui nomme le test."""
    for d in ctx.validations:
        if nom in d.texte:
            return f"validé par {d.id}"
    specs = ctx.projet.gf("tests", "spec_paths", defaut=["memoire/decisions/**"])
    for c in outils.filtrer(ctx.changes, specs):
        texte = ctx.lire(c) or ""
        if nom in texte and nom not in (ctx.lire_base(c) or ""):
            return f"spécification changée : {c}"
    return None


@controle("tests.attendus", base=True)
def attendus(ctx, r):
    """Supprimer un test ou changer une valeur attendue exige un changement de
    spécification qui le nomme, ou une validation humaine (politique, point 2)."""
    cfg = cfg_tests(ctx.projet)
    if cfg is None:
        r.indisponible("tests.attendus", "adaptateur sans `[tests]`")
        return
    assertion = re.compile(cfg.get("assertion", r"assert"))
    changes = set(ctx.changes)
    avant_fichiers = [c for c in fichiers_tests(ctx, ctx.fichiers_base) if c in changes]
    if not avant_fichiers:
        return
    avant = [f for f in fonctions(ctx, avant_fichiers, rev_tete=False) if f.est_test]
    apres_tous = [f for f in fonctions(ctx, fichiers_tests(ctx, ctx.fichiers)) if f.est_test]
    par_cle = {(f.fichier, f.nom): f for f in apres_tous}
    par_corps = {re.sub(r"\s+", " ", f.corps) for f in apres_tous}
    for a in avant:
        b = par_cle.get((a.fichier, a.nom))
        if b is None:
            if re.sub(r"\s+", " ", a.corps) in par_corps:
                continue  # déplacé tel quel
            pourquoi = _justifie(ctx, a.nom)
            if pourquoi:
                r.avertir("tests.attendus", f"test `{a.nom}` supprimé ({pourquoi})", a.fichier, a.ligne)
            else:
                r.erreur("tests.attendus", f"test `{a.nom}` supprimé sans validation humaine ni changement de spécification qui le nomme", a.fichier, a.ligne)
            continue
        av = Counter(l.strip() for l in a.lignes_corps if assertion.search(l))
        ap = Counter(l.strip() for l in b.lignes_corps if assertion.search(l))
        disparues = av - ap
        if disparues:
            pourquoi = _justifie(ctx, a.nom)
            exemple = next(iter(disparues))
            if pourquoi:
                r.avertir("tests.attendus", f"assertion changée dans `{a.nom}` ({pourquoi})", b.fichier, b.ligne)
            else:
                r.erreur("tests.attendus", f"assertion changée ou retirée dans `{a.nom}` : « {exemple} » — "
                         "valeur attendue modifiée sans spécification ni validation humaine", b.fichier, b.ligne)


def est_correctif(projet, message: str) -> bool:
    sujet = message.strip().splitlines()[0] if message.strip() else ""
    motif = projet.gf("regression", "fix_subject", defaut=FIX_DEFAUT)
    tr = outils.trailers(message)
    return bool(re.search(motif, sujet)) or "corrige" in tr or "fixes" in tr


@controle("tests.regression", etages=("ci",), base=True, lent=True)
def regression(ctx, r):
    """Tout correctif livre un test qui échoue sur le commit parent et passe sur
    le correctif, vérifié en l'exécutant."""
    cap = ctx.projet.adaptateur.get("capabilities", {}).get("regression", {})
    correctifs = [c for c in ctx.commits if len(c["parents"]) == 1 and est_correctif(ctx.projet, c["message"])]
    if not correctifs:
        return
    if "command" not in cap:
        r.indisponible("tests.regression", f"capacité absente : {cap.get('absent', 'non déclarée')} — remplacement : {cap.get('replacement', '?')}")
        return
    motifs = cap.get("test_paths") or (cfg_tests(ctx.projet) or {}).get("paths", [])
    for c in correctifs:
        sha, parent = c["sha"], c["parents"][0]
        sujet = c["message"].strip().splitlines()[0]
        touches = outils.fichiers_changes(ctx.racine, parent, sha)
        tests = [t for t in outils.filtrer(touches, motifs) if outils.lire_a(ctx.racine, sha, t) is not None]
        if not tests:
            r.erreur("tests.regression", f"correctif sans test de régression : {sha[:10]} « {sujet} » "
                     f"(aucun fichier de {', '.join(motifs)} ajouté ou modifié)")
            continue
        code_parent = _executer_superpose(ctx, parent, sha, tests, cap)
        if code_parent is None:
            r.erreur("tests.regression", f"{sha[:10]} : impossible de préparer le commit parent")
            continue
        if code_parent == 0:
            r.erreur("tests.regression", f"{sha[:10]} « {sujet} » : son test passe déjà sur le parent — il ne prouve pas le correctif")
            continue
        code = _executer_superpose(ctx, sha, sha, tests, cap)
        if code != 0:
            r.erreur("tests.regression", f"{sha[:10]} « {sujet} » : son test de régression échoue sur le correctif lui-même")


def commande_regression(cap: dict, tests: list[str]) -> str:
    """Remplit `{files}`, `{stems}` et `{test_args}` (un `test_arg` par
    fichier, où `{file}`, `{stem}` et `{module}` se remplacent)."""
    gabarit = cap.get("test_arg", "--test {stem}")
    args = []
    for t in tests:
        module = t[: -len(Path(t).suffix)].replace("/", ".") if Path(t).suffix else t.replace("/", ".")
        args.append(gabarit.replace("{file}", t).replace("{stem}", Path(t).stem).replace("{module}", module))
    return (
        cap["command"]
        .replace("{files}", " ".join(tests))
        .replace("{stems}", " ".join(Path(t).stem for t in tests))
        .replace("{test_args}", " ".join(args))
    )


def _executer_superpose(ctx, rev: str, rev_tests: str, tests: list[str], cap: dict) -> int | None:
    """Exécute les tests de `rev_tests` sur l'arbre de `rev`, dans un worktree
    jetable. Rend le code de sortie."""
    atelier = Path(tempfile.mkdtemp(prefix="socle-regression-"))
    arbre = atelier / "arbre"
    try:
        if not outils.git_reussit(ctx.racine, "worktree", "add", "--detach", str(arbre), rev):
            return None
        for t in tests:
            contenu = outils.lire_a(ctx.racine, rev_tests, t)
            cible = arbre / t
            cible.parent.mkdir(parents=True, exist_ok=True)
            cible.write_text(contenu or "", encoding="utf-8")
        commande = commande_regression(cap, tests)
        p = subprocess.run(commande, shell=True, cwd=arbre, capture_output=True, text=True,
                           timeout=cap.get("timeout", 1800))
        return p.returncode
    finally:
        outils.git_reussit(ctx.racine, "worktree", "remove", "--force", str(arbre))
        shutil.rmtree(atelier, ignore_errors=True)


@controle("mutation.couverture")
def couverture_mutation(ctx, r):
    """Tout module qui porte du code est dans le cliquet de mutation, et le
    cliquet ne nomme que des modules qui existent."""
    cap = ctx.projet.adaptateur.get("capabilities", {}).get("mutation", {})
    if "command" not in cap:
        return  # absence déclarée : `adaptateur.capacites` en répond
    caps = ctx.projet.gf("mutation", "caps", defaut={}) or {}
    porte = re.compile(cap.get("has_code", r"."))
    modules = outils.filtrer(ctx.fichiers, cap.get("modules", []))
    for m in modules:
        if m not in caps and porte.search(ctx.lire(m) or ""):
            r.erreur("mutation.couverture", "module hors du cliquet de mutation : lui mesurer un plafond "
                     "(`[mutation.caps]` des garde-fous), depuis un arbre vert", m)
    for m in caps:
        if m not in ctx.fichiers:
            r.erreur("mutation.couverture", f"le cliquet nomme `{m}`, qui n'existe pas", ".socle/garde-fous.toml")
        elif "reason" not in caps[m] and caps[m].get("max", 0) > 0:
            r.erreur("mutation.couverture", f"plafond non nul sans raison écrite pour `{m}`", ".socle/garde-fous.toml")
