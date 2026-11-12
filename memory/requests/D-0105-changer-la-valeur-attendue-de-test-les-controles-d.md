<!-- socle: couche=demandes zone=publique -->
# D-0105 — Changer la valeur attendue de test_les_controles_d_adoption_citent_leur_objet pour la clé d'une copie (répète D-0104)

> date : 2026-11-12 · forme : séance

## Question posée

Précise D-0104@26f570ad, sur la même réponse de Théo. Sa validation a été commitée et poussée seule, avant le changement qu'elle autorise ; or le contrôle d'avant push ne juge que ce qui part, et ne la voit plus (B-0191). Théo a accepté qu'elle soit consignée une seconde fois : « Seconde trace me convient ».

Le changement autorisé, réduit après la revue à la seule clé d'un paragraphe recopié (ADR-0070) : dans `tests/test_adoption.py`, la valeur attendue de `test_les_controles_d_adoption_citent_leur_objet` passe, pour le contrôle des copies, de « copie en b.md » à « copie en b.md : Un long paragraphe recopié tel quel dans deux ». La valeur attendue du contrôle des tests creux ne change pas.

Théo autorise-t-il ce changement de valeur attendue ?
