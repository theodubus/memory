<!-- socle: couche=backlog zone=publique -->
# B-0231 — Le hook de l'agent juge les filtres d'un find un par un : une conjonction (-name et -path) est refusée pour ce qu'aucun des deux ne vise seul

> statut : ouvert · origine : J-2026-11-14-AJ · lu : backlog@618d1053

Depuis la correction des bloquants du lot 3 (J-2026-11-14-AI), le hook
de l'agent juge l'expression d'un `find` qui supprime ou écrit, mais une
conjonction de filtres se juge filtre par filtre : `find . -name '*.json'
-path './build/*' -delete` est refusé, parce que `-name '*.json'` seul
croiserait un réglage de Claude Code, alors que la conjonction ne vise que
`build/`. Un faux refus dans l'usage normal (un nettoyage ciblé), vu par
l'implémenteur des corrections ; aucun trou.

La piste : un fichier protégé n'est touché que s'il satisfait chaque
filtre de la conjonction ; juger l'intersection, et refuser seulement ce
que tous les filtres d'une même conjonction peuvent viser ensemble.

## Fait quand

- [ ] `find . -name '*.json' -path './build/*' -delete` passe le hook, `find . -name '*.json' -path './.claude/*' -delete` reste refusé, et un test le montre
