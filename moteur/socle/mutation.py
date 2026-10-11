"""Le verdict de mutation : les survivants d'un balayage, module par module,
confrontés au plafond des garde-fous.

Le plafond est un cliquet : il CASSE à la hausse et SIGNALE la baisse. Un
mutant qui expire sur une machine chargée est compté « expiré » plutôt que
« survivant », donc une baisse peut n'être qu'un artefact de charge ; une
hausse, jamais (`chess:.github/mutation-verdict.sh`).

Les lecteurs de résultats sont propres à chaque outil ; l'adaptateur nomme le
sien (`parser`). Un module du plafond sans aucun résultat est un balayage qui
n'a pas tourné : il casse, il ne passe pas pour une couverture parfaite.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from socle import config
from socle.rapport import Rapport


def lire_cargo_mutants(dossier: Path) -> dict[str, Counter]:
    """`missed.txt`, `caught.txt`, `timeout.txt`, `unviable.txt` de chaque
    `mutants.out` sous `dossier` : une ligne `chemin:ligne:col: description`."""
    res: dict[str, Counter] = {}
    vus: set[tuple[str, str]] = set()
    for nom, issue in (("missed.txt", "survivants"), ("caught.txt", "attrapes"),
                       ("timeout.txt", "expires"), ("unviable.txt", "inviables")):
        for f in sorted(dossier.rglob(nom)):
            for ligne in f.read_text(encoding="utf-8", errors="replace").splitlines():
                if not ligne.strip() or (issue, ligne) in vus:
                    continue
                vus.add((issue, ligne))
                module = ligne.split(":", 1)[0]
                res.setdefault(module, Counter())[issue] += 1
    return res


# Ce que mutmut prouve d'un mutant. Un statut absent d'ici ne prouve pas le
# mutant attrapé (`not checked`, un balayage interrompu, un statut nouveau) :
# il compte comme survivant, et casse au lieu de passer.
STATUTS_MUTMUT = {"killed": "attrapes", "caught by type check": "attrapes", "timeout": "expires",
                  "suspicious": "expires", "segfault": "expires", "skipped": "inviables"}
NOM_MUTMUT = re.compile(r"^(?P<module>[\w.]+?)\.x[_ǁ].*__mutmut_\d+$")


def lire_mutmut(dossier: Path) -> dict[str, Counter]:
    """La sortie de `mutmut results --all true` redirigée dans
    `mutmut-results.txt` (sans `--all`, les mutants attrapés manquent, et un
    module tout attrapé passerait pour jamais balayé) : une ligne par mutant,
    `paquet.module.x_fonction__mutmut_N: statut`, ou `xǁClasseǁméthode` pour
    une méthode. Le nom ne dit pas où vit le fichier : le mutant compte pour
    chaque chemin possible (module, `__init__.py` d'un paquet, sous `src/`),
    et le verdict ne lit que celui du plafond."""
    res: dict[str, Counter] = {}
    for f in sorted(dossier.rglob("mutmut-results.txt")):
        for ligne in f.read_text(encoding="utf-8", errors="replace").splitlines():
            nom, _, statut = ligne.rpartition(":")
            m = NOM_MUTMUT.match(nom.strip())
            if not m:
                continue
            issue = STATUTS_MUTMUT.get(statut.strip(), "survivants")
            chemin = m["module"].replace(".", "/")
            for module in (f"{chemin}.py", f"{chemin}/__init__.py", f"src/{chemin}.py", f"src/{chemin}/__init__.py"):
                res.setdefault(module, Counter())[issue] += 1
    return res


def _suffixes(chemin: str) -> list[str]:
    """Un chemin et tous ses suffixes (`/a/b/src/x.js` → `src/x.js`, `x.js`…) :
    un outil qui écrit des chemins absolus, ou relatifs à un autre dossier,
    compte pour chacun, et le verdict ne lit que celui du plafond."""
    morceaux = [m for m in chemin.replace("\\", "/").split("/") if m and m != "."]
    return ["/".join(morceaux[i:]) for i in range(len(morceaux))]


def _compter(res: dict[str, Counter], chemin: str, issue: str):
    for module in _suffixes(chemin):
        res.setdefault(module, Counter())[issue] += 1


def _json(f: Path):
    import json

    try:
        return json.loads(f.read_text(encoding="utf-8", errors="replace"))
    except ValueError:
        return None


# Stryker (JavaScript, TypeScript) : le rapport `mutation.json` du schéma
# commun des rapports de mutation. Un statut absent d'ici compte survivant.
STATUTS_STRYKER = {"Killed": "attrapes", "Timeout": "expires", "CompileError": "inviables",
                   "RuntimeError": "inviables", "Ignored": "inviables"}


def lire_stryker(dossier: Path) -> dict[str, Counter]:
    res: dict[str, Counter] = {}
    for f in sorted(dossier.rglob("mutation.json")):
        if "node_modules" in f.parts or not isinstance(d := _json(f), dict):
            continue
        for chemin, contenu in (d.get("files") or {}).items():
            for m in contenu.get("mutants", []):
                _compter(res, chemin, STATUTS_STRYKER.get(m.get("status", ""), "survivants"))
    return res


# gremlins (Go) : `gremlins unleash --output=gremlins.json`.
STATUTS_GREMLINS = {"KILLED": "attrapes", "TIMED OUT": "expires", "NOT VIABLE": "inviables", "SKIPPED": "inviables"}


def lire_gremlins(dossier: Path) -> dict[str, Counter]:
    res: dict[str, Counter] = {}
    for f in sorted(dossier.rglob("gremlins.json")):
        if not isinstance(d := _json(f), dict):
            continue
        for fichier in d.get("files") or []:
            for m in fichier.get("mutations") or []:
                _compter(res, fichier.get("file_name", ""), STATUTS_GREMLINS.get(m.get("status", ""), "survivants"))
    return res


# PIT (Java) : `target/pit-reports/mutations.xml`. Le fichier se déduit du
# paquet de la classe mutée et du nom de son fichier source.
STATUTS_PIT = {"KILLED": "attrapes", "TIMED_OUT": "expires", "MEMORY_ERROR": "expires",
               "RUN_ERROR": "inviables", "NON_VIABLE": "inviables"}


def lire_pit(dossier: Path) -> dict[str, Counter]:
    import xml.etree.ElementTree as ET

    res: dict[str, Counter] = {}
    for f in sorted(dossier.rglob("mutations.xml")):
        try:
            racine = ET.parse(f).getroot()
        except ET.ParseError:
            continue
        for m in racine.iter("mutation"):
            classe, source = m.findtext("mutatedClass", ""), m.findtext("sourceFile", "")
            paquet = "/".join(classe.split(".")[:-1])
            chemin = f"src/main/java/{paquet}/{source}" if paquet else f"src/main/java/{source}"
            _compter(res, chemin, STATUTS_PIT.get(m.get("status", ""), "survivants"))
    return res


def lire_mutant(dossier: Path) -> dict[str, Counter]:
    """mutant (Ruby) : la session la plus récente sous `.mutant/results/`
    (leurs noms, des UUID v7, se rangent dans le temps). Une mutation est
    attrapée si l'un de ses critères l'a tuée (un test a échoué, le
    processus s'est arrêté) ; expirée si seul le délai l'a fait."""
    res: dict[str, Counter] = {}
    sessions = sorted(dossier.rglob(".mutant/results/*.json"), key=lambda f: f.name)
    if not sessions or not isinstance(d := _json(sessions[-1]), dict):
        return res
    for sujet in d.get("subject_results") or []:
        for r in sujet.get("coverage_results") or []:
            c = r.get("criteria_result") or {}
            issue = ("attrapes" if c.get("test_result") or c.get("process_abort")
                     else "expires" if c.get("timeout") else "survivants")
            _compter(res, sujet.get("source_path", ""), issue)
    return res


# Infection (PHP) : le journal JSON (`logs.json` de `infection.json5`).
ISSUES_INFECTION = {"killed": "attrapes", "timeouted": "expires", "errored": "inviables",
                    "syntaxErrors": "inviables", "ignored": "inviables", "escaped": "survivants",
                    "uncovered": "survivants"}


def lire_infection(dossier: Path) -> dict[str, Counter]:
    res: dict[str, Counter] = {}
    for f in sorted(dossier.rglob("infection.json")):
        if "vendor" in f.parts or not isinstance(d := _json(f), dict) or "stats" not in d:
            continue
        for cle, issue in ISSUES_INFECTION.items():
            for m in d.get(cle) or []:
                _compter(res, (m.get("mutator") or {}).get("originalFilePath", ""), issue)
    return res


LECTEURS = {"cargo-mutants": lire_cargo_mutants, "mutmut": lire_mutmut, "stryker": lire_stryker,
            "gremlins": lire_gremlins, "pit": lire_pit, "mutant": lire_mutant, "infection": lire_infection}


def verdict(projet: config.Projet, dossier: Path) -> Rapport:
    r = Rapport()
    ident = "mutation.verdict"
    r.execute(ident)
    cap = projet.adaptateur.get("capabilities", {}).get("mutation", {})
    if "command" not in cap:
        r.indisponible(ident, f"capacité absente : {cap.get('absent', 'non déclarée')}")
        return r
    lecteur = LECTEURS.get(cap.get("parser", ""))
    if lecteur is None:
        r.erreur(ident, f"lecteur de résultats inconnu : « {cap.get('parser')} » (connus : {', '.join(LECTEURS)})")
        return r
    if not dossier.is_dir():
        r.erreur(ident, f"dossier de résultats introuvable : {dossier}")
        return r
    plafonds = projet.gf("mutation", "caps", defaut={}) or {}
    if not plafonds:
        r.erreur(ident, "plafond vide : rien à comparer — un vert ici serait silencieux")
        return r
    resultats = lecteur(dossier)
    total = 0
    for module, p in plafonds.items():
        c = resultats.get(module)
        if not c:
            r.erreur(ident, f"{module} : aucun résultat — le balayage n'a pas tourné sur ce module")
            continue
        n = c["survivants"]
        total += n
        if n > p.get("max", 0):
            r.erreur(ident, f"{module} : {n} survivant(s) pour un plafond de {p.get('max', 0)} — du code a cessé "
                     "d'être couvert. Corriger les tests, ou demander à relever le plafond (raison écrite).")
        elif n < p.get("max", 0):
            r.avertir(ident, f"{module} : {n} survivant(s) sous le plafond {p.get('max', 0)} — resserrer le plafond")
    return r
