<!-- socle: couche=backlog zone=publique -->
# T-0006 — Le hook de l'agent laisse passer un push forcé dont l'option vient des arguments d'une fonction ou d'une variable

> statut : ouvert · origine : J-2026-11-16-B · besoin : B-0254 · lu : backlog@9966bbbd

La tâche de B-0254, que la migration du backlog en quatre formes a posée dans le lot L-0005 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] les trois formes ci-dessus sont refusées par le hook, `git push origin travail` et `B=travail; git push origin "$B"` passent, et un test le montre
