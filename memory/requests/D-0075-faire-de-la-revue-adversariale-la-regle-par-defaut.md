<!-- socle: couche=demandes zone=publique -->
# D-0075 — Faire de la revue adversariale la règle par défaut des instructions posées dans un projet (B-0124, ADR-0042)

> date : 2026-11-05

## Décision demandée

Faire de la revue adversariale d'un lot la règle par défaut des
instructions que l'installeur pose dans tout projet, comme ADR-0042 le
prévoit quand le banc montre qu'elle trouve des défauts que les contrôles
ratent.

## Contexte

La revue adversariale fait relire un lot, avant son push, par un sous-agent
sans contexte qui cherche à le prendre en défaut. Sa spécification, que vous
avez validée (ADR-0042), la commence comme une option : ce dépôt l'applique
à ses propres lots, le banc la mesure, puis une demande décide. Si elle
trouve des défauts que les contrôles ratent, elle devient la règle par
défaut des instructions posées dans un projet ; sinon, une option des
questions de départ.

Le banc l'a mesurée le 5 novembre. Le projet jetable portait une décision,
et un lot qui passe ses tests et ses contrôles mais la contredit en quatre
points. Les trois revues ont trouvé les quatre défauts, chacune à la ligne
exacte, avec le cas qui le prouve. Sur un lot sain, aucune n'a prétendu
que le code contredisait la décision ; leurs constats étaient de vrais trous
de test et des cas que la décision ne traite pas. Une revue a coûté 0,12
dollar sur ce petit lot ; elle coûtera davantage sur un lot plus gros, le
diff étant plafonné à 60 000 caractères.

Concrètement, la section « Livrer le travail » des instructions d'un projet
gagnerait une ligne : avant le push d'un lot qui change du code, une
spécification ou un test, l'agent le fait relire avec le skill
`socle-review`, et son récap dit les constats. La règle propre à ce dépôt
disparaît alors, devenue celle de tout projet. Cela suppose le skill, que
D-0074 vous soumet : sans lui, la ligne renverrait à un skill absent.

## Éléments cités

- ADR-0042@f52272e6 — la spécification de la revue adversariale : une
  option d'abord, mesurée au banc, puis cette demande.
- D-0074@a5cc393b — la demande qui vous soumet le skill `socle-review`,
  sans lequel cette règle ne peut pas s'appliquer.
- B-0124@dfa9917f — le sujet de la revue adversariale, et ses deux
  critères de fin, la procédure écrite et la mesure au banc.

## Où regarder

- [le relevé du banc](https://github.com/theodubus/memory/blob/454247c654fc74feb9e7c24aab4c8ce924e8a926/bench/reports/2026-11-05-revue.md) : ce que
  les revues ont trouvé, lot par lot, et ce que ça n'établit pas.
- [ADR-0042](https://github.com/theodubus/memory/blob/454247c654fc74feb9e7c24aab4c8ce924e8a926/memory/decisions/ADR-0042-la-revue-adversariale-d-un-lot-par-un-relecteur-sa.md) :
  la section « Décision », qui prévoit cette demande.

## Options

- **La règle par défaut** (recommandée) : tout projet équipé fait relire
  ses lots de code ; effort faible, une ligne des instructions, et une
  revue par lot, quelques dixièmes de dollar sur l'abonnement de chaque
  projet ; risque, des constats à écarter, et un coût qui croît avec le
  lot ; réversible, la ligne se retire.
- **Une option des questions de départ** : chaque projet la choisit à son
  installation ; effort moyen, une question de plus, sa réponse, et la ligne
  posée selon elle ; risque, la plupart des projets garderaient le défaut
  sans y penser ; réversible.

## Conséquences

Si vous validez, une fois le skill commité (D-0074), la ligne entre dans
les instructions posées dans un projet, en deux langues, la règle propre
à ce dépôt disparaît, et B-0124 se clôt. Si vous refusez, la revue devient
une option des questions de départ, que l'agent écrit ensuite. Sans
réponse, ce dépôt seul l'applique, et l'agent travaille sur autre chose.

## Recommandation

La règle par défaut. Vérifié : sur le banc, la revue trouve les quatre
défauts à chaque passage, sans prétendre fautif un lot sain, pour 0,12
dollar. Supposé : qu'elle garde cette justesse sur des lots réels, plus
gros et moins nets ; ce dépôt, qui l'applique d'abord, le dira.

## Réponses possibles

- `valider` — la revue devient la règle par défaut des instructions posées dans un projet.
- `refuser` — la revue devient une option des questions de départ.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
