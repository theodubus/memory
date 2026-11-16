<!-- socle: couche=backlog zone=publique -->
# B-0265 — Un mot pour une chose dans le backlog : le format appelle « sujet » un sujet, un lot et un jalon, et « tâche » ce qu'attend un jalon

> statut : en cours · origine : J-2026-11-16-I · priorité : haute · après : D-0123 · lu : backlog@c0a47b1b

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

Théo élargit le sujet le 16 novembre (J-2026-11-16-K, J-2026-11-16-L) :
le backlog mélange des entrées qui demandent plusieurs livrables et des
livrables seuls ; « on mélange les choux et les carottes ». La
proposition de l'agent, corrigée par Théo (« tout n'est pas forcement un
probleme (il peut y avoir de l'ajout de feature par ex) ») :

- un **besoin** : ce qu'on veut obtenir, un défaut (ce qui ne va pas) ou
  une fonction (ce qu'on ajoute ou améliore) ; ses constats ou sa
  motivation, sa spécification s'il n'est pas tranché, et « Satisfait
  quand », un résultat, jamais une implémentation ; il se ferme quand ses
  tâches sont faites et ce résultat tenu ;
- une **tâche** : un livrable, qu'un implémenteur fait en un commit, qui
  nomme le besoin qu'il sert, avec un « Fait quand » qu'un test vérifie ;
- un **lot** : des tâches, jamais des besoins, qui touchent les mêmes
  fichiers, menées et relues ensemble en une session ;
- un **jalon** : des besoins qui servent un même but.

Des contrôles empêchent de remélanger, chacun avec son défaut injecté :
chaque entrée a sa forme ; une tâche nomme son besoin ; un lot n'attend
que des tâches, un jalon que des besoins ; un constat de revue devient une
tâche si sa correction est claire, un besoin sinon. Une commande crée en
une fois le besoin et sa tâche quand la correction est évidente. Le
backlog ouvert se reclasse, et chaque besoin à plusieurs livrables se
découpe en tâches.

Les deux choix, tranchés par Théo le 16 novembre (J-2026-11-16-M) :
D-0121@ec62e9fd, `2a`, la structure s'écrit en premier, au lot B-0264 ;
D-0122@dbcc64c1, `1b`, chaque forme d'entrée a son préfixe, pour la
qualité à long terme. La spécification, soumise à Théo avant le code,
tranche : les préfixes (`B-` gardé pour le besoin, B comme besoin, ce qui
limite la renumérotation ; `T-` pour une tâche ; `L-` pour un lot ; un
préfixe pour le jalon, `J-` étant pris par le journal) ; l'ancien
identifiant que garde chaque entrée renumérotée (`ancien : B-NNNN`), que
`socle show` et les contrôles de références résolvent, le journal en ajout
seul citant les anciens numéros ; la migration de ce dépôt, et celle d'un
projet équipé par l'installeur, chess compris ; les contrôles qui
empêchent de remélanger, chacun avec son défaut injecté. Le backlog
ouvert se reclasse alors, chaque besoin à plusieurs livrables découpé en
tâches, et les lots du jalon B-0224 refaits avec des tâches.

## Fait quand

- [ ] le format, les skills du produit, le guide et les messages de l'état n'appellent plus « sujet » un lot ni un jalon, ni « tâche » un sujet, et un test le montre pour les messages de l'état
- [ ] la spécification de la structure et de ses préfixes (D-0122) est soumise à Théo avant son code
- [ ] la structure besoin, tâche, lot, jalon, avec un préfixe par forme (D-0122), s'écrit dans le format et les contrôles, chacun avec son défaut injecté, et le backlog ouvert y est reclassé
