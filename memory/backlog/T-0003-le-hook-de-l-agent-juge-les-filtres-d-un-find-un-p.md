<!-- socle: couche=backlog zone=publique -->
# T-0003 — Le hook de l'agent juge les filtres d'un find un par un : une conjonction (-name et -path) est refusée pour ce qu'aucun des deux ne vise seul

> statut : ouvert · origine : J-2026-11-14-AJ · besoin : B-0231 · lu : backlog@9966bbbd

La tâche de B-0231, que la migration du backlog en quatre formes a posée dans le lot L-0005 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] `find . -name '*.json' -path './build/*' -delete` passe le hook, `find . -name '*.json' -path './.claude/*' -delete` reste refusé, et un test le montre
- [ ] `find build -path '*.toml' -delete` passe le hook, `find . -path '*.toml' -delete` reste refusé, et un test le montre
