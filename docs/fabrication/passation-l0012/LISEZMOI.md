# Passation du lot L-0012, le 17 novembre à 2 h

La session du 17 novembre (J-2026-11-17-A à J-2026-11-17-E) a livré le
lot L-0013, fusionné par l'agent, puis ouvert L-0012. Elle s'arrête au
seuil de la fenêtre de cinq heures (60 %, atteint à 2 h 12, heure de
Paris), selon la consigne de Théo : la passation se fait avant la
limite. Tout est poussé, sauf deux commits pas encore relus, rangés ici
en correctif. Ce dossier se retire dans le commit qui les intègre. À 7 h
40, dans la même session, Théo a tranché la place des formes du shell
(J-2026-11-17-G), puis voulu trois pratiques de l'atelier dans le
produit (J-2026-11-17-H) : le correctif a été régénéré deux fois, ses
numéros décalés à la main, le défaut que B-0280 relève.

## Ce qu'il contient

`l0012-non-relu.patch`, deux commits au format de `git format-patch`,
pris sur c4cf2c0 et laissés en clair : le contrôle des références sait
alors que les chemins qu'ils créent existeront ; `git am -3` les applique
sans conflit sur la tête de la branche.

1. T-0044 : le lanceur parallele.py, sous tests, et son test
   test_parallele.py (Opus 5.5) ; son entrée de journal, la neuvième
   du 17 novembre, avec les mesures ; deux lignes dans T-0044. La suite y passe en 174 à
   176 s au mur, contre 648,7 s par `unittest discover`.
2. La demande à Théo, la suivante après les deux décisions de séance du
   matin, pas encore relue à froid ni poussée : la ligne de l'adaptateur que Théo changerait lui-même
   (`.socle/adapter.toml`, protégé), et la spécification de T-0045 ;
   T-0044 et T-0045 l'attendent (`après`).

Les numéros sont déjà ceux qui suivent la branche : J-2026-11-17-F à H,
D-0128 et D-0129 y sont pris depuis (la passation, et les deux décisions
de Théo du matin, sur les formes du shell et sur trois pratiques de
l'atelier pour le produit). Une entrée écrite avant l'application les décalerait de
nouveau.

## La reprise, dans l'ordre

1. Appliquer le correctif (`git am -3`), le retirer avec ce dossier dans
   un commit, puis `python3 .socle/socle verify --fast`.
2. La relecture à froid de la demande (skill `socle-request`, étape 4) ;
   ses liens pointent sur fe47899, un commit qui ne sera jamais poussé :
   les refaire sur le commit poussé (`python3 .socle/socle url <chemin>`).
3. La revue du lot, passe 1 de L-0012, sur le lanceur, son test et la
   spécification de la demande (skill `delegate-lot`) ; les bloquants
   corrigés.
4. Pousser, donner le lien de la demande à Théo, et attendre sa réponse
   en travaillant ailleurs : son geste, la ligne de l'adaptateur sur
   GitHub, vient avec elle.
