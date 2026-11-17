<!-- socle: couche=backlog zone=publique -->
# T-0057 — La commande socle roadmap : ses formats compact et détaillé, par lot et par besoin, et l'alerte d'un ordre de lots ambigu

> statut : fait · origine : J-2026-11-16-AD · besoin : B-0274 · ref : J-2026-11-17-Q · lu : backlog@c366bd9b

La première tâche de B-0274 (J-2026-11-16-AD) : la commande
`socle roadmap` et ses deux formats, selon la spécification de B-0274,
dans le produit, en français et en anglais, avec la note de version.

## Fait quand

- [x] `socle roadmap` donne le format compact, et `--format markdown` le format détaillé, par lot et `--by need` par besoin, sur un backlog d'essai à deux jalons, trois lots et des besoins hors lot, et un test le montre
- [x] deux lots qui attendent le même lot sans ordre entre eux sont signalés, et un test le montre
- [x] la sortie par défaut détaille le lot en cours et les deux suivants, les autres en une ligne, et `--all` les détaille tous
