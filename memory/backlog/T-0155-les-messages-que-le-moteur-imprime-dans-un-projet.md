<!-- socle: couche=backlog zone=publique -->
# T-0155 — Les messages que le moteur imprime dans un projet installé sans identifiant de la mémoire de l'atelier, gardés par un test

> statut : ouvert · origine : J-2026-11-21-Q · besoin : B-0326 · après : T-0153 · lu : backlog@6c894b15

Un commit, après la réponse de Théo à la demande de T-0153 pour les textes du hook de l'agent : les messages de l'installeur (« (D-0071) » dans `et_maintenant`, `engine/socle/installer.py`) et ceux du catalogue anglais (`engine/socle/messages_en.py`) qui citent un identifiant de l'atelier, remplacés par leur raison en clair, et un test qui garde les messages du produit, comme `tests/test_notes_de_version.py` garde les notes ; une note de version. Le refus du hook qui finit par « (D-0098) » ne change que si la réponse le permet (ADR-0098).

## Fait quand

- [ ] aucun message que le moteur imprime dans un projet installé ne cite un identifiant de la mémoire de l'atelier, hors de ce que la règle retenue exempte, et un test le garde
