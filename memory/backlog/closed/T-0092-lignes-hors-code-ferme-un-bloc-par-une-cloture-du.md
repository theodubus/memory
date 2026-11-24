<!-- socle: couche=backlog zone=publique -->
# T-0092 — lignes_hors_code ferme un bloc par une clôture du même caractère, au moins aussi longue, et un test le lit

> statut : abandonné · origine : J-2026-11-18-R · besoin : B-0287 · lu : backlog@b1dd0b99 · ref : D-0168

Le livrable de B-0287, un commit : `lignes_hors_code` ferme un bloc
par une clôture du même caractère, au moins aussi longue que celle qui
l'ouvre, comme `_hors_des_blocs_de_code` d'`engine/socle/human.py`, ou
par une même fonction pour les deux.

T-0092 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0287, sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] un test lit, sur un texte où un bloc ~~~ contient une ligne ```, que les lignes du bloc sont dans le code et celles d'après hors du code, et qu'un lien cassé écrit après est signalé
- [ ] un test lit de même un bloc ```` qui contient une ligne ```, et une ligne « ```a``` » ou une clôture suivie d'un texte, que la revue de L-0016, passe 2, a relevés : la lecture des liens et celle du récap y rendent les mêmes lignes
