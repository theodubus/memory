<!-- socle: couche=backlog zone=publique -->
# T-0204 — Récrire le prompt de chess pour la mise à jour suivante, depuis la version du 26 novembre, sur la réponse à D-0215

> statut : ouvert · origine : J-2026-11-26-AH · ref : D-0215 · besoin : B-0366 · lu : backlog@5a843592

Sur `valider` à D-0215 : l'assertion du point 17 se retire de
`tests/test_suite_du_projet.py`, et le prompt reprend le texte récrit
dans L-0046 (commit `a8b8411f`), complété des notes parues depuis. Sur
`refuser` : le prompt garde ses 37 points, et les notes nouvelles s'y
ajoutent au point de leur thème. Elle passe avant L-0047, qui ajoute sa
propre note au prompt.

## Fait quand

- [ ] le prompt dit « Ta version date du 26 novembre », et chaque note de version d'après `2026-11-26-c` y est citée par un point
- [ ] la suite de tests passe, l'assertion retirée seulement sur `valider` à D-0215
