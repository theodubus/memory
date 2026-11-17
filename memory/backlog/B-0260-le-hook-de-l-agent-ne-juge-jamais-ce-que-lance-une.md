<!-- socle: couche=backlog zone=publique -->
# B-0260 — Le hook de l'agent ne juge jamais ce que lance une substitution entre guillemets : x="$(cd .. && rm -rf projet)" supprime le projet sans refus

> statut : ouvert · origine : J-2026-11-16-F · priorité : haute · lu : backlog@e7ed1bbf

La troisième passe de revue du lot L-0004 (J-2026-11-16-F) : le découpage
(`engine/socle/commands.py`) ne juge pas la commande que lance une
substitution entre guillemets, `"$(…)"`, sur les moteurs d1d296e,
08b925a et la tête : `echo "$(rm -rf ..)"`, `echo "$(cd memory; rm -rf
../../<racine>)"` et `x="$(f; rm -rf ../../<racine>)"` passent. B-0207@faf7a185
l'avait laissé en risque accepté, avant ADR-0080. La forme
`x="$(commande)"` est de celles qu'un agent écrit dans son travail, et la
suppression du projet que rien ne rattrape : de priorité haute, sous la
règle d'aujourd'hui comme sous celle que propose D-0120.

La piste : juger le texte d'une substitution entre guillemets comme celui
d'une substitution nue (`_analyser` sur son texte, avec les fonctions
connues), que `_preparer` sait déjà délimiter (B-0207).

## Satisfait quand

- [ ] le « Fait quand » de T-0007 est tenu
