<!-- socle: couche=backlog zone=publique -->
# T-0152 — Un projet Compose Multiplatform ou Android a des commandes de compilation et de tests qui lancent ses tests ou échouent en le disant, selon la piste que Théo retient

> statut : fait · origine : J-2026-11-21-Q · besoin : B-0147 · après : T-0151 · ref : D-0191, J-2026-11-25-M · lu : backlog@6c894b15

Un commit, sur la réponse de Théo à la demande de T-0151 : l'adaptateur (`engine/socle/adapters/`) et la spécification des adaptateurs ; une note de version. Si Théo n'en veut rien, la tâche s'abandonne en renvoyant à sa réponse.

## Fait quand

Sur D-0191 (J-2026-11-25-M), l'option retenue : l'installeur le dit, et la
spécification donne les commandes.

- [x] à l'installation comme à la mise à jour, l'installeur nomme les fichiers de Gradle qui déclarent un module multiplateforme ou Android, en clair ou dans le catalogue des versions, tant que la copie `kotlin` garde `./gradlew -q test`, et se tait sinon ; des tests le montrent
- [x] la spécification des adaptateurs dit ce que la copie `kotlin` suppose et donne les commandes selon les modules, et un test le lit
- [x] la note de version le dit, en français et en anglais
