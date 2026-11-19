<!-- socle: couche=backlog zone=publique -->
# T-0006 — Le hook juge un git push par son argv développé, et refuse un argument qu'il ne connaît pas

> statut : fait · origine : J-2026-11-16-B · besoin : B-0254 · lu : backlog@9966bbbd · ref : J-2026-11-19-U

Un commit : `irreversible` (`engine/socle/hooks.py`) juge l'argv d'un `git push` après le développement des variables connues, lit les arguments de l'appel d'une fonction dont le corps pousse, et refuse un argument inconnu comme ADR-0072 refuse un chemin inconnu ; ses cas dans `tests/test_garde.py`.

## Fait quand

- [x] `f() { git push "$@"; }; f --force origin travail`, `F=--force; git push $F origin travail` et `git push "$X" origin travail` sont refusés par le hook, et un test le montre
- [x] `git push origin travail` et `B=travail; git push origin "$B"` passent le hook, et un test le montre
