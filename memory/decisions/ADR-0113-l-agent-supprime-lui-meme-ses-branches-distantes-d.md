<!-- socle: couche=decisions zone=publique -->
# ADR-0113 — L'agent supprime lui-même ses branches distantes déjà contenues ailleurs : la commande prune-branches, vérifiée sur l'origine et sous bail, le hook de l'agent inchangé hors de son message

> statut : acceptée · date : 2026-11-26 · source : B-0351@bf78a534, D-0202@0eec86fd, D-0198@74687954, ADR-0098@3081a5ed, J-2026-11-24-BC@ef97ab6d · lu : decisions@a51cbbe1

## Contexte

L'état donne à l'humain, après chaque fusion et chaque passation, les
branches distantes que la branche par défaut ou la branche de travail
poussée contient en entier : la politique range la suppression distante
parmi les actions irréversibles (point 4), et le hook de l'agent la refuse.
Théo a demandé que l'agent supprime les siennes (J-2026-11-24-BC@ef97ab6d),
avant la mise à jour de chess (D-0198@74687954), et retenu « 1A 2A »
(D-0202@0eec86fd) : seulement les branches de l'agent, dont le dernier
commit porte sa marque, et par défaut dans le produit, une ligne de la
politique la coupant. Le mécanisme revenait à l'agent ; la spécification
de B-0351@bf78a534 le décrit, avec son modèle de menace. La preuve
qu'ADR-0098@3081a5ed exige pour toucher au hook de l'agent est la branche
donnée à l'humain à chaque fin de lot.

## Décision

1. Une commande du socle, `socle prune-branches`, supprime les branches
   que l'état calcule à supprimer et dont le dernier commit porte l'un des
   motifs de `[agents] markers` : après `git fetch --prune origin`, elle
   vérifie par `git ls-remote --heads origin` que chacune est encore à la
   tête que le fetch connaît, et que la branche qui la garde (la branche
   par défaut, ou la branche de travail courante) la contient sur
   l'origine ; puis elle la supprime par un push gardé par cette tête
   (`--force-with-lease=refs/heads/<b>:<sha>`), qui échoue si elle a
   bougé. Elle imprime la commande qui recrée chaque branche supprimée.
   `--dry-run` dit ce qu'elle supprimerait.
2. Un refus de l'origine se garde dans `.git/socle/prune-refused.json`,
   avec la tête refusée : tant qu'un fetch ne montre pas la branche
   changée, l'état la redonne à l'humain, avec la raison, et la commande
   ne la retente pas. Un bail refusé (la branche a bougé) n'est pas un
   refus : la branche est laissée, rien n'est gardé.
3. L'état ne donne plus à l'humain que ses branches et celles que
   l'origine a refusées ; une ligne pour l'agent, hors de ce qui revient à
   l'humain, nomme les siennes et la commande.
4. `prune_branches`, dans `[irreversible]` de la politique, vaut vrai par
   défaut ; toute autre valeur qu'un booléen vrai coupe la suppression :
   l'état redonne alors tout à l'humain, et la commande refuse en le
   disant. Les gabarits de la politique portent la ligne en commentaire.
5. Le hook avant push de git laisse passer, sans rien lancer, un push qui
   ne fait que supprimer. Le hook de l'agent refuse toujours
   `git push --delete` et `git push origin :<branche>` ; seul son message
   change, qui nomme la commande.

## Conséquences

La gêne de B-0351@bf78a534 disparaît : une passation ou une fusion ne
laisse plus de branche de l'agent à l'humain. Une pull request ouverte
depuis une branche supprimée se ferme avec elle ; son contenu reste dans
la branche qui la contient, et la commande donne de quoi la recréer. Une
marque d'agent que l'humain pose sur son propre commit lui fait traiter sa
branche comme celle de l'agent. Se défait, pour un projet, par
`prune_branches = false` ; pour le produit, en retirant la commande et la
partition de l'état, la liste de l'humain redevenant entière.
