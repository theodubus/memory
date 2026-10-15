<!-- socle: couche=backlog zone=publique -->
# B-0039 — Éprouver sur GitHub les étapes de CI que posent les cinq adaptateurs nouveaux

> statut : fait · origine : J-2026-10-11-Q · lu : backlog@7813094e · ref : J-2026-10-15-K, F-0019, F-0020

Chaque adaptateur nouveau ajoute au workflow de CI ses étapes
d'installation (Node, Go, Java, Ruby, PHP avec pcov, et leurs dépendances).
Le banc des adaptateurs les a éprouvés ici, pas dans un workflow GitHub :
ces étapes sont supposées. Les éprouver sur un dépôt jetable de chaque
langage, poussé sur GitHub, avec le workflow que pose l'installeur.

Éprouvé le 15 oct. pour le workflow « Socle » : 5 sur 5 sur GitHub (F-0019,
J-2026-10-15-C). Reste le workflow du balayage de mutation, que GitHub n'a
pas enregistré dans le dépôt d'essai : le lancer à la main depuis l'onglet
Actions, ou attendre son créneau planifié, puis lire son verdict, surtout
celui de PHP (Infection avec pcov).
