<!-- socle: couche=backlog zone=publique -->
# T-0030 — L'installeur nomme les hooks de fin de tour que le projet avait déjà

> statut : fait · origine : J-2026-11-12-A · ref : J-2026-11-21-K · besoin : B-0183 · lu : backlog@9966bbbd

Un commit : à l'installation et à la mise à jour, l'installeur lit les hooks de fin de tour des réglages de Claude Code du projet et nomme ceux qui ne sont pas du socle, comme il signale un second état de démarrage ; une note de version.

## Fait quand

- [x] un projet qui a son propre hook de fin de tour reçoit de l'installeur une ligne qui le nomme et dit qu'il peut doubler celui du socle, et un test le montre
