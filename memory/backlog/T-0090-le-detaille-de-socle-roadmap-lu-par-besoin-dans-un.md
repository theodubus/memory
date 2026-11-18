<!-- socle: couche=backlog zone=publique -->
# T-0090 — Le détaillé de socle roadmap lu par besoin dans un backlog sans jalon : un test lit son titre « Besoins, dans l'ordre des lots »

> statut : ouvert · origine : J-2026-11-18-P · besoin : B-0274 · lu : backlog@f9db3bd9

Relevé par la revue de L-0016, passe 1 (J-2026-11-18-P). Le format
détaillé lu par besoin, dans un backlog sans aucun jalon, rend le titre
« ### Besoins, dans l'ordre des lots » (`engine/socle/roadmap.py`) ; un
test l'assertait avant L-0016, aucun ne le lit plus. Le livrable, un
commit : un test qui le lit.

## Fait quand

- [ ] un test de `tests/test_suite_du_projet.py` rend le détaillé lu par besoin d'un backlog sans jalon et lit son titre et le tableau des tâches de chaque besoin
