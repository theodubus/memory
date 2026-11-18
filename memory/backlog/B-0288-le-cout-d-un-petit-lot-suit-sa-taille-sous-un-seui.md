<!-- socle: couche=backlog zone=publique -->
# B-0288 — Le coût d'un petit lot suit sa taille : sous un seuil mesuré, la session qui orchestre l'implémente elle-même, et son relecteur reçoit un dossier court

> statut : ouvert · origine : D-0134 · lu : backlog@670d431f

La proposition 1 de `docs/fabrication/allegements.md`, que Théo a
validée dans sa forme actuelle (D-0134, J-2026-11-18-U). L-0016, un
correctif de format, a coûté 75 % d'une fenêtre de cinq heures : un
sous-agent qui implémente ou un relecteur neuf relit les instructions,
les skills et le code avant d'écrire une ligne, 200 000 à 300 000
jetons, même pour dix lignes. Sous un seuil, la session qui orchestre
implémente elle-même ; le relecteur, toujours un sous-agent pour rester
à froid, reçoit le diff et les critères des tâches, avec la consigne de
juger le diff sans explorer au-delà des fichiers touchés. Un lot qui
touche un garde-fou, ou un format que d'autres parties du socle lisent,
garde la revue complète : le bloquant du récap de L-0016 n'a été trouvé
que parce que le relecteur a lu le code du hook, hors du diff. Le seuil
se mesure (T-0033, B-0291) plutôt que de rester à 150 lignes.

## Satisfait quand

- [ ] un lot sous le seuil est implémenté par la session qui l'orchestre, sans sous-agent
- [ ] le relecteur d'un lot sous le seuil reçoit un dossier court, le diff et les critères de ses tâches, et ne juge que le diff et les fichiers touchés
- [ ] un lot qui touche un garde-fou, ou un format que d'autres parties du socle lisent, garde la revue complète
