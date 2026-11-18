<!-- socle: couche=backlog zone=publique -->
# T-0042 — Le démarrage tient pour branché un core.hooksPath qui se résout vers .socle/git-hooks de la racine

> statut : ouvert · origine : J-2026-11-16-A · besoin : B-0252 · lu : backlog@9966bbbd

Un commit : `hooks.installer_hooks_git` (`engine/socle/hooks.py`) accepte le chemin absolu des hooks du socle de la racine ; un chemin vers les hooks d'un autre worktree reste un choix local, signalé ; un correctif, avec son test.

## Fait quand

- [ ] `core.hooksPath` égal au chemin absolu de `.socle/git-hooks` de la racine ne fait plus dire les hooks git débranchés, et un test le montre
- [ ] un chemin absolu vers les hooks d'un autre worktree reste signalé comme un choix local, et un test le montre
