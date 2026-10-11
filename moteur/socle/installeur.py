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

from socle import VERSION, config, empreinte, langue, outils
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


# Le fichier qui dit le langage d'un dépôt, et l'adaptateur maintenu qui va
# avec ; le premier trouvé l'emporte.
MARQUEURS_LANGAGE = (
    (("Cargo.toml",), "rust"),
    (("pyproject.toml", "setup.py", "setup.cfg"), "python"),
    (("go.mod",), "go"),
    (("pom.xml",), "java"),
    (("Gemfile",), "ruby"),
    (("composer.json",), "php"),
    (("package.json",), "javascript"),
)


def detecter_langage(cible: Path) -> str | None:
    for fichiers, langage in MARQUEURS_LANGAGE:
        if any((cible / f).is_file() for f in fichiers):
            return langage
    return None


def detecter_adaptateur(cible: Path) -> str | None:
    """L'adaptateur maintenu qui convient au dépôt, déduit de ses fichiers ;
    `None` si rien ne le dit : la question revient alors à l'humain."""
    langage = detecter_langage(cible)
    fichiers = outils.fichiers_courants(cible)
    if langage is None and any(f.endswith(".py") for f in fichiers):
        langage = "python"
    if langage != "python":
        return langage
    indices = [f for f in fichiers if f.endswith("conftest.py") or f in ("pytest.ini", "tox.ini")]
    for f in [f for f in fichiers if f in ("pyproject.toml", "setup.cfg") or f.startswith("requirements")]:
        if "pytest" in (cible / f).read_text(encoding="utf-8", errors="replace"):
            indices.append(f)
    return "python-pytest" if indices else "python"


def politique_privee(texte: str, mode: str, relecture: str | None, demandes: bool) -> str:
    """La politique du gabarit, avec la mémoire privée choisie à
    l'installation au lieu de son exemple en commentaire."""
    bloc = f'[private]\nmode = "{mode}"\n'
    if relecture:
        bloc += f'review = "{relecture}"\n'
    bloc += f"requests = {'true' if demandes else 'false'}\n"
    debut = texte.index("# [private]\n")
    fin = texte.find("\n\n", debut)
    fin = len(texte) if fin == -1 else fin + 1
    return texte[:debut] + bloc + texte[fin:]


def garde_fous_initiaux(cible: Path, texte_adaptateur: str) -> str:
    """Les garde-fous du gabarit, avec chaque module qui porte déjà du code
    posé « à mesurer » au cliquet de mutation : une installation sur un
    projet existant finit verte, et le premier balayage pose les plafonds
    mesurés (B-0034, P1)."""
    texte = gabarit("garde-fous.toml")
    cap = tomllib.loads(texte_adaptateur).get("capabilities", {}).get("mutation", {})
    if "command" not in cap:
        return texte
    porte = re.compile(cap.get("has_code", r"."))
    fichiers = [f for f in outils.fichiers_courants(cible) if not f.startswith(config.DOSSIER + "/")]
    modules = [m for m in outils.filtrer(fichiers, cap.get("modules", []), cap.get("modules_exclude", []))
               if porte.search(outils.lire_a(cible, None, m) or "")]
    if not modules:
        return texte
    entrees = "".join(f"{json.dumps(m, ensure_ascii=False)} = {{ pending = true }}\n" for m in sorted(modules))
    exemple = '# "src/lib.rs" = { max = 0 }\n'
    return texte.replace(exemple, exemple + entrees, 1)


def politique_langue(texte: str, lg: str) -> str:
    """La politique du gabarit, avec la langue de la mémoire choisie à
    l'installation au lieu de son exemple en commentaire (B-0031)."""
    return texte.replace('# [memory]\n# language = "fr"\n', f'[memory]\nlanguage = "{lg}"\n', 1)


def diff_politique(cible: Path) -> list[str]:
    """Ce qui sépare la politique du projet de celle du gabarit de cette
    version : affiché à la mise à jour, jamais appliqué. La politique est à
    l'humain."""
    import difflib

    p = cible / config.chemins(cible).politique
    if not p.is_file():
        return []
    projet, gab = p.read_text(encoding="utf-8").splitlines(), gabarit("politique.toml").splitlines()
    return list(difflib.unified_diff(projet, gab, "politique du projet", "gabarit de cette version", lineterm=""))


