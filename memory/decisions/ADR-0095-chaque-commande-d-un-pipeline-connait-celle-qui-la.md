<!-- socle: couche=decisions zone=publique -->
# ADR-0095 — Chaque commande d'un pipeline connaît celle qui la précède, et un xargs qui supprime ce qu'il lit se juge par le find qui lui donne sa liste

> statut : acceptée · date : 2026-11-19 · source : B-0246@dce35223, T-0004@47e316ea, B-0206@63623cf6, T-0002@e006b68b, ADR-0082@beb85978, ADR-0094@ae9b262f · lu : decisions@9a299840

## Contexte

`xargs rm` ne se jugeait que par les chemins protégés que la commande
cite (B-0206) : `find .. -maxdepth 0 | xargs rm -rf` supprimait un
dossier qui contient le projet sans refus, et `find . -type f | xargs rm
-f` le projet lui-même, quand `find .. -delete` et `find . -type f
-delete` sont refusés (B-0246@dce35223). Le découpage ne disait pas, d'une
commande d'un pipeline, celle qui écrit ce que lit son entrée.

## Décision

- **Un champ de la commande.** `Commande.amont` porte la commande qui la
  précède dans son pipeline, la dernière lue avant le `|` (ou `|&`), celle
  d'un groupe ou d'une boucle qui s'y ferme comprise ; `None` en tête
  d'un pipeline. Comme `Commande.entree` (ADR-0094@ae9b262f), le découpage
  le pose, et le hook le lit.
- **Le jugement.** Derrière un `find`, un `xargs` d'un programme qui
  supprime ce qu'il lit (`SONDE` dans les `suppressions` de la commande
  qu'il lance, comme `_departs_de_find` le fait pour `-exec`) supprime
  les départs du `find`, comme un `find` qui les supprime lui-même
  (`_supprimes_par_xargs`, `engine/socle/hooks.py`) : refusé si un départ
  contient le projet, ou si le départ est la racine et qu'aucun filtre de
  nom ou de chemin ne garde ce que le `find` écrit sur sa sortie.
- **Ce qui garde la sortie d'un `find`.** Chacun de ses `-print`,
  `-print0`, `-printf` ou `-ls`, gardé comme une action par les filtres
  qui le précèdent dans sa conjonction ; sans eux, l'expression entière,
  que garde le `-print` implicite. `_expression_find` le rend à qui le
  demande (`sortie`).

## Conséquences

- Un autre producteur (`echo .. | xargs rm`, `ls`) garde le jugement
  d'avant : la liste des formes connues que le hook ne juge pas le dit
  déjà (ADR-0082@beb85978).
- Les écritures d'un fichier protégé par `xargs` d'un écrivain derrière
  un `find`, un `grep -r` ou un `git ls-files` (T-0002) peuvent lire le
  même champ.
- Pour défaire : retirer `Commande.amont` et `_supprimes_par_xargs` ;
  `xargs` ne se juge plus que par les chemins que la commande cite.
