<!-- socle: couche=backlog zone=publique -->
# B-0225 — Relancé avant le commit d'une mise à jour, l'installeur ne nomme plus les notes de version : le message de commit et « Et maintenant » les perdent

> statut : ouvert · origine : J-2026-11-14-X · lu : backlog@9590ed19

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

## Fait quand

- [ ] relancé avant le commit d'une mise à jour, l'installeur nomme les mêmes notes qu'au premier passage, dans le message de commit et dans « Et maintenant » ; un test qui échoue sur le commit parent le prouve

