"""Une commande shell, découpée en commandes simples, pour que les hooks
jugent ce qu'elle fait et non le texte qu'elle cite.

Un heredoc, une chaîne entre guillemets ou un message de commit qui
nomment une commande dangereuse ne la lancent pas ; un lanceur entre
guillemets, un `git -C .`, des drapeaux groupés (`-fu`) ou un `cd` la
lancent bien. Le découpage suit les guillemets, les séparateurs (`;`, `&&`,
`||`, `|`, fin de ligne), les redirections, les `cd`, les préfixes (`env`,
`sudo`, `nohup`…) et les `bash -c`.

Les variables affectées dans la commande (`F=x`, `export F=x`) et les
dossiers où elle passe (`cd`, `pushd`, `popd`) se suivent ; `developper`
rend un mot comme le shell le développerait, de son `~` et de ses
variables, et marque ce qu'il ne sait pas développer ; `accolades` et
`se_croisent` disent ce qu'une accolade et un motif du shell nomment
(B-0171).

Heuristique, comme tout ce qui lit du shell sans l'exécuter : les
substitutions (`$(…)`, accents graves), les alias et les fonctions ne sont
pas suivis. Le hook n'est qu'un étage ; la CI juge ce qui est commité.
"""

from __future__ import annotations

import posixpath
import re
import shlex
from dataclasses import dataclass, field

# Les préfixes qui lancent la commande qui les suit.
PREFIXES = {"sudo", "command", "exec", "nohup", "time", "builtin", "nice", "stdbuf", "timeout", "xargs", "env"}
# Les options de ces préfixes qui prennent une valeur.
VALEURS = {"sudo": ("-u", "-g", "-C"), "nice": ("-n",), "env": ("-u", "-C"), "timeout": ("-s", "-k"),
           "xargs": ("-I", "-L", "-P", "-n", "-s", "-E", "-d")}
HEREDOC = re.compile(r"(?<!<)<<(-?)\s*(['\"]?)([\w.-]+)\2")
AFFECTATION = re.compile(r"([A-Za-z_]\w*)=(.*)", re.S)
# Ce qui affecte une variable du shell courant par ses arguments `NOM=valeur`.
DECLARATIONS = {"export", "declare", "typeset", "local", "readonly"}
# Les options de `read` qui prennent une valeur.
VALEURS_READ = ("-p", "-d", "-n", "-N", "-t", "-u", "-a")
# Une part d'un mot que le hook ne sait pas développer : une variable
# inconnue, une substitution de commande.
INCONNU = "\0"


@dataclass
class Commande:
    argv: list[str]
    # Les fichiers que ses redirections écrivent (`>`, `>>`, `>|`, `&>`).
    redirige: list[str] = field(default_factory=list)
    # Le dossier où elle s'exécute, relatif au dossier de départ (`""` : le
    # même), ou absolu après un `cd` absolu.
    dossier: str = ""
    # Ce qui la précède et que `_sans_prefixes` retire : affectations de
    # variables (`GIT_DIR=…`), `env`, `sudo`… et leurs options.
    prefixe: list[str] = field(default_factory=list)
    # Les variables affectées avant elle dans le même texte, dans l'ordre :
    # (nom, valeur telle qu'écrite), la valeur `None` quand elle vient
    # d'ailleurs (`read`, `for`).
    affectations: list[tuple[str, str | None]] = field(default_factory=list)

    @property
    def programme(self) -> str:
        return self.argv[0].rsplit("/", 1)[-1] if self.argv else ""

    def chemin(self, nom: str) -> str:
        """Un chemin de la commande, rapporté au dossier de départ."""
        if nom.startswith(("/", "~")) or not self.dossier:
            return nom
        return posixpath.normpath(posixpath.join(self.dossier, nom))


def sans_heredocs(texte: str) -> str:
    """Le texte sans le corps de ses heredocs : un document, pas une commande."""
    res, attendus = [], []
    for ligne in texte.split("\n"):
        if attendus:
            fin, tabs = attendus[0]
            if (ligne.lstrip("\t") if tabs else ligne) == fin:
                attendus.pop(0)
            continue
        res.append(ligne)
        attendus += [(m.group(3), m.group(1) == "-") for m in HEREDOC.finditer(ligne)]
    return "\n".join(res)


