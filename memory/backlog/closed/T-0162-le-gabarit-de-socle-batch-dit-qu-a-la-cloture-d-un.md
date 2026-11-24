<!-- socle: couche=backlog zone=publique -->
# T-0162 — Le gabarit de socle-batch dit qu'à la clôture d'un lot, une tâche ouverte qu'aucun lot formé ne prend forme un lot nouveau dans le jalon de son besoin

> statut : fait · ref : J-2026-11-24-Y · origine : J-2026-11-23-E · besoin : B-0335 · après : T-0079 · lu : backlog@f95c1458

Un commit : le gabarit français et anglais de `socle-batch`
(`engine/socle/templates/skills/socle-batch/`), étape 5 de « Intégrer,
pousser, livrer », dit qu'à la clôture d'un lot, chaque tâche que sa
revue a ouverte rejoint le prochain lot dont la règle s'applique, ou, à
défaut, forme un lot nouveau dans le jalon de son besoin ; sa note de
version. Le gabarit français fait 7 998 octets pour un plafond de 8 000 :
la phrase se paie d'un resserrement ailleurs. Sa copie protégée se remet
avec celles de L-0026 (T-0136).

## Fait quand

- [x] les deux gabarits de `socle-batch` le disent, sous leur plafond, et les tests des skills passent
