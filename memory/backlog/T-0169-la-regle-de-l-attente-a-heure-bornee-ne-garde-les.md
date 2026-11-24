<!-- socle: couche=backlog zone=publique -->
# T-0169 — La règle de l'attente à heure bornée ne garde les réveils que pour un événement qui rouvrira la session, fait traiter l'événement refusé, et la réponse en texte seul la respecte

> statut : ouvert · origine : J-2026-11-23-U · besoin : B-0339 · lu : backlog@070104b3

Un commit : le gabarit de `socle-resume` et son anglais, sous leur budget (ou une demande qui le relève), disent les trois cas de B-0339 ; le test de T-0082 les lit ; une note de version.

## Fait quand

- [ ] le gabarit et son anglais disent que seule une attente qui rouvrira la session garde ses réveils, que l'événement refusé se traite au réveil, et qu'une réponse en texte seul pendant une attente les garde, et un test le lit
