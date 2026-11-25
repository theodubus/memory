<!-- socle: couche=demandes zone=publique -->
# D-0190 — Valider la reprise sur « reprends » seul : la passation écrite dans un fichier du dépôt, que la session neuve trouve, juge et retire, selon sa spécification

> date : 2026-11-25

## Décision demandée

Valider la spécification de la reprise sur « reprends » seul : la session qui passe la main écrit sa passation dans un fichier du dépôt, et la session neuve, d'un compte comme d'un autre, la reprend sur ce seul mot, sans prompt à copier.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet, vérifie le travail de l'agent et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Chess, votre jeu d'échecs, recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Une session (une conversation avec l'agent, dans Claude Code) ne mène qu'un lot, un ensemble de tâches qu'elle livre par une pull request ; puis elle passe la main à une session neuve : c'est la passation. Le 24 novembre, vous avez validé la passation programmée : l'agent programme lui-même la session suivante ; ou, dans le mode « prompt à copier » que ce dépôt garde pour jongler entre vos comptes, il vous donne un texte de neuf lignes à coller dans une session que vous ouvrez. Le même jour, vous avez demandé si ce texte était utile : la passation pourrait vivre dans le dépôt, et vous n'auriez qu'à écrire « reprends ». Vous avez retenu les trois propositions de l'agent pour la concevoir, puis placé ce chantier avant la mise à jour de chess.

**La question.** Avant d'écrire le code, il reste à valider comment la passation s'écrit, se trouve et se protège contre le travail en double, et ce que deviennent la commande d'aujourd'hui et ses tests.

**Ce que dit la spécification :**

- **Le fichier.** La session qui part écrit le fichier `handoff.md` de la mémoire du projet : sa branche (la ligne de commits où elle a travaillé), l'heure, le nombre de lots menés sans message de vous, ce qui attend. Elle l'enregistre en dernier (un commit) et l'envoie sur GitHub (un push). La commande `socle handoff write` remplace `socle handoff prompt`, avec les mêmes options et les mêmes refus. Écrit mais pas envoyé, l'état du projet, ce résumé que l'agent lit au démarrage, le dit à la session qui part.
- **« reprends ».** En premier message d'une session neuve, l'agent rapatrie les branches du dépôt (`git fetch`), puis lance `socle handoff check` sans argument : la commande trouve la passation, la plus récente toutes branches confondues, et juge sa garde comme aujourd'hui. Vous n'écrivez que « reprends » ; la tâche programmée (le message envoyé à l'heure dite à la session programmée) aussi.
- **La garde**, la vérification qui empêche deux sessions de faire le même travail. Vos trois points du 24 novembre : sa tête est le dernier commit qui a écrit la passation, son heure, la date de ce commit ; la session neuve, acceptée, retire la passation dans son premier commit, envoyé aussitôt ; sans passation, « reprends » fait ce que fait une session neuve, et le dit. La garde refuse comme aujourd'hui si la branche a bougé depuis, ou si une autre session a écrit la mémoire du projet depuis ; et, nouveau, si la passation a déjà été reprise par une session qui y travaille.
- **Ce qu'elle laisse passer.** Deux sessions qui écrivent « reprends » dans la même minute, avant que l'une ait envoyé son retrait : toutes deux reprennent, comme le même texte collé deux fois aujourd'hui. Et une pull request fusionnée par squash (en un seul commit), sa branche supprimée, que la garde refusait : la session repart de `main`, la branche principale, qui porte tout le travail.
- **L'état** dit la passation qui attend : `passation : en attente sur origin/<branche>, écrite à <heure> — « reprends » la reprend`. Le hook de l'agent, le programme qui filtre ses commandes, ne change pas.
- **« reprends » dans une session qui a déjà travaillé** garde son sens d'aujourd'hui : continuer.

**Les tests que `valider` autorise à changer ou retirer**, parce qu'ils lisent le texte d'aujourd'hui ou la commande `handoff prompt` : dans `tests/test_passation.py`, `test_il_refuse_tant_que_la_tete_locale_n_est_pas_poussee`, `test_il_nomme_la_tete_distante_et_l_heure_puis_le_prompt_d_une_session_neuve`, `test_apres_une_fusion_la_garde_nomme_la_branche_par_defaut`, `test_les_bornes_d_une_session_programmee`, `test_le_lot_de_l_etat`, `test_la_commande_ecrit_le_prompt_puis_juge_sa_garde`, `test_ses_refus_d_usage`, `test_le_prompt_ne_prend_plus_le_lien_de_la_session_qui_part`, `test_le_prompt_dans_la_langue_de_la_memoire` ; dans `tests/test_skills.py`, qui lisent les consignes de l'agent (ses skills), `test_changer_de_session_range_puis_renvoie_a_socle_handoff`, `test_ses_commandes_sont_celles_du_moteur`, `test_les_deux_modes_et_leur_commutateur`, `test_le_moment_ses_seuils_et_les_bornes`, `test_en_session_programmee_le_rangement_programme_la_session_neuve`, `test_la_garde_la_pull_request_voir_et_arreter_et_l_ancienne_session`, `test_les_instructions_et_le_guide_le_disent` ; et quatre défauts injectés (les erreurs que l'auto-test du moteur commet exprès pour vérifier qu'un contrôle les attrape) qui visent la commande remplacée, `passation-non-poussee`, `passation-non-commitee`, `passation-borne-de-la-chaine` et `passation-sans-tache-prete`. Ces tests changeront dans un lot à venir : votre réponse les couvrira si la piste B de D-0189 est retenue et faite avant ; sinon, ils vous seront redemandés à ce lot.

## Éléments cités

Plus bas : `B-`, un besoin ; `T-`, une tâche ; `L-`, un lot ; `D-`, une demande ou une décision ; `J-`, une entrée du journal ; après @, l'empreinte de la version lue.

- B-0346@0cc7064f — le besoin : la session neuve reprend sur « reprends » seul, la passation écrite dans le dépôt.
- T-0180@ec227028 — la tâche qui vous soumet cette spécification ; votre réponse la clôt.
- L-0038@3287cadb — le lot de cette seule tâche, au jalon en cours.
- D-0174@95b3c303 — votre validation du 24 novembre de la passation programmée, dont cette spécification remplace deux sections.
- D-0177@4e9a5869 — vos trois points retenus le 24 novembre : la tête de la garde, le retrait par la session neuve, « reprends » sans passation.
- D-0185@0953ba62 — votre décision : ce chantier passe avant la mise à jour de chess.
- D-0173@163bc9a2 — votre décision : ce dépôt reste au prompt à copier.
- J-2026-11-24-AF@1eb7df79 — votre question du 24 novembre : le prompt est-il utile ?
- D-0189@3bd90cfd — la demande précédente, qui règle si votre réponse couvre des tests changés plus tard.

## Où regarder

- [La spécification](https://github.com/theodubus/memory/blob/fca571ecbf5735ef17a98a48526ec3731ec36403/docs/fabrication/reprends-specification.md) : « La trouver », « La garde », « Reprendre, ou rien à reprendre » et « Modèle de menace ». Vérifier que la règle du fichier le plus récent et les refus de la garde vous conviennent.

## Options

- **La spécification telle qu'écrite** (recommandée). Effort : une ou deux tâches menées par un agent auxiliaire, de 3 à 4 points de la semaine chacune (un point : 1 % de la limite d'usage hebdomadaire de votre compte), puis une demande courte pour remettre les copies protégées des skills, que vous seul approuvez. Risque faible : la garde d'aujourd'hui reste, et la session neuve s'arrête dès qu'un doute apparaît. Réversible : le prompt à copier revient par une tâche.
- **Avec vos changements** (répondre `refuser`, en disant ce qui change). Effort : une réécriture et une demande nouvelle. D'ici là, le prompt à copier reste.

## Conséquences

Si vous validez : T-0180 se ferme ; les tâches qui l'appliquent s'ouvrent dans ce lot (le moteur, les skills, le guide, la note de version), et changent les tests nommés plus haut ; chess reçoit « reprends » à sa mise à jour ; ici, à la fin de chaque lot, l'agent vous dira d'écrire « reprends » dans une session neuve au lieu de vous donner un texte. Si vous refusez : la spécification se réécrit sur ce que vous dites et revient en demande. Sans réponse : rien ne change, et le prompt à copier reste.

## Recommandation

La spécification telle qu'écrite. Vérifié : le clone de ce dépôt rapatrie toutes les branches de GitHub ; la garde d'aujourd'hui et ses tests ; vos trois points. Supposé : qu'une session neuve d'un autre compte rapatrie de même toutes les branches, et que la règle du fichier le plus récent suffise ; les tests de la tâche le vérifieront avec git, le reste au premier usage réel.

## Réponses possibles

- `valider` — la spécification telle qu'écrite, et le changement ou le retrait des tests et des défauts injectés nommés plus haut.
- `refuser` — elle ne convient pas : dites ce qui change ; elle se réécrit et revient en demande.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
