<!-- socle: couche=backlog zone=publique -->
# T-0077 — Sur chess, le balayage de mutation du socle mesuré contre le sien, puis le sien retiré

> statut : ouvert · origine : J-2026-11-18-J · besoin : B-0172 · après : T-0027 · lu : backlog@84ad299e

Ce que produit la mise à jour de chess qui suit T-0027 : le balayage du socle y tourne, ses mutants survivants comparés à ceux du balayage propre à chess, puis celui-ci retiré ; le prompt de mise à jour de chess le dit.

## Fait quand

- [ ] le relevé de la mesure, dans `docs/fabrication/chess`, montre le balayage du socle dans la durée de la CI de chess, avec les mêmes mutants survivants que le sien
- [ ] la mise à jour de chess retire son balayage propre
