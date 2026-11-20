<!-- socle: couche=backlog zone=publique -->
# B-0305 — Le hook de l'agent laisse passer un push vers la branche par défaut écrit HEAD (git push -u origin HEAD depuis elle), et un push sans destination après un changement de branche dans la même commande

> statut : abandonné · origine : J-2026-11-19-AM · ref : D-0143 · priorité : haute · lu : backlog@3711f154

Relevé en écrivant T-0106 (J-2026-11-19-AM), mesuré sur le hook de ce
commit, dans un projet d'essai. `_git_irreversible`
(`engine/socle/hooks.py`) prend pour destination d'un push le nom écrit
après `:`, ou le refspec entier : `HEAD` et `@` ne sont pas des
branches protégées, et `git push -u origin HEAD`, lancé depuis la branche
par défaut, passe ; il pousse pourtant cette branche, ce que rien ne
rattrape ensuite. Un agent écrit couramment cette forme pour pousser sa
branche. Et la branche courante qu'il lit pour un push sans destination
est celle d'avant la commande : `git checkout main && git push` passe
depuis une branche de travail. T-0106 (ADR-0097) ne résout une
substitution de la branche courante que si rien ne change de branche
avant le push ; la même garde manque à `HEAD` et au push sans
destination.

Abandonné le 20 novembre par D-0143 (ADR-0098) : le hook de l'agent est terminé, et cette entrée ne cite aucune preuve vue dans une session.

## Satisfait quand

- [ ] un push dont la destination est `HEAD` ou `@`, ou qui n'en nomme pas, se juge sur la branche courante, et il arrête l'agent au hook quand elle est la branche par défaut ou quand la même commande change de branche avant lui
