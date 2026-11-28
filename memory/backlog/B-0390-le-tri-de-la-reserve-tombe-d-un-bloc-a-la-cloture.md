<!-- socle: couche=backlog zone=publique -->
# B-0390 — Le tri de la réserve tombe d'un bloc à la clôture d'un lot, et revient en bloc quinze lots plus tard

> statut : ouvert · origine : J-2026-11-28-D · ref : ADR-0118, D-0213 · priorité : basse · lu : backlog@68df6bf7

Le constat 7 du relevé d'après de chess
(`docs/fabrication/chess/cout-et-frictions-2026-11-28.md`). À la clôture
d'un lot ordinaire, l'état demandait de ranger 30 besoins « à placer »
d'un coup, un geste plus gros que le lot lui-même, reporté faute de
budget.

Le bloc vient surtout des besoins de chess d'avant ADR-0118, sans raison :
une fois. Mais un tri entier donne à tous le même `trié`, et l'état les
redit tous ensemble quinze lots clos plus tard (`a_placer` de
`engine/socle/memory.py`) : le bloc revient. Le tri entier que la
clôture d'un jalon exige (D-0213) ne change pas.

## Satisfait quand

- [ ] à la clôture d'un lot, l'état ne demande de trier que quelques besoins de la réserve, les plus anciens d'abord, et un test le montre sur une réserve de trente
- [ ] un tri réparti sur plusieurs lots ne fait pas revenir la réserve en un seul bloc
