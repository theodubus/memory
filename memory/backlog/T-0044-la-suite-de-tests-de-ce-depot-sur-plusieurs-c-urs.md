<!-- socle: couche=backlog zone=publique -->
# T-0044 — La suite de tests de ce dépôt sur plusieurs cœurs : verify --fast passe près de douze minutes sur un seul cœur

> statut : ouvert · après : D-0130 · origine : J-2026-11-16-E · besoin : B-0257 · lu : backlog@9966bbbd

La tâche de B-0257, que la migration du backlog en quatre formes a posée dans le lot L-0012 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

Où elle en est (J-2026-11-17-I) : le lanceur `tests/parallele.py` et son test sont livrés ; la suite rapide y passe en 175 s au mur contre 649 s par `unittest discover`, verte trois fois de suite en local. Reste le changement de la commande de tests de `.socle/adapter.toml`, protégé, par une demande à Théo, puis le relevé de `verify --fast --redo` après lui et les trois passages en CI.

## Fait quand

- [ ] la durée de `verify --fast --redo` est relevée dans une session de travail, avant et après
- [ ] la suite lancée en parallèle passe trois fois de suite, en local et en CI
- [ ] après le changement, `verify --fast --redo` prend moins de cinq minutes dans une session de travail
