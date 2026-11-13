"""L'état dérivé : calculé à chaque démarrage de session et après chaque
compactage, jamais écrit à la main.

Tout ce qui est imprimé ici vient de git, de la mémoire ou de la trace des
hooks : rien n'est recopié, donc rien ne peut vieillir. Ce script ne doit
jamais empêcher une session de démarrer : un échec se traduit par une ligne
en moins, jamais par un code non nul.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from collections import Counter
from dataclasses import dataclass
from typing import Callable

from socle import config, requests as demandes, memory as memoire, utils as outils
from socle.messages import a_traduire, trad


def _ligne_ci(racine, branche) -> str:
    """L'état de la CI, si `gh` est là et authentifié. Sinon on le dit : le
    moteur n'exige aucun service externe."""
    if not shutil.which("gh"):
        return trad("non disponible localement (gh absent) — voir la pull request")
    try:
        p = subprocess.run(
            ["gh", "run", "list", "--branch", branche, "--limit", "1",
             "--json", "status,conclusion,workflowName,headSha"],
            cwd=racine, capture_output=True, text=True, timeout=8,
        )
    except (subprocess.TimeoutExpired, OSError):
        return trad("non disponible (gh ne répond pas)")
    if p.returncode != 0 or not p.stdout.strip() or p.stdout.strip() == "[]":
        return trad("non disponible (gh non authentifié ou aucune exécution)")
    import json

    try:
        r = json.loads(p.stdout)[0]
    except (ValueError, IndexError):
        return trad("non disponible (réponse illisible)")
    return trad("{ci} : {etat} sur {sha}", ci=r.get("workflowName"), etat=r.get("conclusion") or r.get("status"),
                sha=r.get("headSha", "")[:7])


def _gh_json(racine, chemin: str):
    """Une réponse de l'API de GitHub par `gh`, ou `None`."""
    import json

    try:
        p = subprocess.run(["gh", "api", chemin], cwd=racine, capture_output=True, text=True, timeout=5)
        return json.loads(p.stdout) if p.returncode == 0 else None
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return None


def nom_de_la_ci(projet: config.Projet) -> str:
    """Le nom du travail de la CI du socle, tel que GitHub l'exige."""
    return outils.nom_du_travail(outils.lire_a(projet.racine, None, ".github/workflows/socle.yml") or "") or "Socle"


def ci_exigee(projet: config.Projet) -> tuple[bool | None, str]:
    """La CI du socle est-elle exigée avant de fusionner sur la branche par
    défaut, par un ensemble de règles ou une protection de branche de
    GitHub ? Sans elle, une CI rouge n'empêche pas de fusionner : la
    garantie « seule la CI est incontournable » tombe. `None` quand on ne peut pas le savoir, avec la raison ; sinon
    le nom de la branche, et si la revue des propriétaires du code est
    exigée aussi."""
    from socle import links as liens

    url = liens.url_depot(projet) or ""
    if not url.startswith("https://github.com/"):
        return None, trad("dépôt hors de GitHub")
    nom = (outils.branche_par_defaut(projet.racine) or "").removeprefix("origin/")
    if not nom:
        return None, trad("aucune branche par défaut connue")
    if not shutil.which("gh"):
        return None, trad("gh absent")
    depot = url.removeprefix("https://github.com/")
    regles = _gh_json(projet.racine, f"repos/{depot}/rules/branches/{nom}")
    branche = _gh_json(projet.racine, f"repos/{depot}/branches/{nom}")
    if not isinstance(regles, list) or not isinstance(branche, dict):
        return None, trad("gh non authentifié, ou réponse illisible")
    ci = nom_de_la_ci(projet)
    exigees = [c.get("context") for r in regles if r.get("type") == "required_status_checks"
               for c in (r.get("parameters") or {}).get("required_status_checks", [])]
    classique = ((branche.get("protection") or {}).get("required_status_checks") or {})
    if classique.get("enforcement_level", "off") != "off":
        exigees += classique.get("contexts", []) + [c.get("context") for c in classique.get("checks", [])]
    revue = any((r.get("parameters") or {}).get("require_code_owner_review") for r in regles
                if r.get("type") == "pull_request")
    return ci in exigees, nom + (trad(" ; revue des propriétaires du code exigée") if revue else
                                 trad(" ; revue des propriétaires du code non exigée"))


