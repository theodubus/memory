<!-- socle: couche=decisions zone=publique -->
# ADR-0086 — Un passage des étapes rapides où une étape échoue ne garde pas sa durée : le dernier passage complet est le dernier qui a tout passé

> statut : acceptée · date : 2026-11-18 · source : D-0130@ae44699b, J-2026-11-17-L@f4405447, B-0258@ae67caba · lu : decisions@4678c1d9

## Contexte

La spécification de la durée des étapes, validée par Théo (le second
point de D-0130@ae44699b, J-2026-11-17-L@f4405447), fait garder à
`verify --fast`, quand il lance toutes les étapes rapides, leur total et
la plus longue, « avec la trace de ce passage » ; l'avertissement d'un
total au-delà du seuil se répète ensuite, dans l'état et sur la ligne des
étapes déjà passées, « tant que le dernier passage complet dépasse le
seuil ». Elle ne dit pas ce que devient un passage où une étape échoue.

Un tel passage ne mesure pas les étapes telles qu'elles passent : une
compilation qui échoue s'arrête avant les tests, une étape bloquée finit
en erreur de délai (B-0258, son modèle de menace, la laisse passer). Gardé,
son total court effacerait une dérive mesurée au passage d'avant ; son
total long, une étape bloquée, avertirait sur un temps qui n'en est pas un.

## Décision

Le dernier passage complet est le dernier où toutes les étapes rapides
ont passé : le même critère que la marque des étapes déjà passées, écrite
à côté. Un passage où une étape échoue imprime ses durées et leur total,
comme tout passage, mais ne remplace pas la trace du précédent et
n'avertit pas.

## Conséquences

- `verification.etapes_rapides` écrit la marque et la trace des durées
  sous la même condition ; un test le garde (un passage en échec laisse la
  trace d'avant).
- Une dérive que seul un passage en échec montrerait se dit au bout du
  premier passage qui réussit, quel qu'en soit le lanceur : `verify
  --fast` dans sa sortie, le hook avant envoi sur sa sortie d'erreur, la
  fin de tour à l'humain, sans bloquer, et à l'agent seulement quand elle
  bloque déjà ; l'agent ne livre pas sur un échec.
- Pour défaire : une ADR qui la remplace, par exemple pour garder la durée
  d'un échec qui a lancé toutes ses étapes jusqu'au bout.
