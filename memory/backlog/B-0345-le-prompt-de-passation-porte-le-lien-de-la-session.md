<!-- socle: couche=backlog zone=publique -->
# B-0345 — Le prompt de passation porte le lien de la session qui part, dont la session neuve ne se sert pas

> statut : ouvert · origine : J-2026-11-24-AF · ref : D-0176 · lu : backlog@87515a69

`socle handoff prompt --session <lien>` ouvre le prompt de passation
par « Passation de <lien de la session qui part> », et les skills
`socle-handoff` et `delegate-lot` disent de le passer. La session neuve
ne s'en sert pas : la garde ne lit que la branche, la tête et l'heure,
tout le reste est dans le dépôt, et ses commits portent déjà le lien de
leur session ; d'un autre compte, il ne s'ouvre même pas. Théo le
retire du produit (D-0176, J-2026-11-24-AF).

## Satisfait quand

- [ ] le prompt de passation ne porte plus le lien d'une session, dans le produit comme dans ce dépôt
