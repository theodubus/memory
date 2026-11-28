<!-- socle: couche=backlog zone=publique -->
# B-0387 — Un commit que crée git revert, cherry-pick, merge ou rebase échappe au hook avant commit, et sauf merge à commit-msg

> statut : ouvert · origine : J-2026-11-28-D · lu : backlog@68df6bf7

Le constat 2 du relevé d'après de chess
(`docs/fabrication/chess/cout-et-frictions-2026-11-28.md`). Une même
commande y enchaînait un commit, un `git revert --no-edit`, puis un
`git commit --amend` : le journal des hooks ne montre, pour le revert,
qu'un prepare-commit-msg, et seul l'amend a été refusé, au nom de la
règle d'un commit par commande.

Rejoué ici le 28 novembre, sur un dépôt jetable, avec git 2.43 :
`git revert` et `git cherry-pick` ne lancent que prepare-commit-msg et
post-commit ; `git merge` lance pre-merge-commit, que le socle ne pose
pas, puis prepare-commit-msg et commit-msg ; `git rebase` ne lance aucun
de ces hooks. Le compte du filtre de l'agent repart à chaque
prepare-commit-msg (`compter_depuis_le_commit` de
`engine/socle/hooks.py`) : le revert prend le passage que le commit
suivant attend.

Rien ne part pourtant sans jugement : le hook avant push rejuge le
dernier commit et la plage qui part, `prive.fuites` compris, qui lit les
messages de ses commits, puis la CI. Le trou est local : un défaut se
voit au push au lieu du commit, et les avertissements de commit-msg
(fonction sans test, correctif sans test, hooks absents) manquent.

## Modèle de menace

À écrire à la conception : ce qui doit être arrêté au commit (un commit
d'agent sans ses hooks, une fuite de la mémoire privée dans un message),
et ce qui peut attendre le push, qui juge déjà la plage.

## Satisfait quand

- [ ] un commit d'agent que crée `git revert`, `git cherry-pick` ou `git merge` passe les contrôles rapides du hook avant commit et ceux de commit-msg, ou est refusé, et un test le montre pour chacun
- [ ] la règle d'un commit par commande compte aussi les commits de ces commandes
- [ ] ce que fait `git rebase`, qui ne lance aucun de ces hooks, est dit, et jugé au plus tard avant le push
