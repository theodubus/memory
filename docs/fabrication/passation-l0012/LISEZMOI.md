# Passation du lot L-0012, le 17 novembre à 2 h

La session du 17 novembre (J-2026-11-17-A à J-2026-11-17-E) a livré le
lot L-0013, fusionné par l'agent, puis ouvert L-0012. Elle s'arrête au
seuil de la fenêtre de cinq heures (60 %, atteint à 2 h 12, heure de
Paris), selon la consigne de Théo : la passation se fait avant la
limite. Tout est poussé, sauf deux commits pas encore relus, rangés ici,
compressés comme dans les passations d'avant, pour qu'aucun contrôle ne
lise le correctif comme un texte du dépôt. Ce dossier se retire dans le
commit qui les intègre.

## Ce qu'il contient

`l0012-non-relu.patch.gz`, deux commits au format de `git format-patch`,
pris sur cac8a20 ; `gunzip -c` puis `git am` :

1. T-0044 : le lanceur parallele.py, sous tests, et son test
   test_parallele.py (Opus 5.5) ; son entrée de journal, numérotée
   J-2026-11-17-F, avec les mesures ; deux lignes dans T-0044. La suite y
   passe en 174 à 176 s au mur, contre 648,7 s par `unittest discover`.
2. La demande à Théo, numérotée dans le correctif, pas encore relue à
   froid ni poussée : la ligne de l'adaptateur
   que Théo changerait lui-même (`.socle/adapter.toml`, protégé), et la
   spécification de T-0045 ; T-0044 et T-0045 l'attendent (`après`).

Le numéro J-2026-11-17-F est repris, sur la branche, par l'entrée de
cette passation : à l'application, celle du correctif se renumérote
(le prochain numéro libre, et la mention dans T-0044 et le message du
commit avec elle).

## La reprise, dans l'ordre

1. Appliquer le correctif (`gunzip -c` puis `git am -3`) : seul le
   journal entre en conflit, les deux entrées ajoutées au même endroit ;
   garder les deux, renuméroter celle du correctif, puis
   `python3 .socle/socle verify --fast`.
2. La relecture à froid de la demande (skill `socle-request`, étape 4) ; ses
   liens pointent sur fe47899, un commit qui ne sera jamais poussé : les
   refaire sur le commit poussé (`python3 .socle/socle url <chemin>`).
3. La revue du lot, passe 1 de L-0012, sur le lanceur, son test et la
   spécification de la demande (skill `delegate-lot`) ; les bloquants
   corrigés.
4. Pousser, donner le lien de la demande à Théo, et attendre sa réponse en
   travaillant ailleurs : son geste, la ligne de l'adaptateur sur GitHub,
   vient avec elle.
