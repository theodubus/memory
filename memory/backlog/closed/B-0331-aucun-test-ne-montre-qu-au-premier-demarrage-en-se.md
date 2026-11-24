<!-- socle: couche=backlog zone=publique -->
# B-0331 — Aucun test ne montre qu'au premier démarrage en session cloud, sans marque d'échec, l'historique du clone reçoit ses 120 secondes

> statut : fait · ref : J-2026-11-23-M · origine : J-2026-11-22-Q · lu : backlog@3a8162c0

La revue de L-0009 (J-2026-11-22-Q), constat 1 pour le backlog. Selon
ADR-0105, au premier démarrage d'un conteneur, sans marque d'échec,
l'historique du clone reçoit 120 secondes au plus (`DELAI_HISTORIQUE`,
`completer_historique` dans `engine/socle/hooks.py`). Le relecteur y a
mis le délai court de la reprise, 15 secondes, à chaque démarrage : les
onze tests des deux classes de session cloud de `tests/test_hooks.py`
passent encore. Une telle régression laisserait superficiel le clone de
toute session dont l'historique prend plus de 15 secondes, et le premier
commit de l'agent serait refusé jusqu'au fetch à la main.

## Satisfait quand

- [x] au premier démarrage d'un conteneur, sans marque d'échec, l'historique du clone reçoit le délai qu'ADR-0105 lui donne, et une régression vers le délai court se voit
