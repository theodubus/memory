<!-- socle: couche=backlog zone=publique -->
# T-0102 — Le skill delegate-lot fait fusionner la branche de passation à son intégration, après l'application de ses correctifs

> statut : ouvert · origine : J-2026-11-19-A · besoin : B-0293 · lu : backlog@6599f863

Un commit, à la prochaine session, à la demande de Théo : la section
« Changer de session » du skill `delegate-lot` dit qu'à l'intégration
d'une passation, après l'application de ses correctifs par `git am`, la
branche de passation se fusionne (`git merge --no-edit`) dans la branche
de travail, son dossier retiré ensuite, pour que l'état la donne à
supprimer après la fusion de la pull request.

## Fait quand

- [ ] le skill `delegate-lot` dit de fusionner la branche de passation après l'application de ses correctifs, et un test de `tests/test_suite_du_projet.py` ou du skill lit la phrase
