# Passation du lot 3, le 14 novembre

Le lot 3 (B-0221, le hook) est fait en grande partie, pas relu : la
fenêtre de cinq heures a atteint sa limite pendant le travail des deux
implémenteurs. Rien de ce code n'est sur la branche par défaut ; il est
ici en correctifs, partis de 08f170a, le commit qui a fini le lot 2.

- Dossier `a` : trois commits, la règle 2 de D-0112 (une ADR nouvelle,
  le guide et les notes de version), B-0208 et B-0205. Le dernier
  `verify --fast` de l'implémenteur n'a pas rendu son résultat.
- Dossier `b` : deux commits, B-0204 et B-0207 ; puis
  `en-cours-B-0206.diff`, B-0206 presque fini et pas commité (son défaut
  injecté attrapé, son témoin sain passant, un sujet neuf ouvert pour le
  script qu'un heredoc donne à python).

Chaque série s'applique seule sur la branche partie de la branche par
défaut (vérifié) ; l'une après l'autre, elles se heurtent, ayant changé
les mêmes fichiers (les notes de version, le journal, l'auto-test, le
hook) : la seconde se résout à la main. Leurs entrées de journal ont
pris des lettres que la branche par défaut a prises depuis : elles se
renumérotent (`python3 .socle/socle renumber`). Ensuite, selon le skill
delegate-lot : appliquer `a` (`git am`), puis `b` et le diff (`git apply
--index`), finir et commiter B-0206, `verify --fast`, une seule revue sans contexte du lot
(skill socle-review, la règle de D-0111), ses bloquants corrigés, la
pull request, sa fusion ; ce dossier retiré dans le commit qui intègre
le lot.
