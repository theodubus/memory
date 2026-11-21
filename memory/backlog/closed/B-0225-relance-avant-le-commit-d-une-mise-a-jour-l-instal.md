<!-- socle: couche=backlog zone=publique -->
# B-0225 — Relancé avant le commit d'une mise à jour, l'installeur ne nomme plus les notes de version : le message de commit et « Et maintenant » les perdent

> statut : fait · origine : J-2026-11-14-X · ref : T-0025, J-2026-11-21-H · lu : backlog@9590ed19

La revue du lot 2 (J-2026-11-14-X), constat 1. Dans
`engine/socle/installer.py`, les identifiants des notes déjà lues se
lisent dans la copie du moteur de l'arbre : relancé avant le commit de
la mise à jour, l'installeur trouve la copie déjà neuve et ne voit plus
de notes nouvelles. Le message de commit que propose « Et maintenant »
redevient `Mettre à jour le socle <version>`, et l'étape qui ouvre
l'agent ne nomme plus les notes ; seule la première sortie les a
montrées. L'installeur dit lui-même de se relancer (après `git fetch
--unshallow`, ou pour corriger `--adapter`) : le cas est d'usage normal,
et rien ne rattrape l'effet. `tests/test_notes_de_version.py` fige le
comportement actuel.

Piste : lire les identifiants dans la copie du dernier commit
(`git show HEAD:<engine_dir>/socle/CHANGES*.md`), comme ADR-0052 lit
l'historique.

## Satisfait quand

- [x] relancer l'installeur avant de commiter une mise à jour ne fait plus perdre ses notes de version : le message de commit proposé et « Et maintenant » les nomment encore