def installer(cible: Path, adaptateur: str, proprietaire: str = "", adoption: bool = False,
              mode: str = config.MODE_PROJET, source: Path | None = None, prive: str | None = None,
              relecture: str | None = None, demandes_privees: bool = False, filtre: str = "git-crypt",
              langue_memoire: str | None = None) -> int:
    from socle import migrations

    if not outils.est_depot(cible):
        print(f"refus : {cible} n'est pas un dépôt git", file=sys.stderr)
        return 2
    source = source or Path(__file__).resolve().parent.parent
    if adaptateur == "auto":
        detecte = detecter_adaptateur(cible)
        if detecte is None:
            connus = "|".join(sorted(x.stem for x in ADAPTATEURS.glob("*.toml")))
            print("refus : langage non détecté (aucun de Cargo.toml, pyproject.toml, go.mod, pom.xml, Gemfile, "
                  "composer.json, package.json, ni fichier Python) : le demander à l'humain, "
                  f"puis `--adapter <{connus}>` ou le chemin d'un .toml", file=sys.stderr)
            return 2
        adaptateur = detecte
    texte_adaptateur, nom_adaptateur = charger_adaptateur(adaptateur)
    config.oublier_formats()
    ancien = config.Projet.charger(cible).lock if (cible / config.chemins(cible).lock).is_file() else {}
    try:
        tomllib.loads(texte_adaptateur)
    except tomllib.TOMLDecodeError as e:
        print(f"refus : adaptateur « {nom_adaptateur} » illisible : {e}", file=sys.stderr)
        return 2
    journal = [f"adaptateur : {nom_adaptateur}" + (" (détecté)" if adaptateur != nom_adaptateur else "")]
    if ancien:
        journal.append(f"mise à jour : moteur {ancien.get('version', 'amont')} → {VERSION}")
        try:
            journal += migrations.migrer(cible, int(ancien.get("format", 1)))
        except RuntimeError as e:
            print(f"refus : {e}", file=sys.stderr)
            return 2
        config.oublier_formats()
    ch = config.FORMAT_ACTUEL

    # 1. Le moteur, remplacé en bloc.
    if mode == config.MODE_AMONT:
        dossier_moteur = str(source.relative_to(cible)) if source.is_relative_to(cible) else "moteur"
    else:
        dossier_moteur = ch.moteur
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
        _ecrire(cible / ch.lock, (
            "# Verrou du moteur — écrit par l'installeur, jamais à la main.\n"
            "# Mode amont : ce dépôt fabrique le moteur, dont l'empreinte n'est pas figée ici.\n"
            f'mode = "{mode}"\n'
            f'engine_dir = "{dossier_moteur}"\n'
            f"format = {migrations.FORMAT}\n"
        ))
        journal.append(f"verrou en mode amont : le moteur est la source, sous {dossier_moteur}/socle")
    else:
        calculee, n = empreinte.calculer(cible, dossier_moteur)
        _ecrire(cible / ch.lock, (
            "# Verrou du moteur — écrit par l'installeur, jamais à la main.\n"
            "# La CI recalcule l'empreinte ; un moteur altéré dans le projet fait échouer `moteur.empreinte`.\n"
            f'version = "{VERSION}"\n'
            f'mode = "{mode}"\n'
            f'engine_dir = "{dossier_moteur}"\n'
            f'fingerprint = "{calculee}"\n'
            f"files = {n}\n"
            f"format = {migrations.FORMAT}\n"
        ))
        journal.append(f"verrou : {empreinte.courte(calculee)} sur {n} fichiers")

    # 3. Les fichiers du projet : posés s'ils manquent, jamais écrasés.
    politique = gabarit("politique.toml")
    if prive:
        politique = politique_privee(politique, prive, relecture, demandes_privees)
    if langue_memoire and not (cible / ch.politique).is_file():
        politique = politique_langue(politique, langue_memoire)
    # La langue de la mémoire : celle choisie ici pour un projet neuf, sinon
    # celle que sa politique dit déjà.
    lg = langue_memoire if langue_memoire and not (cible / ch.politique).is_file() else (
        langue.du_projet(config.Projet.charger(cible)) if (cible / ch.politique).is_file() else "fr")
    # Une mémoire privée demandée sur un projet déjà installé : la politique
    # existe et se garde, mais c'est l'humain qui lance la commande, et sans
    # sa section la mémoire privée resterait « non configurée » (B-0034, P4).
    # Une section déjà là est un choix fait : elle ne se réécrit pas.
    p_pol = cible / ch.politique
    if prive and p_pol.is_file():
        texte_pol = p_pol.read_text(encoding="utf-8")
        if not re.search(r"(?m)^\[private\]\s*$", texte_pol):
            if "# [private]\n" in texte_pol:
                texte_pol = politique_privee(texte_pol, prive, relecture, demandes_privees)
            else:
                texte_pol = politique_privee(texte_pol.rstrip("\n") + "\n\n# [private]\n", prive, relecture,
                                             demandes_privees)
            p_pol.write_text(texte_pol, encoding="utf-8")
            journal.append(f"mémoire privée ajoutée à la politique ({prive}) : un changement protégé, à approuver")
    if ancien and (cible / ch.politique).is_file():
        ecart = diff_politique(cible)
        if ecart:
            journal.append("la politique du projet diffère du gabarit de cette version ; rien n'est écrit, "
                           "elle est à l'humain — à relire :\n      " + "\n      ".join(ecart))
    for nom, contenu in (
        (ch.politique, politique),
        (ch.adaptateur, texte_adaptateur),
        (ch.garde_fous, garde_fous_initiaux(cible, texte_adaptateur)),
    ):
        p = cible / nom
        if p.is_file():
            journal.append(f"{nom} existe : conservé (comparer au gabarit à la main si besoin)")
        else:
            _ecrire(p, contenu)
            journal.append(f"{nom} posé")

    # 4. La mémoire initiale.
    jour = date.today().isoformat()
    for nom, lieu in (("canonique.md", ch.canonique), ("actif.md", ch.actif), ("backlog.md", ch.backlog)):
        p = cible / lieu
        if not p.is_file():
            _ecrire(p, gabarit(f"memoire/{nom}", lg))
    for lieu in (ch.decisions, ch.demandes):
        d = cible / lieu
        d.mkdir(parents=True, exist_ok=True)
        if not any(d.iterdir()):
            _ecrire(d / ".gitkeep", "")
    jdir = cible / ch.journal
    if not jdir.is_dir() or not any(jdir.glob("*.md")):
        from socle import memoire

        ident = memoire.Memoire.charger(cible).prochain_id("J", date=jour)
        _ecrire(jdir / f"{jour[:7]}.md", gabarit("memoire/journal.md", lg)
                .replace("@@MOIS@@", jour[:7]).replace("@@ID@@", ident).replace("@@VERSION@@", VERSION)
                .replace("@@ADAPTATEUR@@", nom_adaptateur)
                .replace("@@ADOPTION@@", ("" if not adoption else ", in adoption mode" if lg == "en"
                                          else ", en mode adoption")))
        journal.append(f"mémoire initiale posée, journal ouvert par {ident}")

    # 5. Les instructions : AGENTS.md fait foi, CLAUDE.md l'importe.
    journal += _instructions(cible, dossier_moteur, lg)

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
    if prive:
        journal += _prive(cible, prive, filtre)

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
    code, echecs = _audit(cible)
    print("\nEt maintenant :")
    for i, etape in enumerate(et_maintenant(cible, bool(ancien), echecs), 1):
        print(f"  {i}. {etape}")
    return code


