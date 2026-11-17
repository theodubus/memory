<!-- socle: couche=backlog zone=publique -->
# B-0217 — Le dossier des worktrees des sous-agents, .claude/worktrees, n'est pas ignoré : le hook de fin de tour de l'environnement cloud demande de le commiter

> statut : ouvert · origine : J-2026-11-14-D · lu : backlog@f3069fbc

Un sous-agent lancé avec un worktree (skill `delegate-lot`) a son dossier
sous le dossier .claude/worktrees, que le `.gitignore` de ce dépôt n'ignore pas.
Le hook de fin de tour de l'environnement cloud voit des fichiers non
suivis et demande de les commiter (J-2026-11-14-D). La session l'a exclu
localement, dans `.git/info/exclude`, qui ne survit pas au conteneur.

Le 16 novembre, Théo le passe de priorité basse à normale (J-2026-11-16-I) : le dossier non ignoré a fait refuser la fin de tour deux fois dans la session du lot L-0004.

## Satisfait quand

- [ ] le « Fait quand » de T-0013 est tenu
