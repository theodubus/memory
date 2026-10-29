<!-- socle: couche=demandes zone=publique -->
# D-0048 — Rendre automatique, en session cloud, l'installation des outils de l'adaptateur par le hook de démarrage

> date : 2026-10-29 · forme : séance

## Question posée

Je peux supprimer ce geste manuel. Dans une session cloud seulement, le hook de démarrage que le socle pose dans chaque projet installerait lui-même les outils de l'adaptateur. Ce sont les commandes que la CI lance déjà, ici `pip install pytest mutmut`. Coût : quelques secondes au démarrage de chaque session cloud ; sur votre machine, rien ne change. Je le recommande, et j'écrirais une ADR pour cette décision.

Pour toi : me dire si je rends l'installation des outils automatique en session cloud.