def jetons(texte: str) -> list[str]:
    """Les mots et les opérateurs de la commande, guillemets retirés."""
    texte = sans_heredocs(texte.replace("\\\n", " "))
    lex = shlex.shlex(texte, posix=True, punctuation_chars=";&|()<>\n")
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    try:
        return list(lex)
    except ValueError:  # guillemets non fermés : on juge chaque mot tel quel
        return texte.split()


def _operateur(jeton: str) -> bool:
    return bool(jeton) and all(c in ";&|()<>\n" for c in jeton)


def _sans_prefixes(argv: list[str]) -> list[str]:
    """La commande lancée derrière ses affectations et ses préfixes."""
    while argv:
        if re.fullmatch(r"[A-Za-z_]\w*=.*", argv[0], re.S):
            argv = argv[1:]
        elif argv[0].rsplit("/", 1)[-1] in PREFIXES:
            nom = argv[0].rsplit("/", 1)[-1]
            argv = argv[1:]
            # Leurs options, et la valeur de celles qui en prennent une.
            while argv and (argv[0].startswith("-") or (nom == "env" and "=" in argv[0])
                            or (nom == "timeout" and re.fullmatch(r"[\d.]+[smhd]?", argv[0]))):
                argv = argv[2:] if argv[0] in VALEURS.get(nom, ()) else argv[1:]
        else:
            break
    # `python3 -m module …` : le module est le programme.
    if argv and re.fullmatch(r"python[\d.]*", argv[0].rsplit("/", 1)[-1]) and argv[1:2] == ["-m"] and len(argv) > 2:
        argv = argv[2:]
    return argv


def _affectations(argv: list[str]) -> list[tuple[str, str | None]]:
    """Les variables qu'une commande simple affecte dans le shell courant :
    `export F=x`, `unset F`, et, d'une valeur que le hook ignore, `read F`,
    `for F in …`, `printf -v F`."""
    nom, args = (argv[0], argv[1:]) if argv else ("", [])
    if nom in DECLARATIONS:
        return [(m.group(1), m.group(2)) for a in args if (m := AFFECTATION.fullmatch(a))]
    if nom == "unset":
        return [(a, "") for a in args if not a.startswith("-")]
    if nom in ("for", "select") and args and re.fullmatch(r"[A-Za-z_]\w*", args[0]):
        return [(args[0], None)]
    if nom == "printf" and "-v" in args[:-1]:
        return [(args[args.index("-v") + 1], None)]
    if nom == "read":
        res, i = [], 0
        while i < len(args):
            if args[i] in VALEURS_READ:
                if args[i] == "-a" and i + 1 < len(args):
                    res.append((args[i + 1], None))
                i += 2
                continue
            if not args[i].startswith("-"):
                res.append((args[i], None))
            i += 1
        return res or [("REPLY", None)]
    return []


