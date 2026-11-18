<!-- socle: couche=demandes zone=publique -->
# D-0132 — Changer neuf tests qui lisent mot pour mot les textes du lot L-0014, dont deux mots du guide que vous aviez validés, et remettre trois copies protégées à leurs gabarits

> date : 2026-11-18

## Décision demandée

Autoriser l'agent à changer les valeurs attendues des neuf tests nommés plus bas, qui lisent mot pour mot des textes où le mot « sujet » laisse place à « entrée du backlog », « tâche » ou « besoin », dont deux phrases du guide que vous aviez validées telles quelles, et à remettre les copies protégées de ce dépôt du workflow de la CI et des skills `socle-batch` et `socle-review` au texte exact que l'installeur pose.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code entretenu par un agent d'IA : il garde la mémoire du projet, dont le backlog (la liste du travail à faire), vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Son hook refuse à l'agent, avant qu'elle ait lieu, une commande que la politique interdit ; son guide (`HELP.md`, et `HELP.en.md` en anglais) dit à l'humain comment s'en servir. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote.

**Le chantier.** Le 16 novembre, vous avez validé un backlog en quatre formes, chacune son préfixe : un besoin (`B-`), dont le critère, « Satisfait quand », dit un résultat ; une tâche (`T-`), un livrable d'un commit, dont le critère est « Fait quand » ; un lot (`L-`), des tâches menées et relues ensemble ; un jalon (`JA-`), des besoins qui servent un même but. Avant, toute entrée s'appelait « sujet ». Le lot en cours, L-0014, en finit la suite : il découpe en tâches les besoins du jalon en cours, le travail à finir avant toute fonction nouvelle ; il corrige la migration, qui convertit à la mise à jour un backlog d'avant les quatre formes et pouvait perdre un critère ; il fait refuser par le hook l'ancien numéro d'une entrée renumérotée, en nommant l'actuel ; il retire les derniers « sujet » des textes du produit ; il ajoute `socle roadmap`, la suite du projet d'un coup d'œil, dont vous avez validé la spécification le 16 novembre et choisi, le 17, que son option `--by` prenne `batch` (par lot) ou `need` (par besoin). Un relecteur sans contexte, un autre agent qui cherche à prendre le lot en défaut, l'a relu : trois défauts bloquants, corrigés, et cinq points renvoyés au backlog, qui ne touchent ni ces tests ni ces copies.

**La question.** La politique interdit à l'agent de changer la valeur attendue d'un test sans un accord de vous qui le nomme. Des tests lisent mot pour mot des textes qui disaient « sujet » : sans ce changement, ils échouent, et le lot ne se livre pas. Deux de ces phrases sont dans la règle du hook que vous avez validée le 16 novembre. Et trois fichiers de ce dépôt sont des copies protégées : le gabarit que l'installeur pose dans chaque projet a changé, la copie d'ici non, et seul votre accord permet de la changer. Les gabarits, eux, sont du produit : chess les recevra à sa mise à jour, quelle que soit votre réponse ; elle ne vaut que pour les copies de ce dépôt.

**Les tests, dans `tests/`.** Chacun garde ce qu'il prouvait.

- `test_revue.py`, le dossier que reçoit le relecteur. `test_la_consigne_donne_la_barre_et_les_trois_classes` : la consigne dit « Ta barre est celle des entrées du backlog que sert le lot, plus bas : leurs critères (« Fait quand » d'une tâche, « Satisfait quand » d'un besoin) », au lieu de « …des sujets du lot, plus bas : leur critère « Fait quand » ». Le dossier donnait déjà au relecteur les besoins avec leur critère : la consigne le dit désormais. Quatre tests lisent les titres du dossier, « Les entrées du backlog que sert le lot : leurs critères sont ta barre » au lieu de « Les sujets du lot : leur critère « Fait quand » est ta barre », « Les entrées que le lot ouvre » au lieu de « Les sujets que le lot ouvre », « …qu'elles citent » au lieu de « …qu'ils citent » : `test_un_sujet_encore_ouvert_que_le_lot_touche_donne_son_critere_et_son_modele_de_menace`, `test_un_sujet_que_le_lot_ouvre_ne_donne_que_son_titre`, `test_un_sujet_que_le_lot_clot_et_range_reste_la_barre`, `test_la_specification_que_le_lot_ecrit_est_dans_le_dossier_sans_etre_citee`. `test_un_sujet_encore_ouvert_n_est_pas_dans_le_dossier` vérifiait l'absence d'un titre qui n'a jamais existé ; il vérifie désormais celle du vrai, « Les entrées du backlog que sert le lot », dans le dossier d'un lot qui ne sert aucune entrée. `test_le_guide_dit_la_regle_et_chaque_forme_cite_sa_note` lit la règle du hook (plus bas).
- `test_skills.py`, `test_les_constats_le_dossier_et_le_modele_de_menace_d_une_seule_maniere` : le skill de la revue dit « puis celles que ses entrées citent » au lieu de « ses sujets » (en anglais, « its entries » au lieu de « its topics »).
- `test_initialisation.py`, `test_les_questions_de_depart_posent_la_livraison` : la question posée à l'installation sur la livraison propose « une pull request par tâche » au lieu de « par sujet ».

