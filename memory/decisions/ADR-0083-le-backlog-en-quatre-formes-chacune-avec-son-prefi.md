<!-- socle: couche=decisions zone=publique -->
# ADR-0083 — Le backlog en quatre formes, chacune avec son préfixe : besoin B-, tâche T-, lot L-, jalon JA-

> statut : acceptée · date : 2026-11-16 · validation : D-0123@61a56e15 · source : B-0265@f07750af, D-0121@ec62e9fd, D-0122@dbcc64c1, J-2026-11-16-T@45c1634d, ADR-0079@d9cd58c2 · lu : decisions@f49444c2

## Contexte

Le backlog mélangeait des entrées qui demandent plusieurs livrables et des
livrables seuls, et le mot « sujet » y désignait un travail, un lot et un
jalon (B-0265@f07750af). Théo a choisi d'écrire la structure en premier
(D-0121@ec62e9fd) et un préfixe par forme (D-0122@dbcc64c1), puis validé
la spécification telle qu'écrite, avec `JA-` pour le jalon
(D-0123@61a56e15, J-2026-11-16-T@45c1634d). Elle remplace, pour la forme
d'un lot, ce qu'en disait ADR-0079@d9cd58c2 (`forme : lot`) ; sa conduite
reste au skill `socle-batch`.

## Décision

La spécification de D-0123@61a56e15, ses neuf points, telle qu'écrite :
les quatre formes et leurs préfixes, ce que chacune attend, la clôture,
les contrôles, l'état, les commandes, l'ancien identifiant, la migration
et les textes. Ce qu'elle ne tranchait pas, tranché ici :

1. *Les mots.* Le champ `besoin` (`need` en anglais), le champ `ancien`
   (`former`), la section `## Satisfait quand` (`Satisfied when`) ; les
   commandes `socle new need|task|batch|milestone`, `--need` et `--task`.
   Une entrée privée garde son `P` devant le préfixe (`PT-`, `PJA-`).
2. *La forme se lit sur l'identifiant* partout : l'index du backlog
   (`backlog@…`), la lecture prouvée, le rangement des clos et la bascule
   en privé valent pour les quatre formes. Un besoin, sa tâche et leur lot
   s'écrivent ensemble, dans un ordre que leurs numéros ne disent pas d'une
   forme à l'autre : la lecture de l'index vaut aussi sans les entrées que
   le même travail ajoute dans d'autres formes.
3. *Une tâche hérite de son besoin* sa priorité, quand elle n'en a pas, et
   ce qu'il attend : elle n'est prête qu'une fois clos ce qu'elle attend et
   ce qu'attend son besoin. Une priorité sur un lot ou un jalon, ou un
   champ `besoin` hors d'une tâche, est refusé : ils ne sont jamais prêts.
4. *L'état.* Le prochain jalon dit ses besoins et ses demandes encore
   ouverts ; un besoin est « à fermer » quand ses tâches sont closes, l'une
   au moins faite, et « à découper » quand il n'a aucune tâche ouverte, ni
   rien d'ouvert qu'il attend ; le reste se compte selon ce qu'il attend,
   une entrée du backlog ou une demande.
5. *Les sections.* Un lot et un jalon gardent la section qu'ils ont ; rien
   ne leur en exige une.
6. *Les contrôles.* Un contrôle nouveau, `memoire.formes`, porte les refus
   du point 4 ; ceux qu'il ne porte pas s'étendent : `memoire.backlog`
   juge les cases de la section de chaque forme, `memoire.ordre` les
   quatre préfixes, `memoire.format` un ancien numéro réattribué,
   `memoire.references`, `memoire.lectures` et `memoire.ajout-seul`
   l'ancien numéro résolu.
7. *La migration*, à chaque mise à jour, idempotente sur le contenu (le
   format du verrou reste `3`) : les lots et les jalons prennent leur
   préfixe par ordre de leur ancien numéro, leur champ `forme` retiré,
   et leur priorité, que le point 3 refuse : avant cette décision déjà, un
   lot ou un jalon n'était jamais pris (le moteur l'écartait des entrées à
   prendre), et sa priorité ne changeait aucun ordre ; le bilan de la mise
   à jour nomme chaque entrée dont elle l'a retirée. Les tâches se numérotent dans l'ordre des lots puis de leur `après`.
   Une tâche posée par la migration prend le titre, l'origine et le statut
   de son besoin, ses critères, ou, s'il n'en a pas, un seul critère non
   coché qui le nomme ; ni priorité ni `après`, qu'elle hérite. La section
   du besoin renvoie alors à elle d'une seule case : une copie divergerait,
   et `docs.copie` la refuse. Dans l'`après` d'un jalon, un lot devient
   tous ses besoins, clos compris ; dans celui d'un besoin, un lot ou un
   jalon devient ses besoins et ses demandes encore ouverts. La section des
   besoins ne se renomme qu'une fois, tant que le backlog n'a aucune entrée
   à préfixe `T-`, `L-` ou `JA-`.

## Conséquences

Le backlog se lit en quatre formes, et les contrôles empêchent de les
remélanger. Ce dépôt est migré dans le même travail ; chess le sera à sa
mise à jour. Le découpage des besoins à plusieurs livrables, leurs
critères récrits en résultats et les lots du jalon en cours refaits sont
une tâche du besoin, pour une session suivante. Défaire : une migration
inverse, à écrire, qui rendrait `forme` aux lots et aux jalons et leur
ancien numéro, et rendrait aux lots leurs besoins.
