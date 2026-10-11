"""Archivage : ce qui sort d'une couche bornée part dans le journal, avec son
identifiant, pour que toute référence vers lui reste vivante."""

from __future__ import annotations

from datetime import date

from socle import config, memoire


def archiver_backlog(projet: config.Projet) -> int:
    racine = projet.racine
    ch = config.chemins(racine)
    chemin = racine / ch.backlog
    if not chemin.is_file():
        print("pas de backlog")
        return 0
    texte = chemin.read_text(encoding="utf-8")
    f = memoire.analyser(ch.backlog, texte)
    clos = [e for e in f.entrees if e.type == "B" and e.statut in memoire.BACKLOG_CLOS and e.refs("ref")]
    if not clos:
        print("aucun sujet clos à archiver")
        return 0
    jour = date.today().isoformat()
    mem = memoire.Memoire.charger(racine)
    ident = mem.prochain_id("J", date=jour)
    blocs = []
    for e in clos:
        # Le sujet descend d'un niveau : il devient un sous-titre de l'entrée.
        lignes = e.texte.splitlines()
        lignes[0] = "#" * (e.niveau + 1) + lignes[0][e.niveau:]
        blocs.append("\n".join(lignes))
        texte = texte.replace(e.texte, "", 1)
    texte = "\n".join(l for l in _sans_vides_multiples(texte.splitlines())).rstrip("\n") + "\n"
    chemin.write_text(texte, encoding="utf-8")
    journal = racine / ch.journal / f"{jour[:7]}.md"
    if not journal.is_file():
        journal.parent.mkdir(parents=True, exist_ok=True)
        journal.write_text(f"<!-- socle: couche=journal zone=publique -->\n# Journal — {jour[:7]}\n", encoding="utf-8")
    ids = ", ".join(e.id for e in clos)
    entree = f"\n## {ident} — Backlog clos archivé : {ids}\n\n" + "\n\n".join(blocs) + "\n"
    journal.write_text(journal.read_text(encoding="utf-8").rstrip("\n") + "\n" + entree, encoding="utf-8")
    print(f"{len(clos)} sujet(s) archivé(s) dans {ident} ({journal.relative_to(racine)})")
    return 0


def _sans_vides_multiples(lignes):
    vide = False
    for l in lignes:
        if not l.strip():
            if vide:
                continue
            vide = True
        else:
            vide = False
        yield l
