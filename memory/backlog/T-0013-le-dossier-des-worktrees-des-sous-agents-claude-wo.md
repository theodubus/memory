<!-- socle: couche=backlog zone=publique -->
# T-0013 — Le dossier des worktrees des sous-agents, .claude/worktrees, n'est pas ignoré : le hook de fin de tour de l'environnement cloud demande de le commiter

> statut : ouvert · origine : J-2026-11-14-D · besoin : B-0217 · lu : backlog@9966bbbd

La tâche de B-0217, que la migration du backlog en quatre formes a posée dans le lot L-0006 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] le dossier .claude/worktrees est ignoré par le dépôt, et par un projet que l'installeur équipe si le produit lance des sous-agents en worktree
