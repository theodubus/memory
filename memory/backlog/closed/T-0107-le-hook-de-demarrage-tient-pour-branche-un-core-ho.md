<!-- socle: couche=backlog zone=publique -->
# T-0107 — Le hook de démarrage tient pour branché un core.hooksPath absolu qui désigne le dossier des hooks git du projet

> statut : abandonné · origine : J-2026-11-19-AJ · besoin : B-0304 · ref : T-0042, J-2026-11-21-B · lu : backlog@a2e56e38

Un commit : `installer_hooks_git` (`engine/socle/hooks.py`) compare la valeur de `core.hooksPath`, résolue depuis la racine du projet, au dossier `.socle/git-hooks` résolu ; égale, les hooks sont branchés ; ses cas dans `tests/`.

## Fait quand

- [ ] un `core.hooksPath` absolu qui désigne le dossier des hooks git du projet ne fait plus ajouter « hooks git non branchés » à l'état, et un test le montre
- [ ] un `core.hooksPath` qui désigne un autre dossier le fait toujours, sans être écrasé, et un test le montre

Abandonnée le 21 novembre, doublon de T-0042 (L-0010), qui corrige la même
fausse alerte de `installer_hooks_git` et garde en plus le cas d'un autre
worktree ; relevé par la revue de cap 2 (J-2026-11-21-A).
