# Les adaptateurs

## En une phrase

Un adaptateur est un petit fichier de réglages, en TOML, qui apprend au socle
à faire **dans un langage donné** les quelques gestes qu'il ne peut pas
deviner : lancer les tests, reconnaître un test et une assertion dans un
fichier, rejouer un test seul, lancer la mutation.

## Pourquoi il en faut un

Le socle surveille trois choses : la mémoire, la documentation et les tests.
La mémoire et la documentation sont du markdown, que le moteur lit de la même
façon dans n'importe quel projet. Les tests, non : chaque langage les écrit
et les lance à sa manière.

Prenons une règle du socle : **un correctif livre un test qui échoue sur le
commit d'avant**, preuve qu'il attrape le bogue corrigé. Pour l'appliquer, le
moteur doit :

1. trouver le test que le correctif ajoute : en Rust, une fonction précédée
   de `#[test]` ; en Python, une méthode dont le nom commence par `test` ;
2. lancer ce test seul sur le commit d'avant : `cargo test <nom>` en Rust,
   `python3 -m unittest <module>` en Python ;
3. constater qu'il échoue.

Le troisième geste est le même partout : le moteur le fait. Les deux premiers
dépendent du langage : l'adaptateur les lui dit. C'est comme un adaptateur de
prise électrique : l'appareil (le moteur) ne change pas, seule la prise (le
langage) change.

Sans adaptateur, le socle vérifierait encore la mémoire et la documentation,
mais il ne verrait rien des tests.

## Ce qu'il contient

Les deux adaptateurs maintenus, côte à côte. Ce sont des extraits : les
fichiers [rust.toml](rust.toml) et [python.toml](python.toml) font foi.

| Ce que le moteur demande | Rust (repris de chess) | Python | Qui s'en sert |
| --- | --- | --- | --- |
| Lancer les tests | `cargo test` | `unittest` | `socle verify`, hook de fin de tour, CI |
| Vérifier le code | `clippy` | compilation de chaque fichier | idem |
| Vérifier le formatage | `cargo fmt` | absent : relecture du diff | idem |
| Reconnaître une fonction de test | `fn` sous `#[test]` | `def test…` | `tests.creux`, `tests.attendus` |
| Reconnaître une assertion | `assert!`, `assert_eq!`… | `assert`, `self.assert…` | `tests.creux` : un test sans assertion est refusé |
| Reconnaître un test désactivé | `#[ignore]` | `@unittest.skip` | `tests.creux` : désactivé sans raison écrite, refusé |
| Rejouer un test sur le commit d'avant | `cargo test` d'un fichier de `tests/` | `unittest` d'un module | `tests.regression` |
| Mesurer la mutation | `cargo-mutants` | absente pour l'instant | `mutation.couverture`, `socle mutation-verdict` |

La mutation consiste à modifier le code exprès (changer un `+` en `-`, un
`<` en `<=`) et à vérifier qu'un test au moins échoue. Un « mutant » qui
survit montre du code qu'aucun test ne vérifie vraiment.

## Une capacité absente se déclare

Chaque capacité est soit une commande, soit déclarée absente avec ce qui la
remplace. Rien ne manque en silence : le contrôle `adaptateur.capacites`
refuse une capacité ni fournie ni déclarée. L'adaptateur Python déclare ainsi
le formatage absent (la bibliothèque standard n'a pas de formateur) et la
mutation absente (l'outil n'est pas encore éprouvé, voir plus bas).

## Où il vit

- Les adaptateurs maintenus sont dans ce dossier.
- L'installeur copie celui qu'on choisit (`socle install --adapter rust`)
  dans le projet, sous `.socle/adaptateur.toml`. Le projet y ajoute ses
  étapes propres, par exemple un banc de performance.
- Ce fichier est **protégé** : seul l'humain le modifie. Un agent qui
  remplacerait la commande des tests par une commande qui réussit toujours
  rendrait tous les contrôles de tests aveugles.
- Ce dépôt est lui-même écrit en Python : son
  [adaptateur](../../../.socle/adaptateur.toml) est l'adaptateur Python.
  Le socle ne marche donc pas que pour Rust : il tourne en Python ici, à
  chaque commit.

## Pour un autre langage

On écrit un nouveau fichier, avec les mêmes clés ; le moteur ne change pas.
Une seule exception : si l'outil de mutation du langage est nouveau, le
moteur doit apprendre à lire ses résultats (`moteur/socle/mutation.py`, une
fonction par outil ; il en connaît deux, `cargo-mutants` et `mutmut`).

## Ce qui reste à prouver : le jalon 6

L'adaptateur Python sert tous les jours à ce dépôt, mais sans mutation, et le
lecteur des résultats de `mutmut` (l'outil de mutation de Python) est écrit
sans avoir jamais tourné. Le jalon 6 installe le socle sur un petit projet
Python jetable, avec `mutmut`, et fait tourner toute la chaîne. Sa porte :
aucune ligne du moteur ne change pour y arriver.
