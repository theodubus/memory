<!-- socle: couche=decisions zone=publique -->
# ADR-0039 — Les réponses de base, les mêmes dans toute demande : valider, refuser, contexte-insuffisant

> statut : acceptée · date : 2026-10-31 · source : D-0053@a43f62b7 · lu : decisions@366e992c

## Contexte

Le socle n'imposait que `contexte-insuffisant`, et `valider` à une demande
qui nomme un test ou une clé des seuils (D-0040@48979125) ; une demande de
choix et une décision en séance prenaient le vocabulaire de l'agent. Sur
le pilote, l'agent demandait d'« approuver » là où ce dépôt demande de
`valider`, et le moteur ne reconnaît que `valider` pour autoriser un geste
réservé à l'humain. Théo a choisi l'option 1 de D-0053@a43f62b7.

## Décision

- Toute demande en attente propose les réponses de base : `valider` (la
  recommandation telle quelle, ou l'option recommandée), `refuser` et
  `contexte-insuffisant` (`approve`, `reject`, `insufficient-context` en
  anglais) ; une demande de choix y ajoute ses options.
- Le lint refuse un synonyme d'une réponse de base (`approuver`,
  `accepter`, `oui`, `rejeter`…), qui se dirait à sa place.
- `socle decision` consigne une décision en séance sous une réponse de
  base, ou sous une option que la question nomme entre accents graves ; le
  texte exact de l'humain reste dans la citation.
- Une demande retirée n'attend plus de réponse : la règle ne la concerne
  pas. Une demande déjà répondue n'est pas relue.

## Conséquences

Une seule façon de répondre, et `valider` qui veut toujours dire « la
recommandation ». Le test qui acceptait une demande de choix sans
`valider`, et le témoin de l'auto-test qui le montrait, attendent
désormais les réponses de base (D-0053) ; un défaut injecté éprouve le
refus d'un synonyme. Un projet installé le reçoit à la mise à jour de son
socle, et ses demandes en attente se réécrivent. Pour défaire : retirer
la règle du lint et de `socle decision`.
