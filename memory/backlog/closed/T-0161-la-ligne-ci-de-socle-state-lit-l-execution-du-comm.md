<!-- socle: couche=backlog zone=publique -->
# T-0161 — La ligne CI de socle state lit l'exécution du commit de tête (gh run list --commit), et un test le montre sur une branche repartie de la branche par défaut après la fusion

> statut : fait · origine : J-2026-11-23-C · besoin : B-0334 · lu : backlog@7b07030b · ref : J-2026-11-24-AK

Un commit : `_ligne_ci` (`engine/socle/state.py`) demande à `gh` les
exécutions du commit de tête (`--commit`), et dit qu'il n'en a aucune
plutôt que la dernière de la branche ; le test simule `gh` sur une
branche repartie de la branche par défaut après la fusion.

## Fait quand

- [x] un test montre la ligne « CI » d'un commit de tête qui a une exécution, et celle d'un commit qui n'en a pas, sur une branche dont la dernière exécution est celle d'un autre commit
