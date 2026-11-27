<!-- socle: couche=backlog zone=publique -->
# L-0056 — Lot — la réserve triée à ses trois moments, et la mise à jour de chess rejouée

> statut : en cours · origine : J-2026-11-27-AO · lu : backlog@c0e72dd2 · après : L-0055, T-0220, T-0221, T-0222, T-0223, T-0224

Le cinquième lot de JA-0006 dans l'ordre de D-0235, point 12 : le tri de
la réserve (B-0365, sous la condition du point 8 : ni appel ni refus de
plus), puis la mise à jour de chess rejouée par un test (B-0368), avant
le prochain prompt de chess. T-0220 et T-0221 touchent `engine/socle/`
(`cli.py`, `checks_memory.py`, `state.py`, `roadmap.py`, `memory.py`,
`selftest.py`, les textes) ; T-0222 la mémoire de ce dépôt ; T-0223 un
test neuf dans `tests/`. Le lot pose un garde-fou : revue adversariale.

## Revues

### Passe 1 — 2026-11-27

Commits : c198fba7..7b52c2d3

- Bloquant : clore un jalon dans la séance de son dernier besoin coûtait un refus, la ligne « jalons à clore » ne se lisant qu'au démarrage
- Bloquant : en mémoire privée, memoire.reserve prenait un besoin privé d'avant pour nouveau, la base publique ne lisant pas la zone privée
- Ouvre : rien
