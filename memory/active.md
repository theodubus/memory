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

1. Fait : le retrait du code de compatibilité (D-0033, D-0035,
   J-2026-10-20-U). Maintenant : la documentation (B-0046), à reconcevoir ;
   la première version (J-2026-10-20-W) n'est pas validée par Théo
   (J-2026-10-20-Y).
2. Fait aussi : B-0077, le moteur ne renvoie plus à la mémoire de ce dépôt
   (J-2026-10-20-X). La publication du paquet du seul produit (B-0042)
   attend Théo : D-0037 (pip depuis GitHub, PyPI, une archive, ou rien).
3. Ensuite B-0079 (session reprise hors de la racine, non détectée), B-0080
   (un clone sans la branche par défaut), B-0081 (une demande à plusieurs
   réponses positives ne valide rien), B-0082 (les noms d'une classe du
   test de mutation). B-0076 revient à Théo.
4. Puis le projet pilote ; B-0071 et B-0066. Les autres sujets ouverts
   attendent des données ou Théo : B-0010, B-0012, B-0009, B-0006, B-0018,
   B-0048, B-0078.
