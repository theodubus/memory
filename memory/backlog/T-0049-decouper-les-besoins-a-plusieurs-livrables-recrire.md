<!-- socle: couche=backlog zone=publique -->
# T-0049 — Découper les besoins à plusieurs livrables, récrire leurs critères en résultats, refaire les lots du jalon en cours

> statut : ouvert · origine : J-2026-11-16-U · besoin : B-0265 · lu : backlog@9966bbbd

La seconde moitié du point 8 de D-0123, pour une session neuve. La
migration (ADR-0083) a posé une tâche par besoin qu'attendait un lot
ouvert, de T-0001 à T-0048 : chacune reprend tels quels les critères de
son besoin, dont la section « Satisfait quand » renvoie à elle. Reste, par
l'agent :

- découper chaque besoin ouvert qui demande plusieurs livrables en tâches,
  un commit chacune (`python3 .socle/socle new task "…" --need B-NNNN`) ;
  une tâche de la migration se récrit en l'une d'elles, ou s'abandonne en
  renvoyant au besoin ;
- récrire les critères de chaque besoin en résultats, jamais en
  implémentation, et ceux de ses tâches en livrables qu'un test vérifie ;
- refaire les lots du jalon en cours, JA-0005 (L-0005 à L-0010, puis
  L-0012), avec ces tâches, chacune dans un lot au plus ;
- les besoins que l'état dit à découper, hors des lots, reçoivent leurs
  tâches quand ils sont pris.

## Fait quand

- [ ] chaque tâche ouverte du jalon en cours est un livrable d'un commit, et `python3 .socle/socle state` n'y dit plus de besoin à découper
- [ ] les critères des besoins ouverts du jalon en cours disent des résultats, et ceux de leurs tâches des livrables qu'un test vérifie
- [ ] les lots du jalon en cours n'attendent que ces tâches, et `python3 .socle/socle check` passe
