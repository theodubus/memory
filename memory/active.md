<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit et borné ; ce qui en sort va au journal.

## En cours

Le lot B-0010 et B-0171 attend une session neuve, sur un autre compte :
ses deux commits et les constats de la revue de B-0010 sont en
correctifs sous `docs/fabrication/passation/`, dont le README dit comment
reprendre (J-2026-11-13-E). Le pilote est en pause (ADR-0059) : B-0179
n'attend que sa reprise. Une question à Théo attend sa réponse : passer
en priorité haute les deux contournements du hook trouvés par B-0171
(les numéros que leur donnera l'intégration). À la fusion du lot, lui
dire que chess peut être mis à jour (J-2026-11-13-C), avec le prompt de
mise à jour complété de ce qui a changé.

## Consignes en cours

Leur texte exact est dans l'entrée du journal citée.

- Opus partout depuis le 12 novembre (D-0095, J-2026-11-12-L).
- Un lot par session : un lot rendu que la fenêtre ne permet pas de
  suivre d'un autre entier, tout se range pour une session neuve, même
  sur un autre compte, et la session le dit avec son prompt
  (J-2026-11-12-P).
- Chaque session travaille sur la branche de son environnement, partie
  de la branche par défaut (J-2026-11-13-A).
- Aucun autre dépôt dans la session, ni lecture de JustCook ou de
  `theodubus/socle` ; donner leurs liens reste permis (J-2026-11-09-M).
- Le pilote est un essai de choc : seules les imperfections du socle se
  corrigent ici (J-2026-10-31-E).
- La documentation se conçoit avant de s'écrire, son plan soumis à Théo
  dans la conversation ; ton formel, sans tutoiement ; chaque question à
  un seul endroit ; elle dit à quoi sert l'outil sans rapporter ses
  essais ; le guide suit le parcours de l'utilisateur ; ses schémas se
  vérifient rendus ; elle n'est faite que validée (J-2026-10-20-Y,
  J-2026-10-21-A, J-2026-10-22-A).
- Une limite d'usage proche décide de l'ordre des sujets, jamais de la
  profondeur du travail (J-2026-11-09-C).
- Une attente annoncée dans le récap s'accompagne d'un réveil programmé
  (J-2026-10-13-N).
- « Pour toi » ne contient que les gestes de Théo, chacun compréhensible
  seul (ce que c'est, pourquoi, ce que change sa réponse) ; ce que
  l'agent fera se dit à part (J-2026-10-31-S, J-2026-10-14-F).
- Les heures données à Théo, à l'heure de Paris (J-2026-10-14-G).
- Un autre dépôt se clone hors du dossier des dépôts de la session, sans
  être déclaré racine ; à chaque reprise, vérifier que l'état a été
  injecté, sinon le dire et ne rien pousser (J-2026-10-14-S).
- Pas de rétro-compatibilité avec une version antérieure du socle
  (J-2026-10-19-A).
- Le but : un produit pratique qui réunit les avantages du socle et ceux
  de BMAD, construits à sa manière (J-2026-10-19-E, D-0051).
- Sessions d'un agent réel sur l'abonnement, chacune plafonnée à
  l'équivalent de 2 dollars, sa consommation rapportée (J-2026-10-19-H).
- En autonomie sur le backlog, sauf arbitrage (J-2026-10-20-C).

## Prochaines étapes

1. Finir le lot selon `docs/fabrication/passation/README.md`.
2. Avant toute nouvelle fonction : B-0142 (avec la gêne 6 de chess), les
   deux contournements de B-0171, B-0176, B-0196 ; puis B-0151, B-0156,
   B-0167, B-0172, B-0197. Ensuite la planification (B-0101), puis la
   répartition entre agents (B-0055).