**Les deux phrases de la règle du hook.** Un trou est une forme du shell, une manière d'écrire une commande, que le hook ne sait pas juger. Le guide dit : « Un trou ouvre une entrée du backlog si sa forme est de celles qu'un agent écrit dans son travail […]. Une autre forme s'inscrit d'une ligne dans la liste des formes connues que le hook ne juge pas, sans entrée au backlog » ; avant : « ouvre un sujet » et « sans sujet ». En anglais : « A hole opens a backlog entry » et « without a backlog entry », au lieu de « opens a topic » et « without a topic ». Le reste est votre texte.

**Les trois copies protégées**, ce qui change de la copie actuelle au gabarit :

- Le workflow de la CI (`.github/workflows/socle.yml`), qui lance les contrôles à chaque envoi sur GitHub : une étape écrit la suite du projet dans le résumé de chaque exécution, lisible sur GitHub, sans pouvoir faire échouer la CI ; il ne se lance plus aux envois sur une branche jetable (`proto/…`), comme vous l'avez validé le 10 novembre, et se lance sur un tag comme avant (sans cette ligne, GitHub cesserait de le faire dès qu'une branche est exclue).
- `socle-batch`, la conduite d'un lot : le récap de la clôture d'un lot colle la suite du projet ; trois phrases resserrées, au même sens.
- `socle-review`, la conduite de la revue : « les entrées dont le lot change le statut ou les critères » au lieu de « les sujets… le « Fait quand » » ; dans un projet installé, une forme du shell que le hook ne juge pas se signale au dépôt public du socle, par l'humain, comme le guide le dit depuis le 17 novembre ; cinq phrases resserrées, au même sens.

Avec `tests-seuls`, les copies d'ici décrivent l'ancien dossier, sans autre effet ; aucun contrôle ne signale aujourd'hui une copie en retard (une tâche du backlog le prévoit). La section du socle du fichier d'instructions de ce dépôt (`AGENTS.md`) suit plus tard : elle dépasserait son budget de 16 000 octets ; la tâche T-0069 l'y recopiera.

## Éléments cités

- .claude/skills/socle-batch/SKILL.md sha256:1fd976d515435ddb
- .claude/skills/socle-review/SKILL.md sha256:27989e97b2c786e1
- .github/workflows/socle.yml sha256:10da7cbe8c62e719

L'empreinte de ces trois lignes est celle que la copie aura : votre accord porte sur ce texte exact. Plus bas : `D-`, une demande comme celle-ci ; `ADR-`, une décision que l'agent écrit seul quand elle est réversible ; après @, l'empreinte de la version lue.

- D-0120@f10e0e80 — votre validation du 16 novembre de la règle du hook de l'agent, dont deux phrases changent un mot.
- D-0123@61a56e15 — votre validation du 16 novembre de la structure du backlog en quatre formes.
- D-0127@4d91f8cd — votre validation du 16 novembre de la vue de la suite, que le workflow et `socle-batch` déclenchent.
- D-0133@51dbb960 — la seconde demande de ce lot, l'exception à la règle des critères d'une tâche, qui se décide à part.
- B-0265@6a1180af — le besoin : un mot pour une chose dans le backlog.
- T-0050@cd5c89bf — la tâche : les textes que des tests lisent mot pour mot.
- L-0014@cd0d35b8 — le lot en cours, avec l'historique de sa revue.
- B-0218@fd498240 — le besoin des copies protégées en retard sur leurs gabarits.
- T-0069@92a4d3a7 — la tâche qui recopiera plus tard la section du socle du fichier d'instructions.
- T-0060@4ff7dafb — la tâche, d'un lot suivant, qui retirera du produit les phrases de procédure de la règle du hook.

