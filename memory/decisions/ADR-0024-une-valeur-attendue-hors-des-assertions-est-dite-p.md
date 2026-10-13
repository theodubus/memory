<!-- socle: couche=decisions zone=publique -->
# ADR-0024 — Une valeur attendue hors des assertions est dite, pas refusée

> statut : acceptée · date : 2026-10-13 · lu : decisions@a0fade71 · source : fichier:docs/recul.md

## Contexte

Changer une valeur attendue exige une validation humaine (politique, point
2 ; ADR-0017@9e0e51eb). Le contrôle `tests.attendus` ne lisait que les
lignes d'assertion : une valeur écrite ailleurs (une variable, une
constante, une table de Go, un paramètre, une aide qui affirme) changeait
sans bruit, d'après le relevé de la passe de recul (section D), qui
proposait de comparer les valeurs par leurs littéraux. Une assertion écrite
sur plusieurs lignes est déjà lue en entier depuis J-2026-10-13-B@904189de.

## Décision

- Les littéraux d'un test (chaînes, nombres, booléens, nul, hors de ses
  commentaires, attributs et ligne de définition compris) se comparent
  avant et après ; ceux du fichier de test hors de tout test (une
  constante, une aide) aussi, rattachés à chaque test qui nomme la
  constante ou l'aide. Dans un fichier de code, seul le module de tests
  compte, jamais le code de production.
- Une valeur ainsi retirée ou changée est dite, pas refusée : un
  avertissement par fichier, qui nomme les tests, à la fin du tour, au
  commit et en CI, sauf si une validation ou une spécification de l'humain
  nomme le test.
- L'assertion, lue en énoncé entier, reste le refus.

Mesuré avant de choisir : la version qui refuse aurait refusé à tort 34
tests sur la plage de cette branche, tous pour des chemins de fixtures que
la migration de format a renommés (B-0032@71e92526). Rien, dans le texte d'un test,
ne distingue une donnée d'une valeur attendue ; un refus sur cette base
ferait d'un renommage mécanique une décision humaine.

## Conséquences

Une valeur attendue déplacée hors de l'assertion n'échappe plus au regard :
l'agent et le relecteur la voient à chaque étage, et l'agent sait qu'il doit
poser une demande si c'en est une. Elle n'est pas bloquée : un agent qui
ignore l'avertissement passe, ce qui reste la faiblesse connue. Pour
durcir, l'avertissement devient un refus dans `moteur/socle/controles_tests.py`,
au prix des refus à tort mesurés ; pour défaire, retirer la comparaison des
littéraux.
