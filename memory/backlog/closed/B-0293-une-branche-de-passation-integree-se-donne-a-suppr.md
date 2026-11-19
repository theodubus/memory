<!-- socle: couche=backlog zone=publique -->
# B-0293 — Une branche de passation intégrée se donne à supprimer : l'état la voit contenue dans la branche par défaut

> statut : fait · origine : J-2026-11-19-A · lu : backlog@6599f863 · ref : J-2026-11-19-B

Le 19 novembre, Théo demande ce que devient la branche
`ccr-f1f3601d-yvlfnh`, en avance d'un commit sur la branche par défaut
(J-2026-11-19-A). Ce commit, a5a2040, est la seconde passation de
L-0014 : ses correctifs ont été appliqués par `git am` dans une autre
branche, sous d'autres SHA, sans que la branche de passation soit
fusionnée (J-2026-11-18-K). Git ne la voit donc pas contenue dans la
branche par défaut : l'état ne la donne pas à supprimer, et ne la dira
« à examiner » qu'après sept jours. La passation de L-0016, elle, a été
fusionnée après l'application de ses correctifs, et l'état la donne à
supprimer dès la fusion de la pull request.

## Satisfait quand

- [x] une branche de passation dont les correctifs sont intégrés est donnée à supprimer par l'état dès la fusion de la pull request qui les porte
