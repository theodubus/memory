<!-- socle: couche=backlog zone=publique -->
# T-0001 — Le hook de l'agent ne juge pas le script python qu'un heredoc lui donne (python3 - <<EOF)

> statut : ouvert · origine : J-2026-11-14-AG · besoin : B-0229 · lu : backlog@9966bbbd

La tâche de B-0229, que la migration du backlog en quatre formes a posée dans le lot L-0005 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] `python3 - <<'EOF'` dont le corps cite un fichier protégé est refusé par le hook, un heredoc qui n'en cite aucun passe, et un test le montre
