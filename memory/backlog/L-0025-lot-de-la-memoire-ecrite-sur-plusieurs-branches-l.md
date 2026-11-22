<!-- socle: couche=backlog zone=publique -->
# L-0025 — Lot de la mémoire écrite sur plusieurs branches : l'identifiant de next-id, la renumérotation après un cherry-pick, l'index que cite un sous-agent

> statut : ouvert · origine : J-2026-11-21-P · après : L-0024, T-0118, T-0128, T-0129 · lu : backlog@6c894b15

La mémoire écrite sur plusieurs branches ou worktrees : `socle next-id`, qui calcule l'identifiant comme `socle new` (T-0118, B-0314), et `socle renumber` après un cherry-pick (T-0128, B-0315), dans `engine/socle/identifiers.py` et `tests/test_identifiants.py` ; l'index du backlog que cite une entrée ouverte par un sous-agent, que le hook avant envoi refuse quand la branche a été poussée depuis son départ (T-0129, B-0272, `memoire.lectures`, `tests/test_lectures.py`), un garde-fou dont le modèle de menace s'écrit avant le code. Il passe tôt : chaque lot qui suit intègre les entrées de ses sous-agents. Formé le 21 novembre, sur la décision de Théo (D-0154, J-2026-11-21-Q).
