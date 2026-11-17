<!-- socle: couche=backlog zone=publique -->
# T-0002 — Le hook de l'agent ne juge xargs et python -c que par les chemins qu'ils citent : la liste qu'un find ou un grep -r donne à xargs, le chemin passé en argument au script

> statut : ouvert · origine : J-2026-11-14-AH · besoin : B-0230 · lu : backlog@9966bbbd

La tâche de B-0230, que la migration du backlog en quatre formes a posée dans le lot L-0005 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] `grep -rl x . | xargs sed -i …` et `find . -type f | xargs sed -i …` sont refusés, `find . -name '*.py' | xargs sed -i …` passe, et un test le montre
- [ ] un `python -c` qui reçoit un fichier protégé en argument est refusé, et un test le montre
