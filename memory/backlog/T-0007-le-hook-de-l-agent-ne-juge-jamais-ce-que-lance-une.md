<!-- socle: couche=backlog zone=publique -->
# T-0007 — Le hook de l'agent ne juge jamais ce que lance une substitution entre guillemets : x="$(cd .. && rm -rf projet)" supprime le projet sans refus

> statut : ouvert · origine : J-2026-11-16-F · besoin : B-0260 · lu : backlog@9966bbbd

La tâche de B-0260, que la migration du backlog en quatre formes a posée dans le lot L-0005 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] les trois commandes ci-dessus sont refusées par le hook, `x="$(git rev-parse HEAD)"; echo "$x" > notes.txt` passe, et un test le montre
