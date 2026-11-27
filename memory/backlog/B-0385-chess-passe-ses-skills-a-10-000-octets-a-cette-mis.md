<!-- socle: couche=backlog zone=publique -->
# B-0385 — Chess passe ses skills à 10 000 octets à cette mise à jour, comme l'annonçait l'option A de D-0223

> statut : ouvert · origine : J-2026-11-27-AY · ref : D-0241, D-0223 · lu : backlog@08d230c4

Théo a choisi, le 26 novembre (D-0223, option A), de relever le plafond
des skills de 8 000 à 10 000 octets, ici et dans le gabarit des
garde-fous, et son texte disait : « Chaque projet installé, dont chess,
aura à valider la même valeur à sa mise à jour ». Le point 13 du prompt
de mise à jour ne fait poser cette demande à chess que si un skill
approche de son plafond : chess garde 8 000, et L-0056 a resserré deux
skills pour y tenir (T-0224), l'option C que Théo n'avait pas choisie.
Trois gabarits sont à 41, 46 et 99 octets de 8 000 (revue de cap 12,
J-2026-11-27-AX). Sur D-0241, le prompt fait poser la demande à chess à
cette mise à jour ; chess à 10 000, Théo dit ce que devient
`TestLePlafondDesProjetsInstalles`, qui garde les gabarits sous 8 000.

## Satisfait quand

- [x] le prompt de mise à jour de chess lui fait poser à Théo la demande de reprendre 10 000 octets pour ses skills, en nommant la clé
- [ ] chess à 10 000, Théo a dit ce que devient le test qui garde les skills du produit sous 8 000 octets
