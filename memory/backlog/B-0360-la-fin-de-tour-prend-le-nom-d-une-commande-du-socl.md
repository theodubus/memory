<!-- socle: couche=backlog zone=publique -->
# B-0360 — La fin de tour prend le nom d'une commande du socle, cité entre accents graves dans « Pour toi », pour une branche à supprimer absente de l'origine

> statut : ouvert · origine : J-2026-11-26-AA · ref : B-0323, B-0311 · lu : backlog@dd11ac18

La gêne 5 de la mise à jour de chess du 26 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-26.md`) : une ligne de
« Pour toi » qui dit de supprimer une branche et cite `prune-branches`
entre accents graves fait refuser la fin de tour, ce nom étant lu comme
une branche que l'origine n'a plus (`links.branches_a_supprimer_citees`,
B-0311). L'agent doit récrire un récap juste.

## Satisfait quand

- [ ] une ligne de « Pour toi » qui cite une commande du socle à côté d'une branche à supprimer ne fait refuser la fin de tour que pour la branche
