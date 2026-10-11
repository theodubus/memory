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
                       raison et son contrôle de remplacement ;
- `tests.code-teste` : une fonction publique ajoutée ou modifiée est nommée
                       par au moins un test, ou dispensée avec sa raison.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import tomllib
from collections import Counter
from pathlib import Path

from socle import config, langue, outils, tests_lecture
from socle.contexte import controle

CAPACITES = ("format", "lint", "build", "tests", "mutation", "coverage", "regression")
# `f(x) == f(x)` est creux… sauf dans un test de déterminisme, qui appelle
# deux fois pour comparer. La raison s'écrit, comme pour un test désactivé.
VOULU = re.compile(r"socle\s*:\s*(?:voulu|intended)\s*[—–:-]\s*\S.{2,}", re.I)
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
        r.erreur("adaptateur.capacites", f"aucun adaptateur (`{ctx.projet.chemins.adaptateur}`)")
        return
    caps = ctx.projet.adaptateur.get("capabilities", {})
    for nom in CAPACITES:
        c = caps.get(nom)
        if c is None:
            r.erreur("adaptateur.capacites", f"capacité « {nom} » non déclarée : une commande, ou `absent` + `replacement`", ctx.projet.chemins.adaptateur)
        elif "command" not in c and not ("absent" in c and "replacement" in c):
            r.erreur("adaptateur.capacites", f"capacité « {nom} » : ni `command`, ni `absent` avec `replacement`", ctx.projet.chemins.adaptateur)
    if cfg_tests(ctx.projet) is None:
        r.erreur("adaptateur.capacites", "section `[tests]` sans `function` : les tests creux ne peuvent pas être détectés", ctx.projet.chemins.adaptateur)


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
        # Un test se désactive par un attribut (`#[ignore]`, `@Disabled`), sur
        # la ligne qui le définit (`test.skip(…)`, `xit "…"`) ou dans son corps
        # (`t.Skip(…)`, `markTestSkipped(…)`).
        marques = [*f.attributs, f.entete, *f.lignes_corps]
        desactive = ignore and any(ignore.search(a) for a in marques)
        if desactive and not (raison and any(raison.search(a) for a in marques)):
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
    """Une validation humaine, ou une spécification que l'humain a changée et
    qui nomme le test (politique, point 2, option B tranchée par Théo,
    ADR-0017) : une spécification que l'agent écrit dans le même travail ne
    l'autorise pas à changer le test."""
    for d in ctx.validations:
        if nom in d.texte:
            return f"validé par {d.id}"
    for c in _specs_nommant(ctx, nom):
        if _ecrite_par_l_humain(ctx, c, nom):
            return f"spécification changée par l'humain : {c}"
    return None


def _en_attente(ctx, nom: str) -> str | None:
    """À la fin du tour seulement (étage agent), une demande en attente,
    poussée telle quelle, qui nomme le test (B-0033) : le travail qui attend
    la réponse de l'humain peut rester dans l'arbre, au lieu d'être remisé
    hors de la mémoire. Le commit et la CI le refusent toujours."""
    from socle import demandes

    if ctx.etage != "agent":
        return None
    for d in ctx.demandes:
        if (d.id and d.reponse is None and d.entree is not None and "retiree" not in d.entree.meta
                and nom in d.texte and demandes.illisible(ctx.projet, d) is None):
            return d.id
    return None


def _specs_nommant(ctx, nom: str) -> list[str]:
    """Les spécifications changées dans la plage qui nomment le test."""
    specs = ctx.projet.gf("tests", "spec_paths", defaut=[ctx.projet.chemins.decisions + "/**"])
    return [c for c in outils.filtrer(ctx.changes, specs)
            if nom in (ctx.lire(c) or "") and nom not in (ctx.lire_base(c) or "")]


def _ecrite_par_l_humain(ctx, chemin: str, nom: str) -> bool:
    """La mention du test est commitée, et aucun commit d'agent de la plage
    n'a touché la spécification : une écriture en cours est celle de
    l'agent qui travaille."""
    from socle.controles_cliquet import est_agent

    if nom not in (outils.lire_a(ctx.racine, ctx.rev_commit, chemin) or ""):
        return False
    plage = ctx.rev_commit if ctx.base in (None, outils.ARBRE_VIDE) else f"{ctx.base}..{ctx.rev_commit}"
    touches = set(outils.git(ctx.racine, "log", "--format=%H", plage, "--", chemin, check=False).split())
    return not any(c["sha"] in touches and est_agent(ctx.projet, c["message"]) for c in ctx.commits)


