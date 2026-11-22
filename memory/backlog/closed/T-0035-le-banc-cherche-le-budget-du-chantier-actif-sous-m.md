<!-- socle: couche=backlog zone=publique -->
# T-0035 — Le juge du scénario s4 lit le budget du chantier actif par le chemin du format actuel

> statut : fait · origine : J-2026-11-13-G · ref : J-2026-11-22-K · besoin : B-0210 · lu : backlog@9966bbbd

Un commit : `_budget_actif` (`bench/bench.py`) prend la clé du chantier actif par le format actuel, sans nom écrit en dur ; un correctif, avec son test.

## Fait quand

- [x] le juge du scénario s4 lit la clé du chantier actif par le chemin du format actuel (`config.FORMAT_ACTUEL.actif`), sans nom écrit en dur
- [x] un test montre qu'il voit un budget relevé dans HEAD et dans l'arbre de travail, et rien quand le budget est inchangé
