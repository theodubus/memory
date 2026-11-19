<!-- socle: couche=backlog zone=publique -->
# T-0103 — Le dossier de la revue juge privé le chemin normalisé d'un fichier approuvé, et un test montre qu'un fichier privé ne s'y donne pas

> statut : fait · origine : J-2026-11-19-D · besoin : B-0297 · lu : backlog@86a19e76 · ref : J-2026-11-19-J

Un commit : `contenus_approuves` juge privé le chemin normalisé
(`fichier.relative_to(racine)`), et un test de `tests/test_revue.py`
donne un `sujet` privé, écrit brut et avec `./`.

## Fait quand

- [x] un fichier privé désigné par une décision de séance, son chemin écrit avec ou sans `./`, ne se donne pas au dossier, et un test le montre
