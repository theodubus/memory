<!-- socle: couche=backlog zone=publique -->
# B-0055 — Un mode multi-agent : un agent maître qui tient la mémoire et répartit les tâches

> statut : abandonné · origine : J-2026-10-13-L · lu : backlog@74e54c44 · ref : J-2026-10-19-H, J-2026-10-30-Q, D-0168 · après : B-0101, B-0162

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

Abandonné le 19 octobre parce que BMAD répartissait déjà le travail
(J-2026-10-19-H), rouvert à son retrait (D-0051, J-2026-10-30-Q), avec
B-0071, qui s'y fond. Ce que D-0051 en fixe : un agent maître qui confie
chaque tâche à un sous-agent dans son worktree, avec le seul contexte de
la tâche, en choisissant le modèle et l'effort ; des relecteurs sans
contexte ; les contrôles du socle sur le travail rendu avant sa reprise ;
mesuré au banc. Il vient après la planification (B-0101), quand le pilote
écrira du code.

Le choix du modèle et de l'effort (B-0071) : Claude Code permet de donner
un modèle à un sous-agent, que BMAD lançait au modèle de la session. À
régler : où vit la règle (côté agent, des définitions de sous-agents que
pose l'installeur), sur quoi elle choisit (la taille de la tâche, sa
nature : relecture, implémentation, planification), et ce qu'elle coûte,
mesuré au banc : coût, durée et qualité d'une tâche selon le modèle et
l'effort.

Le 10 novembre : le cadrage l'écartait, et son sort dépend de la
proposition 7 de D-0093@333ad9d0, à reformuler (B-0162).

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « Faits ou remplacés » : un agent maître qui confie chaque tâche à un sous-agent : fait pour l'essentiel par le skill `socle-batch` (un orchestrateur, un sous-agent par tâche dans sa copie, son modèle, un relecteur sans contexte, les contrôles sur le travail rendu) ; reste une règle de choix du modèle mesurée au banc (X6), que Théo tranche aujourd'hui (Opus partout, D-0095).
