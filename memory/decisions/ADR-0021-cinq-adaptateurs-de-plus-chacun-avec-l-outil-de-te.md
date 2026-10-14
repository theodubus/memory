<!-- socle: couche=decisions zone=publique -->
# ADR-0021 — Cinq adaptateurs de plus, chacun avec l'outil de tests et de mutation le plus courant

> statut : acceptée · date : 2026-10-11 · source : J-2026-10-11-Q@9e45f044 · lu : decisions@7945802c

## Contexte

Théo veut des adaptateurs pour d'autres langages courants que Rust et
Python (B-0030@b2175cfd). Un adaptateur maintenu doit être éprouvé, comme le
second adaptateur Python l'a été au jalon 6 (ADR-0012@af7986fb), et le
moteur ne doit connaître aucun langage. Chaque langage a plusieurs outils de
tests et de mutation ; il faut en choisir un par adaptateur.

## Décision

Cinq adaptateurs maintenus de plus, chacun avec l'outil le plus courant de
son langage et un outil de mutation qui écrit un rapport lisible :
JavaScript et TypeScript (vitest, Stryker), Go (go test, gremlins), Java
(Maven, JUnit 5, PIT), Ruby (RSpec, mutant), PHP (PHPUnit, Infection). Une
variante (jest, Gradle, Minitest) se fait dans la copie du projet.

Le moteur apprend à lire les cinq rapports, et gagne des mécanismes
génériques, chacun réglé par l'adaptateur : un test reconnu sur sa ligne
(`test("…")`, `it "…" do`), dont la description est le nom ; les blocs
fermés par `end` ; les littéraux et commentaires du langage ; les lignes
qui portent une valeur attendue quand ce ne sont pas les assertions ; un
test désactivé lu dans son corps ; les dépendances que le worktree de la
régression lie ou copie ; les modules que la mutation exclut.

Chaque adaptateur est éprouvé par `banc/adaptateurs.py` sur un projet
jetable, avec ses vrais outils, avant d'être maintenu.

## Conséquences

L'installeur déduit l'adaptateur du dépôt pour les cinq langages. Une
fonction publique se reconnaît selon la convention du langage (exportée,
nom en majuscule, `public`) ; ADR-0011@b3a5aa25 s'applique telle quelle.
Les étapes de CI de chaque adaptateur restent à éprouver sur GitHub, et C#
attend un conteneur qui a dotnet.

Pour défaire : retirer un adaptateur de `moteur/socle/adaptateurs/`, et son
lecteur de `moteur/socle/mutation.py` ; les tests de
`tests/test_adaptateurs.py` et du banc diront ce qui casse.