@controle("tests.attendus", base=True)
def attendus(ctx, r):
    """Supprimer un test ou changer une valeur attendue exige une validation
    humaine, ou un changement de spécification qui le nomme, fait par
    l'humain (politique, point 2)."""
    cfg = cfg_tests(ctx.projet)
    if cfg is None:
        r.indisponible("tests.attendus", "adaptateur sans `[tests]`")
        return
    # Les lignes qui portent une valeur attendue : les assertions, et ce que
    # l'adaptateur y ajoute (`expected` : en Go, la condition `if got != 4`).
    assertion = re.compile(cfg.get("expected") or cfg.get("assertion", r"assert"))
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
            attente = None if pourquoi else _en_attente(ctx, a.nom)
            if pourquoi:
                r.avertir("tests.attendus", f"test `{a.nom}` supprimé ({pourquoi})", a.fichier, a.ligne)
            elif attente:
                r.avertir("tests.attendus", f"test `{a.nom}` supprimé, en attente de {attente} : le tour peut finir, "
                          "le commit et la CI attendent la réponse de l'humain", a.fichier, a.ligne)
            else:
                r.erreur("tests.attendus", f"test `{a.nom}` supprimé sans validation humaine ni changement de "
                         "spécification qui le nomme" + _note_agent(ctx, a.nom), a.fichier, a.ligne)
            continue
        av = Counter(l.strip() for l in a.lignes_corps if assertion.search(l))
        ap = Counter(l.strip() for l in b.lignes_corps if assertion.search(l))
        disparues = av - ap
        if disparues:
            pourquoi = _justifie(ctx, a.nom)
            attente = None if pourquoi else _en_attente(ctx, a.nom)
            exemple = next(iter(disparues))
            if pourquoi:
                r.avertir("tests.attendus", f"assertion changée dans `{a.nom}` ({pourquoi})", b.fichier, b.ligne)
            elif attente:
                r.avertir("tests.attendus", f"assertion changée dans `{a.nom}`, en attente de {attente} : le tour "
                          "peut finir, le commit et la CI attendent la réponse de l'humain", b.fichier, b.ligne)
            else:
                r.erreur("tests.attendus", f"assertion changée ou retirée dans `{a.nom}` : « {exemple} » — "
                         "valeur attendue modifiée sans spécification ni validation humaine" + _note_agent(ctx, a.nom),
                         b.fichier, b.ligne)


def _note_agent(ctx, nom: str) -> str:
    specs = _specs_nommant(ctx, nom)
    if not specs:
        return ""
    return (f" ; la spécification {specs[0]} le nomme, mais elle est écrite par l'agent : elle ne suffit pas "
            "(politique, point 2). Poser une demande à l'humain, ou qu'il change lui-même la spécification")


# `Dispense-test: f, g — raison` : les fonctions nommées, puis pourquoi
# aucun test ne les nomme.
DISPENSE_TEST = re.compile(r"^(?P<noms>[\w.]+(?:\s*,\s*[\w.]+)*)\s+[—–-]+\s+(?P<raison>\S.{9,})$")


def config_code(projet) -> tuple[list, list, str | None]:
    """(chemins, exclusions, motif d'une fonction privée) du code soumis à
    `tests.code-teste`. La section `[code]` de l'adaptateur du projet ; à
    défaut, celle de l'adaptateur maintenu du même langage, venue avec le
    moteur ; à défaut, les sources hors fichiers de test, toute fonction
    comptant comme publique."""
    code = projet.adaptateur.get("code")
    if code is None:
        from socle import installeur

        maintenu = installeur.ADAPTATEURS / f"{projet.adaptateur.get('language', '')}.toml"
        if maintenu.is_file():
            code = tomllib.loads(maintenu.read_text(encoding="utf-8")).get("code")
    # Le dossier du socle n'est jamais du code du projet : le moteur y est
    # installé, immuable, et ses fonctions ne sont pas celles du projet.
    socle = [f"{config.DOSSIER}/**"]
    if code and "paths" in code:
        return code.get("paths", []), code.get("exclude", []) + socle, code.get("private")
    return projet.adaptateur.get("sources", []), (cfg_tests(projet) or {}).get("paths", []) + socle, None


def dispenses_tests(ctx, r) -> set[str]:
    noms = set()
    for c in ctx.commits:
        for v in langue.trailers(c["message"]).get("dispense-test", []):
            m = DISPENSE_TEST.match(v.strip())
            if not m:
                r.erreur("tests.code-teste", f"dispense illisible dans le commit {c['sha'][:7]} : « {v.strip()} » — "
                         "forme attendue : `Dispense-test: f, g — <raison d'au moins dix caractères>`")
                continue
            noms |= {n.strip() for n in m["noms"].split(",")}
    return noms


def _externes(fns: list[tests_lecture.Fonction]) -> list[tests_lecture.Fonction]:
    """Les fonctions qui ne sont pas imbriquées dans une autre : une
    fonction locale compte pour celle qui la contient."""
    res, fin = [], 0
    for f in sorted(fns, key=lambda f: f.ligne):
        if f.ligne > fin:
            res.append(f)
            fin = f.fin
    return res