def analyser(texte: str, dossier: str = "",
             affectations: list[tuple[str, str | None]] | None = None) -> list[Commande]:
    """Les commandes simples d'un texte de shell, dans l'ordre. Chacune porte
    le dossier où elle s'exécute (`cd`, `cd -`, `pushd`, `popd` suivis) et
    les variables affectées avant elle (B-0171)."""
    res: list[Commande] = []
    mots: list[str] = []
    redir: list[str] = []
    jets = jetons(texte)
    vues: list[tuple[str, str | None]] = list(affectations or [])
    # La pile de `pushd`, sous le dossier courant, et le dossier d'avant le
    # dernier `cd` (`cd -`).
    pile: list[str] = []
    precedent = dossier

    def aller(cible: str, depuis: Commande) -> str:
        return cible if cible.startswith(("/", "~")) else depuis.chemin(cible)

    def clore():
        nonlocal mots, redir, dossier, pile, precedent
        argv = _sans_prefixes(mots)
        if not argv and mots and all(AFFECTATION.fullmatch(m) for m in mots):
            # Une affectation seule vaut pour la suite ; devant une commande,
            # elle ne vaut que pour celle-ci.
            vues.extend((m.group(1), m.group(2)) for m in map(AFFECTATION.fullmatch, mots))
        if argv or redir:
            c = Commande(argv, redir, dossier, mots[:len(mots) - len(argv)], list(vues))
            nom = c.programme
            if nom == "cd":
                cible = argv[1] if len(argv) > 1 else "~"
                dossier, precedent = (precedent, dossier) if cible == "-" else (aller(cible, c), dossier)
            elif nom in ("pushd", "popd"):
                options, args = options_et_arguments(argv[1:])
                if args and re.fullmatch(r"[+-]\d+", args[0]):
                    # Une rotation de la pile : le hook ne la suit pas.
                    pile, dossier = [], f"$(dirs {args[0]})"
                elif nom == "pushd" and args and "-n" in options:
                    pile.append(aller(args[0], c))
                elif nom == "pushd" and args:
                    pile.append(dossier)
                    dossier = aller(args[0], c)
                elif nom == "pushd" and pile:
                    pile[-1], dossier = dossier, pile[-1]
                elif nom == "popd" and pile and "-n" in options:
                    pile.pop()
                elif nom == "popd" and pile:
                    dossier = pile.pop()
            elif nom in ("bash", "sh", "zsh", "dash") and "-c" in argv[1:-1]:
                res.extend(analyser(argv[argv.index("-c") + 1], dossier, vues))
            elif nom == "eval":
                res.extend(analyser(" ".join(argv[1:]), dossier, vues))
            vues.extend(_affectations(argv))
            res.append(c)
        mots, redir = [], []

    i = 0
    while i < len(jets):
        j = jets[i]
        if _operateur(j):
            if ">" in j:
                if mots and mots[-1].isdigit():
                    mots.pop()  # le descripteur de `2>`
                cible = jets[i + 1] if i + 1 < len(jets) else ""
                if not (j.endswith("&") and (cible.isdigit() or cible == "-")) and not _operateur(cible):
                    redir.append(cible)
                i += 2 if not _operateur(cible) else 1
                continue
            if "<" in j:
                i += 2
                continue
            clore()
            i += 1
            continue
        mots.append(j)
        i += 1
    clore()
    return res


def accolades(mot: str, plafond: int = 256) -> list[str]:
    """Les mots qu'une accolade du shell rend : `a{b,c}` donne `ab` et `ac`,
    `x{1..3}` donne `x1`, `x2`, `x3` ; une accolade sans virgule ni suite,
    ou celle de `${…}`, reste telle quelle. Au-delà du plafond, le mot reste
    entier."""
    i = 0
    while i < len(mot):
        if mot[i] != "{":
            i += 1
            continue
        profondeur, j, virgules = 0, i, []
        while j < len(mot):
            if mot[j] == "{":
                profondeur += 1
            elif mot[j] == "}":
                profondeur -= 1
                if profondeur == 0:
                    break
            elif mot[j] == "," and profondeur == 1:
                virgules.append(j)
            j += 1
        if j >= len(mot):
            return [mot]
        if i > 0 and mot[i - 1] == "$":
            i = j + 1  # `${…}` : une variable, pas une accolade
            continue
        dedans = mot[i + 1:j]
        suite = re.fullmatch(r"(-?\d+)\.\.(-?\d+)|([A-Za-z])\.\.([A-Za-z])", dedans)
        if virgules:
            bornes = [i] + virgules + [j]
            parts = [mot[a + 1:b] for a, b in zip(bornes, bornes[1:])]
        elif suite:
            a, b = (int(suite.group(1)), int(suite.group(2))) if suite.group(1) else (
                ord(suite.group(3)), ord(suite.group(4)))
            pas = 1 if b >= a else -1
            if abs(b - a) >= plafond:
                return [mot]
            parts = [str(x) if suite.group(1) else chr(x) for x in range(a, b + pas, pas)]
        else:
            i += 1
            continue
        res = [x for p in parts for x in accolades(mot[:i] + p + mot[j + 1:], plafond)]
        return res if len(res) <= plafond else [mot]
    return [mot]


