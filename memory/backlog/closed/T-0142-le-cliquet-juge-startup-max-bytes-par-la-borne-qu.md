<!-- socle: couche=backlog zone=publique -->
# T-0142 — Le cliquet juge [startup] max_bytes par la borne qu'en lit le moteur : 0, une valeur négative ou illisible écrite au lieu d'une borne plus basse l'assouplit

> statut : abandonné · origine : J-2026-11-21-Q · besoin : B-0282 · lu : backlog@6c894b15 · ref : D-0168

Un commit : `assouplissements` (`engine/socle/checks_ratchet.py`) compare la borne du démarrage que lit `Projet.borne_demarrage`, non la valeur écrite : passer de 8 000 à 0 la relève à 9 500, un assouplissement qui exige une demande validée ; son défaut injecté et son témoin sain dans l'auto-test ; une note de version. `Projet.borne_demarrage` ne change pas : `test_la_borne_vient_des_garde_fous_celle_du_gabarit_a_defaut` (`tests/test_demarrage.py`), qui lit qu'une valeur nulle, négative ou illisible vaut celle du gabarit, garde sa valeur attendue (cherché à la création, D-0141). Avant le code, B-0282 reçoit sa section « Modèle de menace ».

T-0142 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0282, sous « X1 — ne compte que si l'agent cherche à contourner le socle » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] écrire 0, une valeur négative ou une valeur qui n'est pas un entier à la place d'une borne plus basse que celle du gabarit est un assouplissement que le cliquet nomme, et un test le montre
- [ ] B-0282 a sa section « Modèle de menace », que `socle show B-0282` montre
