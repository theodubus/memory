<!-- socle: couche=backlog zone=publique -->
# T-0005 — Le hook de l'agent ne lit ni coproc ni uv run ni poetry run : un push forcé ou la suppression du projet y passent

> statut : ouvert · origine : J-2026-11-15-O · besoin : B-0248 · lu : backlog@9966bbbd

La tâche de B-0248, que la migration du backlog en quatre formes a posée dans le lot L-0005 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] `uv run rm -rf ..` et `poetry run git push --force origin main` sont refusés par le hook, `uv run pytest` passe, et un test le montre
