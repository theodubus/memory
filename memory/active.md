<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

L'ordre validé par Théo (J-2026-10-14-Q) : B-0060, fait (J-2026-10-14-R) ;
la demande de B-0039 en parallèle ; puis B-0048 avec B-0018 ; puis B-0059.

D-0025 est validée, réponse `public` (J-2026-10-14-S) : le dépôt d'essai
est github.com/theodubus/tests. J'y pousse un projet jetable par branche
(JavaScript, Go, Java, Ruby, PHP), je lis chaque CI, je corrige les étapes
fausses des adaptateurs, puis je dis à Théo qu'il peut supprimer le dépôt.

D-0026 attend : Théo a posé des questions (ce que veut dire « local », quels
hooks, comment éviter un usage détourné de « une fois ») ; j'y réponds et
je réécris la demande, encore sans réponse.

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

1. D-0025 : les cinq projets jetables dans theodubus/tests, leur CI lue,
   les étapes fausses corrigées ; puis clore B-0039.
2. D-0026 : relayer la réponse de Théo avec son texte exact, une fois la
   demande réécrite poussée.
3. Dans l'ordre validé : B-0059 (ce qui reste en français dans un projet
   anglais).
4. Plus tard : B-0046 (que Théo reprendra), B-0040 (dotnet absent d'ici) ;
   B-0042 attend sa propre demande.
