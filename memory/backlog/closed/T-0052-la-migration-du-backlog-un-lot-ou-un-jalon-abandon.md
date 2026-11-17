<!-- socle: couche=backlog zone=publique -->
# T-0052 — La migration du backlog : un lot ou un jalon abandonné développé dans un après, un critère sur plusieurs lignes coupé, les tâches posées qui gardent les anciens numéros

> statut : fait · origine : J-2026-11-16-V · besoin : B-0265 · lu : backlog@9aec7323 · ref : J-2026-11-17-O

Relevé par la revue du lot L-0013, passe 1 (J-2026-11-16-V), constats 2,
3 et 4 pour le backlog, de même nature : la migration du backlog en
quatre formes (`engine/socle/migration.py`, ADR-0083) perd ou déplace un
contenu sans le dire. À faire avant la mise à jour de chess.

- Un lot ou un jalon abandonné se développe dans un `après` (vers les
  lignes 166-173 et 189-199) : un besoin fait qui attendait un lot
  abandonné se met à attendre les besoins encore ouverts de ce lot, et
  `memoire.ordre` refuse alors une entrée close avant ce qu'elle attend.
- Un critère écrit sur plusieurs lignes est coupé (vers 233-241 et
  `_renvoyer`, vers 269-284) : la tâche n'en reçoit que la première
  ligne, et la suite reste dans le besoin, sous sa case de renvoi.
- Les tâches posées lisent leur besoin avant la réécriture des mentions
  (vers 238-253) : leur titre garde l'ancien numéro (dans ce dépôt, T-0012
  dit « B-0224 a réuni 22 sujets », que son besoin B-0233 dit JA-0005).

Le livrable, un commit : les trois cas corrigés dans la migration, et le
titre de T-0012 dans ce dépôt.

## Fait quand

- [x] une entrée close qui attendait un lot ou un jalon clos ne se met à attendre rien d'ouvert après la migration, et un test le montre
- [x] un critère sur plusieurs lignes passe entier dans la tâche posée, et un test le montre
- [x] le titre et le corps d'une tâche posée citent les identifiants actuels, et un test le montre
