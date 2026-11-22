<!-- socle: couche=backlog zone=publique -->
# T-0154 — Les commentaires du moteur sans identifiant de la mémoire de l'atelier, gardés par un test, selon la règle que Théo retient

> statut : ouvert · origine : J-2026-11-21-Q · besoin : B-0271 · après : T-0153 · lu : backlog@6c894b15

Un commit, sur la réponse de Théo à la demande de T-0153 : chaque renvoi d'un commentaire du moteur à la mémoire de l'atelier remplacé par sa raison en clair, et un test qui le garde, comme `tests/test_notes_de_version.py` garde le guide et les notes ; `engine/socle/hooks.py` et `engine/socle/commands.py` n'y entrent que si la réponse de Théo les y met. Si Théo n'en veut rien, la tâche s'abandonne en renvoyant à sa réponse.

## Fait quand

- [ ] un test échoue sur un commentaire du moteur qui cite un identifiant de la mémoire de l'atelier, hors de ce que la règle retenue exempte, et le moteur le passe
