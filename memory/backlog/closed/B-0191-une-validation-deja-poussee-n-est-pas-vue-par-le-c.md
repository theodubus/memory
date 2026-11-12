<!-- socle: couche=backlog zone=publique -->
# B-0191 — Une validation déjà poussée n'est pas vue par le contrôle d'avant push, qui ne juge que ce qui part

> statut : fait · origine : J-2026-11-12-H · ref : J-2026-11-12-L · lu : backlog@d439d914

Le 12 novembre, la validation de Théo sur une valeur attendue (D-0104) a
été commitée et poussée seule, avant le changement qu'elle autorise. Le
contrôle d'avant push ne juge que la plage qui part, depuis la pointe
distante de la branche : il a vu la valeur attendue changée, pas la
validation, et a refusé (`tests.attendus`). La CI de la pull request, qui
juge depuis la branche par défaut, l'aurait acceptée. Il a fallu consigner
la même réponse une seconde fois (D-0105) ; la veille, de même pour des
fichiers protégés (D-0103). `socle answer` dit bien de commiter la réponse
« avec la suite », mais un ordre de commits ne devrait pas décider d'un
refus.

Piste : pour une validation, comme pour les renommages des clés de
l'adoption (B-0189), lire depuis la branche par défaut plutôt que dans la
seule plage qui part.

## Fait quand

- ~~une validation de l'humain déjà poussée sur la branche, absente de la branche par défaut, compte avant le push comme elle compte en CI, pour une valeur attendue comme pour un fichier protégé ; un test le montre~~ — doublon de B-0142, qui porte ce critère
