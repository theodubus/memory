<!-- socle: couche=decisions zone=publique -->
# ADR-0026 — Un identifiant que deux branches ont pris se renumérote avant la fusion

> statut : acceptée · date : 2026-10-13 · lu : decisions@a1a1eb4f

## Contexte

À l'essai sur la copie du projet d'échecs (J-2026-10-12-Q@d94a6cc7), cinq
branches parties du même commit ont chacune pris le même premier numéro
de backlog et la même lettre de journal du jour, pour des entrées
différentes (B-0053@da088f8c). `socle new`
calcule l'identifiant sur l'arbre de sa branche, qui ne voit pas les
autres. À la fusion, un identifiant défini deux fois casse toute référence
vers lui, et rien ne le signale avant.

Trois voies. Numéroter à la fusion laisse des identifiants provisoires que
toute référence doit suivre, et la fusion se fait hors de la session de
l'agent. Des identifiants que deux branches ne peuvent pas prendre (une
empreinte, un suffixe de branche) changent le format et ôtent à l'humain
des numéros courts qu'il cite. Reste d'éviter ce qui se voit, et de
refuser avant la fusion ce qui ne se voit pas, avec un outil qui répare.

## Décision

- `socle new` prend le numéro qui suit le plus grand qu'il voit, dans
  l'arbre et dans les branches distantes que le dépôt connaît : deux
  branches poussées ne prennent plus le même.
- Le contrôle `memoire.collisions` refuse, au push et en CI, un
  identifiant que la branche définit et que la base définit aussi pour une
  autre entrée, ajoutée depuis leur point de divergence.
- `socle renumber <ID>` donne à l'entrée de la branche le prochain
  identifiant libre (base, branche, branches distantes), le reporte dans
  chaque fichier que la branche a changé, renomme son fichier quand elle
  en a un, et récrit les citations de son empreinte.

## Conséquences

Deux branches qui créent une entrée sans s'être vues prennent encore le
même identifiant ; la collision est dite avant la fusion, avec la commande
qui la répare, au lieu d'après. Les identifiants gardent leur forme. Pour
défaire : retirer le contrôle et la commande, et `socle new` revient à
l'arbre seul.
