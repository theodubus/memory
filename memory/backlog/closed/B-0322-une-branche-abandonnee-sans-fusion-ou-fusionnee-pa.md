<!-- socle: couche=backlog zone=publique -->
# B-0322 — Une branche abandonnée sans fusion, ou fusionnée par écrasement, repartie sous le même nom dans le même clone, est refusée au push sans que le refus ni ADR-0104 disent une sortie qui marche en session cloud

> statut : abandonné · ref : ADR-0098, D-0156, J-2026-11-22-A · origine : J-2026-11-20-AR · ref : ADR-0104, B-0167, T-0018, B-0320 · lu : backlog@689e597f

La revue de L-0020 (J-2026-11-20-AR) l'a éprouvé : une pull request
fermée sans fusion, sa branche distante supprimée, puis la branche
repartie de la branche par défaut sous le même nom, dans le même clone,
est refusée au push suivant (`tests.attendus` pour un test que seule
l'ancienne branche avait, `memoire.ajout-seul` pour ses entrées de
journal, que chaque lot écrit). Avant L-0020, ce push passait. Le refus
est voulu (ADR-0104, B-0167 : abandonner ce qui a été poussé, c'est le
réécrire) ; ce qui manque est la sortie. Le refus ne propose que
`git fetch`, sans effet ici comme après une fusion par écrasement ou
par rebase ; ADR-0104 propose un autre nom de branche, qui peut manquer
en session cloud, où l'agent ne pousse que la branche de son
environnement.

Pistes : le refus d'une branche dont le commit gardé n'est pas dans la
branche par défaut dit les sorties (garder les entrées de la mémoire
poussées, une demande validée pour un test retiré, un autre nom là où
c'est possible) ; ou la trace se retire par une commande que l'humain
lance quand il abandonne une branche.

Abandonné le 22 novembre, comme B-0321, sur la décision de Théo
D-0156 (J-2026-11-22-A) : le message du refus est dans le hook de
l'agent, et ce refus n'a été qu'éprouvé par le relecteur de L-0020, pas
rencontré dans une session (ADR-0098). Une branche ainsi refusée dans
une session rouvrirait un besoin.

## Satisfait quand

- [ ] le refus d'une branche abandonnée, ou fusionnée par écrasement, repartie sous le même nom dit une sortie que l'agent peut suivre en session cloud, et ADR-0104 la dit
