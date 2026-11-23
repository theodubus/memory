<!-- socle: couche=backlog zone=publique -->
# T-0170 — socle consumption compte les messages tapés depuis le dernier appel du modèle avant le refus, et garde le compte sous --until

> statut : ouvert · origine : J-2026-11-23-U · besoin : B-0340 · lu : backlog@070104b3

Un correctif de `engine/socle/consumption.py` : le compte de `fenetres_limitees` part, pour chaque conversation, de son dernier appel avant le refus ; `tronquer` garde les messages tapés ; leurs tests, qui échouent sur le commit parent ; une note de version.

## Fait quand

- [ ] le message tapé qui provoque le premier refus d'une session au repos compte, et un test le montre
- [ ] sous `--until`, le compte des messages tapés reste, et un test le montre
