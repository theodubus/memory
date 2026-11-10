<!-- socle: couche=backlog zone=publique -->
# B-0147 — L'adaptateur kotlin suppose des modules JVM : sur Compose Multiplatform ou Android, sa compilation casse, ses tests sont sautés sans erreur et sa mutation manque

> statut : ouvert · origine : J-2026-11-10-H · lu : backlog@0f220088

La copie `kotlin` suppose des modules JVM (J-2026-11-10-H, sur un
prototype Compose Multiplatform du pilote : module Android seul, AGP 8.13,
Kotlin 2.4.21, Gradle 8.14.3). `./gradlew -q testClasses` échoue sans
module qui applique le plugin java ; dans un module Android, `test` lance
`testDebugUnitTest` et `testReleaseUnitTest`, mais un module
multiplateforme nomme ses tests `jvmTest`, ou `allTests`, que `test` ne
lance pas : ils seraient sautés sans erreur. La tâche `pitest` n'existe
pas : le plugin Gradle de PIT ne gère que les modules JVM. Les motifs de
mutation ne couvrent que `src/main/kotlin` ; ceux du code et des tests
couvrent déjà les dossiers `*Main` et `*Test`.

Pistes du pilote : le dire dans la spécification des adaptateurs ; une
variante maintenue `kotlin-multiplatform` (`allTests`, compilation par
tâche de cible, mutation absente ou limitée aux modules JVM) ; ou des
commandes qui échouent bruyamment quand aucun module n'a la tâche visée.
Le pilote adapte sa copie par une demande en attendant.

## Fait quand

- [ ] un projet Compose Multiplatform ou Android a des commandes de compilation et de tests qui lancent ses tests, ou échouent en le disant, et la spécification des adaptateurs dit ce que la copie `kotlin` suppose
