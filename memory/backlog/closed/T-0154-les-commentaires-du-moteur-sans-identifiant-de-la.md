<!-- socle: couche=backlog zone=publique -->
# T-0154 — Les commentaires du moteur sans identifiant de la mémoire de l'atelier, gardés par un test, selon la règle que Théo retient

> statut : abandonné · origine : J-2026-11-21-Q · besoin : B-0271 · après : T-0153 · lu : backlog@6c894b15 · ref : D-0168

Un commit, sur la réponse de Théo à la demande de T-0153 : chaque renvoi d'un commentaire du moteur à la mémoire de l'atelier remplacé par sa raison en clair, et un test qui le garde, comme `tests/test_notes_de_version.py` garde le guide et les notes ; `engine/socle/hooks.py` et `engine/socle/commands.py` n'y entrent que si la réponse de Théo les y met. Si Théo n'en veut rien, la tâche s'abandonne en renvoyant à sa réponse.

T-0154 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0271, sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] un test échoue sur un commentaire du moteur qui cite un identifiant de la mémoire de l'atelier, hors de ce que la règle retenue exempte, et le moteur le passe