def _balayage(projet: config.Projet, elements: list) -> list[str]:
    """La ligne du balayage de mutation planifié, quand l'adaptateur en
    déclare un ; endormi ou arrêté, le réveiller revient à l'humain."""
    from socle import human as humain, mutation

    niveau, message, _, page = mutation.etat_du_balayage(
        projet, outils.fichiers_courants(projet.racine), lambda f: outils.lire_a(projet.racine, None, f))
    if not message:
        return []
    if niveau == "erreur":
        elements.append(humain.Element("action", trad("remettre en marche le balayage de mutation : {message}",
                                                      message=message), page or ""))
    return [trad("mutation : {message}", message=message)]


def page_protection(projet: config.Projet) -> str | None:
    """La page des réglages de GitHub où l'humain pose ses ensembles de
    règles (rulesets)."""
    from socle import links as liens

    url = liens.url_depot(projet) or ""
    return f"{url}/settings/rules" if url.startswith("https://github.com/") else None


# La sortie du démarrage (ADR-0071) : chaque groupe a sa part de la borne
# `[startup] max_bytes`, en fraction. 9 500 octets donnent 2 375 à l'état
# dérivé, 3 800 au chantier actif, 2 090 aux faits, 1 235 aux décisions. Le
# budget du chantier actif des garde-fous (3 700 dans le gabarit) tient dans
# sa part, en-tête déduit (`budget_actif_permis`) : un chantier actif dans son
# budget n'est pas coupé.
PARTS = {"etat": 0.25, "actif": 0.40, "faits": 0.22, "decisions": 0.13}
# Une ligne de l'état dérivé, en octets au plus (l'alerte des hooks non
# chargés, la plus longue des lignes fixes, en fait 953) ; une ligne de
# titre (un commit, un fait, une décision), bien moins ; le titre d'un sujet
# du backlog, que sa ligne précède et que sa priorité peut suivre, moins
# encore.
LIGNE = 1000
TITRE = 80
TITRE_DE_SUJET = 70
# Les éléments montrés de chaque liste de l'état dérivé : `git log`, `socle
# show --index backlog` et `socle state --short` donnent le reste.
COMMITS_MONTRES = 5
PRETS_MONTRES = 5
ELEMENTS_MONTRES = 4
BASSES_MONTREES = 10


def budget_actif_permis(projet: config.Projet) -> int:
    """La taille, en octets, que le chantier actif peut avoir sans être
    coupé au démarrage : sa part de la borne, moins son en-tête."""
    return int(projet.borne_demarrage() * PARTS["actif"]) - _octets(["", f"--- {projet.chemins.actif} ---"])


def _liste(elements: list, plafond: int | None, rendre: Callable[[object], list[str]]) -> list[str]:
    """Les lignes des `plafond` premiers éléments, puis le nombre des autres."""
    res = [l for e in elements[:plafond] for l in rendre(e)]
    if plafond is not None and len(elements) > plafond:
        res.append(trad("  … et {n} autre(s)", n=len(elements) - plafond))
    return res


