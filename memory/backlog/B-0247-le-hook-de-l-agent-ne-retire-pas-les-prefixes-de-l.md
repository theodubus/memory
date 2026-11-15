<!-- socle: couche=backlog zone=publique -->
# B-0247 — Le hook de l'agent ne retire pas les préfixes de la commande d'un find -exec : find .. -exec sudo rm -rf {} passe

> statut : ouvert · origine : J-2026-11-15-O · priorité : haute · lu : backlog@fc46feff

La revue du lot B-0234 (J-2026-11-15-O), premier constat pour le
backlog. Le hook de l'agent lit la commande que lance un `find -exec`
(`_lire_find`, `engine/socle/hooks.py`) sans en retirer les préfixes
(`sudo`, `env`, `nice`…) : `find .. -maxdepth 0 -exec sudo rm -rf {} \;`
et `find .. -maxdepth 0 -exec sudo rsync -a --delete vide/ {} \;`
passent, avant le lot comme après ; la forme avec `rm` passe depuis
B-0208. Rien ne rattrape ensuite la suppression du projet : ADR-0080 (sa
première conséquence) ouvre ce sujet, de priorité haute comme B-0208.

La piste : appliquer `_sans_prefixes` (`engine/socle/commands.py`) à la
commande de `-exec` avant de la juger.

## Fait quand

- [ ] `find .. -maxdepth 0 -exec sudo rm -rf {} \;` est refusé par le hook, `find . -name '*.pyc' -exec sudo rm -f {} \;` passe, et un test le montre
