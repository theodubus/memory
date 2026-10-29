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

Le 22 oct., Théo le veut à terme (J-2026-10-22-A) : `rien` à D-0037 ne vaut
que pour aujourd'hui, et le dépôt de distribution est l'étape prévue à la
première version mûre, pour épargner à l'utilisateur la friction de la
séparation.

Le 22 oct., il reprend deux sujets abandonnés à son profit (J-2026-10-22-G).
B-0042, le paquet installable par pip : la question d'un paquet en plus du
dépôt de distribution, déjà posée ici. B-0006, comparer l'empreinte du
moteur à la version publiée : sans version publiée, rien à comparer, et le
moteur comme son verrou sont des fichiers protégés ; le dépôt de
distribution pourra publier l'empreinte de chaque version, que la CI d'un
projet comparera.
