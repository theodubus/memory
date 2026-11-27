<!-- socle: couche=backlog zone=publique -->
# L-0053 — Lot — la clôture d'une tâche en un geste

> statut : fait · origine : J-2026-11-27-AB · après : L-0052, T-0214 · lu : backlog@f10e1061 · ref : ce commit

Le deuxième lot de ce que D-0235 retient (point 12) : la clôture d'une
tâche en un geste, T-0214 seule. Elle touche le contrôle du backlog
(`engine/socle/checks_memory.py`), le rangement
(`engine/socle/archive.py`), la commande (`engine/socle/cli.py`), le
format, le guide, le skill `socle-batch` et le gabarit d'`AGENTS.md`.
Environ 150 lignes de code et de tests : une revue adversariale.

## Revues

### Passe 1 — 2026-11-27

Commits : 67546e33..1ab291d3
- Bloquant : la clôture du lot ne rangeait plus les consignes levées
- Bloquant : socle close écrasait et effaçait un fichier à sa place
- Ouvre : rien
