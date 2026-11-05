<!-- socle: couche=decisions zone=publique -->
# ADR-0044 — Le relecteur de la revue peut lire le dépôt, et son dossier le lui dit

> statut : acceptée · date : 2026-11-05 · source : D-0076@7b4ed056, ADR-0042@f52272e6 · lu : decisions@02c80171

## Contexte

ADR-0042@f52272e6 dit le dossier de `socle review` « tout ce que le
relecteur reçoit », et sa consigne disait au relecteur « tu n'as que ce
dossier ». C'est faux sous Claude Code : le sous-agent reçoit aussi les
instructions du projet et peut lire le dépôt. Théo a validé D-0076@7b4ed056,
qui corrige le skill `socle-review` sur ce point. La revue du lot suivant
l'a relevé : la consigne du dossier contredisait encore le skill, et
pouvait détourner le relecteur de vérifier un constat dans le dépôt. Trois
de ses sept constats venaient pourtant de fichiers hors du diff.

## Décision

- La consigne du dossier dit au relecteur qu'il n'a ni la conversation ni
  le raisonnement de l'agent, qu'il peut lire le dépôt pour vérifier un
  constat, et qu'il ne modifie rien.
- Le dossier reste ce que l'agent transmet, tel quel : rien ne s'y ajoute,
  rien ne s'en retire (D-0076).
- Le reste d'ADR-0042 et de ADR-0043@9be187f0 tient.

## Conséquences

Le relecteur peut chercher, au-delà du diff, ce que le lot oublie : une
doc qui renvoie à l'ancien texte, un passage dupliqué ailleurs. Le banc de
la revue (`bench/review.py`) lance encore le relecteur dans un dossier
vide : il mesure le dossier seul, le cas le plus dur. Se défait en
rétablissant l'ancienne consigne, dans `review.py` et son message
anglais.
