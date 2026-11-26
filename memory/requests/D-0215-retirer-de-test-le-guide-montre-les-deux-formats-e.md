<!-- socle: couche=demandes zone=publique -->
# D-0215 — Retirer de test_le_guide_montre_les_deux_formats_et_une_note_de_version_le_dit l'assertion qui exige le point 17 de l'ancien prompt de chess, pour que ce prompt se récrive pour la mise à jour suivante

> date : 2026-11-26

## Décision demandée

Retirer de `tests/test_suite_du_projet.py` la dernière assertion du test `test_le_guide_montre_les_deux_formats_et_une_note_de_version_le_dit`, qui exige que le prompt de mise à jour de chess contienne encore son point 17, pour que ce prompt se récrive pour la prochaine mise à jour.

## Contexte

**Le projet.** Le socle est l'outillage que ce dépôt fabrique pour les projets menés avec un agent de code : une mémoire versionnée, des contrôles et des hooks, installés dans chaque projet. Chess, ton projet d'échecs, est le premier projet qui l'utilise pour de vrai.

**Le chantier.** Le 21 novembre, tu as décidé de mettre chess à jour d'un coup, puis de corriger ce que cette mise à jour montrerait. Chess a été mis à jour le 26 novembre avec un prompt à coller, qui lui disait en 37 points ce qui avait changé depuis le 13 novembre. Le lot en cours corrige quatre des gênes qu'il a relevées, et chaque correction doit aussi s'écrire dans le prompt de la prochaine mise à jour.

**La question.** Le prompt doit maintenant repartir de la version du 26 novembre : sinon, la prochaine mise à jour redonnerait à chess les 37 points qu'il a déjà reçus. Le lot l'a récrit en quatre points, mais un test exige encore la phrase du point 17, et changer ce qu'un test attend exige ta validation.

Le point 17 disait à chess que la feuille de route (la commande `socle roadmap`) se lisait désormais en deux formats, ceux que tu avais validés le 18 novembre. Le test vérifie, outre le guide et la note de version de ce changement, que le prompt de chess le reprenait. Chess l'a reçu le 26 novembre : la vérification a rempli son office. Les autres assertions du test, sur le guide et la note de version, restent. De plus, le format de la feuille de route que tu viens de valider le 26 novembre remplacera ces deux formats : ce test changera de toute façon avec ce chantier.

En attendant ta réponse, le lot remet le prompt à sa version du 26 novembre, que le test accepte, et la réécriture attend dans une tâche, sans rien bloquer d'autre.

## Éléments cités

- B-0366@8f978c65 — le besoin : le prompt de la prochaine mise à jour de chess redit les 37 points déjà reçus.
- T-0204@e626b94f — la tâche qui récrira le prompt et retirera l'assertion, selon ta réponse.
- B-0364@af10fb66 — le besoin de la feuille de route qui permet de piloter, dont le format remplacera les deux formats actuels.
- D-0214@982e025e — ta validation, le 26 novembre, du nouveau format de la feuille de route.
- `a8b8411f` — le commit du lot qui contient le prompt récrit en quatre points.

## Où regarder

- Le test, ligne 605 : [tests/test_suite_du_projet.py](https://github.com/theodubus/memory/blob/a362954168b9776126ae097a53498cc69e0dc908/tests/test_suite_du_projet.py#L603-L605). L'assertion à retirer est la dernière, avec les deux lignes qui lisent le prompt.
- Le prompt récrit, proposé : [prompt-mise-a-jour.md au commit a8b8411f](https://github.com/theodubus/memory/blob/a8b8411f49a28c3a72e6e0315dba11a0e5b7f92f/docs/fabrication/chess/prompt-mise-a-jour.md). À vérifier : « Ta version date du 26 novembre », quatre points (CODEOWNERS gardé sans `--owner`, les notes d'une copie sans notes, un correctif de la mémoire non jugé, une commande citée dans « Pour toi »), et des étapes sans les migrations déjà faites.
- Le retour de chess du 26 novembre, ses gênes 2, 4, 5 et 7 : [mise-a-jour-2026-11-26.md](https://github.com/theodubus/memory/blob/a362954168b9776126ae097a53498cc69e0dc908/docs/fabrication/chess/mise-a-jour-2026-11-26.md).

## Options

- **Retirer l'assertion** : trois lignes du test, et le prompt repart de la version du 26 novembre. Effort : quelques minutes. Risque : nul, chess a reçu le point. Réversible : un commit.
- **Garder l'assertion** : le prompt garde ses 37 points et les notes nouvelles s'y ajoutent. Effort : nul maintenant, mais chess relira 37 points déjà appliqués, et des étapes de migration déjà faites, à sa prochaine mise à jour. Réversible.

## Conséquences

- Si tu valides : T-0204, en tête du prochain lot, retire l'assertion et pose le prompt récrit, complété des notes parues entre-temps.
- Si tu refuses : le prompt garde ses 37 points ; T-0204 y ajoute les notes nouvelles au point de leur thème.
- Sans réponse : le prompt reste à sa version du 26 novembre, sans les quatre notes de ce lot ; rien d'autre n'attend.

## Recommandation

Valider. Vérifié : la suite de tests passe avec le prompt récrit, sauf cette seule assertion ; chess a reçu toutes les notes jusqu'à `2026-11-26-c` (son retour du 26 novembre). Supposé : le chantier de la feuille de route changera ce test de toute façon.

## Réponses possibles

- `valider` — retirer l'assertion ; T-0204 pose le prompt récrit pour la version du 26 novembre.
- `refuser` — garder l'assertion ; le prompt garde ses 37 points, et les notes nouvelles s'y ajoutent.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
