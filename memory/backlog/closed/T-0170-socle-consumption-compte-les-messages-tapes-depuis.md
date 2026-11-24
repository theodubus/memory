<!-- socle: couche=backlog zone=publique -->
# T-0170 — socle consumption compte les messages tapés depuis le dernier appel du modèle avant le refus, et garde le compte sous --until

> statut : abandonné · origine : J-2026-11-23-U · besoin : B-0340 · lu : backlog@070104b3 · ref : D-0168

Un correctif de `engine/socle/consumption.py` : le compte de `fenetres_limitees` part, pour chaque conversation, de son dernier appel avant le refus ; `tronquer` garde les messages tapés ; leurs tests, qui échouent sur le commit parent ; une note de version.

T-0170 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0340, sous « X6 — de la mesure dont aucune décision ne dépend » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] le message tapé qui provoque le premier refus d'une session au repos compte, et un test le montre
- [ ] sous `--until`, le compte des messages tapés reste, et un test le montre
