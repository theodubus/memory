<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

L'essai de la CI des adaptateurs sur GitHub est fini (D-0025, D-0027) : le
workflow « Socle » et le balayage de mutation passent dans les cinq
langages (F-0019, F-0020) ; B-0039 est fait. En chemin, GitHub n'enregistre
un workflow sans déclencheur `push` qu'au push qui modifie son fichier
(F-0021) : `mutation.vivante` le dit et le remède le corrige (B-0063, fait).
Le dépôt d'essai et sa session (`session_01L5X5DzSiY59tjT4e5kfzCs`) ne
servent plus : Théo peut supprimer l'un, et l'autre s'archive sur son
accord.

Les sujets clos du backlog sont rangés dans le sous-dossier `closed`
(D-0028, D-0029, ADR-0030, J-2026-10-15-E) : `socle archive` range un sujet
qu'on clôt.

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

1. L'ordre validé par Théo (J-2026-10-17-A) est fait : B-0062
   (J-2026-10-17-B ; la session d'essai éprouve les nouvelles versions sur
   GitHub, si le dépôt d'essai existe encore ; la CI de ce dépôt revient à
   Théo, B-0065), puis B-0064 (J-2026-10-17-C). Proposer la suite.
2. Plus tard : B-0046 (que Théo reprendra), B-0040 (dotnet absent d'ici) ;
   B-0042 attend sa propre demande.
