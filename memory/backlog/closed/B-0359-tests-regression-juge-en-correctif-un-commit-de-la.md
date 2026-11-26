<!-- socle: couche=backlog zone=publique -->
# B-0359 — tests.regression juge en correctif un commit de la mémoire seule intitulé « Correction : … », et exige un test qu'aucun adaptateur ne peut donner

> statut : fait · origine : J-2026-11-26-AA · ref : B-0323, D-0088, J-2026-11-26-AH · lu : backlog@dd11ac18

La gêne 4 de la mise à jour de chess du 26 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-26.md`) : un commit qui ne
touche que la mémoire, intitulé « Correction : … », suit le motif des
correctifs (`(?i)^(fix|corrige|correctif|correction)\b`) ; ne touchant
aucun fichier d'un adaptateur, il tombe sous la règle de D-0088, faite
pour du code qu'aucun adaptateur ne juge : refusé sans une demande
validée, ou une réécriture de l'historique, une fois poussé. Corriger une
entrée de la mémoire est un geste ordinaire, qu'aucun test ne prouve.

## Satisfait quand

- [x] un commit qui ne touche que la mémoire n'est jamais refusé par `tests.regression`, quel que soit son titre ; un correctif qui touche du code hors de tout adaptateur reste refusé comme D-0088 le veut
