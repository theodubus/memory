<!-- socle: couche=decisions zone=publique -->
# ADR-0119 — Un besoin qui n'a jamais eu de tâche se clôt « fait » sur sa section « Satisfait quand » cochée ; l'état ne dit « à fermer » qu'un besoin que socle close accepterait

> statut : acceptée · date : 2026-11-28 · validation : D-0243@86332eab · source : B-0386@30f969b4, ADR-0083@512e719c, ADR-0117@287f443f, B-0363@8c80df98 · lu : decisions@0e9530aa

## Contexte

La spécification du backlog (ADR-0083@512e719c) ferme un besoin « quand
ses tâches sont closes, l'une au moins faite ; sinon il s'abandonne »,
et `memoire.formes` refuse tout besoin « fait » sans tâche faite. Le
produit fait pourtant naître deux sortes de besoins sans tâche : le
besoin `pour : humain`, que l'agent ferme sur la parole de l'humain sans
lui créer de tâche (B-0363@8c80df98), et l'attente, un besoin `bloqué`
qui se lève en se fermant (note `2026-11-27-i`). Ni l'un ni l'autre ne se
clôt « fait » : chez chess, une attente levée a coûté quatre gestes, une
tâche écrite après coup (B-0386@30f969b4). L'état dit aussi « à fermer »
un besoin dont les tâches sont closes mais une case vide, que `socle
close` (ADR-0117@287f443f) refuse. Théo a choisi, le 28 novembre, que
le besoin sans tâche se clôt sur ses cases cochées (D-0243@86332eab,
l'option A), plutôt qu'une tâche écrite par la clôture.

## Décision

1. *La clôture d'un besoin.* Un besoin qui a eu des tâches se ferme
   « fait » quand elles sont closes, l'une au moins faite ; ses tâches
   toutes abandonnées, il s'abandonne. Un besoin qui n'a jamais eu de
   tâche se ferme « fait » sur sa section `## Satisfait quand`, qui a au
   moins une case et les a toutes cochées. Une tâche close, rangée parmi
   les closes, compte : un besoin dont la tâche abandonnée est rangée a
   eu une tâche.
2. *Les refus.* `memoire.formes` garde son refus du besoin « fait » dont
   les tâches sont toutes abandonnées, et refuse le besoin « fait » sans
   tâche ni case ; `memoire.backlog` refuse, comme avant, le besoin
   « fait » dont une case reste vide. Ils ne jugent qu'une clôture
   nouvelle, comme avant.
3. *L'état.* Un besoin est « à fermer » quand `socle close` l'accepterait :
   aucune tâche ouverte, l'une faite ou aucune, et sa section cochée,
   une case au moins quand il n'a pas de tâche. Le reste ne change pas :
   un besoin ouvert qui n'est ni à fermer, ni en attente, ni pour
   l'humain, est « à découper » ; un besoin `bloqué` n'est ni l'un ni
   l'autre.
4. *L'auto-test.* Le défaut injecté `besoin-fait-sans-tache-faite` devient
   un besoin fait dont la seule tâche est abandonnée ; un défaut nouveau,
   le besoin fait sans tâche ni case ; un témoin, le besoin pour l'humain
   sans tâche, ses cases cochées, clos par `socle close`, qui passe le
   commit et la CI.

## Conséquences

Une attente levée et un besoin pour l'humain se closent en un geste,
leurs cases cochées. Un besoin d'avant le format, sans section, garde le
refus, faute de case qui dise ce qui est satisfait. L'état ne dit plus
« à fermer » un besoin que la clôture refuserait : un besoin aux tâches
closes et à une case vide redevient « à découper », ou attend, s'il est
bloqué. La note de version le dit aux projets installés. Se défait en
rétablissant l'exigence d'une tâche faite dans `memoire.formes` et dans
`ordre`.
