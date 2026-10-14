<!-- socle: couche=decisions zone=publique -->
# ADR-0009 — Le récap de fin d'intervention dit aussi la suite

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-N@29b0a201 · lu : decisions@f991d721

## Contexte

ADR-0007@ac16270e exige qu'une intervention qui a agi se termine par une
ligne « Pour toi : ». Théo veut y lire aussi la suite : lance-t-on le jalon
suivant, reste-t-il quelque chose à faire avant ?

## Décision

Le récap se termine par deux lignes, que le hook de fin de tour exige toutes
deux quand l'agent a agi :

- « Pour toi : » ce qui revient à l'humain, ou « rien » ;
- « Ensuite : » la suite proposée, et ce que l'agent attend s'il attend
  quelque chose (une CI, un match : quoi, et jusqu'à quand).

Quand une ligne manque, le hook bloque une fois et rappelle, en plus de ce
qui revient à l'humain, la section « Prochaines étapes » du chantier actif.
Les marqueurs se règlent par projet (`[human] recap_markers`).

## Conséquences

La suite écrite dans le récap et celle du chantier actif peuvent diverger ;
rien ne les confronte, le hook ne fait que rappeler la seconde.

La vérification du récap rend désormais la liste des lignes manquantes au
lieu d'un oui ou non : les valeurs attendues de `test_dernier_texte_de_l_agent`
et de `test_sans_recap`, dans `tests/test_humain.py`, changent en
conséquence.
