<!-- socle: couche=decisions zone=publique -->
# ADR-0062 — Le hook refuse l'installeur sur un projet équipé hors du mode de son verrou

> statut : acceptée · date : 2026-11-11 · source : B-0141@0b4d8ba1, J-2026-11-09-B@2ffde9bb · lu : decisions@55f34c4d

## Contexte

Pendant une revue adversariale, le relecteur sans contexte a lancé
l'installeur, en mode projet, sur ce dépôt en mode amont, au lieu de son
dossier jetable (J-2026-11-09-B@2ffde9bb). Le hook avant outil laissait
passer toute relance de l'installeur, la voie prévue pour rafraîchir les
copies protégées, sans juger sa cible ni son mode : le verrou, la CI et
CODEOWNERS ont changé, et seul le contrôle des fichiers protégés a arrêté
le commit (B-0141@0b4d8ba1).

## Décision

1. Le hook avant outil refuse `socle install` quand sa cible est un projet
   équipé et que le mode demandé (`--mode`, `projet` par défaut) n'est pas
   celui de son verrou. Le projet équipé est la racine du projet, ou toute
   cible qui porte son propre `.socle/engine.lock` (un worktree, une
   copie) ; la cible se lit après un `cd`, par `--target x` ou
   `--target=x`, relative ou absolue. Une cible que le hook ne sait pas
   résoudre comme le shell le fera, elle ou le `cd` qui la précède (une
   variable, `$(…)`, un accent grave, `~autre`), fait refuser
   l'installeur : chaque appel repart d'un shell neuf, où une variable
   est vide, et la cible serait le projet ; le message demande le chemin
   en toutes lettres. Aucune exception ne sort du jugement, qui laisserait
   passer toute la commande. La ligne de commande refuse les options
   abrégées (`--mo` pour `--mode`), que le hook ne lirait pas.
2. Il laisse passer la mise à jour normale, relancée dans le mode du
   verrou, et l'installeur sur une cible sans verrou : un dossier
   temporaire, une première installation. Changer le mode d'un projet
   revient à l'humain.
3. Le dossier de `socle review`, et le skill `socle-review`, disent au
   relecteur d'éprouver une commande dans un dossier temporaire qu'il crée
   hors du dépôt (`mktemp -d`), et de n'écrire que là, par son chemin
   absolu, écrit en toutes lettres dans chaque commande.

## Conséquences

Ce que le hook n'empêche pas, et pourquoi :
- sur un projet en mode projet, c'est-à-dire tout projet équipé sauf ce
  dépôt, la commande de l'incident (`install --target . --adapter kotlin
  --owner @essai`) passe : le mode demandé est celui du verrou. Elle
  réécrit l'adaptateur, CODEOWNERS et les hooks ; le contrôle des
  fichiers protégés arrête le commit, mais la remise en état revient à
  l'humain. Ce cas reste ouvert : la piste, permettre à l'agent de
  remettre un fichier protégé à son état commité, assouplit un
  garde-fou, et va à l'humain (B-0165@c7a9ceae) ;
- l'installeur dans le mode du verrou, même avec un autre `--owner` ou un
  autre adaptateur : c'est la voie de la mise à jour, que l'agent doit
  garder ; le contrôle des fichiers protégés arrête le commit de ce qu'elle
  change sans approbation ;
- une écriture par un programme que le hook ne lit pas (un script Python,
  un outil tiers) : le hook juge les commandes du shell, pas ce qu'un
  programme fait ; même filet, le contrôle des fichiers protégés ;
- la remise d'un fichier protégé à son état commité reste réservée à
  l'humain : la permettre à l'agent assouplirait un garde-fou, au risque
  d'effacer un changement que l'humain n'a pas commité.

Pour défaire : retirer l'appel à `installeur_hors_mode` dans
`refus_bash` (`engine/socle/hooks.py`), son défaut injecté et son témoin.
