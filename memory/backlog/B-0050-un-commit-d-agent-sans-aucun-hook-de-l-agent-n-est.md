<!-- socle: couche=backlog zone=publique -->
# B-0050 — Un commit d'agent sans aucun hook de l'agent n'est vu qu'en CI

> statut : ouvert · origine : <J-… ou commit:… où le sujet est apparu> · lu : backlog@c11291ba

Mesuré à R6 : un commit fait dans la copie du projet d'échecs, depuis une
session ouverte dans ce dépôt, porte `Socle-Hooks: SessionStart=0
PreToolUse=0 Stop=0` ; les hooks de l'agent n'y ont jamais tiré, et rien ne
le dit avant le push : le hook avant push de la copie l'a refusé ensuite
(`hooks.trace`), comme la CI. Le hook `commit-msg` pourrait avertir dès le
commit quand un commit d'agent ne compte aucun hook.
