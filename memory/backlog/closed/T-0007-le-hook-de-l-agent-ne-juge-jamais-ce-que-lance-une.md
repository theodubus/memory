<!-- socle: couche=backlog zone=publique -->
# T-0007 — Le hook juge le texte d'une substitution entre guillemets comme celui d'une substitution nue

> statut : fait · origine : J-2026-11-16-F · besoin : B-0260 · lu : backlog@9966bbbd · ref : J-2026-11-19-W, D-0139

Un commit : le découpage (`engine/socle/commands.py`) juge le texte d'une substitution `"$(…)"`, qu'il sait déjà délimiter, avec les fonctions connues, comme celui d'une substitution nue ; ses cas dans `tests/test_garde.py`.

## Fait quand

- [x] `echo "$(rm -rf ..)"`, `echo "$(cd memory; rm -rf ../../<racine>)"` et `x="$(f; rm -rf ../../<racine>)"` sont refusés par le hook, et un test le montre
- [x] `x="$(git rev-parse HEAD)"; echo "$x" > notes.txt` passe le hook, et un test le montre
