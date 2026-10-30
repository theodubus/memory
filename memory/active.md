<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

BMAD Method est retiré du socle (D-0051, ADR-0036, J-2026-10-30-Q), dans
une PR vers `main` ; restent la déclaration des fichiers tiers et les
décisions en séance. La planification (B-0101) et la répartition du
travail entre agents (B-0055) reviennent au socle. Les projets d'essai
sont dans le dossier de travail de la session, jetables.

D-0026 est répondue `rien` : B-0048 et B-0018 restent ouverts, « on se le
garde en tete et on voit si ça finit par etre bloquant ».

## Consignes en cours

- Le moment venu, donner à Théo ce qu'il faut pour lancer le pilote neuf
  (création du dépôt, prompt d'installation, gestes sur GitHub, premier
  message de la session de travail) ; Théo : « garde en tete de me donner
  ce qu'il faudra pour lancer le pilote le moment venu » (J-2026-10-30-S).
- La branche de travail est `ccr-7128ec56-nnvoun-v2`, tirée de `main` sur la
  réponse `branche-neuve` de Théo à D-0049 (J-2026-10-30-J) ; l'ancienne
  branche reste, pour les SHA que la mémoire cite.
- La documentation se conçoit avant de s'écrire, commence par ce dont le
  projet parle et ce qu'il est, ses schémas se vérifient rendus avant le
  push, et elle n'est faite que validée par Théo ; Théo : « fais un petit
  effort de conception sur ce qu'est censé être une documentation »
  (J-2026-10-20-Y).
- La documentation a un ton formel, clair, sans tutoiement ; elle répond à
  une liste de questions, chacune à un seul endroit et entière, et chaque
  fichier a une portée claire ; Théo : « il faut se lister ce a quoi on veut
  répondre puis se dire ou ça a sa place » (J-2026-10-21-A). Le plan lui est
  soumis dans la conversation avant la nouvelle version.
- La documentation ne rapporte pas les essais de l'outil, dit à quoi il
  sert, reste aussi courte que le fonctionnement le permet, et le guide
  suit le parcours de l'utilisateur ; Théo : « on dit qu'on l'a testé mais
  on ne dit pas a quoi sert l'outil », « j'ai du mal à me projeter dans le
  parcours utilisateur » (J-2026-10-22-A).

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
  les avantages de mon projet (actuel + prévu) et du leur » (BMAD Method,
  J-2026-10-19-E) ; BMAD retiré (D-0051), ses avantages se construisent
  dans le socle, à sa manière : B-0101, B-0055.
- Sessions d'un agent réel : « Tu as mon autorisation pour utiliser
  l'abonnement » (Théo, J-2026-10-19-H) ; chacune plafonnée à l'équivalent
  de 2 dollars, et sa consommation rapportée.
- « Aucun projet n'est deja equipé du socle » (Théo, J-2026-10-19-H).
- En autonomie sur le backlog : « tu peux travailler en autonomie sur la
  backlog sur tous les éléments qui peuvent se faire n'importe quand et
  pour lesquels tu n'as pas besoin d'arbitrage / Tu peux t'arrêter quand
  tu as fini ça ou quand tu as besoin d'un arbitrage » (Théo,
  J-2026-10-20-C) ; d'abord l'installation en une commande (B-0074).

## Prochaines étapes

1. Maintenant : l'ordre du backlog et B-0092 (D-0052), puis le pilote neuf.
2. Le projet pilote : justcook, avec BMAD, installé et éprouvé
   (J-2026-10-29-E à J-2026-10-30-M) ; BMAD retiré, le pilote repart d'un
   dépôt neuf, installé sans BMAD, avec le cadrage, la planification faite
   d'abord à la main sous la consigne de ton de Théo (D-0051). Puis la
   planification (B-0101), puis la répartition entre agents (B-0055),
   quand le pilote écrira du code. B-0095 attend son architecture ;
   attendent le pilote : B-0010, B-0012 ; le dépôt de distribution :
   B-0083 ; gardé en tête : B-0048 ; pour Théo : B-0102.
