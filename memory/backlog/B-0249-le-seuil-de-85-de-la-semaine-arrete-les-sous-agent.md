<!-- socle: couche=backlog zone=publique -->
# B-0249 — Le seuil de 85 % de la semaine arrête les sous-agents même quand ce qui reste couvre un sujet et le rangement : le seuil se calcule sur le coût mesuré d'un sous-agent

> statut : ouvert · origine : J-2026-11-15-P · lu : backlog@b768e7eb

Le skill `socle-batch` ne lance plus aucun sous-agent au-delà de 85 % de
la semaine ou de 60 % de la fenêtre de cinq heures. Sans remise à zéro en
réserve, ce seuil laisse inemployé ce qui reste de la semaine, quand un
sujet et le rangement y tiendraient : Théo a demandé de faire encore un
lot, en tout ou en partie, sur les 15 % restants, tant que la session
passe le relais avant la limite (J-2026-11-15-P).

La piste : un seuil calculé sur le coût mesuré d'un sous-agent (3 à 4
points de la semaine en novembre, J-2026-11-13-E) et du rangement, plutôt
qu'un pourcentage fixe : un sous-agent se lance si ce qui reste couvre sa
part et celle du rangement ; le rangement commence à une marge fixe de la
limite.

## Satisfait quand

- [ ] le « Fait quand » de T-0037 est tenu