def calculer(projet: config.Projet, contenus: bool = True, supplement: list[str] | tuple = ()) -> str:
    """L'état du démarrage : l'état dérivé, puis, avec `contenus`, le
    chantier actif, les faits par leur titre et les dix dernières décisions,
    chaque groupe dans sa part de la borne des garde-fous (`[startup]
    max_bytes`, ADR-0071), que Claude Code remet entière à l'agent ; l'état
    dérivé y a ses lignes bornées et ses listes plafonnées. `supplement` :
    les lignes que le hook de démarrage ajoute (les outils de l'adaptateur,
    les hooks git), comptées dans la part de l'état. Les lignes d'action
    (les demandes, l'humain, les hooks) précèdent le backlog : l'essentiel
    tient dans les premiers octets. Sans `contenus` (`socle state
    --short`), l'état dérivé seul, entier : ni borne, ni plafond."""
    racine = projet.racine
    lignes = []
    nom = racine.name
    plafond = ELEMENTS_MONTRES if contenus else None
    from socle import hooks
    from socle.checks_ratchet import REMEDE_HOOKS

    if hooks.hooks_non_charges(projet):
        # En tête, avant tout le reste : rien de ce qui suit n'est protégé
        # par les hooks de l'agent.
        lignes.append(trad("!! LES HOOKS DE L'AGENT NE SONT PAS CHARGÉS dans cette session : aucun n'a tiré "
                           "pour elle récemment, ni au démarrage ni avant cette commande (une session reprise hors "
                           "de la racine du projet garde ses traces d'avant). Ni le filtre des commandes, ni les "
                           "contrôles de fin de tour, ni l'état au démarrage ne tournent. Le dire à l'humain avant "
                           "tout travail. {remede}",
                           remede=trad(REMEDE_HOOKS)))
        lignes.append("")
    lignes.append(trad("== {nom} — état dérivé par `socle state`, rien de recopié ==", nom=nom))
    try:
        lignes += _git(racine, projet, borne=contenus)
    except outils.ErreurGit as e:
        lignes.append(trad("git : indisponible ({erreur})", erreur=e))
    mem, backlog = None, []
    try:
        mem = memoire.Memoire.charger(racine)
        lignes += _memoire(mem, projet)
        backlog = _backlog(mem, borne=contenus)
    except Exception as e:  # l'état ne bloque jamais le démarrage
        lignes.append(trad("mémoire : illisible ({erreur}) — lancer `python3 .socle/socle check`",
                           erreur=f"{type(e).__name__}: {e}"))
    try:
        lignes += _demandes(racine, plafond)
    except Exception as e:
        lignes.append(trad("demandes : illisibles ({erreur})", erreur=f"{type(e).__name__}: {e}"))
    try:
        lignes += audit_adaptateur(projet)
    except Exception as e:
        lignes.append(trad("adaptateur : audit impossible ({erreur})", erreur=f"{type(e).__name__}: {e}"))
    try:
        from socle import human as humain

        elements = humain.a_faire(projet)
        exigee, detail = ci_exigee(projet)
        # Le détail commence par le nom de la branche, suivi de ce que dit la
        # revue des propriétaires du code.
        nom = (outils.branche_par_defaut(racine) or "").removeprefix("origin/")
        revue = detail[len(nom):] if nom and detail.startswith(nom) else ""
        if exigee is False:
            elements.append(humain.Element(
                "action", trad("protéger la branche `{nom}` : y exiger la CI « {ci} » avant toute fusion", nom=nom,
                               ci=nom_de_la_ci(projet)),
                page_protection(projet) or ""))
        lignes += _balayage(projet, elements)
        if exigee:
            lignes.append(trad("branche  : {nom} — CI du socle exigée avant fusion{revue}", nom=nom, revue=revue))
        elif exigee is False:
            lignes.append(trad("branche  : {nom} — CI du socle NON exigée : une CI rouge n'empêche pas de fusionner",
                               nom=nom))
        else:
            lignes.append(trad("branche  : protection inconnue ({detail})", detail=detail))
        lignes += humain.texte(elements, plafond)
    except Exception as e:
        lignes.append(trad("ce qui revient à l'humain : incalculable ({erreur})", erreur=f"{type(e).__name__}: {e}"))
    try:
        from socle import human as humain

        faits = humain.fait_par_l_humain(projet)
        if faits:
            lignes.append(trad("écrit par l'humain lui-même depuis le dernier commit de l'agent : {n} — à lui "
                               "citer, avec le lien", n=len(faits)))
            lignes += _liste(faits, plafond, lambda e: [f"  {humain.genre(e)} : {e.quoi}", f"    {e.lien}"])
    except Exception as e:
        lignes.append(trad("ce que l'humain a écrit lui-même : incalculable ({erreur})",
                           erreur=f"{type(e).__name__}: {e}"))
    lignes += _hooks(racine)
    try:
        from socle import context as contexte

        lignes += contexte.bilan_adoption(projet)
    except Exception as e:
        lignes.append(trad("adoption : illisible ({erreur})", erreur=f"{type(e).__name__}: {e}"))
    from socle import private as prive

    lignes.append(prive.ligne_etat(projet))
    lignes += [l for bloc in supplement for l in str(bloc).strip("\n").splitlines()]
    lignes += backlog
    lignes.append(trad("vérifier : `python3 .socle/socle verify --fast` (tout : sans `--fast`)"))
    if not contenus:
        return "\n".join(lignes)
    etat = Partie("etat", [outils.raccourcir(l, LIGNE) for l in lignes],
                  lambda n, total: trad("{n} ligne(s) sur {total}, la fin : `python3 .socle/socle state --short`",
                                        n=n, total=total))
    return "\n".join(borner([etat, *parties_injectees(projet, mem)], projet.borne_demarrage()))


