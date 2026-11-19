<!-- socle: couche=backlog zone=publique -->
# B-0294 — En mode amont, socle review --short ne reconnaît pas le code d'un garde-fou du moteur, et une passe courte ne se marque pas dans l'historique du lot

> statut : ouvert · origine : J-2026-11-19-D · lu : backlog@8f032107

`socle review --short` refuse un lot qui touche un garde-fou par
`garde_fous_touches` (`engine/socle/review.py`) : la politique, les
garde-fous, les chemins protégés et l'outillage. En mode amont,
`chemins_proteges()` retire `engine/`, donc le code d'un hook
(`engine/socle/hooks.py`), d'un contrôle (`engine/socle/checks_*.py`) ou
un gabarit de skill du produit passe `--short` mécaniquement : c'est le
cas même de L-0016 que cite B-0288, et seul le jugement de l'agent le
rattrape (le skill `socle-review` le lui confie). `delegate-lot` ne le
dit pas, `--short` ne vérifie pas le seuil de 150 lignes, et la passe
écrite dans la section « Revues » du lot ne dit pas qu'elle était courte :
l'humain ne peut pas l'auditer. Relevé par la revue de L-0018
(J-2026-11-19-D).

## Satisfait quand

- [ ] dans ce dépôt, un lot qui touche le code d'un garde-fou du moteur ne reçoit pas le dossier court
- [ ] une passe faite sur le dossier court se lit comme telle dans l'historique des revues du lot
