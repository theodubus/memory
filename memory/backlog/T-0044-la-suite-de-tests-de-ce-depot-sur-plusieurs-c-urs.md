<!-- socle: couche=backlog zone=publique -->
# T-0044 — La suite de tests de ce dépôt sur plusieurs cœurs : verify --fast passe près de douze minutes sur un seul cœur

> statut : ouvert · origine : J-2026-11-16-E · besoin : B-0257 · lu : backlog@9966bbbd

La tâche de B-0257, que la migration du backlog en quatre formes a posée dans le lot L-0012 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] la durée de `verify --fast --redo` est relevée dans une session de travail, avant et après
- [ ] la suite lancée en parallèle passe trois fois de suite, en local et en CI
- [ ] après le changement, `verify --fast --redo` prend moins de cinq minutes dans une session de travail
