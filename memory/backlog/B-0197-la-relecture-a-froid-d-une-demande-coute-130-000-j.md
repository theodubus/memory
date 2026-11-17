<!-- socle: couche=backlog zone=publique -->
# B-0197 — La relecture à froid d'une demande coûte 130 000 jetons

> statut : ouvert · origine : J-2026-11-13-D · lu : backlog@43666d5c

Relevé à la mise à jour du socle sur chess, le 13 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-13.md`, gêne 7).

La relecture à froid d'une demande avant de la poser (ADR-0046), faite par
un sous-agent sans contexte, a coûté 131 786 jetons et 69 s pour une
demande de mise à jour. C'est l'ordre de grandeur d'une revue de lot :
mesurer ce que lit le relecteur (le dépôt entier, AGENTS.md, les entrées
citées), et borner ce qu'il reçoit, comme B-0173 l'a fait pour la revue
d'un lot (`docs/fabrication/consommation.md`).

## Satisfait quand

- [ ] le « Fait quand » de T-0034 est tenu
