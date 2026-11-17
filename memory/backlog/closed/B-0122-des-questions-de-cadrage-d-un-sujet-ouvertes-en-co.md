<!-- socle: couche=backlog zone=publique -->
# B-0122 — Des questions de cadrage d'un sujet, ouvertes, en cours de projet

> statut : fait · origine : J-2026-11-01-K · lu : backlog@24dfa559 · ref : J-2026-11-01-N

En cours de projet, une demande ne porte qu'une décision aux réponses
fermées, et les questions ouvertes n'existent qu'au départ. Un sujet qui
dépend de l'intention de l'humain pousse l'agent à deviner, ou à proposer
ses propres options. Théo retient (D-0067, `cadrage`) des questions de
cadrage d'un sujet : sur le modèle des questions de départ, à tout moment,
quand l'agent ne peut pas écrire une spécification sans deviner ;
l'humain répond librement, l'agent consigne ses mots, puis soumet la
spécification ou la décision qui en découle.

## Satisfait quand

- [x] `socle new request --questions` pose une demande de questions de cadrage au contrat
- [x] les instructions, le format et le guide le disent (le skill des demandes, protégé dans ce dépôt, n'en a pas besoin : les instructions et le gabarit suffisent)
- [x] un test l'établit
