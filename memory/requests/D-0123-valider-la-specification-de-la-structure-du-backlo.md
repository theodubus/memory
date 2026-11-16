<!-- socle: couche=demandes zone=publique -->
# D-0123 — Valider la spécification de la structure du backlog : besoin, tâche, lot et jalon, chacun avec son préfixe (B-0265)

> date : 2026-11-16

## Décision demandée

Valider la spécification ci-dessous, écrite ici en entier : le backlog en
quatre formes d'entrée, chacune avec son préfixe d'identifiant, les
contrôles qui empêchent de les remélanger, et la migration de ce dépôt et
des projets équipés. Répondez dans la conversation par l'un des mots de
la fin ; une condition que vous y ajoutez sera recopiée mot pour mot.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA comme Claude Code : il
garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose
en « demandes », comme celle-ci, les décisions qui vous reviennent. Le
backlog est la partie de la mémoire qui tient le travail à faire, une
entrée par fichier, chacune avec son identifiant (`B-0265`).

**Le chantier.** Le 16 novembre, vous avez relevé que le backlog mélange
des entrées qui demandent plusieurs livrables et des livrables seuls, et
que le mot « sujet » y désigne à la fois un travail, un lot et un jalon.
L'agent a proposé un « problème » et une tâche ; vous l'avez corrigé :
tout n'est pas un problème, une fonction à ajouter aussi, d'où le
« besoin ». Puis vous avez choisi d'écrire la structure en premier, dans
le lot en cours, et de donner à chaque forme son préfixe, pour la qualité
à long terme plutôt que l'effort minimal.

**La question.** Voici la structure telle que je propose de l'écrire,
avant d'en écrire le code : vous la validez, ou vous la corrigez.

**Les mots.** Le moteur : le programme du socle ; sa mise à jour, la
commande qui le remplace dans un projet. Un contrôle : une règle vérifiée
à chaque fin de tour de l'agent, à chaque commit et dans la CI, les
vérifications que GitHub lance à chaque envoi. Un défaut injecté : une
faute que l'auto-test s'inflige pour prouver que le contrôle l'attrape.
L'état : le résumé calculé au début de chaque session ; une entrée y est
prête quand rien de ce qu'elle attend n'est ouvert. Une entrée se clôt
`fait` ou `abandonné`. Ses critères sont des cases à cocher, aujourd'hui
dans une section « Fait quand ». Le journal, les décisions et les
demandes ne se récrivent jamais. Chess : le projet pilote.

**La spécification.**

1. *Les formes.* Un **besoin**, `B-` (les identifiants actuels le restent)
   : un défaut à corriger ou une fonction à ajouter ; ses constats ou sa
   motivation, sa spécification s'il n'est pas tranché, et « Satisfait
   quand », un résultat, jamais une implémentation. Une **tâche**, `T-` :
   un livrable, en principe un commit ; elle nomme son besoin (`besoin :
   B-NNNN`) ; son « Fait quand » se vérifie par des tests, ou, pour une
   action que vous seul pouvez faire (`pour : humain`), par ce qu'elle
   produit. Un **lot**, `L-` : des tâches qui touchent les mêmes fichiers,
   menées et relues ensemble ; une tâche est dans un lot au plus. Un
   **jalon**, `JA-` (`JA-0005` ; une entrée du journal s'écrit `J-` suivi
   de sa date) : des besoins qui servent un même but. La forme se lit sur
   l'identifiant : le champ `forme`, qui la porte aujourd'hui, disparaît.
2. *Ce que chaque forme attend.* Un besoin : des besoins, des demandes.
   Une tâche : des tâches, des besoins, des demandes. Un lot : ses tâches,
   des demandes, le lot d'avant. Un jalon : ses besoins, des demandes, le
   jalon d'avant. Le prochain lot ou jalon reste le premier ouvert
   qu'aucun autre ne précède. La priorité, haute ou basse, se donne à un
   besoin ou à une tâche ; une tâche sans priorité prend celle de son
   besoin.
3. *La clôture.* Une tâche, son « Fait quand » coché ; un besoin, ses
   tâches closes, l'une au moins faite, et son « Satisfait quand » coché ;
   un lot, ses tâches closes ; un jalon, ses besoins. Une tâche qui se
   révèle un besoin s'abandonne, en renvoyant au besoin ouvert.
4. *Les contrôles*, chacun avec son défaut injecté, refusent : un champ
   `forme` ; une tâche sans besoin, ou dans deux lots ; un `après` que sa
   forme n'attend pas (un lot qui attend un besoin) ; un besoin clos avec
   une tâche ouverte, sans tâche faite ou avec une case vide ; « Fait
   quand » dans un besoin, « Satisfait quand » dans une tâche ; un besoin
   ou une tâche nouveaux sans leur section. Ce qui est clos avant la
   migration reste tel quel : les contrôles de forme jugent les entrées
   ouvertes, ceux de clôture une clôture nouvelle. Un constat de revue
   devient une tâche si sa correction est claire, un besoin sinon.
