<!-- socle: couche=backlog zone=publique -->
# B-0360 — La fin de tour prend le nom d'une commande du socle, cité entre accents graves dans « Pour toi », pour une branche à supprimer absente de l'origine

> statut : fait · origine : J-2026-11-26-AA · ref : B-0323, B-0311, J-2026-11-26-AH · lu : backlog@dd11ac18

La gêne 5 de la mise à jour de chess du 26 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-26.md`) : une ligne de
« Pour toi » qui dit de supprimer une branche et cite `prune-branches`
entre accents graves fait refuser la fin de tour, ce nom étant lu comme
une branche que l'origine n'a plus (`links.branches_a_supprimer_citees`,
B-0311). L'agent doit récrire un récap juste.

## Modèle de menace

Écrit à la revue de L-0046, après le code : le lot l'avait omis.

Le garde-fou qui change : le refus de la fin de tour dont « Pour toi »
donne à supprimer une branche que l'origine n'a plus (B-0311, D-0178).
Ce qu'il arrête : un récap qui fait faire à l'humain un geste vain, sur
une branche reprise d'un récap d'avant sans la vérifier. Ce qui reste
arrêté : tout nom entre accents graves qui n'est pas celui d'une
commande du socle. Ce qui passe désormais : une branche réelle qui
porterait le nom d'une commande (`review`, `state`, `ci`…), donnée à
supprimer sans être vérifiée sur l'origine ; les branches d'une session
d'agent se nomment autrement (`ccr-…`, `claude/…`), et l'humain qui
cherche une telle branche absente ne perd qu'un geste.

## Satisfait quand

- [x] une ligne de « Pour toi » qui cite une commande du socle à côté d'une branche à supprimer ne fait refuser la fin de tour que pour la branche
