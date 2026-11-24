<!-- socle: couche=backlog zone=publique -->
# T-0134 — Le gabarit de socle-batch et le format disent la règle de D-0141 : la tâche qui contredit un test le nomme dès sa création, et sa demande se pose avant le lot

> statut : fait · ref : J-2026-11-24-Y · origine : J-2026-11-21-Q · besoin : B-0303 · après : T-0079 · lu : backlog@6c894b15

Un commit : le gabarit de `socle-batch` (« Former et annoncer »), en français et en anglais, sous son plafond, et le format de la mémoire là où il dit ce qu'est une tâche (`engine/socle/FORMAT.md`), disent la règle que Théo a retenue (D-0141) : écrivant une tâche qui dit ce qu'un comportement doit devenir, l'agent cherche dans les tests ce qui affirme le contraire, nomme ce test dans la tâche et pose la demande aussitôt, avant le lancement du lot ; une note de version.

## Fait quand

- [x] le gabarit de `socle-batch`, son anglais et le format disent la règle de D-0141, et un test le lit
