<!-- socle: couche=backlog zone=publique -->
# B-0297 — Le dossier de la revue juge privé un fichier approuvé par son chemin brut, et aucun test ne montre qu'un fichier privé ne s'y donne pas

> statut : fait · origine : J-2026-11-19-D · ref : T-0103, J-2026-11-19-J · lu : backlog@d2d5bbef

`contenus_approuves` (`engine/socle/review.py`) juge un fichier privé
par le chemin brut que porte le `sujet` d'une décision de séance :
un chemin qui commence par « ./ » vers la mémoire privée passerait. Aucun test ne montre qu'un fichier
privé ne se donne pas au dossier. Relevé par la revue de L-0018
(J-2026-11-19-D).

## Satisfait quand

- [x] un fichier privé désigné par une décision de séance ne se donne jamais au dossier de la revue, quelle que soit l'écriture de son chemin
