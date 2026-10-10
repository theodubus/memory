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


def lire_mutmut(dossier: Path) -> dict[str, Counter]:
    """`mutmut results` redirigé dans `mutmut-results.txt` : une ligne par
    mutant, `module.chemin.x_nom__mutmut_N: statut`."""
    res: dict[str, Counter] = {}
    correspondance = {"survived": "survivants", "killed": "attrapes", "timeout": "expires",
                      "suspicious": "expires", "no tests": "survivants", "skipped": "inviables"}
    for f in sorted(dossier.rglob("mutmut-results.txt")):
        for ligne in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if ":" not in ligne:
                continue
            nom, statut = ligne.rsplit(":", 1)
            issue = correspondance.get(statut.strip())
            if issue is None:
                continue
            module = nom.strip().split(".x_")[0].replace(".", "/") + ".py"
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
