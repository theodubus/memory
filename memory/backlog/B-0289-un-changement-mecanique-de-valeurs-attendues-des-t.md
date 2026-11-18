<!-- socle: couche=backlog zone=publique -->
# B-0289 — Un changement mécanique de valeurs attendues, des tests qui lisent un format que l'humain vient de valider, se valide par une question dans la conversation, sans demande écrite ni relecture à froid

> statut : ouvert · origine : D-0134 · lu : backlog@670d431f

La proposition 2 de `docs/fabrication/allegements.md`, que Théo a
validée dans sa variante légère (D-0134, J-2026-11-18-U). Changer la
valeur attendue d'un test exige une validation de l'humain qui le nomme
(politique, point 2) ; la règle du 12 novembre (J-2026-11-12-F) la
demandait par une demande écrite, relue à froid (130 000 jetons, B-0197),
poussée, son lien donné. Quand le changement est mécanique, des tests
qui lisent un format que l'humain vient de valider, l'agent pose la
question dans la conversation, en nommant chaque test avec sa valeur
avant et après, et consigne la réponse mot pour mot en décision de
séance, qui nomme les tests : le contrôle `tests.attendus` l'accepte
alors comme toute validation. La trace reste ; le document de contexte
relu à froid disparaît. Le skill `delegate-lot` de ce dépôt le dit
déjà ; le skill `socle-request` du produit ne le dit pas.

## Satisfait quand

- [ ] un agent qui change mécaniquement les valeurs attendues de tests qui lisent un format que l'humain vient de valider pose la question dans la conversation, chaque test nommé avec sa valeur avant et après, et consigne la réponse en décision de séance, sans demande écrite ni relecture à froid
- [ ] tout autre changement de valeur attendue, ou suppression de test, garde la demande écrite
