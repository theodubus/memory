<!-- socle: couche=backlog zone=publique -->
# L-0032 — Lot de l'adaptateur kotlin sur Compose Multiplatform et Android

> statut : fait · origine : J-2026-11-21-P · après : L-0036, T-0151, T-0152 · lu : backlog@6c894b15 · ref : J-2026-11-25-M, J-2026-11-25-N

La copie `kotlin` des adaptateurs (`engine/socle/adapters/`), qui suppose des modules JVM : la piste soumise à Théo (T-0151) puis tenue (T-0152, B-0147). Seul dans son lot : aucune autre tâche de JA-0005 ne touche un adaptateur. Formé le 21 novembre, sur la décision de Théo (D-0154, J-2026-11-21-Q).

Le 24 novembre, L-0031 fermé par D-0168, il suit L-0024.

Le 24 novembre, sur D-0180, il suit L-0036, le lot des corrections restantes de JA-0005 (J-2026-11-24-AV).

Le 25 novembre, L-0037 et L-0038 attendant les réponses de Théo (D-0189, D-0190), il passe devant eux (J-2026-11-25-I).

## Revues

### Passe 1 — 2026-11-25

Commits : e173afb8..ef593887
- Bloquant : l'avertissement renvoyait à un chemin de la spécification absent d'un projet installé, où le moteur est dans le sous-dossier socle de son dossier
- Bloquant : une copie Android adaptée selon la spécification (`test` gardé, la compilation changée) restait avertie à chaque mise à jour ; chaque module se juge désormais par la commande qui ne le sert pas
- Ouvre : rien
