<!-- socle: couche=backlog zone=publique -->
# B-0184 — Le hook de l'agent refuse l'aide de socle decision et de socle answer

> statut : ouvert · origine : J-2026-11-12-A · lu : backlog@df54a26c

À l'installation sur chess (`docs/fabrication/chess/installation-2026-11-12.md`, point 6) : le hook de l'agent refuse
`socle decision --help` et `socle answer --help`, comme une réponse donnée
à la place de l'humain. Pour connaître leurs arguments, l'agent de chess a
lu le code ; la session du socle a buté sur le même refus le 11 novembre.

## Fait quand

- [ ] l'aide de ces commandes passe, et rien de plus : une réponse sans `--relayed` ni citation reste refusée ; un test le montre
