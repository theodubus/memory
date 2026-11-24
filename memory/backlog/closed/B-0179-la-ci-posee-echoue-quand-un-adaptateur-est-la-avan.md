<!-- socle: couche=backlog zone=publique -->
# B-0179 — La CI posée échoue quand un adaptateur est là avant le premier fichier de son langage : le cache de Gradle exige un fichier Gradle

> statut : abandonné · origine : J-2026-11-11-Y · priorité : haute · lu : backlog@83423479 · ref : D-0168

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

Bloqué depuis le 15 novembre (J-2026-11-15-A) : le dernier critère attend
la mise à jour du pilote, qui est en pause sur la consigne de Théo
(J-2026-11-13-E) et dont le dépôt ne se lit pas d'ici (J-2026-11-09-M).
Le sujet se rouvre à la reprise du pilote, que Théo décide.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « Attendus d'un fait qui n'arrive pas : ils reviennent s'il arrive » : la CI posée qui échouait sur le pilote sans fichier Gradle : corrigée et publiée le 12 novembre ; son dernier critère attend une reprise du pilote que rien ne date. Si sa CI échoue encore, il revient.

## Satisfait quand

- [x] la CI posée passe sur un projet `python-pytest` et `kotlin` sans aucun fichier `.kt` ni fichier Gradle, ce qu'un cas de l'auto-test ou un test prouve
- [x] les autres adaptateurs maintenus dont le `ci_setup` demande un cache sont vérifiés de même, et corrigés s'il le faut
- [x] une version corrigée est publiée (J-2026-11-12-K)
- [ ] le pilote s'est mis à jour, et sa CI passe : la correction n'a pas pu tourner sur GitHub avant
