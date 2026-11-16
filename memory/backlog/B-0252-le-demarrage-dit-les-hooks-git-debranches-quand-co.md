<!-- socle: couche=backlog zone=publique -->
# B-0252 — Le démarrage dit les hooks git débranchés quand core.hooksPath désigne .socle/git-hooks par un chemin absolu, comme après le redémarrage d'un conteneur cloud

> statut : ouvert · origine : J-2026-11-16-A · priorité : basse · lu : backlog@6e47a32f

Le 16 novembre, à la reprise d'une session cloud dont le conteneur avait
redémarré (J-2026-11-16-A), le démarrage a dit « hooks git non
branchés » : `core.hooksPath` valait le chemin absolu de
`<racine>/.socle/git-hooks`, sans qu'on sache qui l'avait écrit (le
redémarrage, ou la création des worktrees des sous-agents), et
`hooks.installer_hooks_git` ne le reconnaît pas (il n'accepte que
`.socle/git-hooks` écrit tel quel, et laisse tout autre choix local). Les
hooks tiraient pourtant : le push d'avant la coupure a passé le hook avant
envoi. La même ligne était venue le 14 novembre, dans les mêmes
circonstances, sans que le journal dise la valeur (J-2026-11-14-AA).
L'agent les a rebranchés chaque fois par la commande que l'état donne.

La piste : tenir pour branché un `core.hooksPath` qui se résout vers
`<racine>/.socle/git-hooks` ; un chemin absolu vers les hooks d'un autre
worktree reste un choix local, signalé.

## Satisfait quand

- [ ] le « Fait quand » de T-0042 est tenu
