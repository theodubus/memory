<!-- socle: couche=backlog zone=publique -->
# B-0368 — La mise à jour depuis le moteur qu'a chess n'est rejouée nulle part avant de lui donner son prompt : la demande seule a cassé aux deux mises à jour réelles

> statut : ouvert · origine : J-2026-11-26-AQ · ref : D-0219 · après : B-0364, B-0365 · lu : backlog@637a12fb

La suggestion 3 de la revue de cap 9 (J-2026-11-26-AQ), que Théo valide
le 26 novembre (D-0219). L'étape de la demande seule a cassé aux deux
mises à jour réelles de chess, chaque fois autrement : la fin de tour
refusait l'arbre le 13 novembre (B-0196), les hooks git jugeaient
l'index avec le moteur neuf le 26 (B-0357). Chaque casse a coûté un lot
de corrections, une session de chess et le temps de Théo ; le relecteur
de L-0047 a rejoué la mise à jour à la main, pour 265 000 jetons. Les
tests de T-0201 simulent l'ancien moteur par une copie de celui de la
tête (`tests/test_hooks.py`, `TestHooksGitPendantUneMiseAJour`).

Un test d'environ 150 lignes : le moteur publié qu'a chess, pris dans
l'historique de ce dépôt (`git archive`, la CI ayant tout l'historique),
installe un projet et sa mémoire ; le moteur de la tête le met à jour ;
la demande seule se commite et se pousse par les vrais hooks git vers un
dépôt nu, puis les fichiers de la mise à jour. Le commit du moteur
rejoué suit celui qu'a chess, et avance avec chaque mise à jour. Placé
après B-0364 et B-0365, avant le prochain prompt de mise à jour de
chess (D-0219).

## Satisfait quand

- [ ] un test de la suite met à jour, par le moteur de la tête, un projet installé par le moteur publié qu'a chess, et échoue si le commit ou le push de la demande seule, ou ceux des fichiers de la mise à jour, sont refusés
