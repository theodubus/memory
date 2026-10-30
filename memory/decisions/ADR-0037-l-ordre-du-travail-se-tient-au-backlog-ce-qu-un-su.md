<!-- socle: couche=decisions zone=publique -->
# ADR-0037 — L'ordre du travail se tient au backlog : ce qu'un sujet attend, et des jalons ; l'état calcule ce qui vient ensuite

> statut : acceptée · date : 2026-10-30 · source : D-0052@c07e54e4 · lu : decisions@331c06ca

## Contexte

Un sujet du backlog (ADR-0025@f97acbb5) a un statut et une origine, ni
ordre, ni dépendance, ni jalon. L'ordre ne vivait qu'en prose, dans les
prochaines étapes du chantier actif, qu'aucun contrôle ne confronte au
backlog : celles de ce dépôt avaient dérivé en historique. BMAD le
comblait par ses epics, ses stories et l'état du sprint ; son retrait
(ADR-0036@d5c2b493) rouvre le trou, avant que la planification du pilote
ne pose ses tâches (B-0101@0eeeab14). Théo a demandé l'ordre avant le
pilote (D-0052@c07e54e4).

## Décision

- **Un sujet nomme ce qu'il attend** : `après : B-NNNN, B-NNNN`, dans sa
  ligne de métadonnées (`after` en anglais). Un sujet clos, fait ou
  abandonné, ne retient plus ceux qui l'attendent.
- **Un jalon est un sujet** marqué `forme : jalon`, qui attend ses tâches,
  et le jalon d'avant s'il y en a un : aucune notion de plus, aucun
  fichier de plus.
- **Ce qui vient ensuite se calcule** : l'état donne le prochain jalon
  (ouvert, qu'aucun jalon ouvert ne précède) et ce qui lui reste, les
  sujets prêts (ouverts, pas encore en cours, dont tout ce qu'ils
  attendent est clos), ceux du
  prochain jalon d'abord, et le nombre de sujets en attente ; le rappel
  de fin de tour le redonne. Sans `après` ni jalon, rien ne s'affiche.
- **Un contrôle, `memoire.ordre`**, refuse un `après` qui nomme autre chose
  qu'un sujet du backlog, un cycle, et un sujet fait avant ce qu'il
  attend. Deux défauts injectés et un témoin sain l'éprouvent.
- Le chantier actif garde le travail en cours et les consignes ; l'ordre
  ne s'y recopie plus.

## Conséquences

L'ordre s'écrit une fois, là où vivent les sujets, et ce qui vient
ensuite ne dérive plus du backlog. Ce qui n'est pas fait : une priorité
entre sujets prêts (l'identifiant les range), une date, une estimation ;
un sujet en cours dont l'attendu est ouvert n'est pas refusé. Pour
défaire : retirer le champ, le calcul et le contrôle ; les sujets qui
portent `après` restent lisibles, le champ étant ignoré.
