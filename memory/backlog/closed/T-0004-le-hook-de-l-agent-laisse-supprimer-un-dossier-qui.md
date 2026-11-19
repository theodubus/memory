<!-- socle: couche=backlog zone=publique -->
# T-0004 — Le hook juge find … | xargs rm comme un find qui supprime depuis ses départs

> statut : fait · origine : J-2026-11-15-N · besoin : B-0246 · lu : backlog@9966bbbd · ref : J-2026-11-19-AF

Un commit : `xargs` d'un programme qui supprime ce qu'il lit se juge, derrière un producteur `find`, comme une suppression depuis les départs du `find` ; ses cas dans `tests/test_garde.py`. Les autres formes que nomme B-0246 sont dans la liste des formes connues que le hook ne juge pas (B-0261), hors de cette tâche.

## Fait quand

- [x] `find .. -maxdepth 0 | xargs rm -rf` est refusé par le hook comme un `find` qui supprime depuis `..`, et un test le montre
- [x] `find . -name '*.pyc' | xargs rm -f` passe le hook, et un test le montre
