<!-- socle: couche=backlog zone=publique -->
# T-0042 — Le démarrage dit les hooks git débranchés quand core.hooksPath désigne .socle/git-hooks par un chemin absolu, comme après le redémarrage d'un conteneur cloud

> statut : ouvert · origine : J-2026-11-16-A · besoin : B-0252 · lu : backlog@9966bbbd

La tâche de B-0252, que la migration du backlog en quatre formes a posée dans le lot L-0010 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] le démarrage ne dit plus les hooks git débranchés quand `core.hooksPath` désigne `.socle/git-hooks` de la racine par son chemin absolu, et un test le montre
