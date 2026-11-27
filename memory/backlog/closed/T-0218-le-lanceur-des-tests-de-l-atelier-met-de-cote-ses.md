<!-- socle: couche=backlog zone=publique -->
# T-0218 — Le lanceur des tests de l'atelier met de côté ses modules les plus longs pendant les étapes rapides, la CI les jouant toujours

> statut : fait · origine : J-2026-11-27-AG · besoin : B-0382 · ref : D-0237, ce commit · lu : backlog@e5be70ef

Les modules les plus longs de la suite se mettent de côté eux-mêmes
quand `SOCLE_RAPIDE` est posée, chacun avec sa raison écrite et sa durée
mesurée : d'après la mesure du 27 novembre, `test_hooks`,
`test_installeur`, `test_adaptateurs_multiples`, `test_adoption` et
`test_attendus`, 481 secondes de calcul sur 1 347, à remesurer. Le
lanceur, protégé (D-0130), ne change pas : son bilan compte déjà les
tests sautés. Validé par D-0237, qui couvre ce changement tant que cette
tâche est ouverte ; le titre dit le résultat, le lanceur le constate.

## Fait quand

- [x] un test montre un module de la liste mis de côté quand `SOCLE_RAPIDE` est posée, et lancé sans elle
- [x] le contrôle des tests creux accepte la mise de côté, sa raison écrite
- [x] la vérification rapide mesurée seule, après le changement, est notée au journal
