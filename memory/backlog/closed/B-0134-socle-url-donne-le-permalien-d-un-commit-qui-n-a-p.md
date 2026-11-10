<!-- socle: couche=backlog zone=publique -->
# B-0134 — `socle url` donne le permalien d'un commit qui n'a pas le fichier quand la branche locale suit `origin/main`

> statut : fait · origine : J-2026-11-08-S · lu : backlog@ac7c2a6d · ref : J-2026-11-09-S

`socle url` prend le dernier commit de `@{upstream}`. Une branche de travail
repartie de `origin/main` (`git checkout -B <branche> origin/main`) le suit
tant qu'on n'a pas fait `git branch -u` : le permalien vise alors le commit
de `main`, qui n'a pas encore le fichier nouveau. Le pilote l'a rencontré
(J-2026-11-08-S), et ce dépôt le contourne par `git branch -u` après chaque
fusion. Préférer la branche distante du même nom, quand elle existe.

Fait quand :
- [x] le permalien vise la branche distante du même nom, et un test le prouve sur une branche qui suit `origin/main`
