<!-- socle: couche=backlog zone=publique -->
# T-0100 — socle roadmap --by need donne les lots d'un besoin dans leur ordre d'exécution, pas dans l'ordre des identifiants de ses tâches

> statut : abandonné · origine : L-0016 · besoin : B-0274 · lu : backlog@9e54ec4a · ref : D-0168

Relevé par la revue de L-0016, passe 2. `_lots_du_besoin`
(`engine/socle/roadmap.py`) donne les lots d'un besoin dans l'ordre des
identifiants de ses tâches : sur ce dépôt, `socle roadmap --by need`
rend B-0274 avec « L-0006, L-0007, L-0016 », quand l'ordre d'exécution
est L-0016, L-0006, L-0007, que le guide et la note 2026-11-18-c disent
suivre strictement. Le livrable, un commit : les lots d'un besoin
viennent dans l'ordre d'exécution, dans le compact et le détaillé.

T-0100 s'abandonne le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`) : son besoin B-0274 est satisfait, et elle ne fait que peaufiner la sortie (X3).

## Fait quand

- [ ] un test de `tests/test_suite_du_projet.py` rend, lu par besoin, un besoin dont les tâches sont dans deux lots ordonnés à l'inverse de leurs identifiants, et lit les lots dans l'ordre d'exécution
