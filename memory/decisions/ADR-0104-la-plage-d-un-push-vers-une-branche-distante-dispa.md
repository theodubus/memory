<!-- socle: couche=decisions zone=publique -->
# ADR-0104 — La plage d'un push vers une branche distante disparue sans fusion se juge depuis le dernier commit que ce clone y a poussé, gardé dans le répertoire git commun

> statut : acceptée · date : 2026-11-20 · source : B-0167@01a077ae, T-0018@9d317948, J-2026-11-11-G@c9715693, B-0043@39049de5, ADR-0055@e49f4839, ADR-0098@3081a5ed · lu : decisions@7b6e01a8

## Contexte

Le hook git avant push juge la plage qui part comme la CI du push la
jugera, du commit distant au commit local (B-0043@39049de5). Une
référence absente en face n'a pas de commit distant : rien de sa plage
n'était jugé, seulement le travail contre la branche par défaut, où un
test que seule la branche a ajouté n'a pas de valeur attendue
antérieure. Supprimer la branche distante effaçait donc le repère : une
valeur attendue, une décision ou une entrée de journal poussées, puis
réécrites, repartaient comme neuves. J-2026-11-11-G@c9715693 l'a montré,
Théo ayant supprimé la branche à la demande de l'agent ; B-0167@01a077ae
le garde, et T-0018@9d317948 en donnait deux pistes. La première est
retenue : la seconde, dire seulement au refus que la suppression n'est
pas une issue, ne rattrape rien.

ADR-0098@3081a5ed ne s'applique pas : il vise le hook de l'agent, qui lit
le shell avant l'outil ; ceci change le hook git avant push, et lui seul.

## Décision

1. Quand le hook avant push laisse passer un push, il garde, pour chaque
   référence distante que le push met à jour, le commit local qui y part,
   dans `pushed.json`, à côté de la trace des hooks, dans le répertoire
   git commun que partagent les worktrees du clone (`.git/socle/`). Une
   suppression n'efface rien. La clé est la référence distante
   (`refs/heads/x`), sans le nom du distant : le script du hook git, posé
   par l'installeur et protégé, ne transmet pas au moteur les arguments
   que git lui donne. Une même référence poussée vers deux distants se
   juge donc depuis le dernier commit poussé vers l'un ou l'autre : plus
   strict, jamais moins.
2. Quand la référence distante est absente (commit distant nul) et que le
   commit gardé pour elle existe dans le clone sans être contenu dans la
   branche par défaut, la plage se juge depuis lui, comme si la branche
   distante y était encore. Contenu dans la branche par défaut, la branche
   a fusionné : repartie d'elle sous le même nom, elle se juge comme une
   branche neuve, contre elle, comme avant. Une branche jetable reste hors
   de ce jugement (ADR-0055@e49f4839).
3. Le refus le dit : la branche distante n'existe plus, la plage se juge
   depuis le dernier commit que ce clone y a poussé, nommé, et supprimer
   la branche distante n'est pas une issue ; si elle a fusionné,
   `git fetch` fait connaître la fusion au clone. La sortie est celle de
   la branche encore présente : rétablir, ou une demande validée.

## Modèle de menace

Rattrapé : dans le même clone, depuis n'importe lequel de ses worktrees,
une valeur attendue, une décision, une entrée de journal ou une dispense
poussées, puis réécrites (un commit de plus, un amendement, un rebase) et
repoussées sous le même nom après la suppression de la branche distante.
La plage se juge depuis le commit gardé, et le contrôle qui l'aurait
refusée sur la branche encore présente la refuse.

Pas rattrapé, et pourquoi c'est accepté :

- **Un clone neuf, une session cloud neuve**, sans la trace locale :
  rien ne garde ce qu'un autre clone a poussé. Réécrire ainsi demande de
  changer de clone exprès, un contournement hors du modèle d'un agent
  coopératif ; et ce qui est réécrit n'a jamais été dans la branche par
  défaut, où rien ne baisse.
- **La trace effacée à la main** (`.git/socle/pushed.json`) : hors du
  dépôt et de ses contrôles, comme `hooks.log` ; l'effacer est un geste
  de contournement, de même.
- **La CI de la pull request**, qui juge contre la branche par défaut :
  un test neuf de la pull request n'y a pas de valeur antérieure. Elle
  reste la dernière barrière pour ce que la branche par défaut a ; ce que
  seule la branche a poussé n'est gardé qu'en local, par le hook.
- **La réécriture poussée sous un autre nom** : une référence neuve, sans
  trace, se juge contre la branche par défaut. L'agent le peut seul, sans
  l'humain ; ce n'est pas tranché ici, et va au backlog (B-0320@9e5f95aa).

Ce que la règle peut refuser à tort, et sa sortie : un push qui échoue
après que le hook l'a laissé passer garde un commit qui n'est pas parti,
et la plage suivante se juge depuis lui ; une fusion par écrasement
(squash) ou par rebase laisse le commit gardé hors de la branche par
défaut, et la branche repartie d'elle sous le même nom se juge depuis lui.
Les deux sont plus stricts, jamais moins ; la sortie est celle d'un refus
sur la branche encore présente, ou un autre nom pour une branche neuve
après une fusion par écrasement. Les fusions de ce dépôt sont des commits
de fusion.

## Conséquences

Le hook avant push lit et écrit `.git/socle/pushed.json` ; rien n'est
versionné, rien ne change au script du hook ni à la CI. Un projet
installé le reçoit à sa mise à jour, sans geste (note de version
`2026-11-20-p`) ; un clone qui n'a encore rien poussé depuis se juge
comme avant. Le refus dit d'où la plage se juge. Défaire : retirer la
lecture du commit gardé dans `_plages_qui_partent` ; le fichier reste
alors inerte.
