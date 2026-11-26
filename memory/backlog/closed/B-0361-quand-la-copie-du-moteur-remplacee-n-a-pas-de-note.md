<!-- socle: couche=backlog zone=publique -->
# B-0361 — Quand la copie du moteur remplacée n'a pas de notes de version, l'installeur les imprime toutes en entier, 122 entrées et 100 Ko chez chess

> statut : fait · origine : J-2026-11-26-AA · ref : B-0323, ADR-0078, J-2026-11-26-AH · lu : backlog@dd11ac18

La gêne 7 de la mise à jour de chess du 26 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-26.md`) : la copie du
13 novembre précédait les notes de version (ADR-0078) ; l'installeur a
imprimé les 122 entrées, environ 100 Ko, que l'agent relit. Tout projet
mis à jour pour la dernière fois avant le 14 novembre y passera à sa
prochaine mise à jour, et chacune en ajoute.

## Satisfait quand

- [x] la mise à jour d'une copie sans notes n'imprime en entier que les notes datées du jour de cette copie ou d'après, les autres par leur titre seul
