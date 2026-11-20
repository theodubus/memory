<!-- socle: couche=backlog zone=publique -->
# T-0119 — socle state dit si l'ensemble de règles de la branche par défaut refuse le push forcé et la suppression, et l'étape 4 du guide les fait régler

> statut : ouvert · origine : J-2026-11-20-AO · besoin : B-0317 · lu : backlog@689e597f

Un commit : `ci_exigee` (ou une fonction voisine de `engine/socle/state.py`)
lit aussi, dans la réponse de `rules/branches/<branche>` qu'elle reçoit
déjà, les règles `non_fast_forward` et `deletion` ; la ligne « branche »
de l'état les dit, et l'absence de l'une devient une action de l'humain,
comme la CI non exigée. L'étape 4 du guide (`HELP.md`, `HELP.en.md`) fait
cocher « Block force pushes » et « Restrict deletions ». Une note de
version.

## Fait quand

- [ ] avec un ensemble de règles qui n'a pas `non_fast_forward`, l'état demande à l'humain de refuser le push forcé, et le dit refusé quand la règle y est ; de même pour `deletion` ; un test le montre
- [ ] l'étape 4 du guide, en français et en anglais, fait refuser le push forcé et la suppression de la branche par défaut, et un test le montre
