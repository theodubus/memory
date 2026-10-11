"""Garde-fous documentation ↔ code.

Chaque règle est un contrôle qui échoue en cas de divergence, au lieu de
compter sur la vigilance de l'agent. Les ensembles contrôlés sont parcourus
par motif, jamais énumérés à la main : une liste écrite à la main laisserait
le jugement décider de la couverture — leçon de `chess:engine/tests/outillage_documente.rs`.
"""

from __future__ import annotations

import re
import subprocess
from collections import defaultdict

from socle import config, outils
from socle.contexte import controle

MARQUEUR_VALEUR = re.compile(
    r"<!--\s*valeur\s*:\s*(?P<nom>[\w.-]+)\s*-->(?P<valeur>.*?)<!--\s*/valeur\s*-->", re.S
)
MOTIFS_OUTILLAGE_DEFAUT = [
    ".socle/git-hooks/*",
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
    ".claude/settings.json",
]


@controle("docs.outillage")
def outillage(ctx, r):
    """Tout dispositif du dépôt est nommé dans la documentation."""
    motifs = ctx.projet.gf("tooling", "paths", defaut=MOTIFS_OUTILLAGE_DEFAUT)
    docs = ctx.documents()
    for chemin in outils.filtrer(ctx.fichiers, motifs):
        nom = chemin.rsplit("/", 1)[-1]
        if not any(nom in texte for c, texte in docs.items() if c != chemin):
            r.erreur("docs.outillage", f"dispositif qu'aucun document ne nomme : `{nom}` — le nommer, avec ce qu'il fait et pourquoi", chemin)


def normaliser_valeur(v: str) -> str:
    """`70 452`, `70 452`, `70,452` et `70452` se valent."""
    v = re.sub(r"<[^>]+>|[`*_]", "", v)
    v = v.strip()
    if re.fullmatch(r"[\d\s  .,]+", v):
        return re.sub(r"[\s  ,]", "", v)
    return re.sub(r"\s+", " ", v)


def valeur_source(ctx, decl: dict) -> tuple[str | None, str | None]:
    """(valeur, erreur). Une source est un fichier ou une commande, lu par une
    expression régulière dont le premier groupe est la valeur."""
    regex = decl.get("regex")
    if not regex:
        return None, "déclaration sans `regex`"
    if "file" in decl:
        texte = ctx.lire(decl["file"])
        if texte is None:
            return None, f"source absente : {decl['file']}"
    elif "command" in decl:
        try:
            p = subprocess.run(decl["command"], shell=True, cwd=ctx.racine, capture_output=True,
                               text=True, timeout=decl.get("timeout", 600))
        except subprocess.TimeoutExpired:
            return None, f"la commande source a dépassé son délai : {decl['command']}"
        if p.returncode != 0:
            return None, f"la commande source a échoué ({p.returncode}) : {decl['command']}"
        texte = p.stdout
    else:
        return None, "déclaration sans `file` ni `command`"
    m = re.search(regex, texte, re.M)
    if not m:
        return None, f"la regex `{regex}` ne trouve rien dans la source"
    return (m.group(1) if m.groups() else m.group(0)), None


@controle("docs.valeurs")
def valeurs(ctx, r):
    """Toute valeur citée dans la doc est liée à sa source, et les deux concordent."""
    decls = {d.get("name"): d for d in ctx.projet.gf("values", defaut=[]) or []}
    docs = ctx.documents()
    sources: dict[str, str | None] = {}
    for nom, decl in decls.items():
        if not nom:
            r.erreur("docs.valeurs", "valeur déclarée sans `name`", config.GARDE_FOUS)
            continue
        if "command" in decl and ctx.rapide and not decl.get("fast", False):
            sources[nom] = None
            continue
        v, err = valeur_source(ctx, decl)
        if err:
            r.erreur("docs.valeurs", f"`{nom}` : {err}", config.GARDE_FOUS)
        sources[nom] = v

    cites = defaultdict(int)
    for chemin, texte in docs.items():
        for m in MARQUEUR_VALEUR.finditer(texte):
            nom = m["nom"]
            ligne = texte.count("\n", 0, m.start()) + 1
            cites[nom] += 1
            if nom not in decls:
                r.erreur("docs.valeurs", f"valeur `{nom}` citée sans source déclarée (`[[values]]`)", chemin, ligne)
                continue
            attendu = sources.get(nom)
            if attendu is None:
                continue
            if normaliser_valeur(m["valeur"]) != normaliser_valeur(attendu):
                r.erreur("docs.valeurs", f"`{nom}` vaut « {attendu.strip()} » à la source, la doc dit « {m['valeur'].strip()} »", chemin, ligne)

    # Une copie non liée de la valeur courante : la doc la porte sans marqueur.
    for nom, v in sources.items():
        if not v or len(normaliser_valeur(v)) < 3:
            continue
        motif = _motif_libre(v)
        for chemin, texte in docs.items():
            if chemin.startswith(config.MEMOIRE + "/journal/"):
                continue  # le journal consigne des valeurs passées, pas des copies
            nu = MARQUEUR_VALEUR.sub(" ", texte)
            for m in motif.finditer(nu):
                ligne = nu.count("\n", 0, m.start()) + 1
                r.avertir("docs.valeurs", f"« {m.group(0).strip()} » ressemble à la valeur `{nom}` sans marqueur : "
                          f"l'encadrer de `<!-- valeur:{nom} -->…<!-- /valeur -->`", chemin, ligne)


