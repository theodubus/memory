<!-- socle: couche=backlog zone=publique -->
# B-0055 — Un mode multi-agent : un agent maître qui tient la mémoire et répartit les tâches

> statut : ouvert · origine : J-2026-10-13-L · lu : backlog@74e54c44

Demandé par Théo (texte exact au journal) : un agent maître qui tient la
mémoire, envoie des sous-agents sur les tâches, décide pour chacune du
niveau d'effort et du modèle, et leur donne le contexte dont elles ont
besoin ; réfléchir d'abord à la meilleure architecture. Ce qu'elle doit
régler, au moins : le moteur ne connaît aucun agent, donc l'orchestration
vit côté agent (hooks, gabarits d'instructions), le moteur ne fournissant
que le contexte d'une tâche (état, chantier, entrées citées avec leurs
empreintes) et les contrôles du travail rendu ; les écritures en mémoire
de sous-agents parallèles, qui prendraient les mêmes identifiants (B-0053) ;
le travail de chacun dans son worktree, jugé par les mêmes contrôles avant
d'être repris ; et la règle de choix de l'effort et du modèle, à mesurer au
banc plutôt qu'à supposer.
