<!-- socle: couche=demandes zone=publique -->
# D-0142 — Changer la raison attendue du refus de find . -type f | xargs sed -i s/a/b/ que D-0140 autorise pour T-0002 : réglages de Claude Code au lieu d'écriture d'un fichier protégé

> date : 2026-11-19

## Décision demandée

Autoriser que `find . -type f | xargs sed -i s/a/b/` entre dans la liste des refus de `test_cp_t_find_xargs_bash_ec_sort_o_et_python_c` (`tests/test_garde.py`) avec la raison « réglages de Claude Code », au lieu de la raison « écriture d'un fichier protégé » que votre accord du 19 novembre, D-0140, nommait.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code entretenu par un agent d'IA, Claude Code : il garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote.

**Le chantier.** Le lot en cours, L-0019, corrige des commandes d'écriture ou de suppression que juge mal le hook de l'agent, le programme qui contrôle chacune de ses commandes avant qu'elle agisse. Cinq de ses six tâches sont faites. Le 19 novembre au soir, vous avez validé une demande, D-0140, qui changeait trois valeurs attendues de tests pour deux de ses tâches ; une valeur attendue est ce qu'un test exige, ici qu'une commande soit refusée ou acceptée par le hook, et pour quelle raison. Les deux valeurs de la tâche sur `git push` sont appliquées ; la troisième, celle de T-0002, ne peut pas l'être telle qu'elle était écrite.

**La question.** T-0002 n'a qu'un objet : faire refuser `find . -type f | xargs sed -i s/a/b/`, qui remplace un texte dans tous les fichiers du projet et passe aujourd'hui le hook. D-0140 disait, mot pour mot : « Après : elle va dans la liste des commandes refusées du même test, avec la raison « écriture d'un fichier protégé » et la décision « refus ». » Le hook la refuse, mais avec une autre raison, « réglages de Claude Code ». La raison fait partie de la valeur attendue, et la politique du projet, que vous seul changez, exige votre accord pour changer celle d'un test.

Les fichiers protégés sont ceux que seul vous modifiez : la politique du projet, ses hooks, sa CI, vos réponses aux demandes, la copie du moteur dans un projet installé. Les réglages de Claude Code en sont : le fichier `.claude/settings.json`, que git suit, dit quels hooks tournent, et son réglage local, `settings.local.json` à côté de lui, que git ne suit pas, peut les couper tous sans que rien ne le voie. Le projet d'essai du test, un petit projet créé pour lui, a ses réglages, comme tout projet que tient Claude Code. Une commande qui réécrit tous les fichiers du projet les réécrit aussi, et quand une commande touche à la fois les réglages et un autre fichier protégé, le hook nomme d'abord les réglages, le plus grave.

La forme équivalente, `find . -type f -exec sed -i s/a/b/ {} +`, est déjà refusée avec cette raison, et un autre test l'exige (`test_un_find_sous_un_dossier_du_projet_ne_vise_pas_les_reglages`). D-0140 le disait elle-même, dans sa recommandation : « `find . -type f -exec sed -i s/a/b/ {} +` est refusé pour les réglages de Claude Code » ; elle nommait par erreur l'autre raison pour la forme en `xargs`. Obtenir quand même « écriture d'un fichier protégé » demanderait soit d'inverser l'ordre des refus, ce que contredit cet autre test, soit de réécrire le message des réglages pour qu'il contienne ces mots, ce qui ne servirait qu'à faire passer le test. Je ne propose ni l'un ni l'autre.

