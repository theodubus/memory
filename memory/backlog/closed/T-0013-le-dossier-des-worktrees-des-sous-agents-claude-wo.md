<!-- socle: couche=backlog zone=publique -->
# T-0013 — Le dossier des worktrees des sous-agents ignoré par git, ici et dans un projet que l'installeur équipe

> statut : fait · origine : J-2026-11-14-D · ref : J-2026-11-20-M · besoin : B-0217 · lu : backlog@9966bbbd

Un commit : le `.gitignore` de ce dépôt ignore le dossier .claude/worktrees ; l'installeur fait de même dans un projet qu'il équipe si le produit y lance des sous-agents en worktree, avec une note de version.

## Fait quand

- [x] un fichier sous le dossier .claude/worktrees n'apparaît pas dans `git status` de ce dépôt, et, si le produit lance des sous-agents en worktree, dans celui d'un projet que l'installeur équipe ; un test le montre
