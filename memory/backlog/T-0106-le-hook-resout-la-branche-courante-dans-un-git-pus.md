<!-- socle: couche=backlog zone=publique -->
# T-0106 — Le hook résout la branche courante dans un git push dont la branche vient de $(git branch --show-current), $(git rev-parse --abbrev-ref HEAD) ou $(git symbolic-ref --short HEAD)

> statut : ouvert · origine : J-2026-11-19-Z · besoin : B-0254 · priorité : haute · lu : backlog@692b5b51

Relevé par la passe 1 de la revue de L-0005 (J-2026-11-19-Z), pour le
backlog. T-0006 refuse un `git push` dont un argument ne se développe
pas, une substitution comprise : `git push -u origin "$(git branch
--show-current)"`, la même sans guillemets ou entre accents graves, et
`BRANCH=$(git branch --show-current); git push -u origin "$BRANCH"` le
sont. Le refus est voulu (ADR-0082, la règle de ce que rien ne
rattrape), et son message dit d'écrire la branche en toutes lettres ;
mais un agent écrit couramment ces formes pour pousser sa branche de
travail. Le hook lit déjà la branche courante pour un push sans
destination (`irreversible`, `engine/socle/hooks.py`). Le livrable, un
commit : ces trois substitutions, seules, se développent en la branche
courante, qui se juge comme écrite en toutes lettres.

## Fait quand

- [ ] `git push -u origin "$(git branch --show-current)"`, `$(git rev-parse --abbrev-ref HEAD)` et `$(git symbolic-ref --short HEAD)`, nus, entre guillemets, entre accents graves ou passés par une variable, passent le hook depuis une branche de travail, et un test le montre
- [ ] les mêmes, depuis la branche par défaut, sont refusés comme un push vers elle, et une autre substitution reste refusée, et un test le montre
- [ ] les mêmes, quand la même commande change de branche (`git checkout`, `git switch`) ou de dépôt (un `cd` ailleurs) avant le push, restent refusés, comme D-0140 le dit à Théo, et un test le montre
