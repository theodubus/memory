<!-- socle: couche=backlog zone=publique -->
# T-0012 — L'état signale un lot ouvert qui attend plus de tâches qu'une session n'en mène, sur un seuil mesuré

> statut : fait · origine : J-2026-11-15-J · besoin : B-0233 · lu : backlog@9966bbbd · ref : J-2026-11-20-S

Un commit : l'état et le rappel de fin de tour avertissent d'un lot ouvert au-delà d'un seuil que la tâche mesure sur les lots faits et écrit dans une décision ; son défaut injecté et son témoin sain. Ce que l'état peut savoir des fichiers d'une tâche pas encore faite se tranche en la menant. Le texte du skill `socle-batch` est T-0073.

## Fait quand

- [x] l'état et le rappel de fin de tour signalent un lot ouvert qui attend plus de tâches que le seuil mesuré, et se taisent en dessous ; un défaut injecté et un témoin sain le montrent
