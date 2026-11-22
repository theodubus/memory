<!-- socle: couche=backlog zone=publique -->
# T-0076 — L'installeur ne réaffiche pas en entier un écart de politique déjà montré à la mise à jour précédente

> statut : fait · origine : J-2026-11-18-J · ref : J-2026-11-22-H · besoin : B-0195 · lu : backlog@84ad299e

Un commit : l'installeur reconnaît un écart de la politique du projet à son gabarit qu'une mise à jour précédente a déjà montré (les lignes que l'humain a écrites exprès), et ne le redit qu'en une ligne.

## Fait quand

- [x] un écart de politique déjà montré à la mise à jour précédente tient en une ligne à la suivante, un écart nouveau s'affiche en entier, et un test le montre
