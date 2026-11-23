<!-- socle: couche=backlog zone=publique -->
# T-0167 — L'installeur tient pour branché un core.hooksPath absolu qui se résout vers les hooks de la racine, comme le démarrage

> statut : ouvert · origine : J-2026-11-23-R · besoin : B-0338 · lu : backlog@12a10d0c

Un correctif : l'installeur juge `core.hooksPath` par le même prédicat que `hooks.installer_hooks_git`, partagé ; un chemin d'un autre worktree reste signalé ; son test, qui échoue sur le commit parent ; une note de version.

## Fait quand

- [ ] une mise à jour avec `core.hooksPath` au chemin absolu des hooks de la racine ne les dit pas débranchés, et un test le montre
- [ ] celui d'un autre worktree reste signalé, et un test le montre
