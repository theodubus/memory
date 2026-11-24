<!-- socle: couche=backlog zone=publique -->
# B-0292 — L'état ne dit pas d'une branche que son contenu est gardé par la branche de travail poussée quand l'origine n'a plus celle-ci

> statut : fait · origine : L-0017 · lu : backlog@c3bfedf2 · ref : J-2026-11-24-AJ, T-0101

Relevé par la revue de L-0017, passe 1. `branches_contenues_dans_le_travail`
(`engine/socle/human.py`) lit la branche de travail poussée dans les
références du dernier fetch : quand l'origine ne l'a plus (fusionnée par
écrasement puis supprimée, ou supprimée sans fusion) et que la session
reste dessus, l'état dit encore d'une autre branche « déjà contenue dans
`origin/<travail>`, la branche de travail poussée : son contenu ne se
perd pas ». Supprimée sans fusion, la branche de travail ne garde plus
rien : supprimer l'autre perdrait ses commits. Même cause que B-0193 :
une référence que l'origine n'a plus.

## Satisfait quand

- [x] l'état ne dit pas qu'une branche est gardée par une branche de travail que l'origine n'a plus
