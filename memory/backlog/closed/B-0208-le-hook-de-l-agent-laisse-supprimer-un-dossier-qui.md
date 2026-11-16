<!-- socle: couche=backlog zone=publique -->
# B-0208 — Le hook de l'agent laisse supprimer un dossier qui contient le projet (rm -rf .., un ancêtre de la racine)

> statut : fait · origine : J-2026-11-13-H · priorité : haute · ref : J-2026-11-14-AC · lu : backlog@f4a491f0

Le hook de l'agent juge un chemin écrit par ce qu'il est dans le projet
(`_relatif`), et ne voit pas une suppression qui l'emporte tout entier :
`rm -rf ..` lancé depuis la racine, ou `rm -rf` d'un dossier qui la
contient (le dossier des worktrees pour un sous-agent, le dossier de
l'utilisateur), passent le hook, alors qu'ils effaceraient la politique,
les hooks et toute la mémoire, ce qu'aucun contrôle ne rattrape ensuite.
`rm -rf .` et `rm -rf` de la racine elle-même, eux, sont refusés.

Vu par la revue sans contexte de B-0171 (son constat 15). La priorité
haute est la décision de Théo (D-0108@96eeead5) : la suppression d'un dossier qui
contient le projet en haute, les autres écritures que le hook ne voit pas
sans priorité (B-0206). Pour rejouer, depuis la racine du dépôt, la
commande de B-0206 avec pour arguments `'rm -rf ..'` et le chemin absolu
du dossier qui contient la racine (`None` : le hook laisse passer).

La piste : dans `hooks._juger_chemin`, refuser une suppression (`rm`,
`mv`, `git clean`, `find -delete`) d'un chemin qui contient la racine
(`hooks._atteint` le sait déjà) ; un dossier temporaire voisin du projet
reste libre.

## Modèle de menace

Borné à la règle 2 de D-0112, qu'écrit ADR-0080@bfb13155 : supprimer le
projet ou un dossier qui le contient est de ce que rien ne rattrape
ensuite, et se juge quelle qu'en soit la forme. Le sujet couvre :

- les suppressions que nomme la piste : les arguments de `rm`, avec ou
  sans `-r` ; les sources d'un `mv`, `-t` compris (la destination n'est
  pas supprimée) ; ce que balaie `git clean`, son dossier (après `cd` ou
  `-C`) ou ses chemins ; les points de départ d'un `find` qui supprime
  (`-delete`, ou `-exec`, `-execdir`, `-ok`, `-okdir` qui lancent `rm`) ;
- d'un dossier qui contient la racine du projet sans être elle, son chemin
  développé comme le hook développe déjà un chemin écrit (ADR-0072) :
  relatif au dossier courant de l'agent (`..`, `../..`), absolu, `~`,
  `$HOME`, une variable connue, un motif (`/home/*`), des accolades, après
  un `cd` ; un chemin qu'il ne sait pas développer est refusé s'il peut
  contenir la racine (rien de connu ne le précède, ou ce qui le précède la
  contient) ;
- le projet lui-même, quand un `find` part de sa racine sans rien filtrer
  (`find . -delete`, `find . -mindepth 1 -exec rm -rf {} +`) ; un `rm` ou
  un `mv` de la racine est déjà refusé, comme tout dossier qui contient un
  fichier protégé.

Restent libres : un dossier voisin du projet ou ailleurs (`rm -rf
../autre`, `rm -rf /tmp/x`), un dossier du projet, un `find` qui filtre ce
qu'il supprime sous la racine (`find . -name '*.pyc' -delete`, qu'un
fichier protégé visé fait juger par B-0206), la destination d'un `mv`.

Dans le modèle, mais hors de ce sujet, qui ne couvre que les formes que
nomme sa piste : un autre programme qui supprime (`rsync --delete`, `git
worktree remove`, `python3 -c` qui appelle `shutil.rmtree`, `xargs rm`),
une expression de `find` qui, depuis la racine, viserait tout le projet
(`-type f`, `! -name x`), et une part inconnue qui vaut elle-même `..`
(ADR-0072) : ils vont à B-0228.

## Satisfait quand

- [x] la suppression d'un dossier qui contient le projet est refusée par le hook, et un test le montre
