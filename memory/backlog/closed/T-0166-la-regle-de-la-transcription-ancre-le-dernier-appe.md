<!-- socle: couche=backlog zone=publique -->
# T-0166 — La règle de la transcription ancre le dernier appel du modèle avant le réveil et ne compte pas le réveil parmi les messages tapés, mesuré sur un réveil réel

> statut : abandonné · origine : J-2026-11-23-R · besoin : B-0337 · lu : backlog@12a10d0c · ref : D-0168

Un commit : relever dans une transcription réelle l'enregistrement d'un message de réveil (`send_later`), puis, dans le gabarit de `socle-resume` et son anglais, sous leur budget, ancrer la coupure sur le dernier appel du modèle avant le réveil et exclure le réveil des messages tapés ; le test de T-0164 lit ces relations, et `socle consumption` ne compte pas un réveil parmi les messages tapés ; une note de version.

T-0166 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0337, sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] le gabarit et son anglais ancrent la coupure avant le réveil et excluent le réveil des messages tapés, et un test échoue sans ces mots
- [ ] l'enregistrement d'un réveil relevé dans une transcription réelle n'est pas compté comme tapé par `socle consumption`, et un test le montre
