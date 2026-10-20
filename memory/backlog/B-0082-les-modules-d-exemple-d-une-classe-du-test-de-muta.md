<!-- socle: couche=backlog zone=publique -->
# B-0082 — Les modules d'exemple d'une classe du test de mutation gardent des noms tirés des échecs

> statut : ouvert · origine : J-2026-10-20-V · lu : backlog@b2111f70

La classe `TestAMesurer` de `tests/test_mutation.py` garde `src/eval.rs`
et `src/tt.rs`, des modules d'un moteur d'échecs. Ses données sont
partagées par `test_poser_ecrit_la_raison_dans_la_langue_du_projet`, que
D-0035 ne nommait pas : la changer exige une validation qui le nomme. Les
autres classes du fichier ont des noms neutres. À joindre à la prochaine
demande qui touche aux tests.