def _sans_entete(montrees: int, total: int) -> list[str]:
    return []


@dataclass
class Partie:
    """Une partie de la sortie du démarrage : le groupe dont elle partage la
    part de la borne (`PARTS`), ses lignes, ce que dit la coupe quand elle en
    retire `n` sur `total`, et son en-tête selon les lignes montrées."""

    groupe: str
    lignes: list[str]
    manque: Callable[[int, int], str]
    entete: Callable[[int, int], list[str]] = _sans_entete


# Les décisions que le démarrage injecte ; l'index entier se lit à la demande.
DERNIERES_DECISIONS = 10
# Ce que dit la ligne de coupe de chaque groupe.
GROUPES = {"etat": a_traduire("l'état dérivé"), "actif": a_traduire("le chantier actif"),
           "faits": a_traduire("les faits"), "decisions": a_traduire("les décisions")}


def ligne_de_titre(ident: str, titre: str, suffixe: str = "") -> str:
    """`ID — titre (suffixe)`, en `TITRE` octets au plus : le titre se
    raccourcit, l'identifiant et le suffixe restent."""
    debut = f"{ident} — "
    place = TITRE - len(debut.encode("utf-8")) - len(suffixe.encode("utf-8"))
    return debut + outils.raccourcir(titre, max(place, 3)) + suffixe


def parties_injectees(projet: config.Projet, mem: memoire.Memoire | None) -> list[Partie]:
    """Le chantier actif, public puis privé, entier ; les faits par leur
    titre, publics puis privés, le statut dit quand il n'est pas « mesuré » ;
    les dix dernières décisions, la plus récente d'abord, le statut dit
    quand elle n'est pas acceptée ; les titres raccourcis, les statuts dans
    la langue du projet. Une mémoire privée illisible ici n'en donne rien :
    l'état dérivé le dit plus haut."""
    from socle import language as langue

    racine, ch = projet.racine, projet.chemins
    lg = langue.du_projet(projet)
    res = []
    for chemin in (ch.actif, ch.dans_prive(ch.actif)):
        texte = outils.lire_a(racine, None, chemin)
        if not texte or not texte.strip() or (memoire.est_prive(chemin) and not memoire.lisible(texte)):
            continue
        res.append(Partie("actif", texte.rstrip().splitlines(),
                          lambda n, total, c=chemin: trad("la fin du chantier actif, {n} ligne(s) sur {total} : lire "
                                                          "{chemin}", n=n, total=total, chemin=c),
                          lambda montrees, total, c=chemin: ["", f"--- {c} ---"]))
    if mem is None:
        return res

    def statut(e: memoire.Entree, attendu: str) -> str:
        if e.statut == attendu:
            return ""
        table = langue.STATUTS.get(e.type, {})
        libelle = langue.mot(table, e.statut, lg) if e.statut in table else memoire.nettoyer(e.meta.get("statut", ""))
        return f" ({libelle})"

    for chemin in (ch.canonique, ch.dans_prive(ch.canonique)):
        f = mem.fichiers.get(chemin)
        faits = [e for e in (f.entrees if f else []) if e.type == "F" and not e.archivee and not e.basculee]
        if not faits:
            continue
        res.append(Partie(
            "faits", [ligne_de_titre(e.id, e.titre, statut(e, "mesure")) for e in faits],
            lambda n, total, c=chemin: trad("{n} fait(s) sur {total} : lire {chemin}", n=n, total=total, chemin=c),
            lambda montrees, total, c=chemin: ["", trad(
                "--- {chemin} : {n} fait(s) par leur titre ; un en entier : `python3 .socle/socle show F-NNNN` ---",
                chemin=c, n=montrees) if montrees == total else trad(
                "--- {chemin} : {n} fait(s) sur {total} par leur titre ; un en entier : `python3 .socle/socle show "
                "F-NNNN` ---", chemin=c, n=montrees, total=total)]))
    decisions = [e for e in mem.entrees("ADR") if not e.archivee and not e.basculee]
    if decisions:
        # Les plus récentes : par date, puis par numéro (une décision privée
        # a sa propre suite de numéros).
        decisions.sort(key=lambda e: (e.meta.get("date", ""), e.id.rsplit("-", 1)[-1], e.prive), reverse=True)
        nombre = len(decisions)
        res.append(Partie(
            "decisions", [ligne_de_titre(e.id, e.titre, statut(e, "acceptee"))
                          for e in decisions[:DERNIERES_DECISIONS]],
            lambda n, total: trad("{n} des {total} dernières décisions : `python3 .socle/socle show --index "
                                  "decisions`", n=n, total=total),
            lambda montrees, total: ["", trad(
                "--- la dernière décision sur {total} ; avant toute décision de conception, l'index entier : "
                "`python3 .socle/socle show --index decisions` ---", total=nombre) if montrees == 1 else trad(
                "--- les {n} dernières décisions sur {total}, la plus récente d'abord ; avant toute décision de "
                "conception, l'index entier : `python3 .socle/socle show --index decisions` ---",
                n=montrees, total=nombre)]))
    return res


