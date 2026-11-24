<!-- socle: couche=backlog zone=publique -->
# T-0027 — Le balayage de mutation du socle : un job par fichier, le profil de compilation porté par l'adaptateur, des plafonds par fichier

> statut : abandonné · origine : J-2026-11-11-Q · besoin : B-0172 · lu : backlog@9966bbbd · ref : D-0168

Un commit : la CI que pose le socle et l'adaptateur du langage de chess balaient fichier par fichier, avec le profil dédié, sous des plafonds repris de `docs/fabrication/chess/mutation-caps.toml` ; ce qui manque se mesure d'abord sur chess. La mesure sur chess et le retrait de son balayage sont T-0077.

T-0027 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0172, sous « X3 — peaufine la machinerie sans gêne constatée » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] la CI que pose le socle lance un job de mutation par fichier, avec le profil que porte l'adaptateur, et un test le montre
- [ ] les plafonds par fichier sont gardés par le cliquet du socle, et un test le montre
