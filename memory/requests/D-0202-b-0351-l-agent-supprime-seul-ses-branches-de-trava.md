<!-- socle: couche=demandes zone=publique -->
# D-0202 — B-0351 : l'agent supprime seul ses branches de travail distantes déjà contenues ailleurs — seulement les siennes (1A), par défaut dans le produit (2A) ?

> date : 2026-11-25 · forme : séance

## Question posée

B-0351, la question d'intention avant sa spécification, posée à Théo dans la conversation le 25 novembre : l'agent supprime lui-même une branche distante dont tout le contenu est déjà dans `main` ou dans sa branche de travail poussée, et l'état ne la lui donne plus ; une branche qui ne l'est pas reste refusée. Deux choix restent. 1. Quelles branches ? A (recommandé) : seulement celles de l'agent, dont le dernier commit porte sa marque (`Socle-Agent`) ; les siennes, même contenues, restent son geste. B : toute branche contenue, sauf celles que sa politique garde (`keep_branches`). 2. Activée comment ? A (recommandé) : par défaut dans le produit ; chess en profite à sa mise à jour ; une ligne de la politique la coupe. B : une option que Théo active dans la politique de chaque projet, comme la fusion par l'agent. Le mécanisme, l'agent le décide : une commande du socle qui vérifie sur GitHub, au moment de supprimer, que la branche n'a pas bougé, et donne le commit qui la recrée ; le hook continue de refuser un `git push --delete` direct.

Réponses : `valider` (1A 2A, la recommandation), `refuser`, `contexte-insuffisant`, ou une autre combinaison.
