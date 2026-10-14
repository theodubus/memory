<!-- socle: couche=backlog zone=publique -->
# B-0057 — Les hooks git passent GIT_DIR aux commandes du projet : depuis un worktree secondaire, ses tests visent le vrai dépôt

> statut : ouvert · origine : J-2026-10-13-X · lu : backlog@44afd8b1

Mesuré en poussant D-0022 depuis un worktree secondaire de ce dépôt : git
passe `GIT_DIR` et `GIT_INDEX_FILE` (absolus) à ses hooks, et le hook
avant push lance les tests du projet avec cet environnement. Les tests qui
créent un dépôt jetable et y appellent git par le moteur visaient alors le
vrai dépôt : le contrôle de régression y ajoutait un worktree par
correctif rejoué, qui relançait la suite, et ainsi de suite — des milliers
de processus, le hook tué, 526 worktrees inscrits, et `core.bare = true`
posé dans la configuration par un `git init --bare` détourné. Rien n'est
parti vers GitHub ; réparé à la main. Depuis le worktree principal, git ne
passe pas `GIT_DIR`, d'où le silence jusqu'ici.

À faire : les hooks git retirent `GIT_DIR`, `GIT_WORK_TREE`,
`GIT_INDEX_FILE` et leurs voisins de l'environnement des commandes du
projet (capacités de l'adaptateur, régression rejouée), après avoir lu
l'index qu'ils jugent ; un test qui reproduit la récursion depuis un
worktree, borné dans le temps.
