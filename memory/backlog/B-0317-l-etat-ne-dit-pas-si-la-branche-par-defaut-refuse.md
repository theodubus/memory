<!-- socle: couche=backlog zone=publique -->
# B-0317 — L'état ne dit pas si la branche par défaut refuse le push forcé et sa suppression, comme il dit la CI exigée, et le guide ne les fait pas régler

> statut : ouvert · origine : J-2026-11-20-AO · ref : B-0262, T-0023 · lu : backlog@6b66623e

Le relevé de T-0023 (`docs/fabrication/garanties-hors-du-hook.md`) :
hors du hook de l'agent, seul l'ensemble de règles de GitHub peut refuser
un push forcé sur la branche par défaut, ou sa suppression, côté serveur.
L'état lit cet ensemble de règles (`ci_exigee`, `engine/socle/state.py`),
mais n'y cherche que la CI exigée et la revue des propriétaires du code ;
les règles `non_fast_forward` (le push forcé) et `deletion` (la
suppression) n'y sont pas lues. Le guide, à l'étape 4 de l'installation,
ne fait exiger que la CI. Ni dans ce dépôt ni dans chess, on ne sait donc
si un push forcé sur `main` serait refusé : la session de T-0023 n'a pas
pu le lire, l'état ne le dit pas.

## Satisfait quand

- [ ] l'humain apprend par l'état si la branche par défaut de son projet refuse le push forcé et la suppression, et le guide lui dit de les refuser
