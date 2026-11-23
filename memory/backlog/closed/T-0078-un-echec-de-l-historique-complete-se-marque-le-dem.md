<!-- socle: couche=backlog zone=publique -->
# T-0078 — Un échec de l'historique complété se marque : le démarrage suivant du même conteneur ne lui redonne pas son délai entier

> statut : fait · origine : J-2026-11-18-J · besoin : B-0219 · lu : backlog@84ad299e · ref : J-2026-11-22-M, ADR-0105

Un commit : `completer_historique` garde la trace d'un échec pour le conteneur, et le démarrage suivant (une reprise, un compactage) ne repaie pas son délai entier.

## Fait quand

- [x] après un fetch de l'historique qui a échoué, le démarrage suivant du même conteneur ne lui redonne pas son délai entier, et un test le montre
