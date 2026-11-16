<!-- socle: couche=backlog zone=publique -->
# B-0228 — Le hook de l'agent laisse supprimer un dossier qui contient le projet par un autre programme que rm, mv, git clean ou find (rsync --delete, git worktree remove, python3 -c)

> statut : fait · origine : J-2026-11-14-AC · ref : J-2026-11-15-N · lu : backlog@2e470e0c

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

## Modèle de menace

Borné à la règle 2 de D-0112, qu'écrit ADR-0080@bfb13155 : supprimer le
projet ou un dossier qui le contient est de ce que rien ne rattrape
ensuite, et se juge quelle qu'en soit la forme. B-0208 en a couvert les
formes de `rm`, `mv`, `git clean` et `find` ; ce sujet range parmi les
suppressions (`hooks.suppressions`), développées et jugées comme elles
(depuis le dossier courant de l'agent, après un `cd`, `~`, variables,
motifs ; une part que le hook ne sait pas développer, refusée si elle
peut contenir la racine, ADR-0072) :

- la destination d'un `rsync` qui supprime ce que ses sources n'ont pas
  (`--delete`, `--del`, `--delete-before`, `--delete-during`,
  `--delete-delay`, `--delete-after`, `--delete-excluded`) : son dernier
  argument, une fois retirées les valeurs de ses options (`-e ssh`,
  `--exclude .git`, `-T dossier`), même écrites après lui ; elle se juge
  entière, quelle que soit la forme de ses sources (une source sans barre
  finale ne viderait que son homonyme dans la destination), un refus de
  trop accepté ;
- les sources d'un `rsync --remove-source-files`, qui en retire chaque
  fichier copié : la racine ou un dossier qui la contient en source
  viderait le projet ;
- le chemin d'un `git worktree remove` (`-f`, `--force`, répétés), et
  celui que déplace `git worktree move`, comme les sources d'un `mv`,
  relatifs au dossier de la commande et à ses `-C` : un sous-agent qui
  retire le sien depuis l'intérieur (`git worktree remove .`, son chemin
  absolu, `cd ..` puis son nom) ;
- les chemins qu'un `python -c` (`python3 -I -c`, et les autres options
  de python) écrit en toutes lettres pour `rmtree` (`shutil.rmtree`, ou
  importé seul), pour la source de `shutil.move`, `os.rename`,
  `os.replace` et `os.renames`, ou dans le `Path` que `rename` ou
  `replace` déplace : une chaîne, un `Path(…)` ou un `os.path.join(…)` de
  chaînes, lus dans l'arbre du script (`ast`), relatifs au dossier de la
  commande ;
- ce qu'un `find` lance par `-exec` sur ce qu'il trouve, quand ce
  programme le supprime selon ce qui précède (`find .. -exec rsync -a
  --delete vide/ {} \;`), et non plus seulement `rm`.

Pour chacun, la racine elle-même compte : aucun de ces chemins, hors de la
destination d'un `rsync`, n'est jugé comme une écriture, qui la refuserait
comme un dossier qui contient un fichier protégé.

La part `find` de la piste était déjà faite : une expression dont les
seuls tests sont `-type`, `-empty` ou une négation ne garde rien, et
`find . -type f -delete` comme `find . ! -name x -delete` sont refusés
depuis la revue du lot 3 (J-2026-11-14-AH@34fc7db1, `_expression_find`) ;
ce sujet ne la change pas.

Restent libres : une destination, une source ou un worktree dans le projet
ou voisin de lui (l'orchestrateur, à la racine, retire le worktree d'un
sous-agent : `git worktree remove -f -f .claude/worktrees/agent-x`), la
source d'un `rsync --delete` et la destination d'un `shutil.move`, qui ne
sont pas supprimées, une destination distante (`hôte:chemin`), un essai à
blanc (`rsync -n`, `--dry-run`, `--list-only`).

Hors du modèle, comme ADR-0080 le dit d'un autre langage : un chemin que
le script de python construit au vol (`os.getcwd()`, `sys.argv[1]`, une
variable, une concaténation, un module renommé à l'import) n'ouvre pas de
refus nouveau. Écarté, exotique et rattrapé : un fichier protégé que
retire `rsync --remove-source-files`, que `protege.fichiers` attrape
ensuite. Risque accepté d'ADR-0072 : une part inconnue qui vaut elle-même
`..`.

Dans le modèle, mais hors de ce sujet, qui ne couvre que la piste et son
« Fait quand » : `xargs rm` d'un dossier qui contient le projet, et une
commande du shell que lance un `python -c` (`os.system`, `subprocess`),
que rien ne rattrape non plus, vont à B-0246, de priorité haute
(D-0108@96eeead5) ; le script d'un heredoc (`python3 - <<EOF`) est à
B-0229, qui le jugera comme celui d'un `python -c`, ses suppressions
comprises.

## Satisfait quand

- [x] la suppression d'un dossier qui contient le projet par `rsync --delete`, `git worktree remove` ou `python3 -c` qui cite son chemin est refusée par le hook, et un test le montre
