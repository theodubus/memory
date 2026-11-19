<!-- socle: couche=backlog zone=publique -->
# T-0094 — socle review --short : le dossier court d'un petit lot, le diff et les critères de ses tâches ; le skill socle-review dit quand le donner et quand garder le dossier complet

> statut : fait · origine : D-0134 · besoin : B-0288 · lu : backlog@81ec91ab · ref : J-2026-11-19-C

Un commit : `socle review --short` rend un dossier court, la consigne
de juger le diff et les fichiers touchés sans explorer au-delà, le diff
et les critères des tâches du lot ; il refuse, en le disant, un lot qui
touche un garde-fou (les chemins que déclarent les garde-fous et la
politique) et renvoie au dossier complet. Le gabarit du skill
`socle-review`, en français et en anglais, dit quand le donner. Le
guide et son anglais, une note de version ; la copie protégée suit par
une demande.

## Fait quand

- [x] `socle review --short` rend le diff, les critères des tâches et la consigne de ne juger que les fichiers touchés, et un test le lit
- [x] `socle review --short` sur un lot qui touche un garde-fou renvoie au dossier complet, et un test le montre
- [x] le gabarit de `socle-review` et son anglais disent quand donner le dossier court, et un test le lit
