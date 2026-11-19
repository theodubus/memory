<!-- socle: couche=backlog zone=publique -->
# T-0096 — Le hook de fin de tour, sur des contrôles en échec, donne leur nom, la première ligne utile de chaque test en échec et la commande qui montre tout, au lieu du rapport entier

> statut : ouvert · origine : D-0134 · besoin : B-0290 · lu : backlog@a1dcf63d

Un commit : `stop` (`engine/socle/hooks.py`), quand des contrôles
échouent, ne recopie plus le rapport entier : pour chaque contrôle en
échec, son nom et la première ligne utile de chaque test en échec, puis
la commande qui montre tout (`socle check --stage agent`, ou `socle
verify --fast`). Le blocage, le compteur, l'escalade et la relance
inchangée ne changent pas. Le guide si le message qu'il cite change, une
note de version.

## Fait quand

- [x] le refus de la fin de tour sur des tests en échec donne le nom du contrôle, la première ligne utile de chaque test en échec et la commande qui montre tout, sans la sortie entière, et un test le lit
- [x] l'escalade et la relance inchangée gardent leur comportement, et les tests existants le montrent
