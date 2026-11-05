"""Le banc de la revue adversariale d'un lot (B-0124, ADR-0042).

Ce que la revue trouve, sur des défauts connus que les contrôles du socle
ne voient pas : un lot qui passe ses tests et ses contrôles, mais dont le
code contredit la décision qu'il prétend appliquer. Le relecteur est un
agent réel, en mode non interactif, qui ne reçoit que le dossier de
`socle review` ; un lot sain mesure ses faux constats.

    python3 bench/review.py --passages 3 --budget 2
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "engine"))

from socle import config, review as revue  # noqa: E402

ADR = """<!-- socle: couche=decisions zone=publique -->
# ADR-0001 — La remise sur quantité

> statut : acceptée · date : 2026-11-02

## Décision

- À partir de 10 unités, le total reçoit 5 % de remise.
- Le total remisé s'arrondit au centime inférieur.
- Une quantité négative ou nulle lève `ValueError`.
- Un montant s'affiche en euros, toujours avec deux chiffres de centimes :
  `1,05 €`.
"""

SUJET = """<!-- socle: couche=backlog zone=publique -->
# B-0001 — La remise sur quantité

> statut : {statut} · origine : ADR-0001

Appliquer ADR-0001 à `total` et à `formater`.

## Fait quand

- [{x}] la remise s'applique à partir de 10 unités
- [{x}] le total remisé s'arrondit au centime inférieur
- [{x}] une quantité négative ou nulle est refusée
- [{x}] un montant s'affiche avec deux chiffres de centimes
"""

BASE = '''def total(prix_unitaire, quantite):
    """Le total d'une commande, en centimes."""
    return prix_unitaire * quantite


def formater(centimes):
    """Un montant en centimes, affiché en euros."""
    return f"{centimes / 100:.2f} €"
'''

# Quatre défauts que ni les tests du lot ni les contrôles du socle ne voient :
# chacun contredit ADR-0001, à une ligne connue.
FAUTIF = '''def total(prix_unitaire, quantite):
    """Le total d'une commande, en centimes, remise comprise (ADR-0001)."""
    if quantite < 0:
        raise ValueError("quantité négative")
    brut = prix_unitaire * quantite
    if quantite > 10:
        return round(brut * 0.95)
    return brut


def formater(centimes):
    """Un montant en centimes, affiché en euros (ADR-0001)."""
    return f"{centimes // 100},{centimes % 100} €"
'''

SAIN = '''def total(prix_unitaire, quantite):
    """Le total d'une commande, en centimes, remise comprise (ADR-0001)."""
    if quantite <= 0:
        raise ValueError("quantité négative ou nulle")
    brut = prix_unitaire * quantite
    if quantite >= 10:
        return brut * 95 // 100
    return brut


def formater(centimes):
    """Un montant en centimes, affiché en euros (ADR-0001)."""
    return f"{centimes // 100},{centimes % 100:02d} €"
'''

TESTS_FAUTIF = '''import unittest

from prix import formater, total


class TestPrix(unittest.TestCase):
    def test_une_grosse_commande_est_remisee(self):
        self.assertEqual(total(100, 20), 1900)

    def test_une_petite_commande_ne_l_est_pas(self):
        self.assertEqual(total(100, 1), 100)

    def test_un_montant_s_affiche_en_euros(self):
        self.assertEqual(formater(1999), "19,99 €")
'''

TESTS_SAIN = TESTS_FAUTIF + '''
    def test_la_remise_commence_a_dix_unites(self):
        self.assertEqual(total(100, 10), 950)

    def test_le_total_remise_s_arrondit_au_centime_inferieur(self):
        self.assertEqual(total(33, 10), 313)

    def test_une_quantite_nulle_est_refusee(self):
        with self.assertRaises(ValueError):
            total(100, 0)

    def test_deux_chiffres_de_centimes(self):
        self.assertEqual(formater(105), "1,05 €")
