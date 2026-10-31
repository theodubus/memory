<!-- socle: couche=demandes zone=publique -->
# D-0053 — Fixer les réponses de base de toute demande : valider, refuser, contexte-insuffisant

> date : 2026-10-31 · lu : decisions@366e992c

## Décision demandée

Choisir si toute demande propose les mêmes réponses de base, `valider`,
`refuser` et `contexte-insuffisant`, avec le même sens partout, ses
options propres venant en plus.

## Contexte

Sur le pilote, l'agent demande à Théo d'« approuver » là où les demandes de
ce dépôt se répondent par `valider`. Le vocabulaire change d'une demande à
l'autre parce que le socle ne l'impose pas : le lint d'une demande exige
seulement `contexte-insuffisant`, et `valider` quand la demande nomme un
test ou une clé des seuils (D-0040@48979125) ; une demande de choix peut
n'offrir que ses options, et une décision en séance prend n'importe quel
mot. Le gabarit d'une demande propose déjà `valider` et `refuser`, sans
l'exiger. Le moteur ne reconnaît que `valider` pour autoriser un geste
réservé à l'humain : un « approuver » n'y autoriserait rien. Rendre les
réponses de base obligatoires change ce que le lint accepte aujourd'hui :
le test `test_qui_propose_valider_ou_ne_nomme_rien_passe` et le témoin de
l'auto-test « une demande de choix qui ne nomme ni test ni seuil passe sans
`valider` » attendent qu'une demande de choix passe sans `valider`. Les
changer revient à l'humain (politique, point 2).

## Éléments cités

- D-0040@48979125 — la règle validée par Théo : une demande qui nomme un test ou une clé des seuils propose `valider`, les autres sont libres.

## Où regarder

- [la fonction linter du moteur des demandes](https://github.com/theodubus/memory/blob/b2d876f95cf09b3b9b6ba36ecb17db0574f83e51/engine/socle/requests.py#L185) : ce que le lint exige des réponses possibles.
- [le gabarit d'une demande](https://github.com/theodubus/memory/blob/b2d876f95cf09b3b9b6ba36ecb17db0574f83e51/engine/socle/templates/request.md) : les réponses qu'il propose déjà.
- [le test qui accepte une demande de choix sans valider](https://github.com/theodubus/memory/blob/b2d876f95cf09b3b9b6ba36ecb17db0574f83e51/tests/test_demandes.py#L167) : la valeur attendue qui changerait.

## Options

- **Option 1, les réponses de base partout** : toute demande propose `valider` (la recommandation telle quelle, ou l'option recommandée), `refuser` et `contexte-insuffisant` ; une demande de choix ajoute ses options. Le lint refuse un synonyme (`approuver`, `accepter`, `oui`, `rejeter`…), et `socle decision` refuse une réponse en séance qui n'est ni une réponse de base ni une option que la question nomme. Le test et le témoin cités attendent alors `valider`. Effort : une heure. Risque faible : les demandes déjà répondues ne sont pas relues. Réversible.
- **Option 2, les synonymes seulement** : le lint refuse `approuver` et les autres synonymes, et la séance se restreint de même ; une demande de choix reste libre de ne pas proposer `valider`. Aucune valeur attendue ne change. Effort : une heure. Risque : le vocabulaire varie encore d'une demande de choix à l'autre. Réversible.
- **Option 3, les instructions seulement** : le skill des demandes et le gabarit disent les réponses de base, sans contrôle. Effort : un quart d'heure. Risque : l'agent peut encore s'en écarter, comme sur le pilote. Réversible.

## Conséquences

- Si Théo valide : l'option 1 se fait dans la PR en cours, avec un défaut injecté ; le pilote la reçoit à la mise à jour de son socle, et ses demandes en attente se réécrivent avec les réponses de base.
- S'il choisit l'option 2 ou 3 : elle se fait de même, sans toucher au test ni au témoin.
- S'il refuse : rien ne change, et le vocabulaire reste au choix de l'agent.
- Sans réponse : rien ne change ; le reste de la PR avance sans attendre.

## Recommandation

L'option 1 : une seule façon de répondre, la même dans toutes les demandes, et `valider` qui veut toujours dire « la recommandation ».

Vérifié : le lint n'exige aujourd'hui que `contexte-insuffisant`, et `valider` pour un test ou une clé des seuils ; le gabarit propose `valider` et `refuser` ; une décision en séance accepte toute réponse ; le moteur ne reconnaît que `valider`, et `approve` en anglais.

Supposé : que l'« approuver » du pilote vienne d'une demande ou d'une séance écrite par l'agent, le pilote n'étant pas lisible d'ici.

## Réponses possibles

- `valider` — l'option 1 : les réponses de base dans toute demande, le test et le témoin cités attendent `valider`.
- `synonymes` — l'option 2 : seuls les synonymes sont refusés.
- `instructions` — l'option 3 : les instructions seulement.
- `refuser` — rien ne change.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
