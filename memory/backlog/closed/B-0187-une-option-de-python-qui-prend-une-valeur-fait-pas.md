<!-- socle: couche=backlog zone=publique -->
# B-0187 — Une option de python qui prend une valeur fait passer au hook une réponse donnée à la place de l'humain

> statut : fait · origine : J-2026-11-12-A · priorité : haute · lu : backlog@aa97dfa8 · ref : J-2026-11-12-C

Trouvé par la revue adversariale du lot de B-0184, hors de son diff : le
hook de l'agent laisse passer `python3 -W ignore .socle/socle answer
D-0001 oui`, et de même avec `-X utf8`. Pour reconnaître une commande du
socle, `arguments_socle` (`engine/socle/hooks.py`) retire les options de
python une à une, mais pas leur valeur (`ignore`, `utf8`) : il ne trouve
plus le lanceur, et ne juge pas la commande. C'est une vraie réponse
donnée à la place de l'humain, ce que le hook existe pour refuser ; le
défaut précède le lot.

## Fait quand

- [x] une commande du socle lancée avec une option de python qui prend une valeur est reconnue et jugée comme sans elle : `answer` sans `--relayed` ni citation est refusé ; un test et un défaut de l'auto-test le montrent
