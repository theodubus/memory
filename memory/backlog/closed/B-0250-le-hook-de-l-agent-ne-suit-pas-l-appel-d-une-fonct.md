<!-- socle: couche=backlog zone=publique -->
# B-0250 — Le hook de l'agent ne suit pas l'appel d'une fonction dans une substitution ni dans un eval : la suppression du projet y passe

> statut : fait · origine : J-2026-11-15-R · priorité : haute · ref : J-2026-11-16-C · lu : backlog@381c20a4

Vu en corrigeant les bloquants 2 et 3 de la revue du lot L-0004
(J-2026-11-15-R) : le découpage suit désormais l'appel d'une fonction
définie dans la commande dont le corps `{ …; }` change le dossier
(`fonctions`, `commands._analyser`), mais ne transmet pas ces fonctions
aux lectures qu'il relance à part : le texte d'une substitution (`$(…)`,
accents graves, `<(…)`) et celui d'un `eval` se découpent par un
`_analyser` neuf, qui ne les connaît pas. Vérifié sur bash : une
substitution hérite des fonctions du shell, et `eval` s'exécute dans le
shell courant ; l'appel y fait valoir le `cd` du corps.

- `f() { cd memory; }; x=$(f; rm -rf ../../<racine>)` passe le hook ;
  bash supprime le projet.
- `f() { cd memory; }; eval "f; rm -rf ../../<racine>"` passe de même.

Un sous-shell `( … )` et un élément de pipeline, eux, se jugent
justement (le premier par le même découpage, le second ne fuit rien dans
bash). Rien ne rattrape la suppression du projet : ADR-0080 (sa première
conséquence) ouvre ce sujet, de priorité haute comme B-0208.

La piste : passer une copie de `fonctions` aux `_analyser` des
substitutions et d'`eval`, pas à celui d'un `bash -c`, un autre
processus qui ne les hérite pas (hors `export -f`).

## Satisfait quand

- [x] `f() { cd memory; }; x=$(f; rm -rf ../../<racine>)` et `f() { cd memory; }; eval "f; rm -rf ../../<racine>"` sont refusés par le hook, `f() { ls; }; x=$(f); rm -rf build` passe, et un test le montre