def _instructions(cible: Path, dossier_moteur: str, lg: str = "fr") -> list[str]:
    res = []
    agents = cible / config.INSTRUCTIONS
    claude = cible / "CLAUDE.md"
    section = (gabarit("AGENTS.md", lg).replace("@@VERSION@@", VERSION).replace("@@MOTEUR@@", dossier_moteur))
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


def _prive(cible: Path, mode: str, filtre: str) -> list[str]:
    """La mémoire privée : le clone du dépôt privé et son verrou, ou le
    filtre de chiffrement ; puis l'accès, vérifié."""
    from socle import prive

    res = []
    zone = prive.dossier(cible)
    if mode == "compagnon":
        p = cible / ".gitignore"
        texte = p.read_text(encoding="utf-8") if p.is_file() else ""
        if f"{zone}/" not in texte.splitlines():
            p.write_text(texte.rstrip("\n") + f"\n# Le clone du dépôt privé (mémoire privée)\n{zone}/\n",
                         encoding="utf-8")
        sha = prive.commit_compagnon(cible)
        if sha:
            prive.ecrire_verrou(cible, sha)
            res.append(f"mémoire privée (compagnon) : dépôt privé trouvé, verrou à {sha[:10]}")
        else:
            res.append("!! mémoire privée (compagnon) : dépôt privé absent — le mettre en place : "
                       "`python3 .socle/socle prive installer --depot <adresse du dépôt privé>`")
    else:
        p = cible / ".gitattributes"
        texte = p.read_text(encoding="utf-8") if p.is_file() else ""
        ligne = f"{zone}/** filter={filtre} diff={filtre}"
        if not any(l.startswith(f"{zone}/**") for l in texte.splitlines()):
            p.write_text(texte.rstrip("\n") + ("\n" if texte.strip() else "") + ligne + "\n", encoding="utf-8")
        if outils.git(cible, "config", "--get", f"filter.{filtre}.clean", check=False).strip():
            res.append(f"mémoire privée (chiffrée) : filtre « {filtre} » configuré")
        else:
            res.append(f"!! mémoire privée (chiffrée) : filtre « {filtre} » non configuré ici — l'initialiser "
                       f"(`{filtre} init`, ou l'équivalent de l'outil) avant d'écrire du privé ; `prive.chiffre` "
                       "refusera tout fichier privé commité en clair")
    return res


