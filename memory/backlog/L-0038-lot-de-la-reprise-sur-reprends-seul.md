<!-- socle: couche=backlog zone=publique -->
# L-0038 — Lot de la reprise sur « reprends » seul

> statut : en cours · origine : J-2026-11-24-BC · après : L-0037, T-0180 · lu : backlog@5d842cca

B-0346, au jalon JA-0005 sur la décision de Théo (D-0185) : la session
neuve reprend sur « reprends » seul, la passation écrite dans le dépôt.
Sa spécification change celle de D-0174 : elle se soumet à Théo d'abord
(T-0180), puis les tâches qui l'appliquent s'ouvrent sur sa réponse.

## Revues

### Passe 1 — 2026-11-25

Commits : c50b2012..f2e68840

- Bloquant : la passation identifiée par son commit revivait après un squash ou un rebase, et la garde partait de l'heure de la fusion ; identifiée par son estampille, la garde depuis l'heure écrite
- Bloquant : un retrait fusionné laissait passer un second « reprends », que le modèle disait arrêté ; dit dans ce qu'elle laisse passer
- Bloquant : la session programmée ne distinguait pas « reprends » de l'humain, et la borne de la chaîne cédait ; un texte distinct, et dans le doute la chaîne plus un
- Bloquant : la liste des tests de D-0190 incomplète ; deux tests, deux défauts et un témoin ajoutés
- Ouvre : rien

### Passe 2 — 2026-11-25

Commits : c2d2d34b..a8fdd86c

- Bloquant : après un squash ou un rebase, la mémoire d'une autre session déjà fusionnée dans la branche par défaut échappait à la garde ; elle juge aussi les ancêtres de la tête écrits après l'heure de la passation
- Ouvre : rien
