<!-- socle: couche=backlog zone=publique -->
# T-0159 — Des cas de test attrapent les trois mutations de bord de la mesure de la consommation que la revue de L-0009 a nommées

> statut : abandonné · origine : J-2026-11-22-Q · besoin : B-0332 · lu : backlog@3a8162c0 · ref : D-0168

Un commit : trois cas dans `tests/test_consommation.py`, deux relevés
égaux au centième dans `_segments` et dans `points_de_semaine`, et une
conversation principale dans `concurrence` ; chaque mutation injectée
une à une, puis retirée.

T-0159 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0332, sous « X6 — de la mesure dont aucune décision ne dépend » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] chacune des trois mutations que nomme B-0332, injectée seule, fait échouer un test
