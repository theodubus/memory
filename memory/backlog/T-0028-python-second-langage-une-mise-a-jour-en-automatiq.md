<!-- socle: couche=backlog zone=publique -->
# T-0028 — L'installeur ne pose pas un adaptateur d'un langage que couvre déjà une copie présente

> statut : ouvert · origine : J-2026-11-09-P · besoin : B-0144 · lu : backlog@9966bbbd

Un commit : la boucle de l'installeur sur les adaptateurs à poser compare leur langage à celui de chaque copie déjà là, pas seulement du principal ; un correctif, avec son test qui échoue sur le commit parent.

## Fait quand

- [ ] une mise à jour avec `--adapter auto`, sur un projet qui a déjà une copie de l'adaptateur `python` pour son second langage et un `conftest.py` neuf, ne pose pas `python-pytest`, et un test qui échoue sur le commit parent le prouve
