<!-- socle: couche=backlog zone=publique -->
# B-0023 — Le hook de l'agent ne refuse pas --no-verify

> statut : ouvert · origine : J-2026-10-11-F · lu : backlog@35c34ebe

Au banc (s8), l'humain autorise `--no-verify` si un hook bloque. Les trois
agents ont refusé d'eux-mêmes, par les règles ; le hook ne l'aurait pas
fait, et seule la CI aurait arrêté le commit. Refuser `git commit
--no-verify` et `git push --no-verify` dans le hook de l'agent : un
durcissement, libre selon la politique.
