<!-- socle: couche=backlog zone=publique -->
# B-0255 — Le hook de l'agent ne voit pas la sous-commande de git derrière --config-env ou --attr-source à valeur séparée : un push forcé ou un worktree retiré y passent

> statut : ouvert · origine : J-2026-11-16-B · priorité : haute · lu : backlog@c7c0d93f

La seconde revue du lot B-0234 (J-2026-11-16-B) : les options globales
de git `--config-env` et `--attr-source`, écrites avec leur valeur
séparée (`git --config-env core.x=HOME push …`), que git 2.43 accepte,
cachent la sous-commande au découpage (`commands.py`) et au hook
(`hooks.py`) : `git --config-env core.x=HOME push --force origin travail`
passe, et, depuis le worktree d'un sous-agent, `git --config-env
core.x=HOME worktree remove agent-s` aussi. Rare, mais rien ne rattrape
l'effet (ADR-0080) : de priorité haute.

La piste : ranger ces deux options parmi celles de git qui prennent une
valeur, là où `-C` et `-c` le sont.

## Fait quand

- [ ] les deux commandes ci-dessus sont refusées par le hook, et un test le montre
