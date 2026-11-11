<!-- socle: couche=backlog zone=publique -->
# B-0170 — L'audit d'initialisation pose un fait par workflow et appelle CI ce qui n'en est pas

> statut : fait · origine : ADR-0059 · ref : J-2026-11-11-U · lu : backlog@276f501a

L'essai à blanc sur chess (`docs/fabrication/chess/essai-a-blanc-2026-11-11.md`, partie 2) : onze des quatorze faits de
l'audit sont « une CI GitHub existe », un par workflow, dont sept ne sont
pas des CI (lancés à la main, ou planifiés). Ils sont relus à chaque
session.

## Fait quand

- [x] les workflows d'un projet tiennent en un fait, qui distingue ceux qui jugent un push ou une pull request des autres
