<!-- socle: couche=backlog zone=publique -->
# T-0221 — Le signal de la réserve : un besoin sans tri depuis quinze lots clos remonte à placer dans l'état, et la clôture d'un jalon exige la réserve retriée

> statut : fait · origine : J-2026-11-27-AO · besoin : B-0365 · lu : backlog@c0e72dd2 · après : T-0220 · ref : ce commit

Les deux autres moments de la règle de B-0365, sur le champ `trié` que
pose T-0220.

- L'état et la feuille de route calculent les besoins « à placer » : en
  réserve, sans raison, ou avec quinze lots clos ou plus d'un numéro
  supérieur à leur `trié` (sans `trié`, tous les lots clos comptent). Le
  compte repart à chaque tri, c'est-à-dire à chaque `trié` récrit. La
  ligne de l'état les nomme, bornée, et donne le `trié` à écrire.
- Un jalon clos dans la plage jugée (ouvert à la base, clos à la tête)
  exige que chaque besoin ouvert de la réserve ait sa raison et un `trié`
  au moins égal au plus haut lot clos : sinon `memoire.reserve` le
  refuse, et `socle close JA-NNNN` avec lui, par le mécanisme de
  l'ADR-0117 ; un besoin proposé à l'abandon reste en réserve, sa raison
  nommant la demande.
- Les textes : le skill `socle-batch` (trier les besoins à placer à la
  clôture d'un lot, retrier la réserve avant de clore un jalon),
  `engine/socle/FORMAT.md`, `engine/socle/HELP.md`, la section installée
  d'`AGENTS.md` si elle dit la naissance d'un besoin ; la note de version,
  française et anglaise, et le point du prompt de mise à jour de chess.

## Fait quand

- [x] un test montre un besoin à quinze lots clos depuis son tri signalé par l'état, et le même non signalé à quatorze, puis après un tri
- [x] un test montre la clôture d'un jalon refusée sur une réserve non retriée, et passant une fois la réserve retriée
- [x] le défaut injecté et le témoin sain de la clôture d'un jalon sont dans `engine/socle/selftest.py`
- [x] la note de version, française et anglaise, dit les trois moments
