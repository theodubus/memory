<!-- socle: couche=backlog zone=publique -->
# B-0335 — Une tâche qu'une revue ouvre reste hors de tout lot quand aucun lot formé ne lui applique sa règle : le jalon ne se clôt plus à la fin de ses lots

> statut : ouvert · origine : J-2026-11-23-D · lu : backlog@f95c1458

La revue de cap 3 (J-2026-11-23-D) : cinq tâches de JA-0005, nées des
revues de L-0021 et de L-0009, n'étaient dans aucun lot, et la fiche du
jalon disait le contraire. Le skill `socle-batch` et AGENTS.md font
rejoindre à une tâche ouverte ensuite le prochain lot dont la règle
s'applique, sans dire quoi faire quand aucun ne s'applique. Théo retient
la suggestion (D-0158) : à chaque clôture, ce qu'une revue ouvre se place
dans un lot, ou en forme un.

## Satisfait quand

- [ ] le gabarit du skill `socle-batch` dit où va une tâche ouverte qu'aucun lot formé ne prend : un lot nouveau dans le jalon de son besoin, formé à la clôture du lot qui l'a ouverte
