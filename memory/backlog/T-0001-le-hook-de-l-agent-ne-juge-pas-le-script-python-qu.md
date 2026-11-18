<!-- socle: couche=backlog zone=publique -->
# T-0001 — Le hook juge le corps d'un heredoc que lit python comme le script d'un python -c

> statut : ouvert · origine : J-2026-11-14-AG · besoin : B-0229 · lu : backlog@9966bbbd

Un commit : le corps d'un heredoc donné à `python` ou `python3` sans `-c`, `-m` ni script se juge, dans `engine/socle/hooks.py`, par les chemins protégés qu'il cite et par ce qu'il supprime (`_supprimes_par_python`) ; ses cas dans `tests/test_garde.py`. Un script lu par `<` d'un fichier reste hors de portée.

## Fait quand

- [ ] `python3 - <<'EOF'` dont le corps écrit un fichier protégé, ou passe `..` à `shutil.rmtree`, est refusé par le hook, et un test le montre
- [ ] un heredoc donné à python qui ne cite aucun fichier protégé et ne supprime rien du projet passe le hook, et un test le montre
