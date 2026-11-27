<!-- socle: couche=backlog zone=publique -->
# B-0382 — La vérification rapide de l'atelier dépasse son seuil de 300 secondes : chaque push attend sa suite de tests entière

> statut : ouvert · origine : J-2026-11-27-AF · ref : D-0237 · lu : backlog@e5be70ef

Mesuré le 27 novembre (J-2026-11-27-AF) : la suite de l'atelier, que
l'étape rapide des tests lance en entier avant chaque push, prend 339
secondes seule et 574 à 580 sous charge, pour un seuil de 300 ; la CI la
relance de toute façon avant chaque fusion. Théo a validé (D-0237) que
ses modules les plus longs se mettent de côté pendant les étapes rapides,
par la variable `SOCLE_RAPIDE` que le moteur pose déjà, la CI les jouant
toujours. Le lanceur de la suite est protégé (D-0130), contrairement à
ce que disait D-0237 : chaque module lent se met de côté lui-même, avec
sa raison écrite, comme le prévoit la règle de la variable. Ni le moteur,
ni l'adaptateur, ni le lanceur ne changent ; aucun test n'est supprimé.

## Satisfait quand

- [ ] la vérification rapide de l'atelier tient sous son seuil de 300 secondes, seule sur la machine
- [ ] la CI joue toujours la suite entière
