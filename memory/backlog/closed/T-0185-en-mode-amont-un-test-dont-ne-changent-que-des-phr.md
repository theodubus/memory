<!-- socle: couche=backlog zone=publique -->
# T-0185 — En mode amont, un test dont ne changent que des phrases du texte d'un skill du produit passe tests.attendus sans validation

> statut : fait · origine : J-2026-11-25-V · besoin : B-0353 · ref : J-2026-11-25-AB · lu : backlog@41302388

Un commit, dans L-0041, selon ADR-0110 (point 3) : dans
`tests.attendus` (`engine/socle/checks_tests.py`), en mode amont, un test
supprimé ou une assertion changée dont les phrases perdues suivent le
texte d'un gabarit de skill du produit que la plage change, et d'aucun
module Python du moteur, passe sans validation ; l'avertissement des
valeurs changées hors des assertions se tait pour elles ; ses tests ;
l'architecture le dit.

## Fait quand

- [x] en mode amont, une assertion qui perd une phrase qu'un gabarit de skill a quittée passe sans validation, et un test le montre
- [x] une phrase écrite aussi dans un module Python du moteur, une assertion sans phrase, un gabarit qui garde la phrase, et le mode projet restent refusés, et un test le montre
