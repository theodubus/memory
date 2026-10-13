<!-- socle: couche=backlog zone=publique -->
# B-0053 — Deux branches parallèles calculent les mêmes identifiants

> statut : fait · origine : J-2026-10-12-Q · lu : backlog@4f28165c · ref : J-2026-10-13-R

Mesuré à R6 : cinq branches parties du même commit ont chacune pris
`B-0001` et `J-2026-10-12-C` pour des entrées différentes ; leur fusion les
heurtera. `socle new` calcule l'identifiant sur l'arbre de la branche, qui
ne voit pas les autres. À trancher avec B-0047 (un fichier par sujet) :
numéroter à la fusion, ou des identifiants que deux branches ne peuvent pas
prendre ensemble.
