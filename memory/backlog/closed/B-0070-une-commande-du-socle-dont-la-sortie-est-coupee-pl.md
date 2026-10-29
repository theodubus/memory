<!-- socle: couche=backlog zone=publique -->
# B-0070 — Une commande du socle dont la sortie est coupée plante avec une trace Python

> statut : fait · origine : J-2026-10-19-G · lu : backlog@5d3fe98c · ref : J-2026-10-20-F

Constaté le 19 oct. : `python3 .socle/socle show --index backlog | head -1`
imprime la première ligne, puis une trace Python (BrokenPipeError) quand
`head` ferme le tube. Un agent coupe souvent une sortie ainsi ; la trace
fait croire à une panne. Le lanceur devrait traiter un tube fermé comme
une fin normale, avec un test qui échoue sans.
