<!-- socle: couche=backlog zone=publique -->
# B-0213 — Le dossier de la revue compare à la base et non à l'ancêtre commun, accepte un --since inconnu ou étranger, et donne pour barre des sujets touchés en passant

> statut : ouvert · origine : J-2026-11-14-A · lu : backlog@c15dd9a2

La revue de B-0209 (J-2026-11-14-A), constats 1, 2 et 4, de même nature :
la plage que juge le dossier de `socle review`.

- Le diff et les sujets se mesurent par `git diff <base>`, pas depuis
  l'ancêtre commun : quand la branche par défaut a avancé, ses
  changements entrent dans le lot, et les sujets qu'elle seule a touchés
  deviennent la barre du relecteur.
- Un sujet que le lot touche en passant (un `après` changé, un constat
  ajouté à un sujet existant, un sujet clos rangé par `socle archive`)
  est donné en entier comme barre.
- `--since` (et `--base`) acceptent une référence inconnue : « rien à
  relire », code 0 ; un `--since` qui n'est pas un ancêtre de la tête
  montre à l'envers des changements étrangers, et les messages de commits
  fusionnés.

La revue de B-0212 (J-2026-11-14-H), constats 1 à 6 et 9, de même nature,
sur la base que choisit ADR-0075 (`engine/socle/review.py`, commit
f73f0b4) :

- un lot de mémoire seule, pas encore poussé, passe pour un lot déjà
  poussé : le dossier donne le lot précédent ;
- une branche distante en avance sur HEAD par du code n'est pas
  reconnue : le « diff du lot » est l'inverse du commit poussé d'ailleurs ;
- un lot poussé à moitié ne montre que sa partie non poussée, sans note ;
- sans ancêtre commun (clone superficiel), ou quand la branche par défaut
  n'est que devinée, la note donne une raison fausse ;
- sous `--since`, la note du dossier vide propose une commande sans
  `--since`, et un `--since` sur la branche par défaut fait disparaître
  les sujets ;
- des lots poussés qui s'accumulent sur la même pull request se relisent
  ensemble ; la pointe d'avant le dernier push (`<amont>@{1}`, dans le
  reflog) pourrait être proposée comme base.

## Fait quand

- [ ] le dossier mesure le lot depuis l'ancêtre commun, refuse une référence inconnue ou qui n'est pas un ancêtre, et un test le montre
- [ ] un sujet touché sans que son « Fait quand » ou son statut change n'est pas donné comme barre, et un test le montre
- [ ] les cas relevés par la revue de B-0212 sont traités, ou écartés d'une raison, et un test montre chaque cas traité
