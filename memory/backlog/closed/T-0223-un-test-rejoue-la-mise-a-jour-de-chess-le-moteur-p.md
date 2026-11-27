<!-- socle: couche=backlog zone=publique -->
# T-0223 — Un test rejoue la mise à jour de chess : le moteur publié qu'il a installe, le moteur de la tête met à jour, la demande seule puis les fichiers passent les vrais hooks git

> statut : fait · origine : J-2026-11-27-AO · besoin : B-0368 · lu : backlog@c0e72dd2 · ref : ce commit

Le test que décrit B-0368 (D-0219), d'environ 150 lignes, dans
`tests/` : le moteur de ce dépôt au commit publié qu'a chess, pris par
`git archive` dans l'historique, installe un projet et sa mémoire ; le
moteur de la tête le met à jour ; la demande seule se commite et se
pousse vers un dépôt nu par les vrais hooks git, puis les fichiers de la
mise à jour. Le commit rejoué est une constante nommée, que la
mise à jour suivante de chess avance.

## Fait quand

- [x] le test échoue si le commit ou le push de la demande seule, ou ceux des fichiers de la mise à jour, sont refusés
- [x] le test se saute en le disant quand l'historique ne contient pas le commit rejoué
