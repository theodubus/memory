<!-- socle: couche=backlog zone=publique -->
# T-0138 — L'étape 2 du gabarit de socle-review écrit la sortie de socle review dans un fichier hors du dépôt, que son bloc de code suivi à la lettre ne met pas dans la conversation

> statut : ouvert · origine : J-2026-11-21-Q · besoin : B-0298 · lu : backlog@6c894b15

Un commit : le bloc de code de l'étape 2 du gabarit `socle-review`, en français et en anglais, écrit la sortie de `socle review` dans un fichier hors du dépôt, par une redirection ou par une option `--output <fichier>` (T-0062 l'envisageait), sous le plafond de 8 000 octets du gabarit ; une note de version.

## Fait quand

- [ ] le bloc de code de l'étape 2 du gabarit `socle-review` et de son anglais écrit le dossier dans un fichier hors du dépôt, sans l'imprimer, et un test le lit
