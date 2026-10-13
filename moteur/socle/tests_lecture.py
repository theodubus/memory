"""Lecture des fonctions de test, paramétrée par l'adaptateur.

Le moteur ne connaît aucun langage : l'adaptateur déclare la forme d'une
fonction (`function`, dont le premier groupe trouvé est le nom), d'un
attribut (`attribute`), ce qui marque un test (`marker_attribute`,
`marker_name`, ou `marker_line` sur la ligne qui le définit, pour
`test("…", …)` ou `it "…" do`), la forme d'un bloc (`braces`, `indent` ou
`end`), ses littéraux (`strings`) et ses commentaires de fin de ligne
(`line_comment`), ce qui ouvre un module de tests dans un fichier de code
(`test_module`, le `#[cfg(test)]` de Rust), et ce qui compte comme
assertion. Le moteur fournit
seulement les mécanismes génériques : l'extraction d'un bloc et la
transitivité des assertions (un test qui appelle une aide qui affirme,
affirme).
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
    entete: str = ""  # la ligne qui la définit
    debut: int = 0  # première ligne, attributs et commentaires au-dessus compris


# Les littéraux et le commentaire de fin de ligne, par défaut ceux de Rust :
# une accolade dans une chaîne ne compte pas.
LITTERAUX = r'"(?:\\.|[^"\\])*"' + r"|'(?:\\.|[^'\\])'"
COMMENTAIRE = r"//.*$"


def _sans_litteraux(ligne: str, litteraux: str = LITTERAUX, commentaire: str = COMMENTAIRE) -> str:
    ligne = re.sub(litteraux, '""', ligne)
    return re.sub(commentaire, "", ligne) if commentaire else ligne


def _bloc_accolades(lignes: list[str], i: int, litteraux: str = LITTERAUX,
                    commentaire: str = COMMENTAIRE) -> tuple[list[str], int]:
    """Le corps entre la première accolade et sa fermante, signature exclue."""
    profondeur, debut = 0, None
    for j in range(i, len(lignes)):
        for c in _sans_litteraux(lignes[j], litteraux, commentaire):
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


# Un bloc fermé par `end` (Ruby, Lua, Elixir…) : ce qui l'ouvre, en tête de
# ligne ou en `do` de fin de ligne ; ce qui le ferme.
OUVRE_FIN = re.compile(r"^\s*(?:def|class|module|if|unless|while|until|case|begin|for|function)\b"
                       r"|\bdo\s*(?:\|[^|]*\|)?\s*$")
FERME_FIN = re.compile(r"\bend\b")


def _bloc_fin(lignes: list[str], i: int, litteraux: str = LITTERAUX,
              commentaire: str = COMMENTAIRE) -> tuple[list[str], int]:
    """Le corps d'un bloc ouvert sur la ligne `i` et fermé par son `end`."""
    profondeur = 0
    for j in range(i, len(lignes)):
        ligne = _sans_litteraux(lignes[j], litteraux, commentaire)
        profondeur += len(OUVRE_FIN.findall(ligne)) - len(FERME_FIN.findall(ligne))
        if profondeur <= 0:
            return lignes[i + 1 : j], j
    return lignes[i + 1 :], len(lignes) - 1


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
    marque_ligne = re.compile(cfg["marker_line"]) if cfg.get("marker_line") else None
    litteraux, commentaire = cfg.get("strings", LITTERAUX), cfg.get("line_comment", COMMENTAIRE)
    lignes = texte.splitlines()
    res = []
    for i, ligne in enumerate(lignes):
        m = fn_re.match(ligne)
        if not m:
            continue
        nom = next((g for g in m.groups() if g), None) if m.groups() else m.group(0)
        if not nom:
            continue
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
        bloc = cfg.get("block", "braces")
        if bloc == "indent":
            corps, fin = _bloc_indentation(lignes, i)
        elif bloc == "end":
            corps, fin = _bloc_fin(lignes, i, litteraux, commentaire)
        else:
            corps, fin = _bloc_accolades(lignes, i, litteraux, commentaire)
        f = Fonction(nom=nom, fichier=fichier, ligne=i + 1, attributs=attributs,
                     corps="\n".join(corps), lignes_corps=corps, fin=fin + 1, entete=ligne, debut=j + 2)
        f.est_test = bool(
            (marque_attr and any(marque_attr.search(a) for a in attributs))
            or (marque_nom and marque_nom.search(nom))
            or (marque_ligne and marque_ligne.search(ligne))
        )
        res.append(f)
    return res





