<!-- socle: couche=backlog zone=publique -->
# B-0140 — Un changement qui attend une demande ne peut ni se commiter ni se pousser : il ne vit que dans le conteneur, perdu s'il est recyclé

> statut : ouvert · origine : J-2026-11-09-A · lu : backlog@86b86f08

Un test dont la valeur attendue change, en attendant la demande qui le
nomme, peut rester dans l'arbre à la fin du tour, mais ne se commite qu'après
la réponse : le travail qui le porte (le skill `socle-resume`, l'adaptateur
`kotlin`) ne vit alors que dans le conteneur de la session, qu'un recyclage
perdrait. Théo s'en est inquiété (J-2026-11-09-A). Un fichier protégé, lui,
se commite et se pousse sous sa demande en attente quand la CI est exigée,
la CI le refusant jusqu'à la réponse (D-0071). Le hook de l'environnement
relance aussi l'agent tant que l'arbre a des changements.

Piste : la même tolérance pour un test sous sa demande en attente, poussée
telle quelle, la CI refusant jusqu'à la réponse ; c'est assouplir le
contrôle des valeurs attendues, donc une demande.

Fait quand :
- [ ] Théo a tranché, et un test sous sa demande en attente se pousse, ou la raison de ne pas le faire est écrite