def _octets(lignes: list[str]) -> int:
    """La taille, en octets UTF-8, de ces lignes imprimées, chacune suivie
    de son saut de ligne : les octets majorent les unités UTF-16 que
    compte Claude Code."""
    return sum(len(l.encode("utf-8")) + 1 for l in lignes)


def borner(parties: list[Partie], borne: int) -> list[str]:
    """Les parties, en `borne` octets au plus, sauts de ligne compris. Chaque
    groupe a sa part de la borne (`PARTS`) ; ce qu'un groupe laisse de sa
    part va à ceux qui dépassent la leur, dans l'ordre. Un groupe au-delà de
    ce qui lui revient perd des lignes entières depuis sa fin, un en-tête
    avec la dernière ligne qu'il annonce : jamais une partie ne mange la part
    d'une autre. Une dernière ligne dit ce qui est coupé, de quel groupe,
    sa taille pour sa part, et où lire le reste : jamais en silence, jamais
    au milieu d'une ligne. La place de cette ligne se prend sur les groupes
    coupés."""
    montrees = [len(p.lignes) for p in parties]
    groupes = list(dict.fromkeys(p.groupe for p in parties))
    membres = {g: [i for i, p in enumerate(parties) if p.groupe == g] for g in groupes}

    def taille(i: int) -> int:
        p, k = parties[i], montrees[i]
        return _octets(p.entete(k, len(p.lignes)) + p.lignes[:k]) if k else 0

    def taille_groupe(g: str) -> int:
        return sum(taille(i) for i in membres[g])

    def retirer(g: str) -> bool:
        """La dernière ligne montrée du groupe, dans sa dernière partie."""
        for i in reversed(membres[g]):
            if montrees[i]:
                montrees[i] -= 1
                return True
        return False

    def coupe(g: str) -> bool:
        return any(montrees[i] < len(parties[i].lignes) for i in membres[g])

    part = {g: int(borne * PARTS.get(g, 0)) for g in groupes}
    demande = {g: taille_groupe(g) for g in groupes}

    def segment(g: str) -> str:
        """Ce que la ligne de coupe dit du groupe : sa taille pour sa part,
        ce qui en est coupé, où le lire."""
        coupees = ", ".join(parties[i].manque(len(parties[i].lignes) - montrees[i], len(parties[i].lignes))
                            for i in membres[g] if montrees[i] < len(parties[i].lignes))
        return trad("{groupe}, {demande} octets pour une part de {part} — {coupees}",
                    groupe=trad(GROUPES.get(g, g)), demande=demande[g], part=part[g], coupees=coupees)

    def place(g: str) -> int:
        """Ce qu'occupe le groupe : ses lignes, et ce que la coupe dit de lui."""
        return taille_groupe(g) + (len(segment(g).encode("utf-8")) + len(" ; ") if coupe(g) else 0)

    permis = {g: min(demande[g], part[g]) for g in groupes}
    reste = borne - sum(permis.values())
    for g in groupes:
        plus = max(0, min(reste, demande[g] - permis[g]))
        permis[g] += plus
        reste -= plus
    for g in groupes:
        while place(g) > permis[g] and retirer(g):
            pass

    def note() -> list[str]:
        manque = [segment(g) for g in groupes if coupe(g)]
        if not manque:
            return []
        return [trad("!! coupé à la borne du démarrage ({borne} octets, `[startup] max_bytes` des garde-fous) : "
                     "{manque}", borne=borne, manque=" ; ".join(manque))]

    # Le début de la ligne de coupe, sur ce qui reste de la borne, ou sur les
    # groupes coupés, le dernier d'abord.
    while sum(taille(i) for i in range(len(parties))) + _octets(note()) > borne:
        if not any(retirer(g) for g in reversed(groupes) if coupe(g)) and \
                not any(retirer(g) for g in reversed(groupes)):
            break
    res = []
    for i, p in enumerate(parties):
        if montrees[i]:
            res += p.entete(montrees[i], len(p.lignes)) + p.lignes[:montrees[i]]
    fin = note()
    if fin:
        # Une borne plus petite que la ligne de coupe : elle, raccourcie à
        # ce qui reste.
        fin = [outils.raccourcir(fin[0], max(0, borne - _octets(res) - 1))]
    return res + fin


