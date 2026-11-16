<!-- socle: couche=backlog zone=publique -->
# B-0265 — Un mot pour une chose dans le backlog : le format appelle « sujet » un sujet, un lot et un jalon, et « tâche » ce qu'attend un jalon

> statut : ouvert · origine : J-2026-11-16-I · priorité : haute · lu : backlog@c0a47b1b

Théo, le 16 novembre (J-2026-11-16-I) : « attention au vocabulaire, un
mot veut dire soit une chose, soit une autre ». Le format du produit
(`engine/socle/FORMAT.md`) écrit : « Un jalon est un sujet marqué `forme :
jalon`, qui attend ses tâches » et « Un lot est un sujet marqué `forme :
lot` » ; l'agent l'a répété dans ses récaps (« un sujet de forme lot »,
ADR-0079). Le mot « sujet » y désigne trois choses, et « tâche » une
quatrième qui est la même que la première.

Le vocabulaire visé, un mot pour une chose :

- une **entrée du backlog** : tout fichier `B-NNNN`, quelle que soit sa
  forme ;
- un **sujet** : une entrée qui se fait, avec son « Fait quand » ;
- un **lot** : une entrée qui réunit des sujets menés ensemble et jugés
  par une seule revue (`forme : lot`) ;
- un **jalon** : une entrée qui réunit des lots et des sujets qui servent
  un même but (`forme : jalon`).

À changer : le format, les skills `socle-batch` et `socle-review` et leurs
gabarits, le guide d'un projet équipé, les messages de l'état (« prochain
lot », « sujet(s) attendent »…) et leur version anglaise.

## Fait quand

- [ ] le format, les skills du produit, le guide et les messages de l'état n'appellent plus « sujet » un lot ni un jalon, ni « tâche » un sujet, et un test le montre pour les messages de l'état