def developper(mot: str, variables) -> tuple[str, list[str]]:
    """Le mot comme le shell le développerait de son `~` et de ses variables
    (`variables` : nom → valeur, la valeur pouvant porter `INCONNU`), et les
    parts qu'il ne sait pas développer, chacune remplacée par `INCONNU` :
    une variable que `variables` ne connaît pas, `${…}` avec un opérateur,
    une substitution `$(…)` ou entre accents graves, un paramètre spécial
    (`$1`, `$$`). Un `$` en fin de mot est celui d'une substitution que le
    découpage a coupée (`$(mktemp)` donne les jetons `$`, `(`…)."""
    res: list[str] = []
    inconnus: list[str] = []
    if mot.startswith("~"):
        tete, barre, reste = mot.partition("/")
        if tete in ("~", "~+", "~-"):
            valeur = variables.get({"~": "HOME", "~+": "PWD", "~-": "OLDPWD"}[tete])
        else:
            # `~nom` : le dossier de cet utilisateur, ou le mot tel quel.
            valeur = posixpath.expanduser(tete)
        if valeur is None:
            res.append(INCONNU)
            inconnus.append(tete)
        else:
            res.append(valeur)
        mot = barre + reste
    i = 0
    while i < len(mot):
        ch = mot[i]
        if ch == "`":
            j = mot.find("`", i + 1)
            j = len(mot) if j < 0 else j + 1
        elif ch != "$":
            res.append(ch)
            i += 1
            continue
        elif mot[i + 1:i + 2] in ("", "("):
            j, profondeur = i + 1, 0
            while j < len(mot):
                profondeur += {"(": 1, ")": -1}.get(mot[j], 0)
                j += 1
                if profondeur == 0:
                    break
        elif mot[i + 1] == "{":
            j = mot.find("}", i)
            j = len(mot) if j < 0 else j + 1
        elif m := re.match(r"[A-Za-z_]\w*|[\d@*#?$!-]", mot[i + 1:]):
            j = i + 1 + m.end()
        else:
            res.append(ch)  # un `$` que rien de développable ne suit
            i += 1
            continue
        nom = mot[i:j].lstrip("$").removeprefix("{").removesuffix("}")
        valeur = variables.get(nom) if re.fullmatch(r"[A-Za-z_]\w*", nom) and ch == "$" else None
        if valeur is None or INCONNU in valeur:
            inconnus.append(mot[i:j])
        res.append(INCONNU if valeur is None else valeur)
        i = j
    return "".join(res), inconnus


def variables_de(c: Commande, environnement) -> dict[str, str]:
    """Les variables que le shell connaît quand la commande s'exécute :
    l'environnement, puis ce que le même texte affecte avant elle, chaque
    valeur développée à son tour ; `INCONNU`, une valeur que le hook ignore."""
    variables = dict(environnement)
    for nom, brute in c.affectations:
        variables[nom] = INCONNU if brute is None else developper(brute, variables)[0]
    return variables


# Les éléments d'un motif : l'ensemble des caractères qu'il rend
# (`(nié, caractères)`), s'il est étoilé (zéro fois ou plus) et s'il est un
# joker (`*`, `?`, `[…]`), qui ne rend pas le `.` qui ouvre un nom.
_SAUF_BARRE = (True, frozenset("/"))
_TOUT = (True, frozenset())


def _elements_shell(motif: str) -> list[tuple[tuple[bool, frozenset], bool, bool]]:
    res, i = [], 0
    while i < len(motif):
        ch = motif[i]
        j = motif.find("]", i + 2) if ch == "[" else -1
        if ch in "*?":
            res.append((_SAUF_BARRE, ch == "*", True))
        elif j > 0:
            dedans = motif[i + 1:j]
            nie = dedans[:1] in ("!", "^")
            dedans = dedans[1:] if nie else dedans
            chars: set[str] = set()
            k = 0
            while k < len(dedans):
                if k + 2 < len(dedans) and dedans[k + 1] == "-":
                    chars.update(chr(x) for x in range(ord(dedans[k]), ord(dedans[k + 2]) + 1))
                    k += 3
                else:
                    chars.add(dedans[k])
                    k += 1
            res.append(((True, frozenset(chars | {"/"})) if nie else (False, frozenset(chars - {"/"})), False, True))
            i = j
        else:
            res.append(((False, frozenset(ch)), False, False))
        i += 1
    return res


