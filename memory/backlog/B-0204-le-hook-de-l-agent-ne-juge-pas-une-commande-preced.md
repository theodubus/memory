<!-- socle: couche=backlog zone=publique -->
# B-0204 — Le hook de l'agent ne juge pas une commande précédée d'un mot du shell (then, do, else, !)

> statut : ouvert · origine : J-2026-11-13-H · lu : backlog@f4a491f0

Le découpage des commandes (`commands.analyser`) ne retire pas les mots
réservés du shell qui précèdent une commande simple : dans `if true; then
rm .socle/policy.toml; fi`, la commande lue est `then rm …`, dont le
programme est `then`, et ni ses écritures ni ce qu'elle a d'irréversible ne
se jugent. `! rm .socle/policy.toml` passe de même, et `for f in *.md; do
sed -i … "$f"; done` n'est pas lu comme un `sed -i`. Les redirections, elles,
se jugent (`{ echo x; } > .socle/policy.toml` est refusé). Vu en mesurant
les faux refus de B-0171 ; un contournement du même garde-fou, que seul
`protege.fichiers` attrape ensuite. La piste : retirer `then`, `do`,
`else`, `elif`, `!`, `{`, `if`, `while`, `until` en tête d'une commande
simple, comme les préfixes.

## Fait quand

- [ ] une écriture d'un fichier protégé derrière `then`, `do`, `else` ou `!` est refusée par le hook, et un test le montre
