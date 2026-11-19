<!-- socle: couche=demandes zone=publique -->
# D-0140 — Changer la valeur attendue de deux tests du hook et d'un défaut de l'auto-test que contredisent T-0002 et T-0106 du lot L-0019

> date : 2026-11-19

## Décision demandée

Autoriser l'agent à changer trois valeurs attendues qui fixent l'ancien comportement que corrigent les tâches T-0002 et T-0106 : un cas de `test_cp_t_find_xargs_bash_ec_sort_o_et_python_c` et un cas de `test_un_push_se_juge_par_ses_arguments_developpes` (`tests/test_garde.py`), et une commande du défaut injecté `push-par-une-variable` de l'auto-test (`engine/socle/selftest.py`).

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code entretenu par un agent d'IA : il garde la mémoire du projet (ses décisions, son journal, son backlog, la liste du travail à faire), vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote.

**Le chantier.** Le lot en cours, L-0019, corrige des commandes d'écriture ou de suppression que juge mal le hook de l'agent, le programme qui contrôle chacune de ses commandes avant qu'elle agisse. Il suit la règle que vous avez validée le 16 novembre : le hook juge les formes du shell qu'un agent écrit dans son travail. Ce soir, un sous-agent, un autre agent lancé pour implémenter, en a fait quatre tâches, pas encore relues ni poussées : le script qu'un heredoc (un texte de plusieurs lignes écrit dans la commande) donne à python, les arguments d'un `python -c` (un script python écrit dans la commande), `find … | xargs rm` (la suppression d'un dossier qui contient le projet), et les filtres d'un `find`. Il s'est arrêté avant le code des deux autres, T-0002 et T-0106 : chacune contredit une valeur attendue existante.

**La question.** La politique d'autonomie du projet, que vous seul changez, exige votre accord par une demande validée pour changer la valeur attendue d'un test existant ; une décision écrite par l'agent ne suffit pas. Voici les trois valeurs, chacune avant et après. Votre accord ne couvre qu'elles : une autre valeur attendue que l'une des deux tâches contredirait reviendrait à vous par une demande nouvelle.

**T-0002, le remplacement global par `xargs`.** `xargs` lit une liste de fichiers sur son entrée et la passe à la commande qu'il lance. `find . -type f | xargs sed -i s/a/b/` remplace un texte dans tous les fichiers du projet, les fichiers protégés compris : ceux que la politique protège, dont elle-même, les hooks, la CI et vos réponses aux demandes. Elle écrit aussi les réglages de Claude Code, dont le fichier local settings.local.json, que git ne suit pas : ni le contrôle de fin de tour ni celui du commit ne le voient changer. Le hook ne juge `xargs` que par les chemins protégés que la commande écrit en toutes lettres : celle-ci n'en écrit aucun et passe, alors que sa forme équivalente, `find . -type f -exec sed -i s/a/b/ {} +`, est refusée. T-0002 fait juger `xargs` par ce que la commande qui lui donne sa liste peut lister : un `find` par ses dossiers de départ et ses filtres, `grep -r` (les fichiers qui contiennent un texte) et `git ls-files` (les fichiers suivis) comme un `find` sans filtre. Une autre commande qui donne la liste (`cat liste`, `ls`, `echo`) garde le jugement d'aujourd'hui. La tâche faite sur `find … | xargs rm` juge un autre effet : la suppression du projet.

- Avant : dans [ce test](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/tests/test_garde.py#L779), `find . -type f | xargs sed -i s/a/b/` est dans la liste des commandes qui passent : `assertIsNone(hooks.refus_bash(projet, cmd))`, aucun refus.
- Après : elle va dans la liste des commandes refusées du même test, avec la raison « écriture d'un fichier protégé » et la décision « refus ».

L'effet dans l'usage : `grep -rl foo . | xargs sed -i s/foo/bar/g`, lancé depuis la racine du projet, sera refusé, puisque sa liste peut contenir un fichier protégé ; l'agent l'écrit alors sur les dossiers visés (`grep -rl foo engine docs | …`), ou avec un filtre de nom qui n'atteint aucun fichier protégé (`find engine -name '*.py' | xargs sed -i …` passe ; `find . -name '*.py'` atteint `tests/parallele.py` et reste refusé, comme sa forme en `-exec` aujourd'hui).

**T-0106, la branche courante d'un `git push`.** Une substitution, `$(…)` ou entre accents graves, lance une commande et met sa sortie à sa place. Le 19 novembre, une tâche a fait refuser un `git push` dont un argument ne se développe pas, une substitution comprise : sans connaître la branche, le hook ne peut pas dire si le push vise la branche par défaut, `main`, ce que la politique vous réserve, comme toute action irréversible ou externe. Mais `git push -u origin "$(git branch --show-current)"`, qui pousse la branche courante, est une forme qu'un agent écrit couramment ; le relecteur sans contexte du lot précédent l'a relevé. T-0106 remplace trois substitutions précises, `$(git branch --show-current)`, `$(git rev-parse --abbrev-ref HEAD)` et `$(git symbolic-ref --short HEAD)`, par la branche courante, que le hook lit déjà pour un push qui ne nomme pas sa branche ; le push se juge alors comme si elle était écrite en toutes lettres : il passe depuis une branche de travail et reste refusé depuis `main`. Toute autre substitution reste refusée, et la substitution ne se résout pas quand la même commande change de branche ou de dépôt avant le push (`git checkout main && git push origin "$(git branch --show-current)"`, un `cd` ailleurs) : elle reste refusée.

- Dans [ce test](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/tests/test_garde.py#L1333), lancé dans un projet d'essai sur sa branche de travail : avant, `git push origin "$(git branch --show-current)"` est dans la liste des refus, comme un argument que le hook ne sait pas développer ; après, il va dans la liste des commandes qui passent (`assertIsNone`). Le test garde une autre substitution refusée, `` git -C . push origin `echo main` ``.
- Dans [ce défaut de l'auto-test](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/engine/socle/selftest.py#L1731), qui remet dans le moteur le défaut que corrigeait la tâche du 19 novembre (un argument de push qui passe par une variable, une fonction ou une substitution, lu tel qu'écrit) et vérifie que chacune de ses cinq commandes est refusée : avant, la cinquième est `git push origin "$(git branch --show-current)"` ; après, `git push origin "$(echo main)"`, une substitution que le hook ne développe pas, pour que le défaut juge encore une substitution.

Rien d'autre ne change dans ces tests ; chaque tâche ajoute ses propres tests, qui échouent sans elle.

## Éléments cités

`T-`, une tâche, le livrable d'un commit ; `B-`, un besoin, un résultat à atteindre ; `L-`, un lot ; `D-`, une demande comme celle-ci ; `ADR-`, une décision de conception ; après @, l'empreinte de la version lue.

- L-0019@31cf0e2e — le lot en cours, les écritures que le hook juge mal, dont ces deux tâches.
- T-0002@e006b68b — la tâche qui juge `xargs` par la liste que lui donne la commande qui le précède.
- B-0230@c28ed387 — le besoin qu'elle sert, en deux points : `xargs`, et `python -c`, que la tâche faite sur ses arguments tient déjà.
- T-0106@cb0ff27c — la tâche, de priorité haute, qui résout la branche courante dans un `git push`.
- B-0254@de1fc754 — le besoin qu'elle sert, de priorité haute : un push forcé ou vers la branche par défaut caché par une variable.
- T-0006@90239e33 — la tâche close du 19 novembre qui refuse un argument de push que le hook ne sait pas développer.
- B-0206@63623cf6 — le besoin clos qui a fait juger `xargs` par les chemins protégés qu'il cite.
- ADR-0082@beb85978 — la règle que vous avez validée le 16 novembre : le hook juge les formes qu'un agent écrit.
- 852b0ac — le dernier commit poussé de la branche de travail, celui qui ouvre le lot ; les liens de cette demande y pointent.

## Où regarder

- [Le test de T-0002](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/tests/test_garde.py#L779) : la commande `find . -type f | xargs sed -i s/a/b/`.
- [Le test de T-0106](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/tests/test_garde.py#L1333) et [le défaut de l'auto-test](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/engine/socle/selftest.py#L1731) : la commande `git push origin "$(git branch --show-current)"`.
- [La tâche T-0002](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/memory/backlog/T-0002-le-hook-de-l-agent-ne-juge-xargs-et-python-c-que-p.md) et [la tâche T-0106](https://github.com/theodubus/memory/blob/852b0ac4b4b62ad9b45b4e1e29868ab505fcae1d/memory/backlog/T-0106-le-hook-resout-la-branche-courante-dans-un-git-pus.md) : ce que chacune doit tenir.

## Options

- Valider : les trois valeurs changent comme dit plus haut, avec T-0002 et T-0106 ; effort : un sous-agent implémente les deux tâches ; risque faible : T-0002 refuse davantage, seulement des écritures dont la liste peut contenir un fichier protégé, et T-0106 laisse passer trois formes précises, jugées sur la branche réelle ; réversible par une demande nouvelle.
- Refuser : T-0002 et T-0106 s'abandonnent en renvoyant à votre réponse ; le remplacement global par `xargs` continue de passer, et le push de la branche courante reste refusé, l'agent écrivant sa branche en toutes lettres ; effort nul ; réversible.
- N'en garder qu'une : le socle n'autorise un changement de test que par la réponse `valider` à une demande qui le nomme ; répondre `refuser` en nommant la tâche à garder, et l'agent pose aussitôt une demande pour ses seules valeurs ; l'autre s'abandonne.

## Conséquences

Si vous validez : l'agent fait implémenter les deux tâches avec ces valeurs changées et les commite avec votre réponse. Avant tout envoi sur GitHub, il fait relire le lot entier par un relecteur sans contexte, un autre agent chargé de le prendre en défaut ; le lot part ensuite, votre réponse dans le même envoi, puis l'agent fusionne sa pull request une fois la CI verte. Une part de ce travail peut attendre la remise à zéro de la limite d'usage de l'abonnement sur cinq heures, à 56 % ce soir, à 01 h 10 (heure de Paris). Si vous refusez : il livre le lot avec ses quatre autres tâches ; B-0230 reste ouvert pour son point sur `xargs`, et B-0254 reste ouvert sans tâche, le push de la branche courante s'écrivant en toutes lettres. Sans réponse : les deux tâches attendent, et l'agent mène la relecture des quatre autres.

## Recommandation

Valider. Vérifié, sur le hook du commit 852b0ac : `find . -type f | xargs sed -i s/a/b/` passe, `find . -type f -exec sed -i s/a/b/ {} +` est refusé pour les réglages de Claude Code, et `git push -u origin "$(git branch --show-current)"` comme `git push origin "$(echo main)"` sont refusés comme un argument que le hook ne sait pas développer ; les trois valeurs avant sont lues dans le code à ce commit. Supposé : que ces deux tâches ne contredisent aucune autre valeur attendue ; le sous-agent l'a vérifié pour les quatre autres, pas encore pour celles-ci.

## Réponses possibles

- `valider` — les trois valeurs attendues changent, avec T-0002 et T-0106, dans le même envoi que votre réponse.
- `refuser` — les trois valeurs restent, T-0002 et T-0106 s'abandonnent ; nommer une tâche à garder fait poser une demande pour elle seule.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
