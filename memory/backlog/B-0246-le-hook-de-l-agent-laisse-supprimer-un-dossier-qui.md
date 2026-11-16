<!-- socle: couche=backlog zone=publique -->
# B-0246 — Le hook de l'agent laisse supprimer un dossier qui contient le projet par xargs rm ou par une commande que lance python -c (echo .. | xargs rm -rf, os.system)

> statut : ouvert · origine : J-2026-11-15-N · priorité : haute · lu : backlog@cec3243f

B-0228 fait refuser par le hook de l'agent la suppression du projet, ou
d'un dossier qui le contient, par `rsync --delete`, `git worktree remove`
et les chemins qu'un `python -c` passe en toutes lettres à
`shutil.rmtree`. Deux formes que sa description nommait restent hors de sa
piste et de son « Fait quand » :

- `xargs rm` (ou un autre programme qui supprime ce qu'il lit) sur un
  dossier qui contient le projet : `echo .. | xargs rm -rf`, `find ..
  -maxdepth 0 | xargs rm -rf`. `xargs` d'un écrivain ne se juge que par
  les chemins protégés que la commande cite (B-0206), et `..` n'en est
  pas un ; la commande que lance `xargs` n'a pas d'argument que
  `suppressions` lise.
- une commande du shell que lance un `python -c` (`os.system('rm -rf
  ..')`, `subprocess.run(['rm', '-rf', '..'])`) : le script ne se juge que
  par ses chemins protégés et par ce qu'il passe à `rmtree` ou déplace.

Rien ne rattrape ensuite la suppression du projet : ADR-0080 (sa première
conséquence) ouvre un sujet pour ce trou, quelle qu'en soit la forme, de
priorité haute comme B-0208 (D-0108@96eeead5).

La piste : pour `xargs` d'un programme qui supprime ce qu'il lit (`SONDE`
dans `suppressions` de la commande lancée), juger comme une suppression
les chemins que la commande entière cite en toutes lettres, et les
départs d'un producteur `find` ou `ls`, comme B-0230 le fera de leurs
écritures ; pour `python -c`, juger comme une commande du shell la chaîne
qu'il passe à `os.system`, `subprocess.*` (`shell=True`) ou la liste de
chaînes qu'il leur passe.

La revue du lot B-0234 (J-2026-11-15-O), deuxième constat pour le
backlog, y ajoute un chemin qu'un `python -c` écrit en toutes lettres sous
une autre forme que celles que lit B-0228 (une chaîne, `Path(…)`,
`os.path.join(…)`) : `shutil.rmtree(os.path.abspath('..'))`, de même avec
`os.path.realpath` ou `os.path.expanduser('~')`, une f-chaîne sans
variable (`f'..'`), `Path('..').resolve(strict=True)`. `abspath` est
courant ; la piste : les lire dans `_chemin_ecrit`
(`engine/socle/hooks.py`).

## Fait quand

- [ ] `echo .. | xargs rm -rf` et `python3 -c "import os; os.system('rm -rf ..')"` sont refusés par le hook, `find . -name '*.pyc' | xargs rm -f` passe, et un test le montre
- [ ] `python3 -c "import shutil, os; shutil.rmtree(os.path.abspath('..'))"` et ses pareils (`realpath`, `expanduser`, une f-chaîne sans variable, `Path('..').resolve(strict=True)`) sont refusés par le hook, et un test le montre
- [ ] depuis le worktree d'un sous-agent, `echo agent-s | xargs git worktree remove` est refusé comme `git worktree remove agent-s` (la recherche de git par la fin du chemin, `_nommes_par_leur_suffixe`, J-2026-11-16-B), et un test le montre
