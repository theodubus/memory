<!-- socle: couche=decisions zone=publique -->
# ADR-0112 — Le contrôle des copies n'exempte d'une consigne que son texte exact, ses lignes citées

> statut : acceptée · date : 2026-11-25 · source : D-0201@04cda4ed, ADR-0016@76982b20, L-0042@39040c48 · lu : decisions@c0b628eb

## Contexte

La couche des consignes (D-0201@04cda4ed) recopie, mot pour mot, la
parole de l'humain consignée au journal ou dans une demande : c'est son
contrat. Le contrôle `docs.copie` refuse un paragraphe de plus de 200
caractères présent dans deux fichiers, une copie qui divergera ; il
refusait trois consignes de ce dépôt à la migration. La première
correction exemptait le fichier des consignes entier, comme les demandes
(ADR-0016@76982b20) ; la revue de L-0042@39040c48 a montré que le contexte
d'une consigne, hors de sa citation, pouvait alors recopier une doc
vivante sans refus.

## Décision

`docs.copie` ne lit pas les lignes citées (`>`) de la couche des
consignes, publique et privée ; le reste d'une consigne se juge comme
tout fichier.

## Modèle de menace

Ce que le contrôle arrête toujours : une consigne dont le contexte, la
ligne de résumé ou l'introduction recopie un paragraphe d'un autre
fichier ; une copie entre deux fichiers hors de la couche.

Ce qu'il laisse passer : une citation identique à un paragraphe
d'ailleurs. À sa source, elle ne diverge pas : le journal est en ajout
seul, une demande répondue est gelée, et le texte exact d'une consigne ne
change jamais (`memoire.ajout-seul`). Une doc vivante qui la recopie
reste refusée contre sa source au journal ; contre une demande, que le
contrôle ne lit pas (ADR-0016), elle ne l'était déjà pas.

## Conséquences

Une consigne se cite telle quelle, sans faux refus. Pour le défaire :
retirer l'exception de `engine/socle/checks_docs.py`, et ses tests dans
`tests/test_consignes.py`.
