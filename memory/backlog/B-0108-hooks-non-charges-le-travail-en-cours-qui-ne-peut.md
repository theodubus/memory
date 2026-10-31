<!-- socle: couche=backlog zone=publique -->
# B-0108 — Hooks non chargés : le travail en cours, qui ne peut plus se commiter, passe par la conversation

> statut : ouvert · origine : J-2026-10-31-I · lu : backlog@4c8a7b4d

Quand les hooks de l'agent ne sont pas chargés, le hook avant commit
refuse tout commit et l'agent ne pousse rien : c'est voulu. Mais le travail
en cours reste alors dans le conteneur, et se perd avec lui ; sur le
pilote, un brouillon de spécification a fini dans un stash
(J-2026-10-31-I).

À faire : le remède que l'état affiche dit aussi de montrer le travail
en cours dans la conversation (son diff, ou le texte des fichiers
nouveaux), sans le commiter, pour que l'humain le donne à la session
neuve.
