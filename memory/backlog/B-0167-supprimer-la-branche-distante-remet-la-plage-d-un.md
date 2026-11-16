<!-- socle: couche=backlog zone=publique -->
# B-0167 — Supprimer la branche distante remet la plage d'un push à la branche par défaut : ce qui a été poussé peut se réécrire sans que le contrôle le voie

> statut : ouvert · origine : J-2026-11-11-G · lu : backlog@6c37c58c

Le hook avant push juge la plage qui part contre la branche distante ;
une branche absente se juge contre la branche par défaut. Supprimer la
branche distante efface donc ce repère : une décision, une entrée de
journal ou la valeur attendue d'un test, poussées puis réécrites, repartent
comme neuves. Théo l'a relevé le 11 novembre (J-2026-11-11-G) : « on peut écrire un
test qui n'existe pas dans main, le pousser, supprimer la branche,
l'affaiblir localement et le repousser ». Seul l'humain peut supprimer la
branche, mais l'agent peut le lui demander. La CI de la pull request, elle,
juge toujours contre la branche par défaut, où un test neuf de la pull
request n'a pas de valeur attendue antérieure.

Pistes : garder en local le dernier commit poussé de chaque branche, et en
juger la plage quand la branche distante a disparu sans fusion ; ou dire,
dans le refus du push, que la suppression de la branche n'est pas une
issue.

## Satisfait quand

- [ ] le « Fait quand » de T-0018 est tenu
