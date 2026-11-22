<!-- socle: couche=backlog zone=publique -->
# T-0137 — En mode amont, socle review --short refuse un lot qui touche le code d'un garde-fou du moteur, et une passe courte se marque dans l'historique du lot

> statut : ouvert · origine : J-2026-11-21-Q · besoin : B-0294 · lu : backlog@6c894b15

Un commit : en mode amont, `garde_fous_touches` (`engine/socle/review.py`) compte aussi ce que `chemins_proteges()` retire d'`engine/` : le code des hooks et des contrôles (`engine/socle/hooks.py`, `engine/socle/checks_*.py`) et les gabarits des skills du produit, que `review.py` nomme sans que le hook de l'agent change ; la passe que `socle review --short` écrit dans la section « Revues » du lot dit qu'elle est courte, et le format le dit ; le skill `delegate-lot` le dit ; une note de version. Avant le code, B-0294 reçoit sa section « Modèle de menace » : ce que le refus du dossier court arrête, ce qu'il laisse au jugement de l'agent.

## Fait quand

- [ ] dans un dépôt en mode amont, un lot qui change `engine/socle/hooks.py` ou un `engine/socle/checks_*.py` ne reçoit pas le dossier court, et un test le montre
- [ ] une passe faite sur le dossier court se lit comme telle dans la section « Revues » du lot, et un test le lit
- [ ] B-0294 a sa section « Modèle de menace », que `socle show B-0294` montre
