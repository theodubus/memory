<!-- socle: couche=backlog zone=publique -->
# T-0143 — Le cliquet connaît le défaut de chaque seuil que le moteur lit avec une valeur par défaut : une clé absente de la base, écrite plus haut, l'assouplit

> statut : ouvert · origine : J-2026-11-21-Q · besoin : B-0283 · lu : backlog@6c894b15

Un commit : le cliquet (`DEFAUTS`, `engine/socle/checks_ratchet.py`) reçoit, de la même source que le moteur, le défaut de chaque clé de seuil qu'il lit avec une valeur par défaut, dont `[nocopy] min_chars` (200) et `[staleness] active_days` (7), lues dans `checks_docs.py`, `checks_memory.py` et `state.py` ; son défaut injecté et son témoin sain dans l'auto-test ; une note de version. Aucune valeur attendue ne change : aucun test ne tient pour libre une telle clé absente de la base et écrite plus haut (cherché dans `tests/test_cliquet.py` à la création, D-0141). Avant le code, B-0283 reçoit sa section « Modèle de menace ».

## Fait quand

- [ ] une clé de seuil absente de la base, écrite plus haut que le défaut du moteur, est un assouplissement que le cliquet nomme, pour chaque clé que le moteur lit avec un défaut, et un test le montre
- [ ] B-0283 a sa section « Modèle de menace », que `socle show B-0283` montre
