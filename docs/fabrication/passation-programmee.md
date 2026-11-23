# La passation programmée : relevé de l'essai

L'essai que demande B-0259, mené par T-0041 le 23 novembre 2026 depuis la
session https://claude.ai/code/session_01Mr1cCdzA4SmjsK13eKa5R4, sur la
branche `ccr-e17be058-0rh9vm`. Les heures sont en UTC (heure de Paris :
plus une heure).

## La question

Près d'une limite d'usage, la session qui orchestre range, puis donne à
Théo le prompt de la session suivante, à coller lui-même. B-0259 propose
que l'agent programme lui-même l'ouverture de la session neuve à la
remise à zéro de la fenêtre, plus cinq minutes. La variante visée, B, en
deux appels : `create_session` sans prompt, puis `create_trigger` avec
`persistent_session_id` et `run_once_at`, qui y envoie le prompt de
passation. Le repli, A, en un appel : `create_trigger` avec
`create_new_session_on_fire`, essayé seulement si B échoue sur un point
qui l'empêche.

## Le protocole

Trois sessions d'essai, créées par `create_session` avec le dépôt
`theodubus/memory` (`source_url`), le modèle `claude-opus-5-5` nommé
explicitement, sans prompt, sans mode de permission ni environnement
(hérités), sous l'étiquette `essai-B-0259`. Chacune est une sonde : son
prompt lui interdit d'écrire, de commiter, de pousser, de lancer un
sous-agent, de créer une session ou de toucher à une tâche programmée, et
lui fait rendre son modèle, sa branche, son état de démarrage, ses hooks,
ses outils et les approbations demandées.

| Session | Créée | Prompt programmé pour | Ce qu'elle lève |
| --- | --- | --- | --- |
| E1 `session_01Mr1cChBUHid4KsanUEzDKn` | 12:37:20 | 12:43 (six minutes) | inconnues 1 à 4 et 7 |
| E2 `session_01Mr1cCg8bdUBpzgaB9LTKfG` | 12:37:39 | le 24 à 05:40 (dix-sept heures) | inconnue 5, une nuit |
| E3 `session_01Mr1cCgJDouU19f3iNrHZwv` | 12:37:40 | 16:00, annulé aussitôt | inconnue 6 |

Après E1, une quatrième sonde, E4 (`session_01Mr1cCiX24mEMb1ddZVUnrt`,
créée à 12:45:31, prompt à 12:48), a été ajoutée pour la branche : la même
que E1, avec `outcome_branch` (`proto/essai-b0259-e4`, un préfixe de
branche jetable).

## Inconnues 1 à 4 et 7 : E1

Ce qu'E1 a rendu, lu dans ses événements (`list_events`) et son état
(`get_session`) :

- **1. Le prompt programmé arrive, et la session travaille sans
  approbation.** Levée pour la lecture. Prévu à 12:43, le prompt est
  arrivé à 12:44:25, marqué comme venu d'une tâche programmée
  (`inbound_origin` : `trigger_fire`) : le planificateur ne tire pas à la
  seconde, d'où une minute et demie de retard. La session a tourné en
  mode `auto`, hérité ; ses deux appels d'outil, en lecture
  (`get_session`, une commande `Bash`), sont passés sans approbation, et
  aucun hook n'a rien refusé ; son tour a fini à 12:44:45, en
  16 secondes. L'écriture (un fichier, un commit, un push) n'est pas
  essayée : la sonde l'interdisait. Le mode `auto` hérité est celui où la
  session qui orchestre écrit, commite et pousse sans approbation.
- **2. Le dépôt, les hooks, la branche.** Levée en partie. Le dépôt est
  cloné dans `/home/user/memory` ; l'état du socle a été injecté au
  démarrage par le hook `SessionStart` ; les hooks git sont branchés
  (`core.hooksPath` : `.socle/git-hooks`). Mais sans `outcome_branch`, la
  session n'a pas de branche : tête détachée sur le dernier commit de la
  branche par défaut (`a68f5bc0`), aucune branche de développement dans
  son contexte (`outcomes` absent, `current_branches` vide). Une
  passation doit donc nommer sa branche, ce que fait `outcome_branch`
  (E4, plus bas).
- **3. Le modèle demandé.** Levée. `configured_model`, le modèle de la
  session et celui qui a servi le tour sont tous `claude-opus-5-5`. Le
  niveau de réflexion (`effort`), lui, ne s'hérite pas : `get_session` ne
  le donne pas pour E1, alors que la session qui l'a créée est en
  `xhigh` ; `create_session` ne le pose que si une consigne le demande.
- **4. L'ancienne session réveillée par la nouvelle.** Levée pour une fin
  propre : rien n'est arrivé dans la session qui orchestre après la fin
  des tours d'E1 (12:44:45) et d'E4 (12:51:08), ni après leurs
  archivages ; ses événements, relus de 12:44 à 12:47 puis de 12:54 à
  13:07, n'en montrent aucun. Un échec n'a pas été provoqué : aucun moyen
  sans risque n'en était sous la main. La documentation de l'outil dit
  qu'un tour en échec, ou un conteneur redémarré, réveille la session qui
  a créé : la spécification dira si cela convient à une ancienne session
  près de sa limite, que B-0259 voulait ne jamais réveiller.
