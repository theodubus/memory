<!-- socle: couche=backlog zone=publique -->
# T-0098 — Le dossier de la revue donne le texte que désigne une décision de séance citée par les tâches du lot

> statut : ouvert · origine : D-0134 · besoin : B-0286 · lu : backlog@8f3622bb

Un commit : `socle review` (`engine/socle/review.py`) ajoute au
dossier, pour chaque décision de séance que citent les tâches du lot et
qui désigne un fichier (son `sujet`), le texte de ce fichier, ou son
chemin quand il dépasse une borne. Le guide et son anglais s'il le
disent, une note de version.

## Fait quand

- [ ] le dossier de la revue d'un lot dont une tâche cite une décision de séance qui désigne un fichier contient ce fichier, et un test le lit
