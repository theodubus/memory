<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

D-0093 validée sauf sa proposition 7 (J-2026-11-10-N) : quatre jalons,
B-0154 (alléger), B-0157 (chess, sous ADR-0057), B-0159, B-0160. Le socle
organise et fiabilise. JustCook est en pause. B-0149 est fait et poussé ;
sa revue passe avant sa fusion. Un sujet coûte les trois quarts d'une
fenêtre (J-2026-11-10-S) : B-0151 et B-0141 attendent que Théo dise sur
quel compte se font les implémentations. Ensuite : B-0010, B-0155, B-0156.

B-0048 et B-0018 restent ouverts, gardés en tête (D-0026, `rien`).

## Consignes en cours

- Le contexte long et les modèles : Théo compacte la conversation ;
  chaque sujet va à un sous-agent au contexte neuf, dont l'agent choisit
  le modèle (J-2026-11-10-O). Jusqu'au 16 novembre, Fable là où il vaut
  son prix (recul, détails, planification, chess), Opus pour les
  implémentations, puis Opus partout ; Théo : « a utiliser la ou ça en
  vaut la peine » (D-0095, J-2026-11-10-T).
- Le pilote est un essai de choc du socle : ses imperfections sont
  attendues, seules celles du socle se corrigent ici ; Théo : « pas grave
  si le pilote n'est pas idéal partout, c'est un crashtest pour le socle
  donc normal » (J-2026-10-31-E).
- La branche de travail est `ccr-82da0a2e-iccil9` (J-2026-11-09-M).
- Aucun autre dépôt dans la session, ni lecture de JustCook ou de
  `theodubus/socle` ; Théo : « N'ajoute aucun autre dépôt à la session, et
  ne lis ni JustCook ni theodubus/socle (donner leurs liens reste
  permis) » (J-2026-11-09-M).
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

- Une limite d'usage proche décide de l'ordre des sujets, jamais de la
  profondeur du travail ; Théo : « jamais de faire une certaine partie du
  travail au rabais » (J-2026-11-09-C).
- Une attente annoncée dans le récap (CI, banc, match) s'accompagne d'un
  réveil programmé pour y revenir (Théo, J-2026-10-13-N).
- Chaque point de « Pour toi » se comprend seul, sans mon raisonnement,
  que Théo ne lit pas : ce que c'est, pourquoi, ce que change sa réponse ;
  Théo : « dans ton recap dire "je pose une étiquette" ne suffit pas du
  tout » (J-2026-10-31-S).
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
- En autonomie sur le backlog : « tu peux travailler en autonomie sur la
  backlog sur tous les éléments qui peuvent se faire n'importe quand et
  pour lesquels tu n'as pas besoin d'arbitrage / Tu peux t'arrêter quand
  tu as fini ça ou quand tu as besoin d'un arbitrage » (Théo,
  J-2026-10-20-C) ; d'abord l'installation en une commande (B-0074).

## Prochaines étapes

1. Maintenant : le pilote neuf (B-0104), sa session de travail lancée ;
   ses retours, au fil de l'eau (J-2026-10-31-C), se corrigent ici et
   lui parviennent à la mise à jour de son socle.
2. La suite se lit dans l'ordre du backlog (`socle state`) : après le
   pilote, la planification (B-0101), puis la répartition entre agents
   (B-0055) ; B-0010, B-0012 et B-0095 attendent le pilote ; gardé en
   tête : B-0048.
