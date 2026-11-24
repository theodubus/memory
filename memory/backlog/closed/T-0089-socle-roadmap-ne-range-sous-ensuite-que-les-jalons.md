<!-- socle: couche=backlog zone=publique -->
# T-0089 — socle roadmap ne range sous « Ensuite » que les jalons qu'aucun lot ne sert : un jalon servi par un lot rangé sous un autre jalon n'y passe plus pour un jalon sans lot

> statut : abandonné · origine : J-2026-11-18-P · besoin : B-0274 · lu : backlog@b1dc0a69 · ref : D-0168

Relevé par la revue de L-0016, passe 1 (J-2026-11-18-P). Un lot dont les
tâches servent les besoins de deux jalons se range sous le premier ; le
second passe alors, dans « Ensuite », pour un jalon sans lot, avec ses
besoins que ce lot sert pourtant (`engine/socle/roadmap.py`, la fonction
`ensuite`). Le livrable, un commit : « Ensuite » ne range que les jalons
qu'aucun lot ne sert, ou nomme pour un jalon servi le lot qui le sert ; le
guide, la note de version et le point du prompt de chess disent la règle
retenue.

T-0089 s'abandonne le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`) : son besoin B-0274 est satisfait, et elle ne fait que peaufiner la sortie (X3).

## Fait quand

- [ ] un test de `tests/test_suite_du_projet.py` rend, dans le compact et le détaillé, un backlog où un lot sert deux jalons, et lit que le second n'y passe pas pour un jalon sans lot
