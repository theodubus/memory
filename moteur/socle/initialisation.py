"""L'initialisation d'un projet : trois entrées cumulables, un document de
cadrage, rien du tout, un dépôt existant (cadrage, section « Initialisation »).

Le moteur fait ce qui se fait sans juger : il archive le document tel quel
avec son empreinte, audite le dépôt en lecture seule et n'en tire que du
vérifiable (un fait « mesuré » a un fichier pour preuve), et pose les
questions de départ, chacune avec son défaut, plafonnées par la politique.
Ce qui demande de comprendre — extraire du document les objectifs et les
contraintes, confronter le document et le dépôt — revient à l'agent, avec
les règles que `socle init` lui imprime. Rien n'est inventé : un fait sans
source est « supposé ».
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from socle import config, langue, memoire, outils
from socle.modeles import gabarit


@dataclass
class Fait:
    titre: str
    preuve: str  # un chemin du dépôt


@dataclass
class Question:
    texte: str
    defaut: str
    effet: str  # ce que le défaut change


def archiver_cadrage(racine: Path, document: Path) -> tuple[str, str]:
    """Le document, copié tel quel dans les archives de la mémoire, et son empreinte."""
    dest = racine / config.chemins(racine).archives / document.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if document.resolve() != dest.resolve():
        shutil.copyfile(document, dest)
    return str(dest.relative_to(racine)), "sha256:" + outils.empreinte_fichier(dest)


def auditer_depot(projet: config.Projet) -> list[Fait]:
    """Ce que le dépôt prouve par ses fichiers : langage, tests, CI, docs."""
    racine = projet.racine
    fichiers = [f for f in outils.fichiers_courants(racine)
                if not f.startswith((config.DOSSIER + "/", ".claude/")) and not memoire.est_memoire(f)]
    faits = []
    if "Cargo.toml" in fichiers:
        faits.append(Fait("Le projet se construit avec cargo (Rust)", "Cargo.toml"))
    for f in ("pyproject.toml", "setup.py", "setup.cfg"):
        if f in fichiers:
            faits.append(Fait("Le projet est un paquet Python", f))
            break
    cfg = projet.adaptateur.get("tests") or {}
    if cfg.get("function"):
        from socle import tests_lecture

        par_fichier = {}
        for f in outils.filtrer(fichiers, cfg.get("paths", []), cfg.get("exclude", [])):
            texte = outils.lire_a(racine, None, f) or ""
            n = sum(1 for fn in tests_lecture.extraire(texte, f, cfg) if fn.est_test)
            if n:
                par_fichier[f] = n
        if par_fichier:
            premier = sorted(par_fichier)[0]
            faits.append(Fait(f"Le dépôt a {sum(par_fichier.values())} fonction(s) de test, dans "
                              f"{len(par_fichier)} fichier(s), dont `{premier}`", premier))
    # La CI du socle n'est pas celle du projet : l'installeur vient de la poser.
    for ci in sorted(f for f in fichiers if f.startswith(".github/workflows/") and f.endswith((".yml", ".yaml"))
                     and f != ".github/workflows/socle.yml"):
        faits.append(Fait(f"Une CI GitHub existe : `{ci.rsplit('/', 1)[1]}`", ci))
    for doc in ("README.md", "README", "README.rst"):
        if doc in fichiers:
            faits.append(Fait("Le dépôt a un README", doc))
            break
    return faits


def questions_de_depart(projet: config.Projet, cadrage: str | None, depot: bool) -> list[Question]:
    """Ce que l'agent ne peut pas déduire, avec un défaut chacune : le
    langage et les outils se lisent dans le dépôt, l'objectif et la
    confidentialité non."""
    q = []
    if cadrage:
        but = "celui du document de cadrage, tel qu'il est écrit"
    elif depot:
        but = "celui que dit le README, s'il en a un ; sinon aucun, et le backlog reste vide"
    else:
        but = "aucun : le backlog reste vide jusqu'à ce que tu en donnes un"
    q.append(Question("Quel est le but du projet, en une phrase ?", but,
                      "le but alimente le backlog ; en défaut, il est noté « supposé »"))
    if not (depot and detecter(projet)):
        q.append(Question("Dans quel langage, avec quels outils de test ?",
                          "celui de l'adaptateur posé à l'installation",
                          "l'adaptateur décide comment le socle lance les tests ; le changer demande ton accord"))
    q.append(Question("Une partie de la mémoire doit-elle rester privée ?",
                      "non : toute la mémoire est publique",
                      "une mémoire privée se pose par l'installeur, en dépôt privé à côté ou chiffrée"))
    q.append(Question("La politique d'autonomie par défaut (les huit points du cadrage) te convient-elle ?",
                      "oui, telle quelle",
                      "la politique dit ce que l'agent décide seul et ce qu'il te demande ; toi seul la modifies"))
    q.append(Question("Des contraintes à respecter (licence, dépendances, plateformes, délais) ?",
                      "aucune connue", "une contrainte devient un fait « supposé » jusqu'à ce que tu la valides"))
    plafond = int(projet.pol("init_questions_max", defaut=7))
    return q[:plafond]


def detecter(projet: config.Projet) -> bool:
    from socle import installeur

    return installeur.detecter_adaptateur(projet.racine) is not None


def demande_de_depart(projet: config.Projet, ident: str, questions: list[Question], cadrage: str | None,
                      entrees: str) -> str:
    plafond = int(projet.pol("init_questions_max", defaut=7))
    lignes = []
    for i, q in enumerate(questions, 1):
        lignes.append(f"{i}. **{q.texte}** Défaut : {q.defaut}. Ce que ça change : {q.effet}.")
    if cadrage:
        cite = (f"- Le document de cadrage, archivé tel quel sous `{cadrage}` : ce que le projet veut, d'où "
                "l'agent tire les faits « supposés » et le backlog de départ.")
        lien = f"- Le document de cadrage : [{Path(cadrage).name}](../{Path(cadrage).relative_to(projet.chemins.memoire)})."
    else:
        cite = "- Aucun élément de la mémoire : le projet commence, et ces questions en posent le départ."
        lien = "- Les instructions du projet : [AGENTS.md](../../AGENTS.md), section de la politique d'autonomie."
    return gabarit("questions-de-depart.md").format(
        id=ident, date=date.today().isoformat(), entrees=entrees, n=len(questions), plafond=plafond,
        questions="\n".join(lignes), elements=cite, lien=lien)


def initialiser(projet: config.Projet, cadrage: Path | None = None, depot: bool = False) -> int:
    from socle import cli

    racine = projet.racine
    if not projet.installe:
        print("refus : le socle n'est pas installé ici (`socle install` d'abord)")
        return 2
    jour = date.today().isoformat()
    lg = langue.du_projet(projet)
    mem = memoire.Memoire.charger(racine)
    entrees = " et ".join(x for x in (
        "un document de cadrage" if cadrage else "", "un dépôt existant" if depot else "") if x) or "rien du tout"
    sortie = [f"initialisation depuis {entrees}"]

    archive = None
    if cadrage:
        archive, emp = archiver_cadrage(racine, cadrage)
        ident = mem.prochain_id("J", date=jour)
        cli._ajouter(racine / projet.chemins.journal / f"{jour[:7]}.md",
                     f"\n## {ident} — Document de cadrage archivé tel quel\n\n"
                     f"{langue.meta(lg, type='initialisation', ref=langue.ref_fichier(archive, lg))} · empreinte : {emp}\n\n"
                     "Archivé sans réécriture. Ce qu'il affirme entre dans la mémoire en « supposé », avec ce "
                     "fichier pour source, jusqu'à validation humaine.\n", langue.entete_fichier("journal", "publique", lg))
        sortie.append(f"document archivé : {archive} ({emp[:23]}…), journal {ident}")
        mem = memoire.Memoire.charger(racine)

    if depot:
        faits = auditer_depot(projet)
        premier = int(mem.prochain_id("F").split("-")[1])
        bloc = ""
        for k, f in enumerate(faits):
            bloc += (f"\n## F-{premier + k:04d} — {f.titre}\n\n"
                     + langue.meta(lg, "F", statut="mesure", preuve=langue.ref_fichier(f.preuve, lg),
                                   source="audit d'initialisation", date=jour) + "\n")
        if bloc:
            cli._ajouter(racine / projet.chemins.canonique, bloc, langue.entete_fichier("canonique", "publique", lg))
        sortie.append(f"audit du dépôt en lecture seule : {len(faits)} fait(s) mesuré(s), chacun avec son fichier")
        mem = memoire.Memoire.charger(racine)

    qs = questions_de_depart(projet, archive, depot)
    ident = mem.prochain_id("D")
    chemin = racine / projet.chemins.demandes / f"{ident}-questions-de-depart.md"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(demande_de_depart(projet, ident, qs, archive, entrees), encoding="utf-8")
    sortie.append(f"questions de départ : {ident}, {len(qs)} question(s), chacune avec son défaut")

    for l in sortie:
        print(f"  - {l}")
    print("\nPour toi :")
    for i, etape in enumerate(pour_toi(ident), 1):
        print(f"  {i}. {etape}")
    print("\n" + gabarit("initialisation.md"))
    return 0


def pour_toi(ident: str) -> list[str]:
    """Ce qui revient à l'humain après `init`, avant la part de l'agent,
    écrite pour lui (B-0034, P2)."""
    return [
        f'commiter puis pousser : `git add -A && git commit -m "Initialiser la mémoire" && git push` '
        f"(la demande {ident} doit être sur GitHub pour que tu puisses la lire)",
        "ouvrir l'agent dans le projet : il relit les questions de départ et te les pose dans la conversation, "
        "avec leur lien",
        "y répondre dans la conversation, une ligne par question ou « défauts » : l'agent consigne ta réponse "
        "telle quelle",
    ]
