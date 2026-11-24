<!-- socle: couche=backlog zone=publique -->
# T-0160 — Le message de socle consumption sans conversation à mesurer dit pourquoi : aucun dossier trouvé, ou un dossier donné que les filtres vident

> statut : abandonné · origine : J-2026-11-22-Q · besoin : B-0333 · lu : backlog@3a8162c0 · ref : D-0168

Un commit : le message de `cmd_consumption` distingue un dossier
introuvable d'un dossier donné, ou trouvé, que les filtres vident, en
français et en anglais ; un test pour chacun.

T-0160 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0333, sous « X3 — peaufine la machinerie sans gêne constatée » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] un test montre le message d'un dossier introuvable, et celui d'un dossier donné que `--day` vide, en français et en anglais
