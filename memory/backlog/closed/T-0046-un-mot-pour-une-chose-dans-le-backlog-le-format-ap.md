<!-- socle: couche=backlog zone=publique -->
# T-0046 — La structure du backlog en quatre formes : le moteur, ses contrôles, la migration et les textes du produit

> statut : fait · origine : J-2026-11-16-I · besoin : B-0265 · ref : J-2026-11-16-U · lu : backlog@9966bbbd

La tâche de B-0265 que la migration a posée, récrite en ce que livre le
commit de J-2026-11-16-U : la spécification de D-0123 (ADR-0083), ses
points 1 à 9, sauf la seconde moitié du point 8, que mène T-0049.

## Fait quand

- [x] la spécification de la structure et de ses préfixes est soumise à Théo avant son code, et validée (D-0123)
- [x] les préfixes `T-`, `L-` et `JA-`, la forme lue sur l'identifiant, l'ancien numéro résolu et jamais réattribué, ce que chaque forme attend, la priorité, la clôture et l'état s'écrivent dans le moteur, et `tests/test_structure.py` le montre
- [x] chaque refus du contrôle `memoire.formes`, et l'ancien numéro réattribué, a son défaut injecté dans l'auto-test, avec un témoin sain
- [x] la mise à jour migre un backlog d'avant ; ce dépôt est migré dans le même commit, et un test montre qu'après la migration d'un projet d'essai aucun contrôle n'échoue
- [x] le format, les skills du produit, le guide, les instructions posées et les messages de l'état n'appellent plus « sujet » un lot ni un jalon, ni « tâche » un sujet, et un test le montre pour les messages de l'état
