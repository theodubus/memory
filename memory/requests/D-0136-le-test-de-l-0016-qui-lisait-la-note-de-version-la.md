<!-- socle: couche=demandes zone=publique -->
# D-0136 — Le test de L-0016 qui lisait la note de version la plus récente cherche la note 2026-11-18-c par son identifiant, ses assertions et leurs valeurs attendues inchangées : valider ce changement ?

> date : 2026-11-18 · forme : séance

## Question posée

Un test que L-0016 a ajouté, test_le_guide_montre_les_deux_formats_et_une_note_de_version_le_dit (tests/test_suite_du_projet.py, ligne 599 sur main), lit la note de version la plus récente et y attend celle du nouveau rendu de socle roadmap. Ma note 2026-11-18-d passe devant, donc le test échoue ; il échouerait de même à chaque note suivante.

Je propose de lui faire chercher la note par son identifiant :

-            premiere = notes[notes.index("\n## "):].split("\n## ")[1]
+            premiere = next(n for n in notes.split("\n## ")[1:] if n.startswith("2026-11-18-c "))

Les assertions et leurs valeurs attendues ne changent pas : le titre de la note et la mention de socle roadmap. Seul change le choix de la note, de « la plus récente » à « la note 2026-11-18-c ». Le critère de T-0088 ne demandait que « une note de version le dit ». Le contrôle des valeurs attendues ne fait qu'avertir. Mais ce test promettait « la plus récente », et ce cas sort du cadre de la variante légère (tests qui lisent un format que tu as validé) : je te le soumets plutôt que de trancher seul.

Réponds « valider » ou « refuser » sur ce changement du test.
