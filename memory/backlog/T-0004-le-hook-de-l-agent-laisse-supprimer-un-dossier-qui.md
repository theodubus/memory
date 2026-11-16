<!-- socle: couche=backlog zone=publique -->
# T-0004 — Le hook de l'agent laisse supprimer un dossier qui contient le projet par xargs rm ou par une commande que lance python -c (echo .. | xargs rm -rf, os.system)

> statut : ouvert · origine : J-2026-11-15-N · besoin : B-0246 · lu : backlog@9966bbbd

La tâche de B-0246, que la migration du backlog en quatre formes a posée dans le lot L-0005 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] `find .. -maxdepth 0 | xargs rm -rf` est refusé comme un `find` qui supprime depuis ce dossier, `find . -name '*.pyc' | xargs rm -f` passe, et un test le montre
