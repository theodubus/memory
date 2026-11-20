<!-- socle: couche=demandes zone=publique -->
# D-0141 — Retenir les propositions 1 et 2 du 19 novembre sur les valeurs attendues des tests du hook

> date : 2026-11-19 · forme : séance

## Question posée

Retenir les propositions 1 et 2 du 19 novembre sur les valeurs attendues des tests du hook ? (La proposition 3, une voie plus légère, n'est pas retenue.)

Proposition 1, une règle pour écrire les listes des tests du hook. Un test du hook a deux listes : les commandes qui doivent être refusées, et celles qui doivent passer, les « témoins sains ». Le 14 novembre, `find . -type f | xargs sed -i s/a/b/` est entré dans la liste « doit passer » alors qu'elle réécrit tous les fichiers du projet, les fichiers protégés compris : elle y était parce que le hook ne la voyait pas. La règle : un témoin qui doit passer est réellement sans danger (il n'écrit aucun fichier protégé, ou un filtre les écarte) ; un trou connu ne s'écrit jamais dans cette liste, mais dans une troisième, « limites connues », avec l'entrée du backlog qui le bouchera ; le relecteur de chaque lot vérifie que chaque nouveau témoin sain l'est. La politique ne change pas : ces changements de valeurs attendues restent soumis à l'accord de Théo.

Proposition 2, chercher le test en conflit avant le lot, pas pendant. Quand l'agent écrit une tâche dont le « Fait quand » dit « telle commande est refusée » ou « telle commande passe », il cherche cette commande dans les tests ; s'il trouve un test qui affirme le contraire, il le nomme dans la tâche et pose la demande tout de suite, avant que le lot commence. Seul l'ordre change : la même demande arrive plus tôt, et le lot ne s'arrête plus en son milieu. C'est une méthode de travail, que l'agent écrit dans le skill des lots.
