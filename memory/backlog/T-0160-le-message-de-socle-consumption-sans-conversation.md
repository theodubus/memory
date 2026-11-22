<!-- socle: couche=backlog zone=publique -->
# T-0160 — Le message de socle consumption sans conversation à mesurer dit pourquoi : aucun dossier trouvé, ou un dossier donné que les filtres vident

> statut : ouvert · origine : J-2026-11-22-Q · besoin : B-0333 · lu : backlog@3a8162c0

Un commit : le message de `cmd_consumption` distingue un dossier
introuvable d'un dossier donné, ou trouvé, que les filtres vident, en
français et en anglais ; un test pour chacun.

## Fait quand

- [ ] un test montre le message d'un dossier introuvable, et celui d'un dossier donné que `--day` vide, en français et en anglais