- Avant (aujourd'hui) : dans [ce test](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/tests/test_garde.py#L779), qui juge les écritures par `cp -t`, `find`, `xargs`, `bash -c`, `sort -o` et `python -c`, `find . -type f | xargs sed -i s/a/b/` est dans la liste des commandes qui passent : aucun refus.
- Après : elle va dans la liste des refus du même test, avec la raison « réglages de Claude Code » (la variable `reglage` que le test définit déjà) et la décision « refus », celle qui arrête la commande.

Dans l'usage, seule la raison qu'affiche le refus diffère : l'agent lit que la commande toucherait `.claude/settings.json`, que seul vous modifiez, au lieu d'un fichier protégé. La commande est arrêtée de même, et l'agent l'écrit sur les dossiers qu'il vise : dans ce dépôt, `find engine -name '*.py' | xargs sed -i s/a/b/` passe. Dans un projet installé, chess compris, la copie du moteur, sous son dossier `.socle`, est protégée : `find . -name '*.py' | xargs sed -i …` y est refusé, comme sa forme en `-exec` aujourd'hui, et `find src -name '*.py' | xargs sed -i …` passe si `src` ne contient aucun fichier protégé.

## Éléments cités

`T-`, une tâche, le livrable d'un commit ; `B-`, un besoin, un résultat à atteindre ; `L-`, un lot ; `D-`, une demande ; `ADR-`, une décision de conception ; `J-`, une entrée du journal ; après @, l'empreinte de la version lue, qui prouve que l'agent l'a lue avant d'écrire.

- D-0140@3c12ff2c — votre accord du 19 novembre sur trois valeurs attendues, dont celle-ci avec l'autre raison.
- T-0002@e006b68b — la tâche qui juge `xargs` par la liste que lui donne la commande qui le précède.
- B-0230@128595b7 — le besoin qu'elle sert, le défaut d'aujourd'hui : le hook ne juge `xargs` que par les chemins protégés écrits en toutes lettres.
- L-0019@3b9f232d — le lot en cours, les écritures que le hook juge mal.
- J-2026-11-19-AL@e363cc96 — l'entrée du journal qui dit l'arrêt de T-0002 avant son code, et pourquoi.
- 852b0ac — le commit poussé où les liens de cette demande montrent la valeur d'aujourd'hui.

## Où regarder

- [La liste des commandes qui passent](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/tests/test_garde.py#L779) : la commande `find . -type f | xargs sed -i s/a/b/`, et, plus haut dans le même test, la variable `reglage`.
- [L'autre test](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/tests/test_garde.py#L830) : `find . -type f -exec sed -i s/a/b/ {} +` y est attendue refusée pour les réglages.
- [Votre accord du 19 novembre](https://github.com/theodubus/memory/blob/85d31e3a7a53d4265b9a0f6e49ae5de5e346f180/memory/requests/D-0140-changer-la-valeur-attendue-de-deux-tests-du-hook-e.md) : sa section « T-0002 », dont cette demande ne change que la raison.

## Options

- Valider : la commande entre dans la liste des refus avec la raison « réglages de Claude Code », et T-0002 s'implémente ; effort : un autre agent, lancé pour implémenter, dont le premier jet existe ; risque faible : le hook refuse davantage, seulement des écritures dont la liste peut contenir un fichier protégé ; réversible par une demande nouvelle.
- Refuser : T-0002 s'abandonne, et la commande reste dans la liste des commandes qui passent ; effort nul ; le remplacement global par `xargs` continue de passer le hook ; réversible.

## Conséquences

Si vous validez : T-0002 s'implémente avec cette valeur, se fait relire par un relecteur sans contexte, un autre agent chargé de la prendre en défaut, et part sur GitHub avec votre réponse, dans le même envoi. Le reste du lot se livre cette nuit, après sa propre relecture : une réponse d'ici là fait clore L-0019 avec T-0002 ; plus tard, T-0002 rejoint le prochain lot qui touche le hook. Si l'implémentation contredit une autre valeur attendue, elle s'arrête et revient à vous par une demande nouvelle : votre accord ne couvre que celle-ci. Si vous refusez : L-0019 se clôt sans T-0002, et B-0230 reste ouvert pour `xargs`. Sans réponse : T-0002 attend ; L-0019 se livre avec ses cinq autres tâches.

## Recommandation

Valider. Vérifié, sur le hook de la branche de travail : `find . -type f -exec sed -i s/a/b/ {} +` est refusé avec la raison des réglages, qui cite `.claude/settings.json`, et `find . -type f | xargs sed -i s/a/b/` passe ; le premier jet de T-0002 la refuse avec la raison des réglages, dans le projet d'essai du test. Supposé : que T-0002 ne contredise aucune autre valeur attendue ; son premier jet n'a été essayé que sur quelques cas, pas sur la suite entière.

## Réponses possibles

- `valider` — la commande entre dans la liste des refus avec la raison « réglages de Claude Code », avec T-0002, dans le même envoi que votre réponse.
- `refuser` — la valeur reste ; T-0002 s'abandonne.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
