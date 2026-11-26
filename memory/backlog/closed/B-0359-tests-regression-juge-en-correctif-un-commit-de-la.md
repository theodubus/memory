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

## Modèle de menace

Écrit à la revue de L-0046, après le code : le lot l'avait omis.

Le garde-fou qui change : `tests.regression`. Ce qu'il arrête : un
correctif de code qui ne livre pas de test qui échoue sur son parent ;
hors de tout adaptateur, D-0088 le refuse, sauf une demande validée qui
l'admet. Ce qui reste arrêté : tout correctif qui touche un fichier hors
de la mémoire, le dossier du socle et `AGENTS.md` compris, et un
correctif vide. Ce qui passe désormais, signalé d'un avertissement : un
correctif dont tous les fichiers, hors tiers, sont dans le dossier de la
mémoire, sa zone privée comprise. D-0088 visait du code qu'aucun
adaptateur ne juge, le Dart de JustCook ; une entrée de la mémoire n'est
pas du code, aucun test ne peut prouver sa correction, et une entrée
publiée ne se récrit que par ajout ou par son statut, que les contrôles
de la mémoire jugent. Un agent qui glisserait un correctif de code dans
un commit de la seule mémoire n'en aurait pas : un fichier hors de la
mémoire fait juger le commit comme avant.

## Satisfait quand

- [x] un commit qui ne touche que la mémoire n'est jamais refusé par `tests.regression`, quel que soit son titre ; un correctif qui touche du code hors de tout adaptateur reste refusé comme D-0088 le veut
