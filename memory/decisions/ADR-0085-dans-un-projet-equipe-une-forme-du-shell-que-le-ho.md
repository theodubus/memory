<!-- socle: couche=decisions zone=publique -->
# ADR-0085 — Dans un projet équipé, une forme du shell que le hook ne juge pas se nomme au récap et se signale au dépôt du socle par l'humain

> statut : acceptée · date : 2026-11-17 · source : ADR-0082@beb85978, B-0270@87c0e74b, ADR-0040@0f8b7bb0, L-0011@b6079dd8 · lu : decisions@0737eddd

## Contexte

ADR-0082@beb85978 range une forme du shell qu'un agent n'écrit pas, et
qui échappe au hook, dans la liste des formes connues du guide, sans
entrée au backlog. Le skill `socle-review` le faisait faire par l'agent
qui mène la revue. Dans un projet équipé, le guide est sous le moteur
installé, protégé : l'agent ne peut pas l'écrire, et rien ne lui disait
quoi faire de la forme (B-0270@87c0e74b, relevé par la revue du lot
L-0011). B-0270 laissait à décider où et comment la signaler.

## Décision

Seul le dépôt qui fabrique le socle écrit la liste. Dans un projet
équipé, la ligne du récap qui écarte la forme la nomme, et « Pour toi »
propose à l'humain de la signaler au dépôt public du socle
(https://github.com/theodubus/socle, ADR-0040) ; il choisit comment.
Rien ne va au backlog du projet : la forme n'y ouvre pas d'entrée, comme
le veut ADR-0082, et la signaler est facultatif, son effet étant hors du
modèle de menace du hook. L'agent ne la publie jamais lui-même : ce
serait une action externe, réservée à l'humain par la politique
d'autonomie.

## Conséquences

- Le skill `socle-review` et son gabarit anglais le disent, à la suite de
  la règle d'ADR-0082, laissée telle quelle ; un test le garde, avec la
  protection du guide dans un projet équipé.
- Une forme signalée entre à la liste du guide par un lot de ce dépôt, sa
  note de version la datant, comme les autres.
- Pour défaire : une ADR qui la remplace, par exemple pour une entrée du
  backlog `pour : humain` si des formes signalées se perdent.
