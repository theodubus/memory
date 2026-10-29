<!-- socle: couche=decisions zone=publique -->
# ADR-0030 — Les sujets clos du backlog rangés à l'écart des ouverts, par le moteur

> statut : acceptée · date : 2026-10-15 · lu : decisions@9a83834a · validation : D-0028

## Contexte

ADR-0025@f97acbb5 a fait du backlog un dossier, un fichier par sujet, et y
a laissé chaque sujet clos à sa place. Théo trouve que les sujets clos,
mêlés aux ouverts, polluent la liste du dossier, et a validé
(D-0028@aa33fbf6) qu'ils aillent dans un sous-dossier, rangés par le
moteur.

## Décision

- Au format 3, un sujet clos (`fait` ou `abandonné`) est rangé dans le
  sous-dossier `closed` du backlog, son pendant privé sous
  `private/backlog/`. Il garde son fichier, son identifiant et le plafond
  d'un sujet ; la lecture de la mémoire voit ce sous-dossier comme le
  backlog.
- `socle archive` range : il y déplace chaque sujet clos, remet parmi les
  ouverts un sujet rouvert, et indexe le déplacement d'un fichier suivi.
  Le dépôt compagnon de la mémoire privée commite le sien lui-même.
- Le contrôle du backlog refuse un sujet clos laissé parmi les ouverts, et
  un sujet ouvert rangé avec les clos ; il le dit avec la commande. Un
  défaut injecté et un témoin sain l'éprouvent à l'auto-test.
- La migration depuis le format 2 range les clos d'emblée ; la mise à jour
  d'un projet déjà au format 3 les range une fois.
- La bascule en privé d'un sujet garde son rangement.

Ce point remplace « un sujet clos reste dans son fichier » d'ADR-0025 ; le
reste d'ADR-0025 vaut toujours.

## Conséquences

La liste du dossier du backlog ne montre que les sujets ouverts ; l'agent,
qui lit l'index des ouverts et l'état, ne change rien à sa lecture. Clore
un sujet demande un geste de plus, `socle archive`, que le contrôle
rappelle. Un lien relatif vers le fichier d'un sujet déplacé devient mort,
et le contrôle des références le signale ; un permalien reste valide.
Pour défaire : retirer le sous-dossier de la lecture, le contrôle et le
rangement, et remettre les fichiers à plat.
