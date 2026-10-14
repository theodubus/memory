<!-- socle: couche=backlog zone=publique -->
# B-0039 — Éprouver sur GitHub les étapes de CI que posent les cinq adaptateurs nouveaux

> statut : ouvert · origine : J-2026-10-11-Q · lu : backlog@7813094e

Chaque adaptateur nouveau ajoute au workflow de CI ses étapes
d'installation (Node, Go, Java, Ruby, PHP avec pcov, et leurs dépendances).
Le banc des adaptateurs les a éprouvés ici, pas dans un workflow GitHub :
ces étapes sont supposées. Les éprouver sur un dépôt jetable de chaque
langage, poussé sur GitHub, avec le workflow que pose l'installeur.
