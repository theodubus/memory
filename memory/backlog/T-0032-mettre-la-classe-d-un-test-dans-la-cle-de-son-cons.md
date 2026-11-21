<!-- socle: couche=backlog zone=publique -->
# T-0032 — La classe d'un test dans la clé de son constat toléré, lue par la structure du fichier, langage par langage

> statut : ouvert · origine : J-2026-11-12-H · besoin : B-0192 · lu : backlog@9966bbbd

Un commit, seulement si un projet en a montré le besoin : une lecture de la structure du fichier par l'adaptateur de chaque langage, pas une expression régulière (ADR-0070). Sans projet qui en a besoin, la tâche s'abandonne en renvoyant au besoin.

Le 21 novembre, Théo le fait passer à JA-0006 (D-0153,
J-2026-11-21-O) : il se juge à la mise à jour de chess.

## Fait quand

- [ ] dans chaque langage qui la lit, deux tests de même nom dans deux classes d'un même fichier ont deux clés, et un test le montre
- [ ] la clé d'un constat déjà toléré ne change pas, et un test le montre