def audit_adaptateur(projet: config.Projet) -> list[str]:
    """L'audit de l'adaptateur, à chaque état : un langage dont le
    dépôt porte un fichier marqueur, et que l'adaptateur ne couvre pas, voit
    son code échapper aux capacités ; la décision revient à l'humain."""
    from socle import installer as installeur

    couverts = [str(a.donnees["language"]) for a in projet.adaptateurs if a.donnees.get("language")]
    if not couverts:
        return []
    couvert = ", ".join(couverts)
    presents = installeur.langages_presents(projet.hors_tiers(outils.fichiers_courants(projet.racine)))
    autres = {l: f for l, f in presents.items() if l not in couverts}
    if not autres:
        return []
    liste = ", ".join(f"{l} ({', '.join(f[:2])}{' …' if len(f) > 2 else ''})" for l, f in sorted(autres.items()))
    return [trad("adaptateur : !! langage(s) que l'adaptateur ({couvert}) ne couvre pas : {liste} — leurs tests, leur "
                 "compilation et leur mutation ne passent par aucune capacité ; le dire à l'humain par une demande "
                 "(un autre adaptateur, ou ces fichiers déclarés tiers)", couvert=couvert, liste=liste)]


def _git(racine, projet, borne: bool = False) -> list[str]:
    """Le commit, la base et ce qui n'y est pas fusionné, la CI ; avec
    `borne`, les commits plafonnés et leur sujet raccourci."""
    if not outils.est_depot(racine) or not outils.a_des_commits(racine):
        return [trad("commit   : aucun (dépôt neuf)")]
    res = []
    court = outils.git(racine, "rev-parse", "--short", "HEAD").strip()
    branche = outils.git(racine, "rev-parse", "--abbrev-ref", "HEAD").strip()
    sales = [l for l in outils.git(racine, "status", "--porcelain").splitlines() if l.strip()]
    propre = trad("arbre propre") if not sales else trad("ATTENTION, {n} fichier(s) non commité(s)", n=len(sales))
    res.append(trad("commit   : {sha} sur {branche} ({propre})", sha=court, branche=branche, propre=propre))
    defaut = outils.branche_par_defaut(racine)
    if defaut:
        non = outils.git(racine, "log", "--oneline", f"{defaut}..HEAD", check=False).splitlines()
        res.append(trad("base     : {defaut} — non fusionné : {n} commit(s)", defaut=defaut, n=len(non)))
        if outils.branche_par_defaut_devinee(racine):
            res.append(trad("  ^ devinée : ce clone n'a ni `origin/HEAD`, ni `main`, ni `master` ; si la branche par "
                            "défaut du dépôt distant est une autre, `git fetch origin <elle>` la fait connaître"))
        res += _liste(non, COMMITS_MONTRES if borne else None,
                      lambda l: [outils.raccourcir(f"  {l}", TITRE) if borne else f"  {l}"])
        base = outils.base_de_travail(racine)
        if base:
            changes = projet.hors_tiers(outils.fichiers_changes(racine, base))
            code = outils.filtrer(changes, projet.chemins_code())
            docs = [c for c in changes if c.endswith(".md")]
            mem = [c for c in changes if memoire.est_memoire(c)]
            res.append(trad("depuis la base : {code} fichier(s) de code, {docs} de doc, {memoire} de mémoire",
                            code=len(code), docs=len(docs), memoire=len(mem)))
            if code and not mem:
                res.append(trad("  ^ du code a changé et la mémoire non : la fin de tour le refusera"))
    else:
        res.append(trad("base     : aucune branche par défaut connue"))
    res.append(trad("CI       : {ci}", ci=_ligne_ci(racine, branche)))
    return res


