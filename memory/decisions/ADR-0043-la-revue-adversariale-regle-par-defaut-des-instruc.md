<!-- socle: couche=decisions zone=publique -->
# ADR-0043 — La revue adversariale, règle par défaut des instructions de tout projet

> statut : acceptée · date : 2026-11-05 · source : D-0075@d38d362d, ADR-0042@f52272e6 · lu : decisions@308fbed3

## Contexte

ADR-0042@f52272e6 commençait la revue adversariale comme une option : ce
dépôt l'appliquait à ses lots, le banc la mesurait, puis une demande
décidait. Le banc l'a mesurée (J-2026-11-05-B@a77786c0) : sur un lot qui passe ses
tests et contredit sa décision, les trois revues ont trouvé les quatre
défauts, sans prétendre fautif un lot sain. Théo a validé D-0075@d38d362d.
ADR-0042 décrit l'état d'avant ; une décision ne se réécrit pas, celle-ci
la complète.

## Décision

- La revue adversariale est la règle par défaut des instructions que
  l'installeur pose dans tout projet, section « Livrer le travail » : avant
  le push d'un lot qui change du code, une spécification ou un test,
  l'agent le fait relire par un relecteur sans contexte (le skill
  `socle-review`), et son récap dit les constats. Le guide le dit.
- La règle propre à ce dépôt, que prévoyait ADR-0042, disparaît : ce dépôt
  suit la règle de tout projet. Elle n'a jamais été commitée, la règle par
  défaut l'ayant remplacée dans le même lot.
- Le reste d'ADR-0042 tient : le dossier de `socle review`, une passe par
  lot, aucun constat qui bloque seul, rien sur GitHub.

## Conséquences

Chaque lot de code d'un projet équipé coûte une revue : 0,12 dollar sur
le petit lot du banc, davantage sur un lot plus gros, le diff étant
plafonné à 60 000 caractères.

Ce que la mesure n'établit pas : le banc lançait le relecteur dans un
dossier vide, sans rien du projet. Sous Claude Code, un sous-agent lancé
dans le dépôt reçoit les instructions du projet et peut le lire : il a
plus de contexte que le relecteur mesuré (relevé par la première revue de
ce dépôt, le 5 novembre).

Pour défaire : retirer la ligne de la section « Livrer le travail » des
gabarits d'instructions et le paragraphe du guide, en deux langues.
