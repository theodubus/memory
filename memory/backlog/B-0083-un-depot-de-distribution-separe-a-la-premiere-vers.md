<!-- socle: couche=backlog zone=publique -->
# B-0083 — Un dépôt de distribution séparé, à la première version mûre ; ce dépôt gardé privé pour la fabrication

> statut : ouvert · origine : J-2026-10-21-B · lu : backlog@7cf0d815

Proposé par Théo en réponse à D-0037@436f2cf4 : à la première version
mûre, un dépôt de distribution ne contient que ce qu'un projet reçoit (le
moteur, son guide, sa licence), et ce dépôt-ci, gardé privé, reste
l'atelier. L'utilisateur ne voit plus la séparation du produit et de
l'atelier : elle devient interne.

Ce que cela change à ADR-0033@ef7d0d5b, qui écartait deux dépôts parce
qu'une session de développement toucherait les deux : le dépôt de
distribution n'est pas un lieu de développement, il est produit d'ici à
chaque version (une copie de `engine/socle/` et d'un README de
distribution, poussée par un workflow ou par Théo). Les sessions ne
travaillent que dans l'atelier. Restent à trancher : qui publie (Théo, ou
un workflow avec un jeton) ; le nom du dépôt ; ce que deviennent les
liens que les projets installés gardent vers l'atelier (le lanceur et les
gabarits n'en ont pas ; la documentation du produit, si) ; et si un
paquet PyPI vient en plus (D-0037). Une publication et un changement de
visibilité : des gestes de Théo, sur demande.