def _elements_chemin(motif: str) -> list[list[tuple[tuple[bool, frozenset], bool, bool]]]:
    """Les variantes d'un motif de chemin à la gitignore (`utils.correspond`),
    `**/` (zéro dossier ou plus) déplié en ses deux formes."""
    variantes: list[list] = [[]]
    i = 0
    while i < len(motif):
        if motif.startswith("**/", i):
            dossiers = [(_TOUT, True, True), ((False, frozenset("/")), False, False)]
            variantes = [v + x for v in variantes for x in ([], dossiers)]
            i += 3
            continue
        if motif.startswith("**", i):
            el, i = (_TOUT, True, True), i + 2
        elif motif[i] in "*?":
            el, i = (_SAUF_BARRE, motif[i] == "*", True), i + 1
        else:
            el, i = ((False, frozenset(motif[i])), False, False), i + 1
        variantes = [v + [el] for v in variantes]
    return variantes


def _commun(a: tuple[bool, frozenset], b: tuple[bool, frozenset]) -> tuple[bool, frozenset]:
    (na, ca), (nb, cb) = a, b
    if na and nb:
        return True, ca | cb
    if not na and not nb:
        return False, ca & cb
    return (False, cb - ca) if na else (False, ca - cb)


def _rend(ensemble: tuple[bool, frozenset], ch: str) -> bool:
    return (ch not in ensemble[1]) if ensemble[0] else (ch in ensemble[1])


def se_croisent(motif_shell: str, motif_chemin: str, dessous: bool = False) -> bool:
    """Un même chemin peut-il répondre au motif du shell (`*`, `?`, `[…]`,
    qui ne traversent pas `/` ni ne rendent le `.` qui ouvre un nom) et au
    motif de chemin (`utils.correspond`) ? Avec `dessous`, un chemin sous ce
    que nomme le motif du shell compte aussi : `rm -rf .so*` vise
    `.socle/policy.toml`."""
    shell = _elements_shell(motif_shell)
    formes = [shell] + ([shell + [((False, frozenset("/")), False, False), (_TOUT, True, False)]] if dessous else [])
    return any(_se_croisent(a, b) for a in formes for b in _elements_chemin(motif_chemin))


def _se_croisent(a: list, b: list) -> bool:
    """Un même chemin peut-il répondre aux deux suites d'éléments ? Un
    parcours du produit des deux : (position dans `a`, dans `b`, au début
    d'un nom), chaque pas rendant un caractère que les deux admettent ; sans
    récursion, qu'un long chemin épuiserait."""
    vus: set = set()
    pile = [(0, 0, True)]
    while pile:
        etat = pile.pop()
        if etat in vus:
            continue
        vus.add(etat)
        i, j, debut = etat
        if i == len(a) and j == len(b):
            return True
        if i < len(a) and a[i][1]:
            pile.append((i + 1, j, debut))
        if j < len(b) and b[j][1]:
            pile.append((i, j + 1, debut))
        if i == len(a) or j == len(b):
            continue
        ensemble = _commun(a[i][0], b[j][0])
        i2, j2 = (i if a[i][1] else i + 1), (j if b[j][1] else j + 1)
        # Le `.` qui ouvre un nom ne répond qu'à un `.` écrit.
        interdits = {"/", "."} if debut and a[i][2] else {"/"}
        if _rend(ensemble, "/"):
            pile.append((i2, j2, True))
        if ensemble[0] or ensemble[1] - interdits:
            pile.append((i2, j2, False))
    return False


def options_et_arguments(argv: list[str]) -> tuple[list[str], list[str]]:
    """Les options (`-x`, `--y`) et les arguments d'une commande ; après
    `--`, tout est argument."""
    options, args = [], []
    fin = False
    for a in argv:
        if not fin and a == "--":
            fin = True
        elif not fin and a.startswith("-") and a != "-":
            options.append(a)
        else:
            args.append(a)
    return options, args


def drapeau(options: list[str], court: str = "", long: tuple[str, ...] = ()) -> bool:
    """Une option présente, seule (`-f`), groupée (`-fu`) ou longue (`--force`)."""
    for o in options:
        if o.startswith("--"):
            if any(o == l or o.startswith(l + "=") for l in long):
                return True
        elif court and court in o[1:]:
            return True
    return False


def git_sous_commande(argv: list[str]) -> tuple[str, list[str]]:
    """La sous-commande de `git` et ses arguments, derrière ses options
    globales (`-C <dossier>`, `-c <clé=valeur>`, `--git-dir=…`)."""
    i = 1
    while i < len(argv) and argv[i].startswith("-"):
        i += 2 if argv[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path") else 1
    return (argv[i], argv[i + 1:]) if i < len(argv) else ("", [])

