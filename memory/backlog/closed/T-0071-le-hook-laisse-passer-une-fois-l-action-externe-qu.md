<!-- socle: couche=backlog zone=publique -->
# T-0071 — Le hook laisse passer une fois l'action externe qu'une demande validée nomme exactement

> statut : abandonné · origine : J-2026-11-18-J · besoin : B-0048 · après : T-0008 · lu : backlog@84ad299e · ref : D-0168

Un commit, sur la spécification que Théo a validée par la demande de T-0008 : le jugement des actions irréversibles (`engine/socle/hooks.py`) et son défaut injecté ; ses cas dans `tests/test_garde.py`. Si Théo n'en veut pas, la tâche s'abandonne en renvoyant à sa réponse.

T-0071 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0048, sous « Attendus d'un fait qui n'arrive pas : ils reviennent s'il arrive » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] l'action externe qu'une demande validée nomme exactement (un push : son dépôt et sa branche) passe le hook une fois, et un test le montre
- [ ] la même action sans demande, une seconde fois ou vers une autre branche reste refusée, et un défaut injecté le montre
