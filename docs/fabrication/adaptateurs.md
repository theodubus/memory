# La fabrication des adaptateurs

Comment chaque adaptateur maintenu a été éprouvé, et ce que ces essais ont
corrigé. Ce que chacun fait est décrit avec le produit :
[les adaptateurs](../../engine/socle/adapters/README.md).

## Un second langage, éprouvé (jalon 6)

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
journal en garde le détail.

## JavaScript, Go, Java, Ruby et PHP

Cinq adaptateurs de plus, à la demande de Théo. Le banc `bench/adapters.py` éprouve les cinq sur un projet jetable de leur
langage, avec leurs vrais outils : le projet sain passe `socle verify` ; un
test sans assertion, un test désactivé sans raison, une valeur attendue
changée et une fonction publique sans test sont refusés par le contrôle
attendu ; un correctif passe avec son test de régression, rejoué sur le
parent, et il est refusé sans ; le balayage de mutation se lit, et son
verdict passe au plafond mesuré et casse en dessous. Le premier passage a
montré deux défauts, corrigés : en PHP, le lien vers `vendor` faisait
charger à Composer le code de l'arbre de travail dans le worktree de la
régression (d'où `copied`), et la commande de mutant devinait mal ses
sujets (d'où `mutant.yml`). Les étapes de CI que chaque adaptateur ajoute
au workflow, et son balayage hebdomadaire, ont ensuite passé sur GitHub,
dans un dépôt d'essai (F-0019, F-0020).

## C#

Le banc l'éprouve comme les cinq précédents, sur une solution xUnit. Les
étapes de CI qu'il ajoute au workflow, et le balayage hebdomadaire,
passent aussi sur GitHub, dans un dépôt d'essai.
