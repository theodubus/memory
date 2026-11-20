<!-- socle: couche=backlog zone=publique -->
# B-0299 — Le refus de la clôture d'un lot relu compte le lot lui-même parmi les entrées qu'il a closes

> statut : abandonné · origine : J-2026-11-19-N · ref : D-0144 · lu : backlog@30eea4fa

Relevé par la revue de L-0015, passe 1 (J-2026-11-19-N), constat 2 pour
le backlog. Le refus de la clôture d'un lot relu sans recul (T-0055)
montre les entrées ouvertes et closes depuis le début du lot ;
`entrees_depuis` (`engine/socle/review.py`) n'en exclut pas le lot
lui-même, qui apparaît parmi celles qu'il a closes : du bruit dans la
deuxième question du recul, à chaque refus de clôture.

Abandonné le 20 novembre par D-0144 : le recul se retire (T-0110), et cette entrée avec lui.

## Satisfait quand

- [ ] le refus de la clôture d'un lot ne compte pas le lot parmi les entrées qu'il a closes
