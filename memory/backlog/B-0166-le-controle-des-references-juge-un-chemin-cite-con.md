<!-- socle: couche=backlog zone=publique -->
# B-0166 — Le contrôle des références juge un chemin cité contre le système de fichiers, pas contre les fichiers suivis : un dossier local seul passe le hook avant push et échoue en CI

> statut : ouvert · origine : J-2026-11-11-F · lu : backlog@69424c1a

Le contrôle `memoire.references` juge un chemin cité entre accents graves
contre le système de fichiers. Un dossier non suivi, présent seulement
dans le conteneur de l'agent (le dossier des worktrees de l'agent), passe
donc les contrôles locaux et le hook avant push, puis échoue en CI, sur un
clone neuf : l'entrée de journal de B-0143 l'a montré sur ce lot. Le
chemin devrait se juger contre les fichiers suivis par git (ceux de
l'index et du commit jugé), comme la CI les voit.

## Fait quand

- [ ] un chemin cité qui n'existe que hors des fichiers suivis est refusé dès le contrôle local, et un test le montre
