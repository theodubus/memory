"""Le mariage avec BMAD Method (ADR-0032) : ce que le socle garde de ce que
BMAD produit, sans le recopier.

- `bmad.reports` : un travail que BMAD reporte (sa liste des travaux
  reportés) entre au backlog du socle, la seule liste des trouvailles ;
  `socle bmad-import` l'y fait entrer, et le report s'y reconnaît à son
  empreinte.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from socle import bmad, config, language as langue, memory as memoire, utils as outils
from socle.context import controle
from socle.messages import trad

TITRE_MAX = 100


def reports_entres(mem: memoire.Memoire) -> set[str]:
    """Les empreintes des reports de BMAD déjà entrés au backlog, ouverts ou
    clos."""
    return {e.meta["report"].strip() for e in mem.entrees("B") if e.meta.get("report")}


def reports_a_entrer(projet: config.Projet, mem: memoire.Memoire, rev: str | None = None) -> list[bmad.Report]:
    if not bmad.present(projet.racine, rev):
        return []
    texte = outils.lire_a(projet.racine, rev, bmad.fichier_des_reports(projet.racine, rev))
    if not texte:
        return []
    entres = reports_entres(mem)
    vus, res = set(), []
    for r in bmad.reports(texte):
        if r.empreinte not in entres and r.empreinte not in vus:
            vus.add(r.empreinte)
            res.append(r)
    return res


def _titre(resume: str) -> str:
    resume = " ".join(resume.split()).rstrip(".")
    if len(resume) <= TITRE_MAX:
        return resume
    coupe = resume[:TITRE_MAX].rsplit(" ", 1)[0]
    return coupe + " …"


def importer(projet: config.Projet) -> list[tuple[str, str]]:
    """Fait entrer au backlog chaque report de BMAD qui n'y est pas : un sujet
    ouvert par report, qui cite sa source sans recopier la spec. Rend les
    identifiants et les chemins posés."""
    from socle import identifiers as identifiants, private as zone_privee

    racine = projet.racine
    mem = memoire.Memoire.charger(racine)
    a_entrer = reports_a_entrer(projet, mem)
    if not a_entrer:
        return []
    ch = projet.chemins
    lg = langue.du_projet(projet)
    prive = "backlog" in zone_privee.couches_privees(projet)
    if prive:
        acces = zone_privee.acces(projet, mem.illisibles)
        if not acces.disponible:
            raise RuntimeError(trad("refus : mémoire privée indisponible ({raison}) ; une entrée privée ne "
                                    "s'écrit pas à l'aveugle", raison=acces.raison))
    zone = "privee" if prive else "publique"
    dossier = racine / (ch.dans_prive(ch.backlog) if prive else ch.backlog)
    source = bmad.fichier_des_reports(racine)
    jour = date.today().isoformat()
    res = []
    for r in a_entrer:
        ident = mem.prochain_id("B", prive=prive, date=jour, pris_ailleurs=identifiants.pris_ailleurs(racine, "B"))
        titre = _titre(r.resume) or r.empreinte
        lu = memoire.empreinte_index(mem, "backlog")
        meta = langue.meta(lg, "B", statut="ouvert", origine=langue.ref_fichier(source, lg), report=r.empreinte,
                           lu=f"backlog@{lu}")
        corps = langue.mot(langue.TEXTES, "report-bmad", lg).format(source=r.source or "?", resume=r.resume)
        if r.preuve:
            corps += "\n\n" + r.preuve
        chemin = dossier / f"{ident}-{memoire.nom_de_fichier(titre)}.md"
        outils.ecrire(chemin, f"{langue.entete_fichier('backlog', zone, lg)}\n# {ident} — {titre}\n\n{meta}\n\n"
                              f"{corps}\n")
        res.append((ident, chemin.relative_to(racine).as_posix()))
        mem = memoire.Memoire.charger(racine)
    return res


@controle("bmad.reports", etages=("agent", "git", "ci"))
def reports(ctx, r):
    """Un travail que BMAD reporte entre au backlog du socle (ADR-0032) : une
    seule liste des trouvailles, que le socle suit et clôt."""
    if not bmad.present(ctx.racine, ctx.tete):
        return
    for rep in reports_a_entrer(ctx.projet, ctx.memoire, ctx.tete):
        r.erreur("bmad.reports",
                 trad("travail reporté par BMAD, absent du backlog : « {resume} » — le faire entrer : `python3 "
                      ".socle/socle bmad-import`", resume=_titre(rep.resume)),
                 bmad.fichier_des_reports(ctx.racine, ctx.tete))
