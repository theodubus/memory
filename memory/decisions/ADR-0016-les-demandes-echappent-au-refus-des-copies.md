<!-- socle: couche=decisions zone=publique -->
# ADR-0016 — Les demandes échappent au refus des copies

> statut : acceptée · date : 2026-10-11 · source : B-0019@50bfd468 · lu : decisions@0e56344c

## Contexte

`docs.copie` refuse un paragraphe d'au moins 200 caractères présent dans deux
fichiers Markdown : une copie finit par diverger. En faisant B-0019, Théo a
approuvé ses changements protégés en deux fois : une demande d'approbation
pour le workflow et le hook git, une autre pour le verrou du moteur. Les
deux demandes sortent du même gabarit, dont les paragraphes fixes sont
longs, et le hook avant commit a refusé le commit pour copie. Toute
seconde approbation sur une branche aurait buté de même.

## Décision

`docs.copie` ne lit pas les demandes (`memoire/demandes/`, et leur miroir
privé). Le contrat d'une demande (ADR-0003@a701a157) veut qu'elle se lise
seule, son contexte résumé sur place plutôt que renvoyé ailleurs : la
recopie y est voulue. Et une demande répondue est gelée, elle ne peut plus
diverger de sa source.

## Conséquences

Une demande peut reprendre mot pour mot un paragraphe de la doc ou d'une
autre demande sans être refusée. Les autres couches de la mémoire et la
documentation restent soumises au contrôle. Pour défaire : retirer
l'exclusion dans `moteur/socle/controles_docs.py` ; le test de
`tests/test_approbation.py` qui l'exige échouera, et il faudra alors
fusionner les approbations d'une même branche.
