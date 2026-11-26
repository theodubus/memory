<!-- socle: couche=backlog zone=publique -->
# T-0202 — socle new et socle show --index font citer l'empreinte de l'index du dernier commit, que les changements pas encore commités ne périment pas

> statut : fait · ref : J-2026-11-26-AO · origine : J-2026-11-26-AB · besoin : B-0362 · lu : backlog@0e2e535a

`cli.cmd_new` et `cli._texte_index` : l'empreinte à citer est celle de
l'index du dernier commit, que le contrôle accepte toujours, ce commit
étant la base ou un commit de la plage ; sans commit, celle de l'arbre.
L'index affiché reste celui de l'arbre, où un doublon se voit. Le
contrôle ne change pas. Son ADR dans le lot.

## Fait quand

- [x] un test crée deux tâches et un lot par `socle new`, passe une tâche existante en cours, et `memoire.lectures` passe
- [x] un test vérifie que `socle show --index backlog` imprime l'empreinte du dernier commit quand l'arbre en diffère
