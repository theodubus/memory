<!-- socle: couche=backlog zone=publique -->
# L-0024 — Lot du récap et de l'état : la branche à supprimer que l'origine n'a plus, la branche gardée par une branche de travail disparue, les clôtures des blocs de code

> statut : en cours · origine : J-2026-11-21-P · après : L-0023, T-0125, T-0126, T-0101, T-0161, T-0119, T-0059 · lu : backlog@6c894b15

Ce que la fin de tour et l'état donnent à l'humain, juste : la branche que le récap lui donne à supprimer quand l'origine ne l'a plus (B-0311, priorité haute : la piste soumise à Théo avec la preuve vue en session, T-0125, puis tenue, T-0126) ; celle que l'état dit gardée par une branche de travail que l'origine n'a plus (T-0101, B-0292, `a_faire` d'`engine/socle/human.py`), du même sujet (J-2026-11-21-M) ; la lecture des lignes hors des blocs de code, que partagent le récap et les liens (T-0092, B-0287, `engine/socle/memory.py` et `engine/socle/human.py`). Le premier des lots nouveaux, pour sa priorité haute. Formé le 21 novembre, sur la décision de Théo (D-0154, J-2026-11-21-Q).

Le 23 novembre, selon la règle qui place une tâche ouverte ensuite au prochain lot dont la règle s'applique (J-2026-11-16-J) : la ligne « CI » de `socle state` qui lit la dernière exécution de la branche, pas celle du commit de tête (T-0161, B-0334, `engine/socle/state.py`), ce que l'état donne à l'humain après la fusion (J-2026-11-23-C).

Le 24 novembre, sur D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`) : T-0092 s'abandonne avec B-0287 (X2) ; T-0119 (de L-0031) et T-0059 (de L-0028), lots fermés, le rejoignent : ce que l'état et un refus disent à l'agent et à l'humain.

## Revues

### Passe 1 — 2026-11-24

Commits : 0bbf84c..fe59939

- Bloquant : la note 2026-11-24-h sans son « À faire », perdu à la résolution d'un conflit
- Ouvre : B-0348