- **7. Le coût.** Levée pour le démarrage. Le tour d'E1 a écrit 29 972
  jetons au cache d'une heure, en a lu 150 352 et en a produit 810, pour
  un contexte final de 90 750 jetons (prompt système, outils, `AGENTS.md`
  et état du socle) ; 0,29 dollar au tarif public. Pondéré comme les
  valeurs du point de `docs/fabrication/consommation.md` (écriture d'une
  heure 2, lecture 0,042, sortie 5), environ 70 000 jetons : ce que coûte
  la relecture à froid d'une conversation de 35 000 jetons, soit environ
  1,1 point de la fenêtre de cinq heures à la valeur médiane du point
  d'Opus (de 0,5 à 5,4 selon cette valeur, mal connue), un sixième de
  point de la semaine. Son
  premier appel a trouvé 60 776 jetons déjà en cache, le début du
  prompt système commun aux sessions du compte. Une vraie passation
  coûte en plus ce que la session neuve lit pour reprendre le lot.

## La branche : E4

E4, créée comme E1 mais avec `outcome_branch` : `proto/essai-b0259-e4`.
Prévu à 12:48, son prompt est arrivé vers 12:50:53, avec près de trois
minutes de retard ; son tour a fini à 12:51:08. Ce qu'elle a rendu :

- la branche est dans son contexte (`outcomes`, `current_branches`), et
  le clone est dessus, partie du dernier commit de la branche par
  défaut ;
- ses instructions de session lui disent d'y développer et d'y pousser
  (« Develop on branch `proto/essai-b0259-e4` ») ;
- l'état du socle injecté dit la même branche.

La branche n'existait que dans son clone : GitHub n'en montre aucune
autre que `main` après l'essai. Levée : une passation qui nomme sa
branche par `outcome_branch` la donne à la session neuve. Non essayé :
une branche qui existe déjà sur GitHub, celle d'un lot en cours, que la
session neuve devrait reprendre à son dernier commit (`source_revision`
la nomme aussi) ; la spécification le prévoit, son essai avec elle. Même
coût qu'E1, à 2 % près (30 407 jetons écrits, 150 655 lus, 633 produits).

## Inconnue 6 : annuler

E3 a reçu sa tâche (`trig_01RQ4H4EgY8LrBajnNok3rQu`, prévue à 16:00),
puis, une minute après, `delete_trigger` l'a supprimée et
`archive_session` a archivé la session. Constaté aussitôt :

- la tâche n'est plus dans `list_triggers` ; l'outil confirme qu'elle ne
  tirera pas ;
- la session reste dans la liste des sessions (`list_sessions`), à
  l'état « archivée » (`SESSION_STATUS_ARCHIVED`, rangée parmi les
  terminées) ; elle ne disparaît pas ;
- archivée sans avoir jamais reçu de prompt, elle avait déjà un conteneur
  démarré (version de Claude Code, mode de permission hérité `auto`).

Levée en partie : la tâche et la session s'annulent, en deux appels, et
il reste dans la liste de Théo une session archivée. La preuve décisive,
aucun prompt reçu par E3 à 16:00, se lit après (plus bas, « Après
coup »).

Une session créée et pas encore servie (E1 et E2 avant leur prompt) est
à l'état « au repos » (`SESSION_STATUS_IDLE`), rangée parmi les sessions
« prêtes à relire » (`REVIEW_READY`) : elle se voit dans la liste de
Théo dès sa création, avec son titre.

## Inconnue 5 : une nuit

E2, créée vide à 12:37:39, attend son prompt pour le 24 novembre à 05:40
(`trig_0135y1zbnewUggBu4Yb9eAUZ`), dix-sept heures plus tard. Non levée à
ce jour : son résultat s'ajoute ici le 24 au matin (plus bas, « Après
coup »).

## A, le repli

Non essayée : B n'échoue sur aucun point levé. Elle ne l'est que si E2
montre qu'une session laissée vide une nuit ne reçoit pas son prompt.

## La règle de choix

B si ses inconnues 1 à 5 se lèvent ; sinon A, si les siennes se lèvent ;
sinon le prompt à copier reste. Au 23 novembre, 1 à 4 sont levées : 1
pour la lecture, 2 sous la condition de nommer la branche, 4 pour une fin
propre ; 5 attend E2. Le choix se fait sur son
résultat ; il est soumis à Théo, qui le confirme, avec ce relevé complet.

## Ce que la spécification devra dire

Observé pendant l'essai, sans être une inconnue de B-0259 :

- **La branche.** `create_session` reçoit `outcome_branch`, la branche du
  travail ; sinon la session neuve n'a pas où pousser (E1, E4).
- **Le niveau de réflexion.** Il ne s'hérite pas ; la session neuve
  tourne au niveau par défaut, sauf consigne qui en nomme un.
- **Le retard.** Le prompt arrive une à trois minutes après l'heure
  demandée (E1 : 1 min 25 s ; E4 : 2 min 53 s).
- **La liste de Théo.** Une session créée s'y voit aussitôt, avec son
  titre, « prête à relire » tant qu'elle attend son prompt ; archivée,
  elle y reste, marquée archivée. Le titre doit dire ce qu'elle est et
  quand elle partira.

Déduit, non essayé :

- **La garde de la reprise.** Avec `outcome_branch` sur la branche du
  travail, la session neuve pousserait là où l'ancienne poussait : la
  garde du skill `socle-resume` (« une autre session a poussé sur la
  branche depuis le dernier commit de l'agent ») la verrait, ce que
  B-0259 demandait de vérifier. Aucune sonde n'a poussé : l'essai de la
  spécification le vérifie, avec une branche qui existe déjà.

## Après coup

- E3, après 16:00 : <!-- à vérifier : aucun prompt reçu -->
- E2, le 24 après 05:40 : <!-- à lire : son prompt reçu ou non, et ce qu'elle a rendu -->