'''


@dataclass
class Defaut:
    id: str
    ligne: int  # dans prix.py
    indices: tuple[str, ...]  # ce qu'un constat qui le trouve en dit, en minuscules


DEFAUTS = [
    Defaut("seuil", 6, ("> 10", ">= 10", "≥ 10", "10 unités", "exactement 10", "quantite == 10", "(100, 10)")),
    Defaut("arrondi", 7, ("round", "inférieur", "floor", "arrondi")),
    Defaut("nulle", 3, ("nulle", "<= 0", "quantite == 0", "(100, 0)", ", 0)")),
    Defaut("centimes", 13, ("02d", "deux chiffres", "1,5 €", "105", "zéro de tête", "leading zero", "1,05")),
]


def git(cwd: Path, *args: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "banc", "GIT_AUTHOR_EMAIL": "banc@x", "GIT_COMMITTER_NAME": "banc",
           "GIT_COMMITTER_EMAIL": "banc@x", "GIT_CONFIG_NOSYSTEM": "1", "HOME": str(cwd)}
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env).stdout


def preparer(dossier: Path, fautif: bool) -> Path:
    """Un projet jetable : la décision et le sujet sur `main`, puis le lot,
    fautif ou sain, sur `travail`, qui ferme le sujet. Ses tests passent."""
    p = dossier / ("fautif" if fautif else "sain")
    (p / "memory/decisions").mkdir(parents=True)
    (p / "memory/backlog").mkdir(parents=True)
    (p / "tests").mkdir()
    git(p, "init", "-q", "-b", "main")
    (p / "prix.py").write_text(BASE)
    (p / "tests/__init__.py").write_text("")
    (p / "memory/decisions/ADR-0001-la-remise-sur-quantite.md").write_text(ADR)
    (p / "memory/backlog/B-0001-la-remise-sur-quantite.md").write_text(SUJET.format(statut="ouvert", x=" "))
    git(p, "add", "-A")
    git(p, "commit", "-qm", "la base")
    git(p, "switch", "-q", "-c", "travail")
    (p / "prix.py").write_text(FAUTIF if fautif else SAIN)
    (p / "tests/test_prix.py").write_text(TESTS_FAUTIF if fautif else TESTS_SAIN)
    (p / "memory/backlog/B-0001-la-remise-sur-quantite.md").write_text(SUJET.format(statut="fait", x="x"))
    git(p, "add", "-A")
    git(p, "commit", "-qm", "la remise sur quantité (B-0001)")
    return p


LIMITE = re.compile(r"limit|usage|rate", re.I)
CONSTAT = re.compile(r"^\s*(?:\*\*)?(\d+)[.)]", re.M)


def constats(sortie: str) -> list[str]:
    """Les constats numérotés de la revue, un texte chacun."""
    debuts = [m.start() for m in CONSTAT.finditer(sortie)]
    return [sortie[a:b].strip() for a, b in zip(debuts, debuts[1:] + [len(sortie)])]


def juger(sortie: str, defauts: list[Defaut] = DEFAUTS) -> dict:
    """Les défauts que la revue trouve : un constat qui en dit l'indice, ou
    qui cite `prix.py` à sa ligne. Les constats qui n'en trouvent
    aucun se comptent à part : sur un lot sain, ce sont des faux constats."""
    trouves, autres = set(), []
    for c in constats(sortie):
        texte = c.lower()
        lignes = {int(n) for n in re.findall(r"prix\.py[^\d\n]{0,12}(\d+)", texte)}
        touches = {d.id for d in defauts
                   if any(i.lower() in texte for i in d.indices) or d.ligne in lignes}
        trouves |= touches
        if not touches:
            autres.append(c)
    return {"trouves": sorted(trouves), "constats": len(constats(sortie)), "autres": autres}


def relire(dossier_revue: str, budget: float) -> dict:
    """Le relecteur : un agent réel, dans un dossier vide, qui ne reçoit que
    le dossier de la revue."""
    # Un agent neuf : rien de la session qui lance le banc (B-0057).
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "SOCLE_", "GIT_"))}
    with tempfile.TemporaryDirectory(prefix="banc-revue-relecteur-") as vide:
        r = subprocess.run(["claude", "-p", "--output-format", "json", "--max-budget-usd", str(budget)],
                           cwd=vide, input=dossier_revue, capture_output=True, text=True, timeout=900, env=env)
    try:
        donnees = json.loads(r.stdout)
    except ValueError:
        donnees = {"result": r.stdout[-4000:], "is_error": True}
    return {"sortie": donnees.get("result") or "", "cout": donnees.get("total_cost_usd"),
            "modeles": sorted((donnees.get("modelUsage") or {}).keys()), "erreur": bool(donnees.get("is_error"))}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--passages", type=int, default=3)
    p.add_argument("--budget", type=float, default=2.0)
    args = p.parse_args(argv)
    resultats = []
    with tempfile.TemporaryDirectory(prefix="banc-revue-") as d:
        for fautif in (True, False):
            projet = preparer(Path(d), fautif)
            dossier_revue = revue.dossier(config.Projet(racine=projet), "main")
            for n in range(args.passages):
                r = relire(dossier_revue, args.budget)
                if r["erreur"] and LIMITE.search(r["sortie"]):
                    # Une limite d'usage n'est pas une mesure : le banc s'arrête,
                    # sans écrire de rapport (le 2 novembre, six passages vides).
                    print(f"limite d'usage atteinte : {r['sortie'][:200]}", file=sys.stderr)
                    return 3
                jugement = juger(r["sortie"])
                if not fautif:
                    # Le lot sain n'a pas de défaut à trouver : ses constats
                    # se lisent, un juge par mots-clés les prendrait pour des
                    # défauts trouvés (le 5 novembre, « 4/4 » sur le lot sain).
                    jugement["trouves"] = None
                r.update({"lot": "fautif" if fautif else "sain", "passage": n + 1, **jugement})
                resultats.append(r)
                trouves = "-" if r["trouves"] is None else len(r["trouves"])
                print(f"{r['lot']} {n + 1} : {trouves}/{len(DEFAUTS)} défauts, "
                      f"{r['constats']} constats, {r['cout']} $", flush=True)
    sortie = RACINE / "bench/reports" / f"{date.today().isoformat()}-revue.json"
    sortie.write_text(json.dumps(resultats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
