<!-- socle: couche=backlog zone=publique -->
# B-0212 — La revue d'un lot déjà poussé : la base par défaut de socle review, la branche distante, contient le lot, et le dossier n'a plus ni diff ni sujets

> statut : fait · origine : J-2026-11-14-A · lu : backlog@f9baa385 · ref : J-2026-11-14-G

La revue de B-0209 (J-2026-11-14-A), constat 3. `socle review` mesure le
lot depuis la branche distante de la branche courante, ce qu'elle n'a pas
encore poussé. Un lot déjà poussé n'y laisse rien : diff vide, aucun sujet,
plus de barre, et un relecteur qui rend « aucun constat ». En session
cloud, c'est le cas ordinaire : le hook de fin de tour de l'environnement
refuse de conclure tant qu'un commit n'est pas poussé (J-2026-11-13-M). La
seconde revue (`--since`) a le même défaut : sans `--base`, ses sujets
disparaissent. La revue de B-0209 s'est faite par `--base origin/main`.

Pistes : mesurer le lot depuis l'ancêtre commun avec la branche par
défaut quand la branche distante le contient déjà ; ou que le dossier
dise qu'il est vide parce que la base contient le lot, et la commande à
lancer.

## Satisfait quand

- [x] le dossier d'un lot déjà poussé, sans `--base`, donne son diff et ses sujets, ou dit pourquoi il est vide et quoi lancer, et un test le montre