@controle("tests.code-teste", etages=("agent", "ci"), base=True)
def code_teste(ctx, r):
    """Une fonction publique ajoutée ou modifiée est nommée par au moins un
    test — ou une dispense motivée la nomme (`Dispense-test: f — <raison>`).

    Pas à l'étage git : le hook pre-commit ne voit pas le message du commit,
    donc pas la dispense qu'il porte."""
    cfg = cfg_tests(ctx.projet)
    if cfg is None:
        r.indisponible("tests.code-teste", "adaptateur sans `[tests]` : fonctions illisibles")
        return
    chemins, exclus, prive = config_code(ctx.projet)
    prive_re = re.compile(prive) if prive else None
    presents = set(ctx.fichiers)
    code = outils.filtrer([c for c in ctx.changes if c in presents], chemins, exclus)
    if not code:
        return
    # Ce que les tests nomment : tout le texte d'un fichier de test qui n'est
    # pas du code ; le corps des seules fonctions de test d'un fichier qui en
    # est (les tests unitaires de Rust vivent dans les sources).
    nommes = []
    for f in fichiers_tests(ctx, ctx.fichiers):
        texte = ctx.lire(f) or ""
        if outils.filtrer([f], chemins, exclus):
            nommes += [fn.corps for fn in tests_lecture.extraire(texte, f, cfg) if fn.est_test]
        else:
            nommes.append(texte)
    nommes = "\n".join(nommes)
    dispenses = dispenses_tests(ctx, r)
    for chemin in code:
        texte = ctx.lire(chemin) or ""
        lignes_texte = texte.splitlines()
        changees = outils.lignes_changees(ctx.racine, ctx.base, ctx.tete, chemin)
        avant = {f.nom for f in tests_lecture.extraire(ctx.lire_base(chemin) or "", chemin, cfg)}
        for f in _externes(tests_lecture.extraire(texte, chemin, cfg)):
            if f.est_test or (prive_re and prive_re.match(lignes_texte[f.ligne - 1])):
                continue
            if changees is not None and not any(f.ligne <= l <= f.fin for l in changees):
                continue
            if f.nom in dispenses or re.search(rf"(?<![\w]){re.escape(f.nom)}(?![\w])", nommes):
                continue
            quoi = "modifiée" if f.nom in avant else "ajoutée"
            r.erreur("tests.code-teste", f"fonction `{f.nom}` {quoi}, qu'aucun test ne nomme : écrire le test qui "
                     f"l'appelle, ou la dispenser par un trailer de commit `Dispense-test: {f.nom} — <raison>`",
                     chemin, f.ligne)


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
    fichier, où `{file}`, `{stem}`, `{module}` et `{dir}`, son dossier, se
    remplacent ; un même argument ne se répète pas)."""
    gabarit = cap.get("test_arg", "--test {stem}")
    args = []
    for t in tests:
        module = t[: -len(Path(t).suffix)].replace("/", ".") if Path(t).suffix else t.replace("/", ".")
        dossier = str(Path(t).parent) if str(Path(t).parent) != "." else ""
        arg = (gabarit.replace("{file}", t).replace("{stem}", Path(t).stem).replace("{module}", module)
               .replace("{dir}", dossier))
        if arg not in args:
            args.append(arg)
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
        # Les dépendances installées, que git ignore (`node_modules`, `vendor`) :
        # le worktree les partage avec l'arbre de travail au lieu de les
        # réinstaller (`shared` de la capacité), ou les copie (`copied`) quand
        # leur chargeur résout les liens : l'autoload de Composer chargerait
        # sinon le code de l'arbre de travail, pas celui du parent.
        for d in cap.get("shared", []):
            if (ctx.racine / d).exists() and not (arbre / d).exists():
                (arbre / d).symlink_to(ctx.racine / d, target_is_directory=(ctx.racine / d).is_dir())
        for d in cap.get("copied", []):
            if (ctx.racine / d).is_dir() and not (arbre / d).exists():
                shutil.copytree(ctx.racine / d, arbre / d, symlinks=True)
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
    # `modules_exclude` : ce que l'outil ne mute pas (les tests de Go vivent à
    # côté du code qu'ils testent).
    modules = outils.filtrer(ctx.fichiers, cap.get("modules", []), cap.get("modules_exclude", []))
    for m in modules:
        if m not in caps and porte.search(ctx.lire(m) or ""):
            r.erreur("mutation.couverture", "module hors du cliquet de mutation : lui mesurer un plafond "
                     "(`[mutation.caps]` des garde-fous), depuis un arbre vert", m)
    for m in caps:
        if m not in ctx.fichiers:
            r.erreur("mutation.couverture", f"le cliquet nomme `{m}`, qui n'existe pas", ctx.projet.chemins.garde_fous)
        elif "reason" not in caps[m] and caps[m].get("max", 0) > 0:
            r.erreur("mutation.couverture", f"plafond non nul sans raison écrite pour `{m}`", ctx.projet.chemins.garde_fous)
