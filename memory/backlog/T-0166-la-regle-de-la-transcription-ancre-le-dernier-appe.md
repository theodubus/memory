<!-- socle: couche=backlog zone=publique -->
# T-0166 — La règle de la transcription ancre le dernier appel du modèle avant le réveil et ne compte pas le réveil parmi les messages tapés, mesuré sur un réveil réel

> statut : ouvert · origine : J-2026-11-23-R · besoin : B-0337 · lu : backlog@12a10d0c

Un commit : relever dans une transcription réelle l'enregistrement d'un message de réveil (`send_later`), puis, dans le gabarit de `socle-resume` et son anglais, sous leur budget, ancrer la coupure sur le dernier appel du modèle avant le réveil et exclure le réveil des messages tapés ; le test de T-0164 lit ces relations, et `socle consumption` ne compte pas un réveil parmi les messages tapés ; une note de version.

## Fait quand

- [ ] le gabarit et son anglais ancrent la coupure avant le réveil et excluent le réveil des messages tapés, et un test échoue sans ces mots
- [ ] l'enregistrement d'un réveil relevé dans une transcription réelle n'est pas compté comme tapé par `socle consumption`, et un test le montre
