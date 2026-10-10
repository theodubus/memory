<!-- socle: couche=decisions zone=publique -->
# ADR-0006 — L'humain répond dans la conversation ; l'agent consigne sa réponse avec le texte exact

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-J

## Contexte

ADR-0004 réservait l'écriture d'une réponse à l'humain lui-même, par une
commande lancée dans un clone du dépôt. Théo l'a refusé : l'utilisateur
répond dans le chat, et c'est à l'agent de faire le reste.

## Décision

Deux canaux de réponse, notés dans le fichier de réponse (`canal`) :

- `conversation` : l'humain répond dans le chat ; l'agent lance
  `socle answer D-NNNN <réponse> --relayed --by <nom> --quote-file <fichier>`,
  qui recopie le texte exact de l'humain dans `citation`. Sans citation, la
  commande refuse, le hook de l'agent refuse, et la CI refuse le fichier.
- `terminal` : l'humain lance lui-même `socle answer`, comme avant.

L'agent ne répond jamais à la place de l'humain : il ne relaie que ce que
l'humain a écrit, et la réponse retenue doit figurer parmi les réponses
possibles de la demande. Une réponse relayée est consignée aussi au journal,
texte exact compris. Le reste d'ADR-0004 tient : une validation ne couvre un
changement que si elle est ajoutée dans la plage et cite ce qu'elle valide.

## Conséquences

- Plus de terminal pour l'humain.
- Ce que l'outillage ne peut pas prouver : que la citation est bien de
  l'humain. La garantie est la relecture du diff, où chaque réponse relayée
  porte sa citation, et la protection de `main`, qui fait passer ce diff
  par une pull request.
- `socle approve` reste réservé à l'humain, au terminal.
