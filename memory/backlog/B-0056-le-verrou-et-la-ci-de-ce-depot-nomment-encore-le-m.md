<!-- socle: couche=backlog zone=publique -->
# B-0056 — Le verrou et la CI de ce dépôt nomment encore le moteur et une commande en français

> statut : fait · origine : J-2026-10-13-W · pour : humain · lu : backlog@44afd8b1 · ref : J-2026-10-14-F

Le moteur de ce dépôt est passé de `moteur/` à `engine/` (ADR-0027). Deux
fichiers protégés, que toi seul modifies, nomment encore l'ancien :

1. `.socle/engine.lock` : remplacer `engine_dir = "moteur"` par
   `engine_dir = "engine"`.
2. `.github/workflows/socle.yml` : remplacer
   `python3 .socle/socle prive recuperer` par
   `python3 .socle/socle private recover` (l'ancien nom marche encore une
   version).

Puis `python3 .socle/socle approve --text "le moteur sous son nom anglais"`
et commiter. Ensuite, le lien `moteur` à la racine du dépôt peut partir ;
l'agent le retire quand le verrou ne le nomme plus.