5. *L'état* dit le prochain jalon et ses besoins ouverts, le prochain lot
   et ses tâches, les tâches prêtes, les besoins à découper (sans tâche
   ouverte), les besoins à fermer (leurs tâches closes), et ce qu'attend
   le reste, tâche ou demande.
6. *Les commandes* `socle new need`, `socle new task --need B-NNNN`,
   `socle new batch` et `socle new milestone` (les commandes sont en
   anglais, les identifiants en français) remplacent `socle new backlog`,
   qui disparaît sans alias ; `socle new need "…" --task "…"` crée le
   besoin et sa tâche quand la correction est évidente.
7. *L'ancien identifiant.* Une entrée renumérotée garde `ancien :
   B-NNNN`, que `socle show` et les contrôles des références résolvent ;
   le journal, les décisions et les demandes gardent les anciens numéros.
   Un ancien numéro ne se réattribue jamais ; `après` et `besoin` nomment
   l'identifiant actuel.
8. *La migration*, mécanique, à la mise à jour du socle, ici puis dans
   chess : chaque lot devient `L-` et chaque jalon `JA-`, clos compris ;
   toute autre entrée reste un besoin, son « Fait quand » renommé ; chaque
   besoin qu'attend un lot ouvert reçoit une tâche qui reprend ses
   critères, et le lot l'attend à sa place (ici, 51 tâches pour 8 lots ;
   chez chess, je ne peux pas le compter d'ici) ; un jalon attend les
   besoins de ses lots. Les citations se récrivent dans le backlog et le
   chantier actif (la page du travail en cours) ; ailleurs, l'ancien
   numéro se résout. Puis ici, par l'agent : les besoins à plusieurs
   livrables découpés, leurs critères récrits en résultats, les lots du
   jalon en cours refaits. Chez chess, l'agent fait de même pour chaque
   besoin quand il le prend ; vous n'y approuvez que l'habituel.
9. *Les textes* du produit, en français et en anglais (le format, le
   guide, les skills, les instructions posées, l'état, les notes de
   version) disent « entrée du backlog » et besoin, tâche, lot, jalon ;
   « sujet » n'y désigne plus rien du backlog.

**L'ordre.** Le moteur, les contrôles et la migration ; puis ce dépôt.
Deux sessions, à mon estimation. Les autres entrées du lot avancent
pendant votre lecture, sans attendre.

## Éléments cités

- B-0265@be0cf1bd — l'entrée du backlog qui porte cette structure, avec vos messages du 16 novembre mot pour mot.
- B-0264@618b9cb1 — le lot en cours : cette structure, puis cinq règles de méthode.
- B-0224@5541e3f1 — le jalon en cours, ce qui doit être fini avant les nouvelles fonctions.
- D-0121@ec62e9fd — votre choix d'écrire la structure en premier, dans le lot en cours.
- D-0122@dbcc64c1 — votre choix d'un préfixe distinct pour chaque forme d'entrée.

## Où regarder

- [B-0265](https://github.com/theodubus/memory/blob/ea73156977df2099381d4ea87a3552d9efc100c5/memory/backlog/B-0265-un-mot-pour-une-chose-dans-le-backlog-le-format-ap.md) :
  la proposition corrigée, résumée plus haut.
- [FORMAT.md](https://github.com/theodubus/memory/blob/ea73156977df2099381d4ea87a3552d9efc100c5/engine/socle/FORMAT.md),
  section « Backlog » : la règle que la spécification remplace.

## Options

- **La spécification, avec `JA-` pour le jalon.** Lisible en français.
  Effort : deux sessions. Risque : vingt entrées renumérotées ici
  (quatorze lots, six jalons) ; un ancien numéro mal résolu casserait une
  référence, ce que les contrôles des références attrapent. Réversible
  avant la fusion ; après, par une migration inverse à écrire.
- **La même, avec `M-` pour le jalon** (milestone) : une lettre, lisible
  en anglais, opaque en français. Même effort, même risque.

## Conséquences

Si vous validez : j'écris la décision, puis le code, relu par un relecteur
sans contexte avant la livraison. Si vous refusez : je corrige ce que
votre réponse dit, et vous soumets une spécification nouvelle. Sans
réponse : rien de la structure ne s'écrit.

## Recommandation

Valider, avec `JA-`. Vérifié : 65 besoins ouverts, dont 14 hors de tout
lot ; les motifs d'identifiant tiennent dans un seul module du moteur ; la
mise à jour range déjà le backlog d'un projet, un point d'entrée prêt pour
la migration. Supposé : que la migration laisse chess sans contrôle en
échec, ce qu'un test sur un projet d'essai vérifiera ; la durée.

## Réponses possibles

- `valider` — la spécification, avec `JA-` pour le jalon ; l'agent écrit la décision, puis le code.
- `jalon-M` — la spécification, avec `M-` pour le jalon.
- `refuser` — l'agent corrige ce que la réponse dit, et soumet une spécification nouvelle.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
