<!-- socle: couche=backlog zone=publique -->
# B-0069 — Brancher le socle sur les workflows de BMAD par sa personnalisation

> statut : en cours · origine : J-2026-10-19-G · lu : backlog@5d3fe98c

Mesuré à l'essai de cohabitation avec BMAD : la personnalisation
officielle de BMAD, un fichier par skill que son installeur ne touche
jamais, fait porter à ses workflows ce que le socle demande (F-0023). Sans
elle, BMAD finit son travail sans toucher la mémoire du socle, qui refuse
alors de conclure (J-2026-10-19-G).

À faire, quand BMAD est présent : l'installeur du socle pose cette
personnalisation pour les workflows qui changent le code ou décident
(construction, revue, planification) : la mémoire en faits persistants,
l'état au démarrage, et la fin du socle (consigner, vérifier, les deux
lignes). L'état du socle lit les statuts de BMAD (specs en cours, travaux
reportés) : un seul état (B-0054). Le socle garde ce que BMAD ne fait que
demander : l'intention figée d'une spec ne change que par l'humain, et une
approbation se consigne avec son texte exact. À éprouver sur un agent
réel, ce qui consomme l'abonnement : une demande à Théo pour la dépense.
