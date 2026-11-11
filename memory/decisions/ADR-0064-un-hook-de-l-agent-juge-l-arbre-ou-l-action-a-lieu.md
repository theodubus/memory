<!-- socle: couche=decisions zone=publique -->
# ADR-0064 — Un hook de l'agent juge l'arbre où l'action a lieu

> statut : acceptée · date : 2026-11-11 · source : B-0164@f9cc399c, J-2026-11-11-L@347cb223 · lu : decisions@aaf863cf

## Contexte

Claude Code lance les hooks de l'agent à la racine de la session
(`CLAUDE_PROJECT_DIR`), et le lanceur passe sa propre racine au moteur :
la copie principale du dépôt. Un sous-agent travaille pourtant dans un
worktree, où il crée ses entrées de mémoire ; le hook avant outil les
jugeait contre la mémoire de la copie principale, qui ne les a pas
encore, et les refusait comme références inventées (B-0164@f9cc399c).

## Décision

Le hook avant outil juge tout contre la racine de la session, comme
avant ; si l'action a lieu dans un autre worktree du même dépôt
(`hooks.arbre_juge` : celui du fichier écrit, pour un outil d'écriture,
sinon le dossier courant de l'agent, le `cwd` de son entrée), équipé du
socle, il la juge EN PLUS contre ce worktree : ses fichiers protégés, sa
politique, sa mémoire. Refusée dans l'un des deux arbres, l'action est
refusée ; aucun refus ne disparaît parce que le dossier courant change.
La seule chose que le second arbre accorde : une référence citée vaut si
elle existe dans l'arbre où l'action a lieu ou dans la racine de la
session. Un autre dépôt, un dossier hors de tout dépôt, ou un worktree
sans le socle ne changent rien.

Les hooks de fin de tour et de démarrage ne changent pas d'arbre : ils
jugent la racine de la session, faute de quoi un tour qui a rendu la copie
principale rouge conclurait depuis un worktree, et le compteur des
tentatives repartirait de zéro en changeant de dossier. La trace reste
commune à tous les worktrees, sous le dossier git commun
(ADR-0005@92bac884).

## Conséquences

Un sous-agent écrit sa mémoire par l'outil d'édition, sans script de
contournement. Le correctif ne vaut qu'une fois dans le moteur que les
hooks exécutent, celui de la copie principale. Une première version
faisait juger le worktree À LA PLACE de la racine : la revue a montré
qu'un `cd` dans un worktree levait alors les refus sur la copie
principale. Pour défaire la décision, retirer l'appel à `arbre_juge`
dans `hooks.pre_tool_use`.
