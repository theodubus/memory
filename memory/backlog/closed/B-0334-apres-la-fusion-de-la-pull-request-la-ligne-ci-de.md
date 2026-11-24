<!-- socle: couche=backlog zone=publique -->
# B-0334 — Après la fusion de la pull request, la ligne CI de socle state dit la dernière exécution de la branche de travail, pas celle du commit de tête : la CI que la fusion lance sur la branche par défaut ne s'y lit pas

> statut : fait · origine : J-2026-11-23-C · lu : backlog@dbd07865 · ref : J-2026-11-24-AK, T-0161

Vu en session le 23 novembre (J-2026-11-23-C) : après la fusion de #81,
la branche de travail repart de la branche par défaut sur le commit de
fusion (15c5d05), mais la ligne « CI » de `socle state` dit encore
« success sur 3480774 », l'ancienne tête. `_ligne_ci`
(`engine/socle/state.py`) lit la dernière exécution de la branche par
son nom (`gh run list --branch`), pas celle du commit de tête. Le skill
`socle-batch` fait attendre les workflows que la fusion lance sur la
branche par défaut ; une boucle qui attend leur conclusion sur le SHA
court de la tête, dans la ligne « CI », n'aboutit jamais.

## Satisfait quand

- [x] après la fusion, la ligne « CI » de `socle state` dit l'exécution du commit de tête, ou qu'il n'en a aucune, jamais celle d'un commit d'avant
