<!-- socle: couche=backlog zone=publique -->
# B-0351 — L'agent ne peut pas supprimer une branche de travail distante déjà contenue dans une branche poussée : l'état la donne à l'humain à chaque fin de lot

> statut : ouvert · origine : J-2026-11-25-A · ref : D-0187, B-0193, ADR-0098, D-0198 · lu : backlog@5d842cca

Théo, le 24 novembre, devant la branche d'une session précédente que
l'état lui donnait à supprimer : « ça ne devrait pas être fait par
l'agent en vrai ? Pouvoir supprimer ses propres branches de travail ? »
(J-2026-11-24-BC). La politique range la suppression d'une branche
distante parmi les actions irréversibles ou externes, réservées à
l'humain (point 4), et le hook de l'agent la refuse. Une branche de
travail dont la tête est contenue dans une branche poussée, ou dans la
branche par défaut, ne perd pourtant rien à disparaître : l'état le
calcule déjà, et la donne à l'humain après chaque passation et chaque
fusion. Après la mise à jour de chess, sur la décision de Théo (D-0187).

Une spécification d'abord, avec son modèle de menace : ce qu'est une
branche « de l'agent », ce qui prouve qu'elle est contenue ailleurs au
moment de la supprimer, ce que le hook laisse passer et ce qu'il refuse
encore ; puis le changement de la politique, que Théo seul fait. Le hook
de l'agent ne change que sur une preuve vue en session (ADR-0098) : la
voici, la branche donnée à Théo à chaque fin de lot (B-0193,
J-2026-11-24-BC).

Le 25 novembre, Théo le passe avant la mise à jour de chess (D-0198),
au lieu d'après (D-0187) : la gêne revient à chaque passation, et chess
la reçoit corrigée dans sa seule mise à jour. B-0323 l'attend.

## Satisfait quand

- [ ] une branche de travail de l'agent, contenue dans une branche poussée, se supprime sans geste de l'humain, et une branche qui ne l'est pas reste refusée