def _memoire(mem: memoire.Memoire, projet) -> list[str]:
    faits = Counter(e.statut or "?" for e in mem.entrees("F") if not e.archivee)
    libelles = {"mesure": a_traduire("mesuré(s)"), "suppose": a_traduire("supposé(s)"),
                "refute": a_traduire("réfuté(s)"), "valide": a_traduire("validé(s)")}
    detail = ", ".join(f"{n} {trad(libelles[s]) if s in libelles else s}" for s, n in sorted(faits.items()))
    adrs = list(mem.entrees("ADR"))
    journal = sorted((e.id for e in mem.entrees("J")), key=lambda i: i.lstrip("P"))
    res = [
        trad("mémoire  : {faits} fait(s) ({detail}) · {adrs} décision(s) · journal : {journal} entrée(s), dernière "
             "{dernier}", faits=sum(faits.values()), detail=detail or trad("aucun"), adrs=len(adrs),
             journal=len(journal), dernier=journal[-1] if journal else "—")
    ]
    # L'index des décisions, que le cadrage prévoit, ne s'injecte plus en
    # entier : les dix dernières suivent les faits, et l'index se lit par
    # `socle show --index decisions`, qui en donne l'empreinte (ADR-0071).
    jours = projet.gf("staleness", "active_days", defaut=7)
    t = outils.git(mem.racine, "log", "-1", "--format=%ct", "--", config.FORMAT_ACTUEL.actif, check=False).strip() \
        if outils.a_des_commits(mem.racine) else ""
    if t:
        age = (time.time() - float(t)) / 86400
        if age > jours:
            res.append(trad("péremption : chantier actif inchangé depuis {age} jours (seuil {jours})",
                            age=f"{age:.0f}", jours=jours))
    return res


def _backlog(mem: memoire.Memoire, borne: bool = False) -> list[str]:
    """Le backlog : ses comptes, ce qui est en cours ou bloqué, et ce qui
    vient ensuite ; avec `borne`, chaque liste plafonnée et les titres
    raccourcis."""
    backlog = [e for e in mem.entrees("B") if not e.archivee]
    par = Counter(e.statut for e in backlog)
    res = [trad("backlog  : {ouverts} ouvert(s), {en_cours} en cours, {bloques} bloqué(s), {clos} clos",
                ouverts=par.get("ouvert", 0), en_cours=par.get("en-cours", 0), bloques=par.get("bloque", 0),
                clos=par.get("fait", 0) + par.get("abandonne", 0))]
    titre = TITRE_DE_SUJET if borne else None
    for statut, libelle in (("en-cours", a_traduire("en cours")), ("bloque", a_traduire("bloqué"))):
        res += _liste([e for e in backlog if e.statut == statut], PRETS_MONTRES if borne else None,
                      lambda e, l=libelle: [f"  {trad(l)} : {e.id} — "
                                            f"{outils.raccourcir(e.titre, titre) if titre else e.titre}"])
    res += [f"  {l}" for l in memoire.lignes_ordre(mem, plafond=PRETS_MONTRES if borne else None, titre=titre,
                                                    basses=BASSES_MONTREES if borne else None)]
    return res


def _demandes(racine, plafond: int | None = None) -> list[str]:
    """Le nombre des demandes en attente ; chacune se dit sous « ce qui
    revient à l'humain », avec son lien, et n'y compte pas deux fois : ici,
    seulement celles qui ne s'y disent pas, illisibles. Puis les demandes
    renvoyées."""
    toutes = demandes.toutes(racine)
    attente = [d for d in toutes if d.reponse is None and d.statut == "en attente"]
    res = [trad("demandes humaines en attente : {n} — chacune sous « ce qui revient à l'humain », avec son lien",
                n=len(attente)) if any(d.entree for d in attente) else
           trad("demandes humaines en attente : {n}", n=len(attente))]
    res += _liste([d for d in attente if not d.entree], plafond, lambda d: [f"  {d.chemin}"])
    res += _liste([d for d in toutes if d.statut == "renvoyée"], plafond, lambda d: [trad(
        "  RENVOYÉE (contexte insuffisant) : {id} — à réécrire en une demande qui la remplace", id=d.id)])
    return res


def _hooks(racine) -> list[str]:
    lignes = config.lire_trace(racine)
    if not lignes:
        return [trad("hooks    : aucune trace — ils n'ont encore jamais tiré dans ce clone")]
    dernier = " ".join(lignes[-1].split("\t")[:2])
    return [trad("hooks    : {n} déclenchement(s) tracé(s), dernier : {dernier}", n=len(lignes), dernier=dernier)]

