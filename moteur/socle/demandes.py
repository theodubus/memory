"""Le contrat des demandes de décision humaine.

Une demande en file est lue quand le contexte est perdu : elle doit se suffire
à elle-même. Le lint vérifie ce qu'un script peut vérifier — les sept champs,
et qu'aucun identifiant interne n'y paraisse sans description. La qualité de
l'explication, elle, ne se contrôle pas : la réponse `contexte-insuffisant`
renvoie la demande à l'agent, et ce renvoi reste consigné dans la réponse.

Une réponse vit à côté de la demande, dans `<demande>.reponse.toml`, et
seul l'humain l'écrit (`socle repondre`). Elle porte l'empreinte du texte
exact auquel l'humain a répondu : la demande est gelée dès qu'elle a une
réponse.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from socle import config, memoire, outils

SECTIONS = {
    "decision-demandee": "Décision demandée",
    "contexte": "Contexte",
    "elements-cites": "Éléments cités",
    "options": "Options",
    "consequences": "Conséquences",
    "recommandation": "Recommandation",
    "reponses-possibles": "Réponses possibles",
}
REPONSE_POSITIVE = "valider"
RENVOI = "contexte-insuffisant"

# Identifiants internes qui ne disent rien à qui n'a pas le projet en tête :
# ceux de la mémoire, un SHA, un numéro de PR ou d'issue. Le projet en ajoute
# d'autres (`requests.internal_id_patterns`), comme les codes de chantier.
MOTIFS_INTERNES = [
    memoire.ID_RE.pattern,
    r"(?<![\w/.-])(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,40}(?![\w-])",
    r"(?<![\w&])#\d+\b",
]
MOTS_DESCRIPTION_MIN = 5
SECTION_MIN = 15
# Un trou du gabarit : `<texte avec des espaces>`, hors commentaire HTML.
TROU = re.compile(r"<(?!!--)[^<>\n]*\s[^<>\n]*>")


@dataclass
class Demande:
    chemin: str
    texte: str
    entree: memoire.Entree | None
    sections: dict[str, str] = field(default_factory=dict)
    reponse: dict | None = None
    chemin_reponse: str | None = None
    erreur_reponse: str | None = None

    @property
    def id(self) -> str | None:
        return self.entree.id if self.entree else None

    @property
    def statut(self) -> str:
        if self.reponse is None:
            if self.entree and "retiree" in self.entree.meta:
                return "retirée"
            return "en attente"
        r = str(self.reponse.get("reponse", ""))
        return "renvoyée" if r == RENVOI else f"répondue : {r}"

    @property
    def validee(self) -> bool:
        return self.reponse is not None and self.reponse.get("reponse") == REPONSE_POSITIVE

    def reponses_possibles(self) -> list[str]:
        bloc = self.sections.get("reponses-possibles", "")
        return re.findall(r"^\s*[-*]\s+`([^`]+)`", bloc, flags=re.M)


def chemin_reponse(chemin_demande: str) -> str:
    return chemin_demande[: -len(".md")] + ".reponse.toml"


def decouper_sections(texte: str) -> dict[str, str]:
    res: dict[str, list[str]] = {}
    courante = None
    for _, ligne, code in memoire.lignes_hors_code(texte):
        m = None if code else re.match(r"^##\s+(.*?)\s*#*\s*$", ligne)
        if m and not ligne.startswith("###"):
            courante = outils.cle(m[1])
            res.setdefault(courante, [])
            continue
        if courante is not None:
            res[courante].append(ligne)
    return {k: "\n".join(v).strip() for k, v in res.items()}


def charger(racine: Path, rev: str | None, chemin: str, texte: str) -> Demande:
    f = memoire.analyser(chemin, texte)
    entrees = [e for e in f.entrees if e.type == "D"]
    d = Demande(chemin=chemin, texte=texte, entree=entrees[0] if entrees else None)
    d.sections = decouper_sections(texte)
    cr = chemin_reponse(chemin)
    brut = outils.lire_a(racine, rev, cr)
    if brut is not None:
        d.chemin_reponse = cr
        try:
            d.reponse = tomllib.loads(brut)
        except tomllib.TOMLDecodeError as e:
            d.reponse = {}
            d.erreur_reponse = f"réponse illisible : {e}"
    return d


def toutes(racine: Path, rev: str | None = None) -> list[Demande]:
    chemins = outils.fichiers_courants(racine) if rev is None else outils.fichiers_a(racine, rev)
    res = []
    for c in sorted(chemins):
        if memoire.couche_attendue(c) == "demandes":
            texte = outils.lire_a(racine, rev, c)
            if texte is not None:
                res.append(charger(racine, rev, c, texte))
    return res


def motifs_internes(projet: config.Projet) -> list[re.Pattern]:
    supp = projet.gf("requests", "internal_id_patterns", defaut=[])
    return [re.compile(m) for m in MOTIFS_INTERNES + list(supp)]


def identifiants_cites(texte: str, motifs: list[re.Pattern]) -> set[str]:
    res = set()
    for _, ligne, code in memoire.lignes_hors_code(texte):
        if code:
            continue
        for m in motifs:
            for x in m.finditer(ligne):
                res.add(x.group(0))
    return res


def linter(d: Demande, projet: config.Projet) -> list[str]:
    """Les manquements au contrat, en clair. Vide : la demande est conforme."""
    fautes = []
    f = memoire.analyser(d.chemin, d.texte)
    if f.couche != "demandes":
        fautes.append("en-tête `<!-- socle: couche=demandes zone=… -->` absent ou faux")
    if d.entree is None:
        fautes.append("pas de titre `# D-NNNN — <décision en une phrase>`")
        return fautes
    if len(d.entree.titre) < 10:
        fautes.append("le titre doit énoncer la décision demandée en une phrase")
    nom = Path(d.chemin).name
    if not nom.startswith(d.entree.id):
        fautes.append(f"le nom du fichier doit commencer par {d.entree.id}")

    for k, titre in SECTIONS.items():
        contenu = d.sections.get(k)
        if contenu is None:
            fautes.append(f"section « {titre} » absente")
        elif len(re.sub(r"\s+", " ", contenu)) < SECTION_MIN:
            fautes.append(f"section « {titre} » vide ou trop courte")
        elif TROU.search(contenu):
            # Le gabarit porte les mots que le lint cherche : un trou laissé
            # tel quel passerait pour une section remplie.
            fautes.append(f"section « {titre} » : texte du gabarit laissé tel quel ({TROU.search(contenu).group(0)[:40]}…)")

    norm = {k: outils.cle(v).replace("-", " ") for k, v in d.sections.items()}
    opts = norm.get("options", "")
    for mot, quoi in (("effort", "l'effort"), ("risque", "le risque"), ("reversib", "la réversibilité")):
        if "options" in d.sections and mot not in opts:
            fautes.append(f"« Options » doit dire {quoi} de chaque option")
    cons = norm.get("consequences", "")
    if "consequences" in d.sections:
        if "valid" not in cons:
            fautes.append("« Conséquences » doit dire ce qui se passe si l'humain valide")
        if "refus" not in cons:
            fautes.append("« Conséquences » doit dire ce qui se passe si l'humain refuse")
        if not re.search(r"sans reponse|pas de reponse|ne repond|aucune reponse", cons):
            fautes.append("« Conséquences » doit dire ce qui se passe sans réponse")
    rec = norm.get("recommandation", "")
    if "recommandation" in d.sections and not ("verifie" in rec and "suppose" in rec):
        fautes.append("« Recommandation » doit séparer ce qui est vérifié de ce qui est supposé")

    possibles = d.reponses_possibles()
    if "reponses-possibles" in d.sections:
        if len(possibles) < 2:
            fautes.append("« Réponses possibles » : au moins deux réponses, en liste `- \\`valeur\\` — sens`")
        if RENVOI not in possibles:
            fautes.append(f"« Réponses possibles » doit proposer `{RENVOI}`")

    # Aucun identifiant interne sans description, dans la même demande.
    decrits = descriptions(d.sections.get("elements-cites", ""), motifs_internes(projet))
    cites = identifiants_cites(d.texte, motifs_internes(projet)) - {d.entree.id}
    for ident in sorted(cites):
        if ident not in decrits:
            fautes.append(
                f"identifiant `{ident}` cité sans description : le décrire en clair dans "
                "« Éléments cités » (`- <identifiant> — ce que c'est, en une phrase`)"
            )
    return fautes


def descriptions(bloc: str, motifs: list[re.Pattern]) -> set[str]:
    """Les identifiants décrits : une puce qui les nomme et dit, en au moins
    cinq mots, ce qu'ils sont."""
    res = set()
    for ligne in bloc.splitlines():
        if not re.match(r"^\s*[-*]\s+", ligne):
            continue
        idents = identifiants_cites(ligne, motifs)
        reste = ligne
        for i in idents:
            reste = reste.replace(i, " ")
        mots = re.findall(r"[^\W\d_]{2,}", reste)
        if len(mots) >= MOTS_DESCRIPTION_MIN:
            res |= idents
    return res


