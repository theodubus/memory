<!-- socle: couche=backlog zone=publique -->
# T-0167 — L'installeur tient pour branché un core.hooksPath absolu qui se résout vers les hooks de la racine, comme le démarrage

> statut : abandonné · origine : J-2026-11-23-R · besoin : B-0338 · lu : backlog@12a10d0c · ref : D-0168

Un correctif : l'installeur juge `core.hooksPath` par le même prédicat que `hooks.installer_hooks_git`, partagé ; un chemin d'un autre worktree reste signalé ; son test, qui échoue sur le commit parent ; une note de version.

T-0167 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0338, sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] une mise à jour avec `core.hooksPath` au chemin absolu des hooks de la racine ne les dit pas débranchés, et un test le montre
- [ ] celui d'un autre worktree reste signalé, et un test le montre
