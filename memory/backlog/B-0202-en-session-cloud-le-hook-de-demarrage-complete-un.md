<!-- socle: couche=backlog zone=publique -->
# B-0202 — En session cloud, le hook de démarrage complète un clone superficiel

> statut : ouvert · origine : J-2026-11-13-F · priorité : haute · lu : backlog@aa0df9d8

Le 13 novembre, le clone de la session cloud était superficiel : le
premier commit a été refusé par `memoire.references`, qui ne trouvait pas
les commits cités par le journal ; `git fetch --unshallow` l'a réglé
(J-2026-11-13-B, et déjà le 11 novembre). Le hook de démarrage, qui
installe déjà les outils de l'adaptateur en session cloud, peut compléter
l'historique de lui-même. Voisin de B-0175.

Le 13 novembre, Théo retient la priorité haute proposée (D-0108@96eeead5) :
le sujet fait partie de ceux à finir avant de revenir aux nouvelles
fonctions.

## Fait quand

- [ ] en session cloud, sur un clone superficiel, le hook de démarrage complète l'historique, et un test le montre
