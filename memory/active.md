<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

Le mariage du socle et de BMAD Method est fait (ADR-0032, B-0069) : le
socle lit BMAD sans le recopier, fait entrer ses reports au backlog,
consigne les décisions de Théo prises en séance et garde les specs
approuvées ; l'installeur pose les chemins tiers (B-0068) et la
personnalisation de BMAD. Une session réelle de bout en bout le confirme
(F-0024, J-2026-10-20-B). Les projets d'essai sont dans le dossier de
travail de la session, jetables.

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
- Sessions d'un agent réel : « Tu as mon autorisation pour utiliser
  l'abonnement » (Théo, J-2026-10-19-H) ; chacune plafonnée à l'équivalent
  de 2 dollars, et sa consommation rapportée.
- On conçoit pour une installation commune du socle et de BMAD : « Aucun
  projet n'est deja equipé du socle » (Théo, J-2026-10-19-H).
- En autonomie sur le backlog : « tu peux travailler en autonomie sur la
  backlog sur tous les éléments qui peuvent se faire n'importe quand et
  pour lesquels tu n'as pas besoin d'arbitrage / Tu peux t'arrêter quand
  tu as fini ça ou quand tu as besoin d'un arbitrage » (Théo,
  J-2026-10-20-C) ; d'abord l'installation en une commande (B-0074).

## Prochaines étapes

1. En autonomie (J-2026-10-20-C), faits sans arbitrage : B-0074, B-0070,
   B-0073, B-0054, B-0008, B-0072, B-0011. D-0031 validée par Théo : B-0040,
   l'adaptateur C#, est fait et passe son banc (F-0025, J-2026-10-20-N) ;
   ses étapes de CI n'ont pas tourné sur GitHub : D-0032 demande de pousser
   le projet jetable sur une branche `csharp` du dépôt d'essai.
2. B-0075, relevé en écrivant C#, est fait : la régression joint les
   classes de test comme l'outil les attend (J-2026-10-20-O).
3. Les autres sujets ouverts demandent Théo ou des données : B-0066 et
   B-0071 (leur conception), B-0010 et B-0012 (une cible, ou des mesures
   sur un vrai projet), B-0009 (un cas réel), B-0042 (une publication),
   B-0006 (après elle), B-0046 (que Théo reprendra), B-0018 et B-0048 (en
   attente de devenir bloquants).
