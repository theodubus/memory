<!-- socle: couche=backlog zone=publique -->
# B-0095 — Un projet à deux langages n'a qu'un adaptateur : le code du second n'est pas jugé

> statut : abandonné · origine : J-2026-10-30-B · ref : D-0153, ADR-0051, B-0147, B-0179 · lu : backlog@8d122b8b · après : B-0104

Le cadrage du pilote recommande Flutter pour l'application et Python
(FastAPI) pour le serveur, dans le même projet. Le socle n'a qu'un
adaptateur par projet (`.socle/adapter.toml`), et aucun pour Dart : le
code de l'application échapperait à `verify`, aux contrôles des tests, au
code nommé par un test et à la mutation. Les étapes `steps` d'un
adaptateur lanceraient `flutter test`, sans les contrôles statiques.

À trancher quand l'architecture du pilote fixera sa pile : un dépôt par
langage, chacun son socle, ou un socle qui juge plusieurs adaptateurs dans
un projet ; et dans les deux cas, un adaptateur Dart.

Abandonné le 21 novembre, sur la réponse de Théo au tri T-0120 (D-0153,
J-2026-11-21-O) : sa question est tranchée. Un projet juge plusieurs
adaptateurs depuis le 9 novembre (ADR-0051, J-2026-11-09-F), éprouvés au
banc sur Python et Kotlin ; le pilote a pris Kotlin, et l'adaptateur Dart
n'a plus d'objet. Ce que le pilote a montré depuis se suit dans B-0147 et
B-0179.
