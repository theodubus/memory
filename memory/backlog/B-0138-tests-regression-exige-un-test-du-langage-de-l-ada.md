<!-- socle: couche=backlog zone=publique -->
# B-0138 — `tests.regression` exige un test du langage de l'adaptateur pour un correctif dans un langage qu'il ne couvre pas

> statut : ouvert · origine : J-2026-11-08-S · lu : backlog@6d946978 · après : D-0088

Sur une branche du pilote, un commit `fix:` sur du Dart fait échouer la CI :
`tests.regression` y exige un test Python, le seul que l'adaptateur
`python-pytest` lit (J-2026-11-08-S). Un correctif dans un langage que
l'adaptateur ne couvre pas devrait le dire, comme le fait déjà l'état pour
un langage non couvert, plutôt qu'exiger un test qu'il ne saura pas lire.
Lié à B-0095 : avec plusieurs adaptateurs, le correctif se juge par celui
qui couvre son chemin.

Fait quand :
- [ ] un correctif dans un langage non couvert est signalé comme tel, sans exiger un test d'un autre langage, avec un test
