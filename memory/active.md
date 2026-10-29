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

1. Faits : le retrait du code de compatibilité (J-2026-10-20-U), B-0077
   (J-2026-10-20-X), la documentation, validée par Théo (D-0039,
   J-2026-10-22-B). D-0037 répondue `rien` pour aujourd'hui ; à terme, le
   dépôt de distribution séparé (B-0083), à la première version mûre.
2. Maintenant : le projet pilote (point 6).
3. Faits en attendant le pilote : B-0078, B-0079, B-0080 (J-2026-10-22-C).
   B-0081 et B-0082 faits sur les réponses de Théo (D-0040, D-0041).
4. Faits : B-0066, les skills, selon l'option 1 de D-0042 (ADR-0034,
   J-2026-10-22-H) ; B-0084 (J-2026-10-22-J) ; la CI de l'auto-test
   protégée de la maintenance de git (J-2026-10-22-I).
5. B-0076 fait : la section `[code]` poussée par Théo, le dernier repli de
   compatibilité retiré (D-0044) ; B-0085 fait par Théo (J-2026-10-29-A).
6. Le projet pilote : un projet neuf de Théo, avec BMAD Method, cadrage
   écrit (J-2026-10-29-E). La branche est fusionnée sur `main`
   (J-2026-10-29-K) ; reste l'installation, depuis `main`, dans le dépôt du
   pilote et une session à lui. Attendent le pilote : B-0010, B-0012, B-0071 ; le dépôt de
   distribution : B-0083 ; gardé en tête : B-0048.
