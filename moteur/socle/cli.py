"""Ligne de commande du socle : `python3 .socle/socle <commande>`.

Les commandes portent des noms anglais (identifiants), leurs messages sont en
français. Toute commande de contrôle rend un code de sortie : 0 si tout passe.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

from socle import VERSION, config, outils


def _projet(args) -> config.Projet:
    return config.Projet.charger(Path(args.root) if getattr(args, "root", None) else None)


def _base(projet: config.Projet, valeur: str | None) -> str | None:
    """La base demandée, ou le point de divergence avec la branche par défaut.
    Une base nulle (`0000…`, premier push d'une branche) retombe sur celui-ci."""
    if valeur and set(valeur) != {"0"} and outils.rev_existe(projet.racine, valeur):
        return outils.resoudre(projet.racine, valeur)
    if valeur and set(valeur) != {"0"}:
        print(f"!! base « {valeur} » introuvable — repli sur la branche par défaut", file=sys.stderr)
    return outils.base_de_travail(projet.racine)


# --------------------------------------------------------------------------


def cmd_state(args) -> int:
    from socle import etat

    print(etat.calculer(_projet(args), contenus=not args.short))
    return 0


def cmd_check(args) -> int:
    from socle import contexte

    projet = _projet(args)
    base = _base(projet, args.base)
    ctx = contexte.Contexte(projet, etage=args.stage, base=base, tete=args.rev, rapide=args.fast)
    ids = [i.strip() for i in args.only.split(",")] if args.only else None
    rapport = contexte.executer(ctx, ids)
    titre = f"socle {VERSION} — contrôles, étage {args.stage}" + (f", base {base[:10]}" if base else ", sans base")
    rapport.afficher(titre)
    return 0 if rapport.reussi else 1


def cmd_verify(args) -> int:
    from socle import contexte, verification
    from socle.rapport import Rapport

    projet = _projet(args)
    base = _base(projet, args.base)
    rapport = Rapport()
    verification.executer_etapes(projet, args.fast, rapport, flux=sys.stderr)
    etage = "git" if args.fast else "ci"
    rapport.fusionner(contexte.executer(contexte.Contexte(projet, etage=etage, base=base, rapide=args.fast)))
    mode = "rapide" if args.fast else "complète"
    rapport.afficher(f"socle {VERSION} — vérification {mode}" + (f", base {base[:10]}" if base else ""))
    return 0 if rapport.reussi else 1


def cmd_ci(args) -> int:
    from socle import autotest, contexte, verification
    from socle.rapport import Rapport

    projet = _projet(args)
    base = _base(projet, args.base)
    rapport = Rapport()
    verification.executer_etapes(projet, False, rapport, flux=sys.stderr)
    rapport.fusionner(contexte.executer(contexte.Contexte(projet, etage="ci", base=base)))
    if not args.no_selftest:
        rapport.fusionner(autotest.executer(projet, bavard=False))
    rapport.afficher(f"socle {VERSION} — CI" + (f", base {base[:10]}" if base else ", sans base"))
    return 0 if rapport.reussi else 1


def cmd_hook(args) -> int:
    from socle import hooks

    projet = _projet(args)
    evt = args.event
    if evt == "session-start":
        return hooks.session_start(projet, hooks.lire_entree())
    if evt == "pre-tool-use":
        return hooks.pre_tool_use(projet, hooks.lire_entree())
    if evt == "stop":
        return hooks.stop(projet, hooks.lire_entree())
    if evt == "git-pre-commit":
        return hooks.git_pre_commit(projet)
    if evt == "git-prepare-commit-msg":
        return hooks.git_prepare_commit_msg(projet, *args.rest[:2])
    if evt == "git-pre-push":
        return hooks.git_pre_push(projet)
    print(f"hook inconnu : {evt}", file=sys.stderr)
    return 2


def cmd_next_id(args) -> int:
    from socle import memoire

    projet = _projet(args)
    mem = memoire.Memoire.charger(projet.racine)
    type_ = TYPES_CLI[args.type]
    print(mem.prochain_id(type_, prive=args.private, date=date.today().isoformat()))
    return 0


TYPES_CLI = {"fact": "F", "backlog": "B", "adr": "ADR", "journal": "J", "request": "D"}


def _slug(titre: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", outils.sans_accents(titre).lower()).strip("-")
    return s[:50].rstrip("-") or "sans-titre"


def cmd_new(args) -> int:
    from socle import memoire

    projet = _projet(args)
    racine = projet.racine
    mem = memoire.Memoire.charger(racine)
    type_ = TYPES_CLI[args.type]
    jour = date.today().isoformat()
    ident = mem.prochain_id(type_, date=jour)
    titre = args.title
    zone = "publique"
    if type_ == "F":
        chemin = racine / "memoire/canonique.md"
        bloc = f"\n## {ident} — {titre}\n\n> statut : supposé · source : <d'où vient ce fait>\n\n<le fait, et ce qui le prouverait>\n"
        _ajouter(chemin, bloc)
    elif type_ == "B":
        chemin = racine / "memoire/backlog.md"
        bloc = f"\n## {ident} — {titre}\n\n> statut : ouvert · origine : <J-… ou commit:… où le sujet est apparu>\n\n<ce qu'il faut faire, et pourquoi>\n"
        _ajouter(chemin, bloc)
    elif type_ == "J":
        chemin = racine / f"memoire/journal/{jour[:7]}.md"
        if not chemin.is_file():
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text(f"<!-- socle: couche=journal zone={zone} -->\n# Journal — {jour[:7]}\n", encoding="utf-8")
        _ajouter(chemin, f"\n## {ident} — {titre}\n\n<ce qui s'est passé, avec ses références>\n")
    elif type_ == "ADR":
        chemin = racine / f"memoire/decisions/{ident}-{_slug(titre)}.md"
        chemin.write_text(
            f"<!-- socle: couche=decisions zone={zone} -->\n# {ident} — {titre}\n\n"
            f"> statut : proposée · date : {jour}\n\n## Contexte\n\n<ce qui oblige à décider>\n\n"
            "## Décision\n\n<ce qui est décidé>\n\n## Conséquences\n\n<ce que ça change, et comment le défaire>\n",
            encoding="utf-8")
    else:
        from socle.modeles import gabarit

        chemin = racine / f"memoire/demandes/{ident}-{_slug(titre)}.md"
        chemin.write_text(gabarit("demande.md").format(id=ident, titre=titre, date=jour), encoding="utf-8")
    print(f"{ident}\t{chemin.relative_to(racine)}")
    return 0


def _ajouter(chemin: Path, bloc: str):
    texte = chemin.read_text(encoding="utf-8") if chemin.is_file() else ""
    chemin.write_text(texte.rstrip("\n") + "\n" + bloc, encoding="utf-8")


def cmd_show(args) -> int:
    """Une entrée de mémoire par son identifiant, où qu'elle soit (archivée
    comprise) ; pour une demande, sa réponse aussi."""
    from socle import demandes, memoire

    projet = _projet(args)
    code = 0
    for ident in args.ids:
        e = memoire.Memoire.charger(projet.racine).entree(ident)
        if e is None:
            print(f"{ident} : aucune entrée de ce nom dans la mémoire", file=sys.stderr)
            code = 1
            continue
        lieu = f"{e.fichier}:{e.ligne}" + (f", archivée dans {e.parent}" if e.parent else "")
        print(f"--- {ident} ({lieu}) ---")
        print(e.texte)
        if e.type == "D":
            d = next((d for d in demandes.toutes(projet.racine) if d.id == ident), None)
            if d and d.chemin_reponse:
                print(f"\n--- réponse ({d.chemin_reponse}) : {d.statut} ---")
                print((projet.racine / d.chemin_reponse).read_text(encoding="utf-8").rstrip())
            elif d:
                print(f"\n--- {d.statut} ---")
    return code


def cmd_answer(args) -> int:
    """L'humain répond lui-même, ou l'agent relaie (`--relayed`) une réponse
    donnée dans la conversation, en citant son texte exact (ADR-0006)."""
    from socle import demandes

    projet = _projet(args)
    cible = [d for d in demandes.toutes(projet.racine) if d.id == args.request]
    if not cible:
        print(f"demande introuvable : {args.request}", file=sys.stderr)
        return 2
    d = cible[0]
    citation = args.quote or ""
    if args.quote_file:
        citation = Path(args.quote_file).read_text(encoding="utf-8")
    if args.relayed and not args.by:
        print("refus : une réponse relayée nomme l'humain qui l'a donnée (--by)", file=sys.stderr)
        return 2
    if not args.relayed:
        print(d.texte)
        print("\n" + "=" * 72)
    try:
        chemin = demandes.ecrire_reponse(projet.racine, d, args.answer, args.text or "", args.by or _auteur(projet),
                                         date.today().isoformat(),
                                         canal="conversation" if args.relayed else "terminal", citation=citation)
    except ValueError as e:
        print(f"refus : {e}", file=sys.stderr)
        return 2
    print(f"réponse « {args.answer} » écrite dans {chemin} — à commiter avec la suite.")
    return 0


def _auteur(projet) -> str:
    return outils.git(projet.racine, "config", "user.name", check=False).strip() or "humain"


def cmd_approve(args) -> int:
    """Réservé à l'humain : valide d'un coup un changement qu'il fait lui-même
    (fichier protégé, clé de garde-fou), en écrivant la demande et sa réponse."""
    from socle import demandes, empreinte, memoire
    from socle.modeles import gabarit

    projet = _projet(args)
    racine = projet.racine
    mem = memoire.Memoire.charger(racine)
    ident = mem.prochain_id("D")
    jour = date.today().isoformat()
    cites = []
    for f in args.files or []:
        p = racine / f
        cites.append(f"- `{f}` — fichier protégé modifié par l'humain lui-même ; empreinte nouvelle "
                     f"`{empreinte.courte(empreinte.fichier(p)) if p.is_file() else 'supprimé'}`.")
    for k in args.keys or []:
        cites.append(f"- `{k}` — clé des garde-fous assouplie par l'humain lui-même, en connaissance de cause.")
    if not cites:
        print("rien à approuver : --files ou --keys", file=sys.stderr)
        return 2
    texte = gabarit("approbation.md").format(id=ident, date=jour, raison=args.text, elements="\n".join(cites))
    chemin = racine / f"memoire/demandes/{ident}-approbation-humaine.md"
    chemin.write_text(texte, encoding="utf-8")
    d = demandes.charger(racine, None, str(chemin.relative_to(racine)), texte)
    demandes.ecrire_reponse(racine, d, "valider", args.text, _auteur(projet), jour)
    print(f"{ident} écrite et validée : {chemin.relative_to(racine)}")
    return 0


def cmd_install(args) -> int:
    from socle import installeur

    return installeur.installer(
        cible=Path(args.target).resolve(),
        adaptateur=args.adapter,
        proprietaire=args.owner,
        adoption=args.adoption,
        mode=args.mode,
        source=Path(__file__).resolve().parent.parent,
    )


def cmd_selftest(args) -> int:
    from socle import autotest

    rapport = autotest.executer(_projet(args), bavard=args.verbose)
    rapport.afficher(f"socle {VERSION} — auto-test par injection de défauts")
    return 0 if rapport.reussi else 1


def cmd_fingerprint(args) -> int:
    from socle import empreinte

    projet = _projet(args)
    calculee, n = empreinte.calculer(projet.racine, projet.dossier_moteur)
    print(f"{calculee}  ({n} fichiers sous {projet.dossier_moteur}/socle et le lanceur)")
    for f in args.files or []:
        p = projet.racine / f
        print(f"{empreinte.courte(empreinte.fichier(p)) if p.is_file() else 'supprimé'}  {f}")
    return 0


def cmd_mutation_verdict(args) -> int:
    from socle import mutation

    rapport = mutation.verdict(_projet(args), Path(args.results))
    rapport.afficher(f"socle {VERSION} — verdict de mutation")
    return 0 if rapport.reussi else 1


def cmd_archive(args) -> int:
    from socle import archivage

    return archivage.archiver_backlog(_projet(args))


def cmd_checks(args) -> int:
    from socle import contexte
    from socle import controles_cliquet, controles_docs, controles_memoire, controles_tests  # noqa: F401

    for c in contexte.REGISTRE.values():
        premiere = c.doc.splitlines()[0] if c.doc else ""
        print(f"{c.id:<28} {','.join(c.etages):<12} {'base ' if c.base else '     '}{'lent ' if c.lent else '     '}{premiere}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="socle", description=f"socle {VERSION} — mémoire, documentation et tests fiables")
    p.add_argument("--root", help="racine du projet (défaut : le dépôt git courant)")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("state", help="état dérivé, injecté au démarrage de session")
    s.add_argument("--short", action="store_true", help="sans le contenu de l'actif et du canonique")
    s.set_defaults(f=cmd_state)

    s = sp.add_parser("check", help="contrôles du socle, un code de sortie")
    s.add_argument("--stage", choices=("agent", "git", "ci"), default="ci")
    s.add_argument("--base", help="révision de base (défaut : divergence avec la branche par défaut)")
    s.add_argument("--rev", help="révision contrôlée (défaut : l'arbre de travail)")
    s.add_argument("--only", help="liste de contrôles, séparés par des virgules")
    s.add_argument("--fast", action="store_true", help="sans les contrôles lents")
    s.set_defaults(f=cmd_check)

    s = sp.add_parser("verify", help="le contrat verify : capacités de l'adaptateur puis contrôles")
    s.add_argument("--fast", "--rapide", action="store_true", dest="fast")
    s.add_argument("--base")
    s.set_defaults(f=cmd_verify)

    s = sp.add_parser("ci", help="tout : capacités, contrôles, auto-test")
    s.add_argument("--base")
    s.add_argument("--no-selftest", action="store_true")
    s.set_defaults(f=cmd_ci)

    s = sp.add_parser("hook", help="point d'entrée des hooks de l'agent et de git")
    s.add_argument("event")
    s.add_argument("rest", nargs="*")
    s.set_defaults(f=cmd_hook)

    s = sp.add_parser("next-id", help="prochain identifiant libre")
    s.add_argument("type", choices=sorted(TYPES_CLI))
    s.add_argument("--private", action="store_true")
    s.set_defaults(f=cmd_next_id)

    s = sp.add_parser("new", help="ajoute une entrée squelette avec son identifiant")
    s.add_argument("type", choices=sorted(TYPES_CLI))
    s.add_argument("title")
    s.set_defaults(f=cmd_new)

    s = sp.add_parser("show", help="afficher une entrée de mémoire par son identifiant")
    s.add_argument("ids", nargs="+")
    s.set_defaults(f=cmd_show)

    s = sp.add_parser("answer", help="répondre à une demande, ou relayer la réponse donnée dans la conversation")
    s.add_argument("request")
    s.add_argument("answer")
    s.add_argument("--text", default="")
    s.add_argument("--by")
    s.add_argument("--relayed", action="store_true", help="réponse donnée par l'humain dans la conversation")
    s.add_argument("--quote", help="texte exact de l'humain (avec --relayed)")
    s.add_argument("--quote-file", help="fichier qui contient le texte exact de l'humain")
    s.set_defaults(f=cmd_answer)

    s = sp.add_parser("approve", help="(humain) valider son propre changement protégé ou assoupli")
    s.add_argument("--files", nargs="*")
    s.add_argument("--keys", nargs="*")
    s.add_argument("--text", required=True)
    s.set_defaults(f=cmd_approve)

    s = sp.add_parser("install", help="installer ou mettre à jour le socle dans un projet")
    s.add_argument("--target", default=".")
    s.add_argument("--adapter", required=True, help="nom d'un adaptateur maintenu (rust, python) ou chemin d'un .toml")
    s.add_argument("--owner", default="", help="propriétaire pour CODEOWNERS, ex. @theodubus")
    s.add_argument("--adoption", action="store_true", help="projet existant : plafonds au niveau actuel")
    s.add_argument("--mode", choices=(config.MODE_PROJET, config.MODE_AMONT), default=config.MODE_PROJET)
    s.set_defaults(f=cmd_install)

    s = sp.add_parser("selftest", help="injecte des défauts connus et vérifie qu'ils sont attrapés")
    s.add_argument("--verbose", action="store_true")
    s.set_defaults(f=cmd_selftest)

    s = sp.add_parser("fingerprint", help="empreinte du moteur et de fichiers")
    s.add_argument("files", nargs="*")
    s.set_defaults(f=cmd_fingerprint)

    s = sp.add_parser("mutation-verdict", help="survivants d'un balayage contre les plafonds")
    s.add_argument("results")
    s.set_defaults(f=cmd_mutation_verdict)

    s = sp.add_parser("archive", help="archive les sujets clos du backlog dans le journal")
    s.set_defaults(f=cmd_archive)

    s = sp.add_parser("checks", help="liste des contrôles")
    s.set_defaults(f=cmd_checks)

    args = p.parse_args(argv)
    return args.f(args)
