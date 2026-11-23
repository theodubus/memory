<!-- socle: couche=backlog zone=publique -->
# T-0158 — Un test lit le délai que reçoit le fetch de l'historique au premier démarrage, sans marque : 120 secondes, ou le reste du délai du démarrage s'il est moindre

> statut : fait · ref : J-2026-11-23-M · origine : J-2026-11-22-Q · besoin : B-0331 · lu : backlog@3a8162c0

Un commit : un test de `tests/test_hooks.py` lit le délai que
`completer_historique` passe au fetch sans marque, `min(DELAI_HISTORIQUE,
reste)`, et qu'il ne vaut pas `DELAI_HISTORIQUE_REPRISE` ; il échoue si
la ligne qui choisit le délai prend le délai court sans marque.

## Fait quand

- [x] un test montre qu'au premier démarrage, sans marque, le fetch de l'historique reçoit 120 secondes ou le reste du délai du démarrage s'il est moindre, et qu'il échoue quand ce délai devient celui de la reprise
