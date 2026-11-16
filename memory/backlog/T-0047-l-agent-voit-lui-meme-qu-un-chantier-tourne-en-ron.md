<!-- socle: couche=backlog zone=publique -->
# T-0047 — L'agent voit lui-même qu'un chantier tourne en rond, et en parle à l'humain avec une proposition : un lot garde l'historique de ses revues et s'arrête sur un recul écrit

> statut : en cours · origine : J-2026-11-16-G · besoin : B-0263 · lu : backlog@9966bbbd

La tâche de B-0263, que la migration du backlog en quatre formes a posée dans le lot L-0013 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] la spécification de l'historique, des moments de recul et de l'arrêt est soumise à Théo avant son code
- [ ] une passe de revue au-delà de la première, et la clôture d'un lot, exigent un paragraphe de recul qui lit l'historique du lot ; sans lui, elles sont refusées, et un test et un défaut injecté le montrent
- [ ] l'historique des passes d'un lot se lit d'une session neuve, et un test le montre
