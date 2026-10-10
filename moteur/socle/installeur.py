"""L'installeur : pose tout le dispositif en une commande, se relance pour
les mises à jour.

Ce qu'il copie et ce qu'il référence décide de tout :
- le moteur est remplacé en bloc et son empreinte enregistrée — aucun merge ;
- la mémoire, la politique, l'adaptateur et les garde-fous appartiennent au
  projet : posés s'ils manquent, jamais écrasés ;
- les hooks, la CI et CODEOWNERS sont régénérés ; leur diff passe par la
  revue humaine (fichiers protégés).

Mode adoption (projet existant) : les budgets sont fixés au niveau actuel,
et les contrôles qui échouent sur l'existant passent en avertissement
(`[adoption] warn_only`), d'où on ne les retire que pour durcir.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import stat
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

from socle import VERSION, config, empreinte, outils
from socle.modeles import DOSSIER as MODELES, gabarit

ADAPTATEURS = Path(__file__).resolve().parent / "adaptateurs"
DEBUT_SOCLE = "<!-- socle:debut — section posée par l'installeur, régénérée à chaque mise à jour -->"
FIN_SOCLE = "<!-- socle:fin -->"


def _ecrire(chemin: Path, texte: str, executable: bool = False):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")
    if executable:
        chemin.chmod(chemin.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def charger_adaptateur(nom: str) -> tuple[str, str]:
    """(texte, nom) d'un adaptateur maintenu ou d'un fichier."""
    p = Path(nom)
    if p.suffix == ".toml" and p.is_file():
        return p.read_text(encoding="utf-8"), p.stem
    q = ADAPTATEURS / f"{nom}.toml"
    if not q.is_file():
        connus = ", ".join(sorted(x.stem for x in ADAPTATEURS.glob("*.toml")))
        raise SystemExit(f"adaptateur inconnu : {nom} (maintenus : {connus} ; sinon un chemin vers un .toml)")
    return q.read_text(encoding="utf-8"), nom


def detecter_langage(cible: Path) -> str | None:
    if (cible / "Cargo.toml").is_file():
        return "rust"
    if any((cible / f).is_file() for f in ("pyproject.toml", "setup.py", "setup.cfg")):
        return "python"
    return None


def installer(cible: Path, adaptateur: str, proprietaire: str = "", adoption: bool = False,
              mode: str = config.MODE_PROJET, source: Path | None = None) -> int:
    if not outils.est_depot(cible):
        print(f"refus : {cible} n'est pas un dépôt git", file=sys.stderr)
        return 2
    source = source or Path(__file__).resolve().parent.parent
    texte_adaptateur, nom_adaptateur = charger_adaptateur(adaptateur)
    try:
        tomllib.loads(texte_adaptateur)
    except tomllib.TOMLDecodeError as e:
        print(f"refus : adaptateur « {nom_adaptateur} » illisible : {e}", file=sys.stderr)
        return 2
    journal = []

    # 1. Le moteur, remplacé en bloc.
    if mode == config.MODE_AMONT:
        dossier_moteur = str(source.relative_to(cible)) if source.is_relative_to(cible) else "moteur"
    else:
        dossier_moteur = ".socle/moteur"
        dest = cible / dossier_moteur / "socle"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(source / "socle", dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        journal.append(f"moteur {VERSION} copié dans {dossier_moteur}/socle")
    _ecrire(cible / config.LANCEUR, gabarit("lanceur.py"), executable=True)

    # 2. Le verrou et son empreinte. En mode amont, le moteur est la source :
    # une empreinte figée y changerait à chaque modification du moteur, et
    # ferait de chacune un changement de fichier protégé.
    if mode == config.MODE_AMONT:
        _ecrire(cible / config.LOCK, (
            "# Verrou du moteur — écrit par l'installeur, jamais à la main.\n"
            "# Mode amont : ce dépôt fabrique le moteur, dont l'empreinte n'est pas figée ici.\n"
            f'mode = "{mode}"\n'
            f'engine_dir = "{dossier_moteur}"\n'
        ))
        journal.append(f"verrou en mode amont : le moteur est la source, sous {dossier_moteur}/socle")
    else:
        calculee, n = empreinte.calculer(cible, dossier_moteur)
        _ecrire(cible / config.LOCK, (
            "# Verrou du moteur — écrit par l'installeur, jamais à la main.\n"
            "# La CI recalcule l'empreinte ; un moteur altéré dans le projet fait échouer `moteur.empreinte`.\n"
            f'version = "{VERSION}"\n'
            f'mode = "{mode}"\n'
            f'engine_dir = "{dossier_moteur}"\n'
            f'fingerprint = "{calculee}"\n'
            f"files = {n}\n"
        ))
        journal.append(f"verrou : {empreinte.courte(calculee)} sur {n} fichiers")

    # 3. Les fichiers du projet : posés s'ils manquent, jamais écrasés.
    for nom, contenu in (
        (config.POLITIQUE, gabarit("politique.toml")),
        (config.ADAPTATEUR, texte_adaptateur),
        (config.GARDE_FOUS, gabarit("garde-fous.toml")),
    ):
        p = cible / nom
        if p.is_file():
            journal.append(f"{nom} existe : conservé (comparer au gabarit à la main si besoin)")
        else:
            _ecrire(p, contenu)
            journal.append(f"{nom} posé")

    # 4. La mémoire initiale.
    jour = date.today().isoformat()
    for nom in ("canonique.md", "actif.md", "backlog.md"):
        p = cible / config.MEMOIRE / nom
        if not p.is_file():
            _ecrire(p, gabarit(f"memoire/{nom}"))
    for sous in ("decisions", "demandes"):
        d = cible / config.MEMOIRE / sous
        d.mkdir(parents=True, exist_ok=True)
        if not any(d.iterdir()):
            _ecrire(d / ".gitkeep", "")
    jdir = cible / config.MEMOIRE / "journal"
    if not jdir.is_dir() or not any(jdir.glob("*.md")):
        from socle import memoire

        ident = memoire.Memoire.charger(cible).prochain_id("J", date=jour)
        _ecrire(jdir / f"{jour[:7]}.md", gabarit("memoire/journal.md")
                .replace("@@MOIS@@", jour[:7]).replace("@@ID@@", ident).replace("@@VERSION@@", VERSION)
                .replace("@@ADAPTATEUR@@", nom_adaptateur)
                .replace("@@ADOPTION@@", ", en mode adoption" if adoption else ""))
        journal.append(f"mémoire initiale posée, journal ouvert par {ident}")

    # 5. Les instructions : AGENTS.md fait foi, CLAUDE.md l'importe.
    journal += _instructions(cible, dossier_moteur)

    # 6. Hooks de l'agent, hooks git, CI, CODEOWNERS, .gitignore.
    journal += _settings(cible)
    for h in (MODELES / "git-hooks").iterdir():
        _ecrire(cible / config.GIT_HOOKS / h.name, h.read_text(encoding="utf-8"), executable=True)
    if outils.git(cible, "config", "--get", "core.hooksPath", check=False).strip() in ("", config.GIT_HOOKS):
        outils.git(cible, "config", "core.hooksPath", config.GIT_HOOKS)
        journal.append("hooks git branchés (core.hooksPath)")
    else:
        journal.append("!! core.hooksPath pointe ailleurs : hooks git NON branchés")
    setup = tomllib.loads(texte_adaptateur).get("ci_setup", "")
    _ecrire(cible / ".github/workflows/socle.yml",
            gabarit("socle.yml").replace("@@ETAPES_ADAPTATEUR@@\n", setup.strip("\n") + "\n" if setup.strip() else ""))
    journal += _codeowners(cible, proprietaire)
    journal += _gitignore(cible)

    # 7. La trace : l'installation se voit dans `Socle-Hooks` d'une session
    # en cours (SessionStart a tiré avant que le hook n'existe).
    from socle.hooks import tracer

    tracer(cible, "Install", "", VERSION)

    # 8. Adoption : budgets au niveau actuel, contrôles en échec en avertissement.
    if adoption:
        journal += _adopter(cible)

    print(f"socle {VERSION} installé dans {cible}")
    for l in journal:
        print(f"  - {l}")
    print("\nAudit :")
    return _audit(cible)


def _instructions(cible: Path, dossier_moteur: str) -> list[str]:
    res = []
    agents = cible / config.INSTRUCTIONS
    claude = cible / "CLAUDE.md"
    section = (gabarit("AGENTS.md").replace("@@VERSION@@", VERSION).replace("@@MOTEUR@@", dossier_moteur))
    socle = section.split("@@SECTION_PROJET@@", 1)[1].strip("\n")
    bloc = f"{DEBUT_SOCLE}\n\n{socle}\n\n{FIN_SOCLE}\n"
    if not agents.is_file() and claude.is_file() and claude.read_text(encoding="utf-8").strip() != "@AGENTS.md":
        dependants = _qui_nomme(cible, "CLAUDE.md")
        if dependants:
            # Le renommer casserait le projet : ses propres fichiers le lisent
            # (essai sur chess, J-2026-10-10-G). La section du socle va dans
            # CLAUDE.md, et le renommage devient une décision humaine.
            _section_dans(claude, bloc)
            res.append(f"!! CLAUDE.md gardé : {len(dependants)} fichier(s) du projet le nomment "
                       f"({', '.join(dependants[:5])}{' …' if len(dependants) > 5 else ''}) ; "
                       "le renommer en AGENTS.md est une décision humaine — section du socle ajoutée à CLAUDE.md")
            return res
    if not agents.is_file():
        if claude.is_file() and claude.read_text(encoding="utf-8").strip() != "@AGENTS.md":
            # Le CLAUDE.md existant devient AGENTS.md, historique compris.
            if not outils.git_reussit(cible, "mv", "CLAUDE.md", config.INSTRUCTIONS):
                shutil.move(str(claude), str(agents))
            res.append("CLAUDE.md existant renommé en AGENTS.md (il fait foi désormais)")
            texte = agents.read_text(encoding="utf-8").rstrip("\n") + "\n\n"
        else:
            texte = f"# {cible.name}\n\nÀ compléter : ce que fait le projet, sa structure, ses commandes.\n\n"
        agents.write_text(texte + bloc, encoding="utf-8")
        res.append("AGENTS.md posé")
    else:
        res.append(_section_dans(agents, bloc))
    claude.write_text("@AGENTS.md\n", encoding="utf-8")
    return res


def _section_dans(fichier: Path, bloc: str) -> str:
    """Pose ou régénère la section du socle entre ses marqueurs."""
    texte = fichier.read_text(encoding="utf-8")
    if DEBUT_SOCLE in texte and FIN_SOCLE in texte:
        avant, reste = texte.split(DEBUT_SOCLE, 1)
        apres = reste.split(FIN_SOCLE, 1)[1]
        fichier.write_text(avant + bloc.rstrip("\n") + apres, encoding="utf-8")
        return f"section du socle de {fichier.name} régénérée"
    fichier.write_text(texte.rstrip("\n") + "\n\n" + bloc, encoding="utf-8")
    return f"section du socle ajoutée à {fichier.name}"


def _qui_nomme(cible: Path, nom: str) -> list[str]:
    """Les fichiers du projet, hors documentation et hors socle, qui citent `nom`."""
    res = []
    for c in outils.fichiers_courants(cible):
        if c.endswith(".md") or c.startswith((".socle/", ".git/")):
            continue
        p = cible / c
        if outils.est_texte(p) and nom in p.read_text(encoding="utf-8", errors="replace"):
            res.append(c)
    return res


def _settings(cible: Path) -> list[str]:
    p = cible / ".claude/settings.json"
    modele = json.loads(gabarit("settings.json"))
    if p.is_file():
        try:
            conf = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return ["!! .claude/settings.json illisible : hooks NON déclarés"]
    else:
        conf = {"$schema": modele["$schema"]}
    hooks = conf.setdefault("hooks", {})
    for evt, blocs in modele["hooks"].items():
        existants = hooks.setdefault(evt, [])
        # Les blocs du socle sont remplacés, ceux du projet gardés.
        existants[:] = [b for b in existants
                        if not any(".socle/socle hook" in h.get("command", "") for h in b.get("hooks", []))]
        existants.extend(blocs)
    _ecrire(p, json.dumps(conf, ensure_ascii=False, indent=2) + "\n")
    return ["hooks de Claude Code déclarés dans .claude/settings.json"]


def _codeowners(cible: Path, proprietaire: str) -> list[str]:
    p = cible / ".github/CODEOWNERS"
    if not proprietaire:
        return ["!! aucun propriétaire (--owner) : CODEOWNERS non posé — la politique n'est protégée que par la CI"]
    lignes = gabarit("CODEOWNERS").replace("@@OWNER@@", proprietaire).splitlines()
    existant = p.read_text(encoding="utf-8").splitlines() if p.is_file() else []
    ajout = [l for l in lignes if l not in existant]
    _ecrire(p, "\n".join(existant + ajout).strip("\n") + "\n")
    return [f"CODEOWNERS : {proprietaire} sur la politique, les hooks et la CI"]


def _gitignore(cible: Path) -> list[str]:
    p = cible / ".gitignore"
    existant = p.read_text(encoding="utf-8") if p.is_file() else ""
    voulues = ["# Trace locale des hooks du socle (voir AGENTS.md)", "/.socle/trace/", "__pycache__/"]
    manquantes = [l for l in voulues if l not in existant.splitlines()]
    if manquantes:
        p.write_text(existant.rstrip("\n") + ("\n\n" if existant.strip() else "") + "\n".join(manquantes) + "\n",
                     encoding="utf-8")
    return []


def _adopter(cible: Path) -> list[str]:
    """Plafonds au niveau actuel ; les contrôles en échec passent en
    avertissement, liste d'où l'on ne retire que pour durcir."""
    from socle import contexte

    gf = cible / config.GARDE_FOUS
    texte = gf.read_text(encoding="utf-8")
    res = []
    claude = cible / "CLAUDE.md"
    if claude.is_file() and claude.read_text(encoding="utf-8").strip() != "@AGENTS.md" and '"CLAUDE.md"' not in texte:
        # Gardé comme source le temps du renommage : il a son budget, au niveau actuel.
        taille = int(math.ceil(len(claude.read_bytes()) / 1000.0) * 1000)
        texte = texte.replace("[budgets]\n", f'[budgets]\n"CLAUDE.md" = {{ max_bytes = {taille} }}\n', 1)
        res.append(f"budget de CLAUDE.md, gardé comme source : {taille} octets (il ne pourra que baisser)")
    gf.write_text(texte, encoding="utf-8")
    projet = config.Projet.charger(cible)
    for motif, b in (projet.gf("budgets", defaut={}) or {}).items():
        tailles = [len((cible / c).read_bytes()) for c in outils.filtrer(outils.fichiers_courants(cible), [motif])]
        if tailles and max(tailles) > b.get("max_bytes", 0):
            nouveau = int(math.ceil(max(tailles) / 1000.0) * 1000)
            texte = re.sub(rf'^("{re.escape(motif)}"\s*=\s*\{{\s*max_bytes\s*=\s*)\d+', rf"\g<1>{nouveau}", texte, flags=re.M)
            res.append(f"budget de {motif} fixé au niveau actuel : {nouveau} octets (il ne pourra que baisser)")
    gf.write_text(texte, encoding="utf-8")
    projet = config.Projet.charger(cible)
    rapport = contexte.executer(contexte.Contexte(projet, etage="ci", base=None))
    en_echec = [c for c in rapport.controles_en_echec() if c != "config"]
    if en_echec:
        texte = gf.read_text(encoding="utf-8").rstrip("\n")
        texte += ("\n\n[adoption]\n# Contrôles en échec sur l'existant, passés en avertissement. En retirer un\n"
                  "# durcit (libre) ; en ajouter un assouplit (demande validée).\n"
                  f"warn_only = {json.dumps(en_echec)}\n")
        gf.write_text(texte, encoding="utf-8")
        res.append(f"adoption : {len(en_echec)} contrôle(s) en avertissement : {', '.join(en_echec)}")
    return res


def _audit(cible: Path) -> int:
    r = subprocess.run([sys.executable, str(cible / config.LANCEUR), "check", "--stage", "ci"], cwd=cible)
    return r.returncode
