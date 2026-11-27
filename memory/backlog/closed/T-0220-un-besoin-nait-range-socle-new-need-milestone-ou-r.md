<!-- socle: couche=backlog zone=publique -->
# T-0220 — Un besoin naît rangé : socle new need --milestone ou --reserve, et le contrôle de la réserve rattrape un besoin nouveau sans place

> statut : fait · origine : J-2026-11-27-AO · besoin : B-0365 · lu : backlog@c0e72dd2 · ref : ce commit

Le premier moment de la règle de B-0365 (D-0213, D-0235, point 8), dans
un commit qui pose aussi la spécification, une ADR avec son modèle de
menace, puisque le lot pose un garde-fou.

- `socle new need "…" --milestone JA-NNNN` ajoute le besoin à la fin de
  l'`après` du jalon ouvert ; `--reserve "<raison>"` écrit sur sa ligne
  de métadonnées `réserve : <raison>` et `trié : L-NNNN`, le plus haut
  identifiant de lot du backlog. Les deux s'excluent ; avec `--task`,
  rien ne change pour la tâche. Sans l'un ni l'autre, quand le projet a
  un jalon ouvert, la sortie dit en une ligne comment le ranger, sans
  refus.
- Le contrôle `memoire.reserve`, contre la base : un besoin ouvert
  nouveau, ou sorti d'un jalon ouvert, qu'aucun jalon ouvert n'attend et
  sans raison de réserve, est refusé, quand le projet a un jalon ouvert ;
  son message dit les deux façons de le ranger.

## Fait quand

- [x] un test crée un besoin par `--milestone` et le trouve dans l'`après` du jalon, un autre par `--reserve` et lit sa raison et son tri
- [x] un test montre le contrôle refusant un besoin nouveau sans place, et passant un besoin nouveau rangé, un besoin d'avant sans raison, et tout besoin d'un projet sans jalon ouvert
- [x] le défaut injecté et le témoin sain du contrôle sont dans `engine/socle/selftest.py`
