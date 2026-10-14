<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

L'ordre validé par Théo (J-2026-10-14-Q) : B-0060, fait (J-2026-10-14-R) ;
la demande de B-0039 en parallèle ; puis B-0048 avec B-0018 ; puis B-0059.

D-0027 est répondue `publier` (J-2026-10-14-V) : l'essai de la CI des
adaptateurs part dans `theodubus/tests`, public, moteur compris, depuis une
session à part qui ajoute ce dépôt ; celle-ci reste sur `memory` seul.
Session d'essai lancée le 14 oct. à 22 h 25 (heure de Paris) :
`session_01L5X5DzSiY59tjT4e5kfzCs`. Elle est bloquée : le contrôle de
permissions du mode automatique lui a refusé l'ajout de `theodubus/tests`,
puis ses commandes ; rien n'est poussé. La suite dépend de Théo.

B-0059 est fait (J-2026-10-14-W, J-2026-10-14-X, ADR-0029) : un projet
anglais ne lit plus de français dans ce que le socle pose ou affiche. Un
bug voisin attend au backlog : B-0061 (la mise à jour d'un projet au
format 2 dont le backlog est vide échoue).

D-0026 est répondue `rien` : le refus reste, son message est plus clair ;
B-0048 et B-0018 restent ouverts, « on se le garde en tete et on voit si
ça finit par etre bloquant ».

## Consignes en cours

- Une attente annoncée dans le récap (CI, banc, match) s'accompagne d'un
  réveil programmé pour y revenir (Théo, J-2026-10-13-N).
- Ce qui revient à Théo ne contient que ses gestes, chacun avec ce qu'il
  fait ; ce que l'agent fera ensuite se dit à part, comme tel ; un constat
  dit ce qu'il change pour Théo et ce qu'on attend de lui, ou « rien »
  (sa remarque sur B-0056 et B-0058, J-2026-10-14-F).
- Les heures données à Théo s'écrivent à l'heure de Paris (UTC+2 jusqu'au
  25 oct., UTC+1 ensuite) ; Théo : « Et quand tu donnes le temps écris en
  heure de paris stp ».
- Travailler avec un autre dépôt peut faire démarrer une session hors de
  la racine du projet, sans les hooks de l'agent ; Théo : « Juste fais
  gaffe, travailler avec d'autres repos c'est ce qui avait causé dans
  l'autre session le déplacement du dossier de conteneur par defaut ».
  Un autre dépôt se clone hors du dossier des dépôts de la session, sans
  être déclaré racine ; à chaque reprise, vérifier que l'état a été
  injecté, sinon le dire à Théo et ne rien pousser (J-2026-10-14-S).

## Prochaines étapes

1. L'essai de la CI des adaptateurs : la session à part pousse les cinq
   projets jetables et rapporte leur CI ; corriger ici les étapes
   fausses, puis clore B-0039 et dire à Théo qu'il peut supprimer le dépôt.
2. L'ordre validé est épuisé : proposer la suite à Théo (B-0061, qui
   casse une mise à jour, en tête).
3. Plus tard : B-0046 (que Théo reprendra), B-0040 (dotnet absent d'ici) ;
   B-0042 attend sa propre demande.
