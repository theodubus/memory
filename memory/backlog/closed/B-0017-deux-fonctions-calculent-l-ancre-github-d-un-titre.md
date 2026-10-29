<!-- socle: couche=backlog zone=publique -->
# B-0017 — Deux fonctions calculent l'ancre GitHub d'un titre

> statut : fait · origine : J-2026-10-10-V · lu : backlog@5630c7c0 · ref : J-2026-10-13-Q

`liens.ancre`, écrite pour les permaliens, refait ce que fait déjà `slug`
dans `controles_memoire.py`, qui vérifie les ancres des liens de la mémoire.
Deux copies divergeront : n'en garder qu'une, que les deux modules
appellent.
