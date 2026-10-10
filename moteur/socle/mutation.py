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


LECTEURS = {"cargo-mutants": lire_cargo_mutants, "mutmut": lire_mutmut}


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