def verifier_reponse(d: Demande) -> list[str]:
    if d.reponse is None:
        return []
    fautes = []
    if d.erreur_reponse:
        return [d.erreur_reponse]
    r = d.reponse.get("reponse")
    if not r:
        fautes.append("réponse sans champ `reponse`")
    elif r not in d.reponses_possibles():
        fautes.append(f"réponse `{r}` absente des réponses possibles de la demande")
    attendue = d.reponse.get("empreinte", "")
    if attendue != "sha256:" + outils.sha256(d.texte):
        fautes.append(
            "la demande a changé après la réponse : la réponse portait sur un autre texte "
            "(une demande répondue est gelée ; en écrire une nouvelle qui la remplace)"
        )
    return fautes


def ecrire_reponse(racine: Path, d: Demande, reponse: str, texte: str, par: str, date: str) -> str:
    """Écrit la réponse humaine. Refuse une réponse hors des réponses possibles."""
    if reponse not in d.reponses_possibles():
        raise ValueError(
            f"`{reponse}` n'est pas une réponse possible : {', '.join(d.reponses_possibles())}"
        )
    if d.reponse is not None:
        raise ValueError(f"{d.id} a déjà une réponse ({d.chemin_reponse})")
    cr = chemin_reponse(d.chemin)
    contenu = (
        "# Réponse humaine — écrite par `socle repondre`, jamais par l'agent.\n"
        f"# Elle porte sur le texte exact de {Path(d.chemin).name}, dont l'empreinte suit.\n"
        f"reponse = {_toml_str(reponse)}\n"
        f"texte = {_toml_str(texte)}\n"
        f"par = {_toml_str(par)}\n"
        f"date = {_toml_str(date)}\n"
        f"empreinte = {_toml_str('sha256:' + outils.sha256(d.texte))}\n"
    )
    (racine / cr).write_text(contenu, encoding="utf-8")
    return cr


def _toml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def validations_ajoutees(racine: Path, base: str | None, tete: str | None) -> list[Demande]:
    """Les demandes validées par une réponse AJOUTÉE dans la plage : une vieille
    validation ne couvre pas un assouplissement nouveau."""
    deja = {d.chemin_reponse for d in toutes(racine, base) if d.reponse is not None} if base else set()
    return [
        d for d in toutes(racine, tete)
        if d.validee and d.chemin_reponse not in deja and not verifier_reponse(d)
    ]
