<!-- socle: couche=backlog zone=publique -->
# T-0075 — Un test dont la valeur attendue change se commite et se pousse sous sa demande en attente, la CI le refusant jusqu'à la réponse

> statut : fait · origine : J-2026-11-18-J · besoin : B-0140 · après : T-0016 · lu : backlog@84ad299e · ref : J-2026-11-20-V

Un commit, sur la réponse de Théo à la demande de T-0016 : le contrôle des valeurs attendues au commit, au push et en CI, et son défaut injecté. Si Théo refuse, la tâche s'abandonne, et sa raison s'écrit au besoin.

## Fait quand

- [x] un test dont la valeur attendue change se commite et se pousse sous sa demande en attente, et un test le montre
- [x] la CI le refuse tant que la demande n'a pas de réponse, et un défaut injecté le montre
