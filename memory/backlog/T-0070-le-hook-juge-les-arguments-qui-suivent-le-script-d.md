<!-- socle: couche=backlog zone=publique -->
# T-0070 — Le hook juge les arguments qui suivent le script d'un python -c comme des chemins que le script cite

> statut : ouvert · origine : J-2026-11-18-J · besoin : B-0230 · lu : backlog@71e91816

Un commit : les arguments d'un `python -c` qui suivent son script se jugent comme les chemins que le script cite en toutes lettres ; ses cas dans `tests/test_garde.py`.

## Fait quand

- [ ] `python3 -c "import sys; open(sys.argv[1], 'w')" .socle/policy.toml` est refusé par le hook, et un test le montre
- [ ] un `python -c` dont les arguments ne nomment aucun fichier protégé passe le hook, et un test le montre
