<!-- socle: couche=backlog zone=publique -->
# B-0356 — En session cloud, la branche qu'une session repousse après la fusion de sa pull request reste sur l'origine, et le proxy refuse à la session suivante de la supprimer : elle revient à l'humain

> statut : ouvert · origine : J-2026-11-26-J · ref : D-0205, J-2026-11-26-H, B-0351, ADR-0114, D-0206 · lu : backlog@99a18fbc

La commande `socle prune-branches` (ADR-0114) supprime les branches de
l'agent déjà contenues ailleurs ; dans une session cloud de Claude Code,
le proxy ne laisse pousser la session que sur sa propre branche, et
refuse la suppression d'une autre (HTTP 403, vu le 26 novembre,
J-2026-11-26-H) : la branche revient à l'humain, avec la raison du refus.
Théo l'accepte pour clore B-0351 et ouvre ce besoin, hors du jalon de
chess (D-0205) ; le même jour, il le passe avant la mise à jour de chess,
dans JA-0006 (D-0206). La consigne C-0025@76701895 reste en vigueur
après lui : une branche d'une ancienne session peut encore rester, pour
une raison ou une autre (Théo, J-2026-11-26-P).

GitHub supprime déjà la branche d'une pull request à sa fusion. Celle qui
reste est celle qu'une session repousse après la fusion, pour écrire sa
passation, comme `ccr-5ee489f7-ukpvc6` le 25 novembre et
`ccr-0451fbf2-5mg4au` le 26 (J-2026-11-26-J) : au prompt à copier, chaque
session neuve a sa branche, et ne peut pas supprimer celle d'avant. En
session programmée, la session suivante reprend la même branche, et rien
ne reste. Pistes, la conception n'étant pas tranchée : une passation qui
ne repousse pas la branche après la fusion, ou la session programmée
seule en cloud ; sa question d'intention se pose à Théo à l'ouverture de
son lot.

La première se tient vraisemblablement (J-2026-11-26-L) : écrite dans le
dernier commit de la pull request, avant sa fusion, la passation arrive
sur `main`, où `handoff check` la trouve, et la branche que GitHub
supprime à la fusion ne se repousse plus. À éprouver : le hook de fin de
tour de la session cloud, qui a fait repousser la branche après la fusion
le 26 novembre (J-2026-11-26-J).

## Satisfait quand

- [ ] après la fusion d'une pull request et la passation d'une session cloud, aucune branche de session ne revient à l'humain à supprimer
