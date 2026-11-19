<!-- socle: couche=backlog zone=publique -->
# B-0306 — Le hook de l'agent ne juge pas find … | filtre | xargs rm : un grep -v, un sort ou un head entre le find et xargs fait passer la suppression du projet

> statut : ouvert · origine : commit:3e83907e · priorité : haute · lu : backlog@bfb48097

Relevé par la passe 1 de la revue de L-0019, sur le commit relu, mesuré
avant et après le lot : `find .. -maxdepth 0 | grep . | xargs rm -rf`,
`find . -type f | grep -v x | xargs rm`, et les mêmes avec `| sort |` ou
`| head -100 |` entre le `find` et `xargs`, passent le hook. T-0004
(ADR-0095) juge `find … | xargs rm` comme un `find` qui supprime depuis
ses départs, mais `Commande.amont` n'est que la commande qui précède
`xargs` (`engine/socle/commands.py`), et `_supprimes_par_xargs`
(`engine/socle/hooks.py`) exige qu'elle soit un `find`. L'effet, la
suppression du projet, `.git` compris, rien ne le rattrape ; et l'idiome
`find | grep -v | xargs rm` est de la documentation courante.

## Satisfait quand

- [ ] `find … | <filtre de lignes> | xargs rm`, un filtre qui ne fait que retirer ou réordonner des lignes, se juge comme `find … | xargs rm`
