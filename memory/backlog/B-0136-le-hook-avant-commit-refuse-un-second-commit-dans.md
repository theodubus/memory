<!-- socle: couche=backlog zone=publique -->
# B-0136 — Le hook avant commit refuse un second commit dans la même commande même quand il a lieu dans un autre worktree

> statut : ouvert · origine : J-2026-11-08-S · lu : backlog@fd4e61e1

Chaque commit d'agent doit avoir vu passer le filtre de l'agent depuis le
commit précédent ; la trace des hooks est commune à tous les worktrees du
dépôt. Un commit dans un worktree, puis un autre dans un second worktree,
dans la même commande, est donc refusé comme un second commit (le pilote,
J-2026-11-08-S). Juger le commit précédent du même worktree.

Fait quand :
- [ ] deux commits dans deux worktrees, dans une même commande, passent, et deux dans le même worktree restent refusés, avec un test