def _adopter(cible: Path) -> list[str]:
    """Plafonds au niveau actuel ; les contrôles en échec passent en
    avertissement, liste d'où l'on ne retire que pour durcir."""
    from socle import contexte

    gf = cible / config.chemins(cible).garde_fous
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


def _audit(cible: Path) -> tuple[int, list[str]]:
    """Les contrôles de la CI, en bref : ce qui échoue ou avertit. Rend le
    code de sortie et les contrôles en échec."""
    r = subprocess.run([sys.executable, str(cible / config.LANCEUR), "check", "--stage", "ci", "--court"],
                       cwd=cible, capture_output=True, text=True)
    print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, end="", file=sys.stderr)
    m = re.search(r"(?m)^ECHEC — \d+ contrôle\(s\) : (.+)$", r.stdout)
    return r.returncode, [c.strip() for c in m.group(1).split(",")] if m else []


def et_maintenant(cible: Path, mise_a_jour: bool, echecs: list[str]) -> list[str]:
    """Ce qui reste à l'humain après l'installation, dans l'ordre où le
    faire (B-0034, P2) : chaque étape avec sa commande."""
    from socle import prive

    projet = config.Projet.charger(cible)
    etapes = []
    if "protege.fichiers" in echecs:
        etapes.append("approuver les fichiers protégés que la mise à jour a changés (la liste s'affiche, "
                      f'à confirmer) : `python3 .socle/socle approve --text "Mise à jour du socle {VERSION}"`')
    autres = [c for c in echecs if c != "protege.fichiers"]
    if autres:
        etapes.append(f"{len(autres)} contrôle(s) en échec ci-dessus ({', '.join(autres)}) : les corriger, "
                      "ou relancer l'installation avec `--adoption`, qui les passe en avertissement sur l'existant")
    mode = prive.mode(projet)
    if mode == "compagnon" and not prive.commit_compagnon(cible):
        etapes.append("mettre en place le dépôt privé (créé vide sur GitHub, privé) : clone, premier commit, "
                      "verrou, clé de déploiement, puis les deux gestes sur GitHub, avec leurs liens : "
                      "`python3 .socle/socle prive installer --depot <adresse du dépôt privé>`")
    elif mode and mode != "compagnon":
        filtre = "git-crypt"
        attributs = cible / ".gitattributes"
        if attributs.is_file():
            m = re.search(rf"(?m)^{re.escape(prive.dossier(cible))}/\*\* filter=(\S+)", attributs.read_text(encoding="utf-8"))
            filtre = m.group(1) if m else filtre
        if not outils.git(cible, "config", "--get", f"filter.{filtre}.clean", check=False).strip():
            etapes.append(f"initialiser le filtre de chiffrement « {filtre} » (`{filtre} init`, ou l'équivalent "
                          "de l'outil) avant d'écrire du privé")
    demandes = cible / projet.chemins.demandes
    if not mise_a_jour and not (demandes.is_dir() and any(demandes.glob("D-*.md"))):
        etapes.append("décrire le projet à l'agent : `python3 .socle/socle init --cadrage <document> --depot` "
                      "(sans document : `--depot` seul ; un dépôt vide : sans option)")
    message = f"Mettre à jour le socle {VERSION}" if mise_a_jour else f"Installer le socle {VERSION}"
    etapes.append(f'commiter puis pousser : `git add -A && git commit -m "{message}" && git push`')
    etapes.append("ouvrir l'agent dans le projet : il lit l'état au démarrage"
                  + ("" if mise_a_jour else ", et te pose les questions de départ dans la conversation"))
    etapes.append("ensuite, tes gestes, chacun avec sa commande : `python3 .socle/socle aide`")
    return etapes
