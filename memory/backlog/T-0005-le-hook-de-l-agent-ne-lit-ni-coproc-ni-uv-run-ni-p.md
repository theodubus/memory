<!-- socle: couche=backlog zone=publique -->
# T-0005 — Le hook retire uv run et poetry run, avec leurs options, comme des préfixes

> statut : ouvert · origine : J-2026-11-15-O · besoin : B-0248 · lu : backlog@9966bbbd

Un commit : `uv run` et `poetry run` rejoignent les préfixes du découpage (`PREFIXES`, `engine/socle/commands.py`), leurs options comprises, à la manière de `python -m` ; ses cas dans `tests/test_garde.py`.

## Fait quand

- [ ] `uv run rm -rf ..` et `poetry run git push --force origin main` sont refusés par le hook, et un test le montre
- [ ] `uv run pytest` passe le hook, et `uv run python -c` qui écrit un fichier protégé est refusé comme sans préfixe, et un test le montre
