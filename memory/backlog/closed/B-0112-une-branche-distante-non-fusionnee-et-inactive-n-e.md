<!-- socle: couche=backlog zone=publique -->
# B-0112 — Une branche distante non fusionnée et inactive n'est signalée à personne

> statut : fait · origine : J-2026-10-31-Q · lu : backlog@21d64bbd · ref : J-2026-10-31-Q

Théo voyait des branches inutiles sur ce dépôt et sur le pilote, sans
que l'agent lui propose de les supprimer. L'état ne signalait que les
branches que la branche par défaut contient en entier ; une branche jamais
fusionnée, comme celles des sessions du pilote, ne se signalait pas.

Fait (J-2026-10-31-Q) : une branche distante non fusionnée, sans commit
depuis une semaine, entre dans ce qui revient à l'humain, à livrer par une
pull request ou à supprimer, avec le lien de la page des branches ;
l'installeur conseille la suppression automatique des branches
fusionnées. Un test l'établit.
