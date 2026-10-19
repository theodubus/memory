<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

L'essai de cohabitation avec BMAD Method est fait (B-0067, J-2026-10-19-G),
sans agent réel : aucun conflit de fichiers ; le socle refuse les fichiers
de BMAD faute de notion de fichiers tiers (F-0022, B-0068) ; BMAD finit son
travail sans toucher la mémoire du socle, mais sa personnalisation
officielle peut lui faire porter la mémoire et la fin de tour du socle
(F-0023, B-0069). Les deux projets d'essai sont dans le dossier de travail
de la session, jetables.

L'essai de la CI des adaptateurs sur GitHub est fini (F-0019, F-0020,
F-0021) ; le dépôt d'essai ne sert plus, Théo peut le supprimer.

D-0026 est répondue `rien` : B-0048 et B-0018 restent ouverts, « on se le
garde en tete et on voit si ça finit par etre bloquant ».

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

- Pas de rétro-compatibilité avec une version antérieure du socle : ni
  sujet de backlog, ni travail pour qu'un projet installé par une version
  antérieure continue de marcher ; Théo : « ne te mets pas des éléments de
  backlog de rétro-compatibilité avec une version antérieure / Le projet
  est EN DEV », « considere que pour le moment personne ne l'a encore
  utilisé » (J-2026-10-19-A).
- Le but : « un produit hyper pratique pour des projets, qui combines tous
  les avantages de mon projet (actuel + prévu) et du leur » (BMAD Method) ;
  ni fusion des codes ni réimplémentation de BMAD, leur cohabitation
  (J-2026-10-19-E, B-0067).

## Prochaines étapes

1. Proposé à Théo après l'essai (J-2026-10-19-G), en attente de son choix :
   B-0068 (les chemins tiers, sans quoi rien ne cohabite), puis B-0069
   (brancher le socle sur BMAD par sa personnalisation, avec un essai sur
   un agent réel qui demande sa validation pour la dépense) ; ensuite les
   sujets qui recoupent BMAD, conçus pour la combinaison (B-0009, B-0042,
   B-0046, B-0054, B-0055, B-0066). Les sujets du socle seul (B-0006,
   B-0008, B-0010, B-0011, B-0012, B-0040) n'en dépendent pas.
2. B-0065 revient à Théo, quand il aura son ordinateur : rien ne presse,
   la CI passe avec les anciennes actions.
