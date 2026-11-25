<!-- socle: couche=backlog zone=publique -->
# T-0180 — La spécification de la reprise sur « reprends » seul, sur les propositions retenues par D-0177, soumise à Théo

> statut : ouvert · origine : J-2026-11-24-BC · besoin : B-0346 · ref : D-0185, D-0177, D-0174 · lu : backlog@2156ec15

Un commit : une demande soumet à Théo la spécification de B-0346, qui
change celle de la passation programmée validée par D-0174 : la session
qui part écrit sa passation dans le dépôt (sa garde, le lot, ce qui
attend), et la session neuve la lit au démarrage et lance la garde sur
« reprends » seul, d'un compte comme d'un autre. Elle part des trois
propositions retenues par D-0177 (la tête de la garde, le dernier commit
qui écrit la passation ; la passation retirée par le premier commit de
la session neuve ; sans passation, « reprends » fait ce que fait une
session neuve), et dit ce que devient `socle handoff prompt`, ce que dit
l'état, et la tâche programmée de la session programmée. Puis les tâches
qui l'appliquent, sur sa réponse.

## Fait quand

- [ ] une demande soumet la spécification à Théo, et sa réponse est consignée au journal
