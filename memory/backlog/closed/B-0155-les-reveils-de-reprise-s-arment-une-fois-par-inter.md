<!-- socle: couche=backlog zone=publique -->
# B-0155 — Les réveils de reprise s'arment une fois par intervention, au lieu d'être réécrits à chaque étape

> statut : fait · origine : J-2026-11-10-N · lu : backlog@ce9f9642 · ref : J-2026-11-11-C

Le skill de reprise fait réécrire les deux réveils à chaque étape et à
chaque sous-agent : deux appels, et plusieurs kilo-octets de réponse, à
chaque fois (constat 2 de la passe de recul, D-0093@333ad9d0, proposition 1). Les
armer une fois par intervention, avec le lot : la mémoire et git disent
où en est le travail. Un réveil armé à une heure déjà passée s'est aussi
déclenché à tort deux fois le 10 novembre : ne jamais l'armer ainsi.

## Satisfait quand

- [x] le skill arme les réveils une fois par intervention, ne les récrit qu'au lancement d'un sous-agent, et ne les arme jamais dans le passé
