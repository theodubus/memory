<!-- socle: couche=backlog zone=publique -->
# B-0171 — Le hook de l'agent ne juge pas un chemin protégé écrit par une variable ou un motif du shell

> statut : ouvert · origine : J-2026-11-11-O · priorité : haute · lu : backlog@65c7a36c

Le hook de l'agent juge les chemins qu'une commande écrit tels qu'ils sont
tapés : une variable ou un motif que le shell développerait n'y est pas
développé. `echo x > $F`, ou `rm .socle/pol*`, passe le hook alors que le
shell écrirait un fichier protégé ; seul le contrôle `protege.fichiers`
l'attrape ensuite, à la fin du tour et au commit. De même, un `pushd`
n'est pas suivi comme un `cd` : `pushd .socle && echo x > policy.toml`
passe le hook. La remise en état de
D-0098 refuse déjà un chemin qui n'est pas écrit en toutes lettres. La
piste : refuser toute écriture du shell dont un chemin n'est pas littéral
et peut viser un chemin protégé, au prix de faux refus à mesurer.

Le 12 novembre, Théo valide la priorité haute proposée (D-0106) : c'est
un contournement possible d'un garde-fou.

## Fait quand

- [ ] une écriture du shell vers un chemin protégé écrit par une variable ou un motif est refusée par le hook, et un test le montre