def sans_commentaires(texte: str, cfg: dict) -> str:
    """Le texte sans ses commentaires : les lignes de commentaire
    (`comment`), les commentaires de bloc (`block_comment` : `/* … */`, une
    docstring de Python) et de fin de ligne (`line_comment`, s'il est
    déclaré), les littéraux gardés. Un mot cité en commentaire n'appelle rien
    ni n'affirme rien (relevé de la passe de recul, D)."""
    litteraux = cfg.get("strings", LITTERAUX)
    if cfg.get("block_comment"):
        texte = re.sub(f"(?:{cfg['block_comment']})|({litteraux})", lambda m: m.group(1) or "", texte)
    comm_re = re.compile(cfg["comment"]) if cfg.get("comment") else None
    fin = re.compile(f"({litteraux})|(?:{cfg['line_comment']})") if cfg.get("line_comment") else None
    res = []
    for ligne in texte.splitlines():
        if comm_re and comm_re.match(ligne):
            continue
        res.append(fin.sub(lambda m: m.group(1) or "", ligne) if fin else ligne)
    return "\n".join(res)

def enonces(lignes: list[str], debut: re.Pattern, cfg: dict) -> dict[str, list[str]]:
    """Les énoncés qui commencent sur une ligne de `debut` (une assertion), en
    entier : prolongés tant qu'une parenthèse ou un crochet reste ouvert, et
    normalisés hors des littéraux (blancs retirés, virgule finale ôtée) ;
    pour chacun, sa première ligne, autant de fois qu'il vient. Une assertion
    reformatée garde son énoncé ; une valeur écrite sur une ligne de
    continuation en fait partie."""
    # Les commentaires restent : le commentaire par défaut, `//`, est une
    # division en Python, et l'ôter cacherait une valeur.
    litteraux = cfg.get("strings", LITTERAUX)
    blancs = re.compile(f"({litteraux})|\\s+")
    res: dict[str, list[str]] = {}
    for i, ligne in enumerate(lignes):
        if not debut.search(ligne):
            continue
        morceaux, profondeur = [], 0
        for suite in lignes[i : i + 50]:
            nu = re.sub(litteraux, '""', suite)
            morceaux.append(suite)
            profondeur += nu.count("(") + nu.count("[") - nu.count(")") - nu.count("]")
            if profondeur <= 0:
                break
        texte = blancs.sub(lambda m: m.group(1) or "", " ".join(morceaux))
        res.setdefault(re.sub(r",(?=[)\]])", "", texte), []).append(ligne.strip())
    return res

def zones_de_test(texte: str, fichier: str, cfg: dict) -> list[tuple[int, int]]:
    """Les lignes de test d'un fichier, comptées depuis zéro, fin exclue :
    chaque fonction de test, attributs et commentaires au-dessus compris, et
    chaque module de tests (`test_module`) en entier, ses aides comprises."""
    zones = [(f.debut - 1, f.fin) for f in extraire(texte, fichier, cfg) if f.est_test]
    if not cfg.get("test_module"):
        return zones
    ouvre = re.compile(cfg["test_module"])
    litteraux, commentaire = cfg.get("strings", LITTERAUX), cfg.get("line_comment", COMMENTAIRE)
    lignes = texte.splitlines()
    for i, ligne in enumerate(lignes):
        if ouvre.search(ligne):
            bloc = cfg.get("block", "braces")
            if bloc == "indent":
                fin = _bloc_indentation(lignes, i)[1]
            elif bloc == "end":
                fin = _bloc_fin(lignes, i, litteraux, commentaire)[1]
            else:
                fin = _bloc_accolades(lignes, i, litteraux, commentaire)[1]
            zones.append((i, fin + 1))
    return zones


def aides_qui_affirment(fonctions: list[Fonction], assertion: re.Pattern, cfg: dict | None = None) -> set[str]:
    """Les fonctions non-tests qui affirment, directement ou par une autre
    aide ; hors de leurs commentaires quand la configuration est donnée."""
    def corps(f):
        return sans_commentaires(f.corps, cfg) if cfg else f.corps

    aides = {f.nom for f in fonctions if not f.est_test and assertion.search(corps(f))}
    for _ in range(5):
        appel = _appel_re(aides)
        if appel is None:
            break
        nouvelles = {
            f.nom for f in fonctions
            if not f.est_test and f.nom not in aides and appel.search(corps(f))
        }
        if not nouvelles:
            break
        aides |= nouvelles
    return aides


def _appel_re(noms: set[str]) -> re.Pattern | None:
    if not noms:
        return None
    return re.compile(r"\b(?:" + "|".join(re.escape(n) for n in sorted(noms)) + r")\s*[(!]")


def affirme(f: Fonction, assertion: re.Pattern, aides: set[str], cfg: dict | None = None) -> bool:
    """Le test affirme, directement ou par une aide qui affirme ; hors de ses
    commentaires quand la configuration du langage est donnée."""
    corps = sans_commentaires(f.corps, cfg) if cfg else f.corps
    if assertion.search(corps) or any(assertion.search(a) for a in f.attributs):
        return True
    appel = _appel_re(aides - {f.nom})
    return bool(appel and appel.search(corps))
