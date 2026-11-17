<!-- socle: couche=backlog zone=publique -->
# T-0045 — La durée des étapes rapides se dit, et a un seuil : verify --fast n'imprime aucune durée, et rien ne signale qu'elle a passé de 143 s à près de douze minutes

> statut : ouvert · après : D-0130 · origine : J-2026-11-16-E · besoin : B-0258 · lu : backlog@9966bbbd

La tâche de B-0258, que la migration du backlog en quatre formes a posée dans le lot L-0012 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] `verify --fast` imprime la durée de chaque étape et le total, et un test le montre
- [ ] un seuil dépassé donne un avertissement qui nomme l'étape, et un test le montre
