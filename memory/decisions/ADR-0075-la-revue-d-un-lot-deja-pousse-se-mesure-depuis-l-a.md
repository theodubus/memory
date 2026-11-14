<!-- socle: couche=decisions zone=publique -->
# ADR-0075 — La revue d'un lot déjà poussé se mesure depuis l'ancêtre commun avec la branche par défaut, et le dossier vide dit pourquoi

> statut : acceptée · date : 2026-11-14 · source : B-0212@11c126ca, ADR-0042@c8fe8e02, ADR-0073@1e48220c · lu : decisions@9d422d25

## Contexte

ADR-0042@c8fe8e02 mesure le lot de `socle review` par ce que la branche
n'a pas encore poussé. Un lot déjà poussé n'y laisse rien : diff vide,
aucun sujet, et un relecteur qui rend « aucun constat ». En session cloud,
c'est le cas ordinaire : le hook de fin de tour de l'environnement exige
un push. La seconde revue d'ADR-0073@1e48220c perd de même ses sujets
quand le commit relu est déjà poussé (B-0212@11c126ca).

## Décision

Sans `--base`, la base reste la branche distante de la branche courante,
sinon la branche par défaut. Mais quand la branche distante **contient
déjà le lot** — rien n'en diffère hors de la mémoire, ni un commit ni
l'arbre ; pour une seconde revue, le commit relu (`--since`) y est
déjà —, le lot se mesure depuis l'ancêtre commun de HEAD et de la branche
par défaut, et le dossier le dit, avec la commande pour un lot qui
commence plus tard : `socle review --base <le commit d'avant le lot>`.

Si cet ancêtre commun contient aussi le lot (la branche est la branche par
défaut, le lot y est fusionné, ou la branche par défaut n'est que devinée),
la base reste la branche distante, et le dossier dit qu'il est vide parce
qu'elle contient le lot, et la commande à lancer.

Un `--base` donné est pris tel quel. L'ancêtre commun ne vaut ici que pour
le lot déjà poussé : la comparaison à l'ancêtre commun en général reste
l'objet de B-0213@3cbbe6e6.

## Conséquences

Un lot poussé avant sa revue en a une, sans option. Sur une branche où
plusieurs lots se suivent, tous poussés, le dossier les donne ensemble ;
la note dit comment réduire. Se défait en revenant à la seule branche
distante dans `engine/socle/review.py`.
