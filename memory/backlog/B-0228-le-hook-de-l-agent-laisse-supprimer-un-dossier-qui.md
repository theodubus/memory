<!-- socle: couche=backlog zone=publique -->
# B-0228 — Le hook de l'agent laisse supprimer un dossier qui contient le projet par un autre programme que rm, mv, git clean ou find (rsync --delete, git worktree remove, python3 -c)

> statut : ouvert · origine : J-2026-11-14-AC · lu : backlog@2e470e0c

B-0208@78acac59 fait refuser par le hook de l'agent la suppression d'un
dossier qui contient le projet par les formes que nommait sa piste : les
arguments de `rm`, les sources d'un `mv`, ce que balaie `git clean`, les
départs d'un `find` qui supprime (`-delete`, `-exec rm`). Son modèle de
menace, borné à la règle 2 de D-0112 (ADR-0080@bfb13155), met dans le
modèle la suppression du projet quelle qu'en soit la forme, et laisse à ce
sujet celles qu'il ne couvre pas, que rien ne rattrape ensuite :

- un autre programme qui supprime : `rsync -a --delete vide/ ..`, `git
  worktree remove` d'un worktree qui est le projet (un sous-agent qui
  range le sien), `python3 -c` qui appelle `shutil.rmtree` sur un chemin
  écrit en toutes lettres, `find -exec` d'un autre programme que `rm` ;
- `xargs rm` sur un dossier qui contient le projet, que B-0206 doit juger
  comme un chemin inconnu ;
- l'expression d'un `find` qui, depuis la racine, viserait tout le projet
  sans paraître ne rien filtrer (`find . -type f -delete`, `find . ! -name
  x -delete`) ;
- une part inconnue qui vaut elle-même `..` (`rm -rf /tmp/$X`, `X` valant
  `../..`), risque accepté d'ADR-0072.

La piste : ranger `rsync --delete` (sa destination), `git worktree remove`
(son chemin) et les chemins qu'un `python3 -c` passe à `shutil.rmtree` en
toutes lettres parmi les suppressions (`hooks.suppressions`) ; pour
`find`, tenir pour non filtrante une expression dont les seuls tests sont
`-type` ou une négation.

## Fait quand

- [ ] la suppression d'un dossier qui contient le projet par `rsync --delete`, `git worktree remove` ou `python3 -c` qui cite son chemin est refusée par le hook, et un test le montre
