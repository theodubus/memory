<!-- socle: couche=backlog zone=publique -->
# B-0375 — Clore une tâche demande environ huit commandes de mémoire, pour une tâche de deux lignes

> statut : fait · origine : J-2026-11-27-U · ref : D-0235, ce commit · après : B-0371, B-0372, B-0373, B-0374 · lu : backlog@4d53be09

Chez chess (`docs/fabrication/chess/cout-et-frictions-2026-11-26.md`, §2) : environ huit gestes de mémoire pour deux
lignes de travail, et un commit refusé de plus pour une entrée close non
rangée. Confirmé (`docs/fabrication/chess/relecture-cout-et-frictions-2026-11-27.md`) : `memoire.backlog`
(`engine/socle/checks_memory.py`) refuse une entrée close sans `ref` et
une entrée close restée parmi les ouvertes ; aucune commande ne clôt une
tâche.

Retenu par Théo le 27 novembre (D-0235, point 5) : une commande pose le
statut, la référence et le rangement ; l'agent coche toujours ses
critères lui-même. La forme de la référence (le commit qui clôt, que le
contrôle retrouverait par l'historique du fichier) se spécifie avant le
code.

## Satisfait quand

- [x] une tâche dont les critères sont cochés se clôt, statut, référence et rangement, en une commande
- [x] une tâche dont un critère reste vide ne se clôt pas, et la commande le dit
