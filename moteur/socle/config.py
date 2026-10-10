"""Le projet tel que le socle le voit : sa racine et ses quatre fichiers.

- `.socle/moteur.lock`     — version et empreinte du moteur (installeur seul) ;
- `.socle/politique.toml`  — politique d'autonomie (humain seul) ;
- `.socle/adaptateur.toml` — capacités du langage (validé par l'humain) ;
- `.socle/garde-fous.toml` — seuils et couverture des contrôles (cliquet :
  durcir est libre, assouplir exige une demande validée).

Les clés sont en anglais, les commentaires et messages en français.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from socle import outils

DOSSIER = ".socle"
LOCK = ".socle/moteur.lock"
POLITIQUE = ".socle/politique.toml"
GARDE_FOUS = ".socle/garde-fous.toml"
ADAPTATEUR = ".socle/adaptateur.toml"
LANCEUR = ".socle/socle"
GIT_HOOKS = ".socle/git-hooks"
TRACE = ".socle/trace/hooks.log"  # ancien emplacement, et hors dépôt git
COMPTEUR_STOP = ".socle/trace/stop-echecs"
MEMOIRE = "memoire"
ARCHIVES = "memoire/archives"
INSTRUCTIONS = "AGENTS.md"

MODE_AMONT = "amont"   # le dépôt qui fabrique le moteur : il le modifie
MODE_PROJET = "projet"  # un projet qui l'utilise : le moteur y est immuable


def chemin_trace(racine: Path) -> Path:
    """La trace des hooks vit dans le répertoire git commun
    (`.git/socle/hooks.log`), que partagent tous les worktrees du dépôt : les
    hooks de l'agent y écrivent depuis le dépôt principal, et le hook git d'un
    commit fait dans un autre worktree y lit la même trace (B-0015). Hors
    dépôt git, l'ancien emplacement."""
    import subprocess

    r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                       cwd=racine, capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return Path(r.stdout.strip()) / "socle" / "hooks.log"
    return racine / TRACE


def lire_trace(racine: Path) -> list[str]:
    """Les lignes de la trace, l'ancien emplacement d'abord s'il en reste."""
    lignes = []
    for p in dict.fromkeys([racine / TRACE, chemin_trace(racine)]):
        if p.is_file():
            lignes += [l for l in p.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    return lignes


def lire_toml(texte: str | None) -> dict:
    if not texte:
        return {}
    return tomllib.loads(texte)


def charger_toml(racine: Path, chemin: str, rev: str | None = None) -> dict:
    return lire_toml(outils.lire_a(racine, rev, chemin))


@dataclass
class Projet:
    racine: Path
    lock: dict = field(default_factory=dict)
    politique: dict = field(default_factory=dict)
    garde_fous: dict = field(default_factory=dict)
    adaptateur: dict = field(default_factory=dict)
    erreurs_config: list[tuple[str, str]] = field(default_factory=list)

    @classmethod
    def charger(cls, racine: Path | None = None, rev: str | None = None) -> "Projet":
        racine = outils.trouver_racine(racine)
        p = cls(racine=racine)
        for attr, chemin in (
            ("lock", LOCK),
            ("politique", POLITIQUE),
            ("garde_fous", GARDE_FOUS),
            ("adaptateur", ADAPTATEUR),
        ):
            try:
                setattr(p, attr, charger_toml(racine, chemin, rev))
            except tomllib.TOMLDecodeError as e:
                p.erreurs_config.append((chemin, f"TOML illisible : {e}"))
        return p

    @property
    def installe(self) -> bool:
        return bool(self.lock)

    @property
    def mode(self) -> str:
        return self.lock.get("mode", MODE_PROJET)

    @property
    def dossier_moteur(self) -> str:
        """Le répertoire qui contient le paquet `socle`."""
        return self.lock.get("engine_dir", ".socle/moteur")

    # --- garde-fous -----------------------------------------------------

    def gf(self, *chemin, defaut=None):
        noeud = self.garde_fous
        for c in chemin:
            if not isinstance(noeud, dict) or c not in noeud:
                return defaut
            noeud = noeud[c]
        return noeud

    def pol(self, *chemin, defaut=None):
        noeud = self.politique
        for c in chemin:
            if not isinstance(noeud, dict) or c not in noeud:
                return defaut
            noeud = noeud[c]
        return noeud

    def chemins_code(self) -> list[str]:
        """Ce qui compte comme du code : l'adaptateur le déclare, les
        garde-fous peuvent l'étendre."""
        res = list(self.adaptateur.get("sources", []))
        res += list(self.gf("memory", "code", defaut=[]))
        return res

    def exclusions_docs(self) -> list[str]:
        """Ce qui n'est pas de la documentation du projet : les archives
        (gardées telles quelles) et le moteur (ses gabarits et son format)."""
        return [ARCHIVES + "/**", self.dossier_moteur.rstrip("/") + "/**"] + list(
            self.gf("references", "exclude", defaut=[])
        )

    def chemins_proteges(self) -> list[str]:
        res = list(self.pol("protected", "paths", defaut=[]))
        if self.mode == MODE_AMONT:
            # Dans le dépôt amont, le moteur EST la source : le protéger
            # empêcherait de le fabriquer.
            res = [m for m in res if not m.startswith(".socle/moteur/")]
        return res

    def maximum_tentatives(self) -> int:
        return int(self.pol("max_attempts", defaut=3))
