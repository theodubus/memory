<!-- socle: couche=backlog zone=publique -->
# B-0095 — Un projet à deux langages n'a qu'un adaptateur : le code du second n'est pas jugé

> statut : ouvert · origine : J-2026-10-30-B · lu : backlog@8d122b8b

Le cadrage du pilote recommande Flutter pour l'application et Python
(FastAPI) pour le serveur, dans le même projet. Le socle n'a qu'un
adaptateur par projet (`.socle/adapter.toml`), et aucun pour Dart : le
code de l'application échapperait à `verify`, aux contrôles des tests, au
code nommé par un test et à la mutation. Les étapes `steps` d'un
adaptateur lanceraient `flutter test`, sans les contrôles statiques.

À trancher quand l'architecture du pilote fixera sa pile : un dépôt par
langage, chacun son socle, ou un socle qui juge plusieurs adaptateurs dans
un projet ; et dans les deux cas, un adaptateur Dart.
