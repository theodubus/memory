<!-- socle: couche=backlog zone=publique -->
# B-0304 — L'état dit les hooks git non branchés quand core.hooksPath pointe vers le dossier des hooks du projet par un chemin absolu

> statut : ouvert · origine : J-2026-11-19-AJ · lu : backlog@2e909c10

Vu le 19 novembre (J-2026-11-19-AJ) : à la reprise de la session de
L-0019, le démarrage a ajouté à l'état « hooks git non branchés », alors
que `core.hooksPath` valait le chemin absolu du dossier des hooks git
du projet, `.socle/git-hooks`, et que les hooks avaient tourné à chaque commit de la soirée. `installer_hooks_git`
(`engine/socle/hooks.py`) ne tient pour branchée que la valeur relative
`.socle/git-hooks`, et prend toute autre valeur pour un choix local
qu'elle n'écrase pas. Une fausse alerte, qui peut faire arrêter un agent
ou inquiéter l'humain. Supposé : la valeur absolue vient de la copie
isolée que Claude Code a créée pour le sous-agent du lot, entre le
démarrage, sans alerte, et la reprise.

## Satisfait quand

- [ ] un `core.hooksPath` qui désigne, en absolu ou en relatif, le dossier des hooks git du projet ne fait plus dire à l'état que les hooks ne sont pas branchés, et un autre dossier le fait toujours
