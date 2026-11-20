<!-- socle: couche=backlog zone=publique -->
# B-0301 — Le skill socle-resume ne dit pas quoi faire des réveils qu'une session archivée du même dépôt a laissés sur le même lot

> statut : ouvert · origine : J-2026-11-19-AI · lu : backlog@c8897434

Vu en ouvrant L-0019 le 19 novembre (J-2026-11-19-AI). Théo avait lancé
une session sur le lot, puis une seconde, avant que la précédente ait
fini de fusionner ; la première, archivée, avait déjà armé ses deux
réveils de reprise, sur sa propre branche et pour le même lot. Le skill
`socle-resume` interdit de toucher au réveil d'une autre session, et ne
dit rien de plus : la session neuve les a vus dans `list_triggers` sans
pouvoir les retirer, et Théo ne savait pas où les annuler. À sa
demande, la session neuve les a désactivés (`update_trigger`,
`enabled: false`). Laissés, ils auraient tiré dans une session archivée,
dont la vérification du réveil aurait conclu de ne pas reprendre, au
prix d'un peu d'usage.

La piste : au début du tour, un réveil de ces deux noms et de ce dépôt
dont la session est archivée (`get_session`, `SESSION_STATUS_ARCHIVED`)
se dit à l'humain, avec ses heures, et ne se désactive qu'à sa demande ;
le skill le dit, et dit où l'humain les retrouve lui-même.

## Satisfait quand

- [ ] une session qui trouve les réveils de reprise d'une session archivée du même dépôt le dit à l'humain et ne les désactive qu'à sa demande, comme le skill `socle-resume` le décrit
