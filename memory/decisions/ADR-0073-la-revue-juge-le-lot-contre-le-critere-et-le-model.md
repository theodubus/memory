<!-- socle: couche=decisions zone=publique -->
# ADR-0073 — La revue juge le lot contre le critère et le modèle de menace de ses sujets : bloquants corrigés dans le lot, le reste au backlog

> statut : acceptée · date : 2026-11-13 · source : B-0209@f600b5a4, ADR-0042@c8fe8e02 · lu : decisions@b9ecf80c

## Contexte

La revue d'ADR-0042@c8fe8e02 demande au relecteur de prendre le lot en
défaut sans lui dire où s'arrêter, et le skill `socle-review` dit de
corriger dans le lot chaque constat fondé. Sur un garde-fou sans fond
(deviner ce qu'une commande du shell écrit), chaque tour trouve une forme
de plus, et chaque correction en ouvre d'autres : le lot qui la précède
a pris quatre revues et trois corrections (B-0209@f600b5a4). Cette
décision en est la spécification, écrite avant son code.

## Décision

**Les sujets du lot.** Le dossier de `socle review` donne en entier, quel
que soit leur statut, les sujets du backlog que le lot touche et qui
existaient à sa base, ou qu'il clôt : leur « Fait quand » est la barre.
Ceux qu'il ouvre sans les clore, il n'en donne que le titre : ce que le
lot renvoie au backlog, que le relecteur ne redemande pas. Suivent, en
entier, les décisions et les demandes que le lot ajoute (sa
spécification, un modèle de menace écrit en décision), que ses sujets,
plus anciens, ne citent pas ; puis celles que citent ses sujets.

**Le modèle de menace.** Un sujet qui pose ou change un garde-fou écrit,
avant son code, son modèle de menace dans une section `## Modèle de
menace` (ou la décision qu'il cite) : ce que le garde-fou arrête, ce qu'il
laisse passer. Le dossier le donne avec le sujet ; un garde-fou sans
modèle de menace est un constat bloquant. Un sujet dont la conception
n'est pas tranchée écrit sa spécification avant son code. Le gabarit
d'AGENTS.md le dit, et FORMAT.md la section.

**Deux classes de constats.** La consigne demande de classer chaque
constat : bloquant (il contredit un critère coché ou une décision citée,
fait régresser ce qui marchait, perd des données, ou contourne le
garde-fou dans son modèle de menace) ou pour le backlog (le reste : un
cas hors du modèle, un critère non coché, un défaut voisin, une
amélioration). Seuls les bloquants se corrigent dans le lot ; les autres
deviennent des sujets du backlog.

**La seconde revue.** Seulement si la correction de bloquants est lourde
(elle change la conception d'une partie, pas quelques lignes), et sur
elle seule : `socle review --since <commit relu>` donne le diff depuis ce
commit, les messages de ses commits, et les sujets du lot entier.

## Conséquences

Une revue rend moins de travail dans le lot et plus au backlog, où
l'humain voit ce qui reste. Le texte du skill `socle-review` change dans
son gabarit ; sa copie protégée de ce dépôt suit sur une demande. Se
défait en revenant au texte d'avant du dossier et du skill.
