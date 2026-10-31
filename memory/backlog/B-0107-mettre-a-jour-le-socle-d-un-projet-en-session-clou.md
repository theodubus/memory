<!-- socle: couche=backlog zone=publique -->
# B-0107 — Mettre à jour le socle d'un projet en session cloud sans aller-retour humain dans la session à deux dépôts

> statut : ouvert · origine : J-2026-10-31-I · lu : backlog@67ab3cec

Mettre à jour le socle d'un projet en session cloud oblige à ajouter le
dépôt du socle, privé : la session passe à deux dépôts et, si son
processus redémarre, repart hors de la racine du projet, sans les hooks de
l'agent. Sur le pilote, le prompt de mise à jour lui faisait attendre la
réponse de Théo à la demande d'approbation des fichiers protégés : elle a
redémarré dans l'attente (J-2026-10-31-I).

À faire : une procédure, dans le guide et dans ce que l'installeur
affiche, où la session à deux dépôts ne fait qu'installer, commiter,
pousser sa branche et ouvrir la pull request, d'une traite et sans rien
attendre ; l'approbation des fichiers protégés (une demande validée dans
la conversation, B-0106) se fait ensuite dans une session neuve sur le
seul dépôt du projet, sur la branche de la mise à jour. Ce que B-0083
rendrait inutile : un dépôt de distribution public se clone sans
l'ajouter à la session.
