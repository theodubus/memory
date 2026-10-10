"""Lecture des fonctions de test, paramétrée par l'adaptateur.

Le moteur ne connaît aucun langage : l'adaptateur déclare la forme d'une
fonction (`function`), d'un attribut (`attribute`), ce qui marque un test
(`marker_attribute`, `marker_name`), la forme d'un bloc (`braces` ou
`indent`) et ce qui compte comme assertion. Le moteur fournit seulement les
deux mécanismes génériques : l'extraction d'un bloc et la transitivité des
assertions (un test qui appelle une aide qui affirme, affirme).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Fonction:
    nom: str
    fichier: str
    ligne: int
    attributs: list[str]
    corps: str
    est_test: bool = False
    lignes_corps: list[str] = field(default_factory=list)
    fin: int = 0  # dernière ligne de la fonction, 1 pour la première du fichier


def _sans_litteraux(ligne: str) -> str:
    ligne = re.sub(r'"(?:\\.|[^"\\])*"', '""', ligne)
    ligne = re.sub(r"'(?:\\.|[^'\\])'", "''", ligne)
    return re.sub(r"//.*$", "", ligne)


def _bloc_accolades(lignes: list[str], i: int) -> tuple[list[str], int]:
    """Le corps entre la première accolade et sa fermante, signature exclue."""
    profondeur, debut = 0, None
    for j in range(i, len(lignes)):
        for c in _sans_litteraux(lignes[j]):
            if c == ";" and debut is None:
                return [], j  # déclaration sans corps
            if c == "{":
                profondeur += 1
                if debut is None:
                    debut = j
            elif c == "}":
                profondeur -= 1
                if debut is not None and profondeur == 0:
                    return _couper(lignes[debut : j + 1]), j
    return (_couper(lignes[debut:]) if debut is not None else []), len(lignes) - 1


def _couper(bloc: list[str]) -> list[str]:
    if not bloc:
        return bloc
    premiere = bloc[0].split("{", 1)[1] if "{" in bloc[0] else ""
    return ([premiere] if premiere.strip() else []) + bloc[1:]


def _bloc_indentation(lignes: list[str], i: int) -> tuple[list[str], int]:
    retrait = len(lignes[i]) - len(lignes[i].lstrip())
    res, fin = [], i
    j = i + 1
    # La signature peut continuer sur plusieurs lignes jusqu'au `:`.
    while j < len(lignes) and j - i < 20:
        if re.sub(r"\s+#.*$", "", lignes[j - 1]).rstrip().endswith(":"):
            break
        j += 1
    for k in range(j, len(lignes)):
        l = lignes[k]
        if not l.strip():
            res.append(l)
            continue
        if len(l) - len(l.lstrip()) <= retrait:
            break
        res.append(l)
        fin = k
    while res and not res[-1].strip():
        res.pop()
    return res, fin


def extraire(texte: str, fichier: str, cfg: dict) -> list[Fonction]:
    fn_re = re.compile(cfg["function"])
    attr_re = re.compile(cfg["attribute"]) if cfg.get("attribute") else None
    comm_re = re.compile(cfg["comment"]) if cfg.get("comment") else None
    marque_attr = re.compile(cfg["marker_attribute"]) if cfg.get("marker_attribute") else None
    marque_nom = re.compile(cfg["marker_name"]) if cfg.get("marker_name") else None
    lignes = texte.splitlines()
    res = []
    for i, ligne in enumerate(lignes):
        m = fn_re.match(ligne)
        if not m:
            continue
        nom = m.group(1)
        attributs, j = [], i - 1
        while j >= 0:
            l = lignes[j]
            if attr_re and attr_re.match(l):
                attributs.insert(0, l.strip())
            elif comm_re and comm_re.match(l):
                pass
            else:
                break
            j -= 1
        if cfg.get("block", "braces") == "indent":
            corps, fin = _bloc_indentation(lignes, i)
        else:
            corps, fin = _bloc_accolades(lignes, i)
        f = Fonction(nom=nom, fichier=fichier, ligne=i + 1, attributs=attributs,
                     corps="\n".join(corps), lignes_corps=corps, fin=fin + 1)
        f.est_test = bool(
            (marque_attr and any(marque_attr.search(a) for a in attributs))
            or (marque_nom and marque_nom.search(nom))
        )
        res.append(f)
    return res


def aides_qui_affirment(fonctions: list[Fonction], assertion: re.Pattern) -> set[str]:
    """Les fonctions non-tests qui affirment, directement ou par une autre aide."""
    aides = {f.nom for f in fonctions if not f.est_test and assertion.search(f.corps)}
    for _ in range(5):
        appel = _appel_re(aides)
        if appel is None:
            break
        nouvelles = {
            f.nom for f in fonctions
            if not f.est_test and f.nom not in aides and appel.search(f.corps)
        }
        if not nouvelles:
            break
        aides |= nouvelles
    return aides


def _appel_re(noms: set[str]) -> re.Pattern | None:
    if not noms:
        return None
    return re.compile(r"\b(?:" + "|".join(re.escape(n) for n in sorted(noms)) + r")\s*[(!]")


def affirme(f: Fonction, assertion: re.Pattern, aides: set[str]) -> bool:
    if assertion.search(f.corps) or any(assertion.search(a) for a in f.attributs):
        return True
    appel = _appel_re(aides - {f.nom})
    return bool(appel and appel.search(f.corps))
