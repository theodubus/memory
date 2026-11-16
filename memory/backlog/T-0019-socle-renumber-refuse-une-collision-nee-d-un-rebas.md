<!-- socle: couche=backlog zone=publique -->
# T-0019 — socle renumber refuse une collision née d'un rebase : l'identifiant pris par la branche passe pour existant avant elle

> statut : ouvert · origine : J-2026-11-11-S · besoin : B-0176 · lu : backlog@9966bbbd

La tâche de B-0176, que la migration du backlog en quatre formes a posée dans le lot L-0007 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] après un rebase qui fait se heurter deux entrées, `socle renumber <id>` renumérote celle de la branche et ses mentions
