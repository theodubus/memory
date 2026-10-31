<!-- socle: couche=backlog zone=publique -->
# B-0111 — Le rythme de l'agent : enchaîner les sujets prêts et livrer par pull request, sans attendre un message

> statut : ouvert · origine : J-2026-10-31-O · lu : backlog@2db0833c

L'agent du pilote finit son tour sur « Je n'attends rien d'autre », et
s'arrête : un tour de Claude Code se termine, et seul un message de
l'humain en ouvre un autre. Une session cloud n'ouvre pas non plus de pull
request sans qu'on la lui demande : le travail fini reste sur sa branche.

À trancher par Théo : les instructions que pose le socle diraient-elles,
par défaut, d'enchaîner les sujets prêts tant que rien ne revient à
l'humain, et de livrer chaque lot fini par une pull request dont le lien
se donne ? Le risque est un agent qui dépense longtemps sans regard ;
l'autre voie est une consigne propre à chaque projet. Le pilote dira ce
que donne la consigne.

Le 31 oct., le pilote, sur cette consigne, enchaîne les sujets et ouvre
cinq pull requests, longues à fusionner (J-2026-10-31-S). Théo tranche la
livraison (D-0058, `branche-de-dev`) : une branche de développement et
une seule pull request ouverte par défaut, que B-0113 pose. Reste à
trancher l'autre moitié : enchaîner les sujets prêts par défaut.
