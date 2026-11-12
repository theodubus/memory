<!-- socle: couche=backlog zone=publique -->
# B-0179 — La CI posée échoue quand un adaptateur est là avant le premier fichier de son langage : le cache de Gradle exige un fichier Gradle

> statut : ouvert · origine : J-2026-11-11-Y · priorité : haute · lu : backlog@83423479

Retour du pilote, relayé par Théo le 11 novembre (J-2026-11-11-Y), que la
session du socle n'a pas lu dans le dépôt du pilote. Passé à la version publiée
du socle, avec `python-pytest` en principal et `kotlin` en second, le pilote n'a
encore ni code Kotlin ni fichier Gradle. La CI de sa pull request échoue en
vingt secondes, avant tout contrôle : l'étape `actions/setup-java@v5` que
pose le `ci_setup` de l'adaptateur (`engine/socle/adapters/kotlin.toml`)
demande `cache: gradle`, et ce cache exige au moins un fichier Gradle
(« No file in … matched to [**/*.gradle*, …] »). La CI du socle étant
exigée sur sa branche par défaut, la pull request ne peut pas être
fusionnée : le défaut bloque le pilote, en pause depuis.

Le même motif est à vérifier dans les autres adaptateurs maintenus dont le
`ci_setup` demande un cache : `engine/socle/adapters/java.toml` demande
`cache: maven`.

Trois corrections proposées par le pilote, une seule suffit : retirer le
cache du `ci_setup` ; ne poser l'étape que si le dépôt contient un fichier
de build du langage ; n'ajouter le `ci_setup` d'un adaptateur que si le
dépôt porte déjà une source de son langage. À choisir en ouvrant le sujet :
la seconde garde le cache et ne dépend pas du moment de l'installation.

Théo ne demande pas la correction tout de suite, le pilote étant en pause ;
elle est à faire avant sa reprise.

## Fait quand

- [ ] la CI posée passe sur un projet `python-pytest` et `kotlin` sans aucun fichier `.kt` ni fichier Gradle, ce qu'un cas de l'auto-test ou un test prouve
- [ ] les autres adaptateurs maintenus dont le `ci_setup` demande un cache sont vérifiés de même, et corrigés s'il le faut
- [ ] une version corrigée est publiée, et le pilote peut se mettre à jour
