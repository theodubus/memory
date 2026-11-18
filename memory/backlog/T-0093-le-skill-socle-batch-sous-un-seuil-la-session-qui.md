<!-- socle: couche=backlog zone=publique -->
# T-0093 — Le skill socle-batch : sous un seuil, la session qui orchestre implémente elle-même la tâche ; une tâche qui touche un garde-fou ou un format lu ailleurs garde son sous-agent

> statut : ouvert · origine : D-0134 · besoin : B-0288 · lu : backlog@9ead3d41

Un commit : le gabarit du skill `socle-batch`, en français et en
anglais, dit qu'une tâche sous un seuil s'implémente dans la session qui
orchestre, sans sous-agent, et qu'une tâche qui touche un garde-fou, ou
un format que d'autres parties du socle lisent, garde son sous-agent ;
le seuil, provisoire à 150 lignes de code et de tests, renvoie à sa
mesure (B-0291). Une note de version ; la copie protégée de ce dépôt
suit par une demande ; le skill `delegate-lot` le dit pour l'atelier.

## Fait quand

- [ ] le gabarit de `socle-batch` et son anglais disent le seuil sous lequel la session qui orchestre implémente elle-même, et l'exception d'un garde-fou ou d'un format lu ailleurs, et un test le lit
