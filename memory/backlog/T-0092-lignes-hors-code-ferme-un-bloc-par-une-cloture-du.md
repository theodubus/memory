<!-- socle: couche=backlog zone=publique -->
# T-0092 — lignes_hors_code ferme un bloc par une clôture du même caractère, au moins aussi longue, et un test le lit

> statut : ouvert · origine : J-2026-11-18-R · besoin : B-0287 · lu : backlog@b1dd0b99

Le livrable de B-0287, un commit : `lignes_hors_code` ferme un bloc
par une clôture du même caractère, au moins aussi longue que celle qui
l'ouvre, comme `_hors_des_blocs_de_code` d'`engine/socle/human.py`, ou
par une même fonction pour les deux.

## Fait quand

- [ ] un test lit, sur un texte où un bloc ~~~ contient une ligne ```, que les lignes du bloc sont dans le code et celles d'après hors du code, et qu'un lien cassé écrit après est signalé
