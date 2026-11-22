<!-- socle: couche=backlog zone=publique -->
# T-0038 — Les tests de l'outil de mesure de la consommation exercent les branches que la revue a nommées

> statut : ouvert · origine : J-2026-11-12-N · besoin : B-0194 · lu : backlog@9966bbbd

Un commit : des cas dans les tests de l'outil de l'atelier (devenus `tests/test_consommation.py`), ou dans les tests de la commande si T-0033 l'a fait entrer dans le produit, pour chaque branche que nomme B-0194.

## Fait quand

- [ ] chacune des mutations que nomme B-0194, injectée une à une, fait échouer un test
