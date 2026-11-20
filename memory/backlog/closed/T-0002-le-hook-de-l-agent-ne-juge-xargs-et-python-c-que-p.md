<!-- socle: couche=backlog zone=publique -->
# T-0002 — Le hook juge xargs d'un écrivain par les départs et les filtres du producteur qui lui donne sa liste : find, grep -r, git ls-files

> statut : abandonné · origine : J-2026-11-14-AH · ref : D-0143 · besoin : B-0230 · lu : backlog@9966bbbd

Un commit : `producteur | xargs écrivain` se juge par ce que le producteur peut lister, `grep -r` et `git ls-files` comme un `find` sans filtre ; ses cas dans `tests/test_garde.py`. Le chemin passé en argument au script d'un `python -c` est T-0070.

Abandonné le 20 novembre par D-0143 (ADR-0098) : le hook de l'agent est terminé, et cette entrée ne cite aucune preuve vue dans une session.

## Fait quand

- [ ] `grep -rl x . | xargs sed -i …`, `git ls-files | xargs sed -i …` et `find . -type f | xargs sed -i …` sont refusés par le hook, et un test le montre
- [ ] `find . -name '*.py' | xargs sed -i …` passe le hook, et un test le montre
