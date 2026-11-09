<!-- socle: couche=backlog zone=publique -->
# B-0144 — Python second langage : une mise à jour en automatique pose python-pytest à côté de la copie python déjà là

> statut : ouvert · origine : J-2026-11-09-P · lu : backlog@d1591831

Relevé par la revue du lot d'ADR-0052, et reproduit sur le moteur
d'avant ce lot. Un projet dont Python est le second langage a sa copie
python.toml dans le dossier des adaptateurs des autres langages ; quand
un `conftest.py` apparaît, une mise à jour avec `--adapter auto` détecte
`python-pytest` et en pose la copie à côté : deux adaptateurs du même
langage, dont les motifs se recouvrent, et que `adaptateur.recouvrement`
refuse ensuite. La boucle de l'installeur sur les adaptateurs à poser ne
compare leur langage qu'à celui du principal, jamais à ceux des copies
déjà présentes.

Fait quand :
- [ ] une mise à jour en automatique ne pose pas un adaptateur d'un langage qu'une autre copie couvre déjà, et un test le montre
