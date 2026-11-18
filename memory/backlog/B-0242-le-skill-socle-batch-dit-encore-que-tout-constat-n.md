<!-- socle: couche=backlog zone=publique -->
# B-0242 — Le skill socle-batch dit encore que tout constat non bloquant va au backlog, contre la règle 1 de D-0112

> statut : ouvert · origine : J-2026-11-15-K · lu : backlog@90ff4f28

La revue du lot 5 (J-2026-11-15-K), constat pour le backlog 2. Le
gabarit du skill `socle-batch`, en français et en anglais
(`engine/socle/templates/skills/socle-batch/SKILL.md`, section « La
revue, avant tout push »), dit encore qu'un bloquant retourne à son
implémenteur et que « le reste va au backlog » : la règle d'avant
D-0112. Le skill `socle-review` et les instructions des projets
écartent désormais un constat exotique dont l'effet est rattrapé, et un
constat infondé. Un agent qui suit `socle-batch` remplit le backlog, ce
que D-0111 et D-0112 voulaient arrêter. La copie protégée de ce dépôt
suit par une demande, avec celles de B-0218.

## Satisfait quand

- [ ] un agent qui suit `socle-batch` trie les constats de la revue comme `socle-review` : un constat exotique et rattrapé, ou infondé, ne va plus au backlog
