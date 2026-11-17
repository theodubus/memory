<!-- socle: couche=backlog zone=publique -->
# T-0035 — Le banc cherche le budget du chantier actif sous memory/actif.md : le juge du scénario s4 ne voit jamais un budget relevé

> statut : ouvert · origine : J-2026-11-13-G · besoin : B-0210 · lu : backlog@9966bbbd

La tâche de B-0210, que la migration du backlog en quatre formes a posée dans le lot L-0009 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] le juge du scénario s4 lit la clé du chantier actif par le chemin du format actuel (`config.FORMAT_ACTUEL.actif`), sans nom écrit en dur
- [ ] un test montre qu'il voit un budget relevé dans HEAD et dans l'arbre de travail, et rien quand le budget est inchangé
