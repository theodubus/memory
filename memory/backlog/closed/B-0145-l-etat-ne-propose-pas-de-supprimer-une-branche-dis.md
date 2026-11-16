<!-- socle: couche=backlog zone=publique -->
# B-0145 — L'état ne propose pas de supprimer une branche distante que la branche de travail poussée contient en entier

> statut : fait · origine : J-2026-11-10-D · lu : backlog@13100dad · ref : J-2026-11-10-F

`human.branches_a_supprimer` ne propose de supprimer qu'une branche
distante que la branche par défaut contient en entier (B-0112). Une
branche fusionnée dans la branche de travail, poussée, n'y figure qu'après
la fusion de sa pull request : ce matin, `ccr-7128ec56-nnvoun-v2`, dont
les cinq commits sont dans la PR #26, n'était pas dite à Théo, qui l'a
relevé (J-2026-11-10-D). Son contenu est déjà sur le distant : la
supprimer ne perd rien.

L'état la dirait à supprimer, en nommant la branche poussée qui la
contient ; la branche par défaut et celles que la politique garde restent
exclues, comme la branche courante.

## Satisfait quand

- [x] l'état liste à supprimer une branche distante que la branche de travail poussée contient en entier, et un test le montre
