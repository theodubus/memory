<!-- socle: couche=backlog zone=publique -->
# L-0054 — Lot — les modules de tests les plus longs mis de côté pendant les étapes rapides

> statut : fait · origine : J-2026-11-27-AG · après : L-0053, T-0218 · lu : backlog@76a2afcd · ref : ce commit

Le troisième lot de JA-0006 dans l'ordre de D-0235, point 12, après la
revue de cap 11 : T-0218 seule (B-0382, D-0237 validée). Elle ne touche
que les tests de l'atelier : les cinq modules les plus longs se mettent
de côté eux-mêmes quand `SOCLE_RAPIDE` est posée, par le décorateur que
`tests/test_banc.py` et `tests/test_autotest.py` portent déjà, que le
contrôle `tests.creux` juge ; un test nouveau, dans
`tests/test_parallele.py`, le montre. Ni le moteur, ni l'adaptateur, ni
le lanceur protégé (D-0130) ne changent ; rien que reçoive un projet.