def _motif_libre(v: str) -> re.Pattern:
    n = normaliser_valeur(v)
    if n.isdigit():
        # Les chiffres, avec n'importe quels séparateurs de milliers.
        corps = r"[\s  ,.]?".join(re.escape(c) for c in n)
        return re.compile(rf"(?<![\d.,]){corps}(?![\d])")
    return re.compile(re.escape(n))


def dispenses(ctx) -> list[str]:
    res = []
    for c in ctx.commits:
        for v in outils.trailers(c["message"]).get("dispense-doc", []):
            if len(v.strip()) >= 15:
                res.append(v.strip())
    return res


@controle("docs.correspondance", etages=("agent", "ci"), base=True)
def correspondance(ctx, r):
    """Si du code change, la doc qui lui est associée change aussi — ou une
    dispense écrite et motivée l'accompagne (`Dispense-doc: <raison>`).

    Pas à l'étage git : le hook pre-commit ne voit pas le message du commit,
    donc pas la dispense qu'il porte."""
    table = ctx.projet.gf("docmap", defaut=[]) or []
    if not table:
        return
    changes = ctx.changes
    motifs_dispense = dispenses(ctx)
    for ligne in table:
        code = outils.filtrer(changes, ligne.get("code", []))
        if not code:
            continue
        docs = outils.filtrer(changes, ligne.get("docs", []))
        if docs:
            continue
        if motifs_dispense:
            r.avertir("docs.correspondance", f"{len(code)} fichier(s) de code sans doc associée, dispensé : « {motifs_dispense[0]} »")
            continue
        r.erreur(
            "docs.correspondance",
            f"code changé sans sa doc associée : {', '.join(code[:5])}{' …' if len(code) > 5 else ''} → "
            f"mettre à jour {' ou '.join(ligne.get('docs', []))}, ou motiver une dispense "
            "par un trailer de commit `Dispense-doc: <raison>`",
        )


def paragraphes(texte: str):
    """(ligne de début, paragraphe normalisé) ; les blocs de code comptent
    pour un paragraphe chacun."""
    bloc, debut = [], None
    for i, ligne in enumerate(texte.splitlines(), start=1):
        if ligne.strip():
            if debut is None:
                debut = i
            bloc.append(ligne.strip())
        elif bloc:
            yield debut, " ".join(bloc)
            bloc, debut = [], None
    if bloc:
        yield debut, " ".join(bloc)


@controle("docs.copie")
def copie(ctx, r):
    """Un même contenu dans deux fichiers est une copie qui divergera : refusé.

    Sauf dans les demandes : le contrat veut qu'une demande se lise seule,
    son contexte résumé sur place plutôt que renvoyé ailleurs, et elle est
    gelée une fois répondue. Deux approbations écrites par le même gabarit
    se ressemblent forcément (B-0019)."""
    minimum = ctx.projet.gf("nocopy", "min_chars", defaut=200)
    exclus = ctx.projet.exclusions_docs() + list(ctx.projet.gf("nocopy", "exclude", defaut=[])) + [
        f"{config.MEMOIRE}/demandes/**", f"{config.MEMOIRE}/prive/demandes/**"]
    vus: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for chemin, texte in ctx.textes(["**/*.md"], exclus).items():
        for debut, p in paragraphes(texte):
            if len(p) >= minimum:
                vus[re.sub(r"\s+", " ", p)].append((chemin, debut))
    for p, lieux in vus.items():
        fichiers = {c for c, _ in lieux}
        if len(fichiers) > 1:
            premier = lieux[0]
            autres = ", ".join(f"{c}:{l}" for c, l in lieux[1:])
            r.erreur("docs.copie", f"paragraphe identique aussi présent en {autres} : garder une source, renvoyer vers elle", premier[0], premier[1])
