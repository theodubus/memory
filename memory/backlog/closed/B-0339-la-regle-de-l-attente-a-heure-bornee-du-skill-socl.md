<!-- socle: couche=backlog zone=publique -->
# B-0339 — La règle de l'attente à heure bornée du skill socle-resume laisse trois cas : l'attente que rien ne rouvre, l'événement refusé à traiter, la réponse en texte seul pendant l'attente

> statut : abandonné · origine : J-2026-11-23-U · lu : backlog@070104b3 · ref : D-0168

Relevé par la passe 2 de la revue de L-0023 (J-2026-11-23-U), constats
1, 6 et 7 pour le backlog, sur la règle 1A qu'écrit T-0082 (ADR-0107) :

1. Le gabarit garde les réveils pendant « une attente à heure bornée (un
   rappel, une commande en arrière-plan, une CI) », sans la condition de
   D-0163 et d'ADR-0107 : un événement qui rouvrira la session. Une CI
   attendue sans abonnement aux événements de la pull request ni boucle
   en arrière-plan ne rouvre rien : le réveil de cinq heures tire alors
   pour rien, un tour relu à froid.
2. ADR-0107 dit que l'agent traite l'événement refusé ; le gabarit ne le
   dit pas, et le point 3 du réveil reprend « à l'étape que disent la
   conversation, git… », où un rappel refusé ne figure pas.
3. « Une réponse en texte seul … retire les réveils laissés » n'a pas
   l'exception de l'attente : une question de l'humain pendant la CI,
   répondue en texte seul, fait perdre la protection de 1A sans le dire.

Le skill français n'a qu'environ 45 octets de marge sous son budget de
8 000.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » : trois cas de l'attente à heure bornée du skill de la reprise. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] une attente que rien ne rouvre ne garde pas de réveil, l'événement refusé se traite au réveil, et une réponse en texte seul pendant une attente garde ses réveils
