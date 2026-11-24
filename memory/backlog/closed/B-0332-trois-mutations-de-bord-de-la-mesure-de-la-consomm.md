<!-- socle: couche=backlog zone=publique -->
# B-0332 — Trois mutations de bord de la mesure de la consommation survivent aux tests : deux relevés égaux au centième, et la conversation principale comptée parmi les sous-agents

> statut : abandonné · origine : J-2026-11-22-Q · priorité : basse · lu : backlog@3a8162c0 · ref : D-0168

La revue de L-0009 (J-2026-11-22-Q), constat 2 pour le backlog. Trois
mutations de `engine/socle/consumption.py`, hors des branches que nommait
B-0194, survivent aux tests : dans `_segments`, `r1[1] < r0[1]` devenu
`<=` ; dans `points_de_semaine`, `b[1] < a[1]` devenu `<=` ; dans
`concurrence`, le filtre `not c.sous_agent` retiré, qui compte la
conversation principale parmi les sous-agents. Deux relevés égaux au
centième se suivent souvent : une régression en `<=` couperait sans
bruit des suites de relevés, et l'étalonnage perdrait des intervalles.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X6 — de la mesure dont aucune décision ne dépend » : trois mutations de bord de la mesure de la consommation. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] une mutation de ces trois bords de la mesure de la consommation ne passe plus inaperçue
