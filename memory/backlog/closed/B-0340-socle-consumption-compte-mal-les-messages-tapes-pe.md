<!-- socle: couche=backlog zone=publique -->
# B-0340 — socle consumption compte mal les messages tapés pendant une limite : il manque celui qui provoque le refus, et le compte disparaît sous --until

> statut : abandonné · origine : J-2026-11-23-U · lu : backlog@070104b3 · ref : D-0168

Relevé par la passe 2 de la revue de L-0023 (J-2026-11-23-U), constats
4 et 5 pour le backlog, sur le compte des messages tapés que la passe 1
a ajouté à `socle consumption` (`engine/socle/consumption.py`) :

1. Le compte prend les messages tapés après le premier refus
   (`refus < h`). Quand la session est au repos, le premier refus suit de
   quelques millisecondes le message tapé qui l'a provoqué, que le compte
   exclut ; le skill `socle-resume`, lui, le compte depuis la passe 2.
2. `tronquer`, que `socle consumption --until` emploie, reconstruit
   chaque conversation sans ses messages tapés : sous `--until`, la ligne
   du rapport ne paraît jamais.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X6 — de la mesure dont aucune décision ne dépend » : le compte des messages tapés pendant une limite. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] `socle consumption` compte, dans chaque fenêtre close par un refus, les messages tapés depuis le dernier appel du modèle avant le refus, avec ou sans `--until`
