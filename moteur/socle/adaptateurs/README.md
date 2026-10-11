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

Trois adaptateurs sont maintenus. Ce sont des extraits : les fichiers
[rust.toml](rust.toml), [python.toml](python.toml) et
[python-pytest.toml](python-pytest.toml) font foi. Les deux adaptateurs
Python ne diffèrent que par le lanceur de tests et la mutation : `python`
s'en tient à la bibliothèque standard (`unittest`), sans mutation ;
`python-pytest` prend pytest et mutmut, qui exige pytest.

| Ce que le moteur demande | Rust (repris de chess) | Python (`unittest`) | Python (`pytest`) | Qui s'en sert |
| --- | --- | --- | --- | --- |
| Lancer les tests | `cargo test` | `unittest` | `pytest` | `socle verify`, hook de fin de tour, CI |
| Vérifier le code | `clippy` | compilation de chaque fichier | idem | idem |
| Vérifier le formatage | `cargo fmt` | absent : relecture du diff | idem | idem |
| Reconnaître une fonction de test | `fn` sous `#[test]` | `def test…` | idem | `tests.creux`, `tests.attendus` |
| Reconnaître une assertion | `assert!`, `assert_eq!`… | `assert`, `self.assert…` | `assert`, `pytest.raises` | `tests.creux` : un test sans assertion est refusé |
| Reconnaître un test désactivé | `#[ignore]` | `@unittest.skip` | `@pytest.mark.skip`, `xfail` | `tests.creux` : désactivé sans raison écrite, refusé |
| Rejouer un test sur le commit d'avant | `cargo test` d'un fichier de `tests/` | `unittest` d'un module | `pytest` d'un fichier | `tests.regression` |
| Mesurer la mutation | `cargo-mutants` | absente | `mutmut` | `mutation.couverture`, `socle mutation-verdict` |
| Dire quel code doit être testé, et quelles fonctions sont privées | `src/`, `fn` sans `pub` | hors `tests/`, `def _…` | idem | `tests.code-teste` : une fonction publique ajoutée ou modifiée est nommée par un test |

La mutation consiste à modifier le code exprès (changer un `+` en `-`, un
`<` en `<=`) et à vérifier qu'un test au moins échoue. Un « mutant » qui
survit montre du code qu'aucun test ne vérifie vraiment.

Un projet installé avant qu'une section existe hérite de celle de
l'adaptateur maintenu du même langage, venue avec le moteur : c'est le cas de
la section `[code]`.

## Une capacité absente se déclare

Chaque capacité est soit une commande, soit déclarée absente avec ce qui la
remplace. Rien ne manque en silence : le contrôle `adaptateur.capacites`
refuse une capacité ni fournie ni déclarée. L'adaptateur Python déclare ainsi
le formatage absent (la bibliothèque standard n'a pas de formateur) et la
mutation absente (mutmut exige pytest : l'adaptateur `python-pytest` la
fournit).

## Où il vit

- Les adaptateurs maintenus sont dans ce dossier.
- L'installeur copie celui qu'on choisit (`socle install --adapter rust`)
  dans le projet, sous `.socle/adaptateur.toml`. Le projet y ajoute ses
  étapes propres, par exemple un banc de performance, et y nomme ce qui lui
  est propre : sous `python-pytest`, les modules soumis à la mutation, quand
  son paquet n'est pas sous `src/`.
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

## Le jalon 6 : un second langage, éprouvé

Le jalon 6 a installé le socle, avec l'adaptateur `python-pytest`, sur un
petit projet Python jetable (un convertisseur de chiffres romains testé sous
pytest), et fait tourner toute la chaîne : vérification, contrôles, CI,
balayage `mutmut` et verdict contre le plafond. Un test sans assertion, un
test supprimé, une fonction publique sans test, un correctif sans test de
régression et des tests affaiblis jusqu'à laisser survivre des mutants y ont
chacun été attrapés.

La porte demandait que le moteur ne change pas. Les contrôles, la mémoire et
les hooks n'ont pas changé ; deux corrections ont été nécessaires : le
lecteur des résultats de `mutmut`, propre à cet outil, qui n'avait jamais
tourné, et `tests.code-teste`, qui prenait le moteur installé dans `.socle/`
pour du code du projet, ce que seul un projet Python pouvait montrer. Le
journal (J-2026-10-10-W) en garde le détail.