## Où regarder

- [Les changements du lot](https://github.com/theodubus/memory/pull/62/files), dans sa pull request : les textes que les tests lisent, dans `engine/socle/` ; [les tests du dossier, avant](https://github.com/theodubus/memory/blob/28755ed989c8807f3fab1743b89e4ab72dbd6ded/tests/test_revue.py), et de même dans `tests/`.
- Le texte nouveau des copies, leurs gabarits : [`socle-batch`](https://github.com/theodubus/memory/blob/ddc01c37051dc2e035167998d0e0ea30e1e9005c/engine/socle/templates/skills/socle-batch/SKILL.md), [`socle-review`](https://github.com/theodubus/memory/blob/ddc01c37051dc2e035167998d0e0ea30e1e9005c/engine/socle/templates/skills/socle-review/SKILL.md), [le workflow](https://github.com/theodubus/memory/blob/ddc01c37051dc2e035167998d0e0ea30e1e9005c/engine/socle/templates/socle.yml) (l'installeur remplace `@@BRANCHES_JETABLES@@` par les branches jetables et les tags) ; leurs copies actuelles : [`socle-batch`](https://github.com/theodubus/memory/blob/28755ed989c8807f3fab1743b89e4ab72dbd6ded/.claude/skills/socle-batch/SKILL.md), [`socle-review`](https://github.com/theodubus/memory/blob/28755ed989c8807f3fab1743b89e4ab72dbd6ded/.claude/skills/socle-review/SKILL.md), [le workflow](https://github.com/theodubus/memory/blob/28755ed989c8807f3fab1743b89e4ab72dbd6ded/.github/workflows/socle.yml).
- [La règle du hook dans le guide](https://github.com/theodubus/memory/blob/ddc01c37051dc2e035167998d0e0ea30e1e9005c/engine/socle/HELP.md), section « Ce que juge le hook de l'agent », et [en anglais](https://github.com/theodubus/memory/blob/ddc01c37051dc2e035167998d0e0ea30e1e9005c/engine/socle/HELP.en.md).

## Options

- Valider : effort faible ; risque faible, chaque test garde ce qu'il prouvait ; réversible par une demande nouvelle.
- Les tests seuls : le lot se livre ; les trois copies restent en retard jusqu'à une demande nouvelle ; effort faible, réversible.
- Refuser : les tests gardent « sujet » ; le lot ne se livre pas tant que les textes ne reviennent pas à l'ancien mot ; effort moyen pour l'agent, qui revoit avec vous ce qui doit changer ; réversible.

## Conséquences

Si vous validez : l'agent commite ces neuf tests, les trois copies posées par l'installeur et votre réponse dans un même push ; la pull request du lot fusionne à la CI verte, une fois D-0133 répondue : si vous la refusez, une tâche récrit d'abord les tâches qu'elle vise. Les tests seuls : de même, sans les copies. Si vous refusez : rien du lot ne fusionne. Sans réponse : le lot reste sur sa branche, sa CI en échec sur ces tests.

## Recommandation

Valider. Vérifié : les neuf tests passent avec leur valeur nouvelle, et la suite entière passe avec eux, dans la copie de travail ; les empreintes sont celles des fichiers que l'installeur pose, recalculées dans un clone jetable ; les différences des copies sont celles dites plus haut. Supposé : que « entrée du backlog » dit bien, dans la règle du hook, ce qu'un trou ouvre, une tâche ou un besoin selon que sa correction est claire.

## Réponses possibles

- `valider` — les neuf tests et les trois copies changent avec le lot.
- `tests-seuls` — les neuf tests changent ; les trois copies attendent.
- `refuser` — rien ne change ; l'agent revoit avec vous le lot.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
