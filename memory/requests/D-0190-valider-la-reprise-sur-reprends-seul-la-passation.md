<!-- socle: couche=demandes zone=publique -->
# D-0190 — Valider la reprise sur « reprends » seul : la passation écrite dans un fichier du dépôt, que la session neuve trouve, juge et retire, selon sa spécification

> date : 2026-11-25

## Décision demandée

Valider la spécification de la reprise sur « reprends » seul : la session qui passe la main écrit sa passation dans un fichier du dépôt, et la session neuve, d'un compte comme d'un autre, la reprend sur ce seul mot, sans texte à copier.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet (le dossier `memory/` du dépôt : décisions, journal, tâches), vérifie le travail de l'agent et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Chess, votre jeu d'échecs, recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Une session (une conversation avec l'agent, dans Claude Code) mène un lot, un ensemble de tâches livré par une pull request ; puis elle passe la main à une session neuve : c'est la passation. Le 24 novembre, vous avez validé la passation programmée, où l'agent programme lui-même la session suivante, et gardé ici le mode « prompt à copier », pour passer d'un de vos comptes à l'autre : l'agent vous donne un texte de neuf lignes à coller dans une session que vous ouvrez. Le même jour, vous avez demandé si ce texte était utile : la passation pourrait vivre dans le dépôt, et vous n'écririez que « reprends ». Vous avez retenu les trois propositions de l'agent pour la concevoir, puis placé ce chantier avant la mise à jour de chess.

**La question.** Avant le code, valider comment la passation s'écrit, se trouve et se protège contre le travail en double, et ce que deviennent la commande d'aujourd'hui et ses tests. Le mode « prompt à copier » reste : son texte devient « reprends ».

**Ce que dit la spécification :**

- **Le fichier.** La session qui part écrit `handoff.md` dans la mémoire : l'heure, sa branche (la ligne de commits où elle a travaillé), le nombre de lots menés sans message de vous, qui arrête une chaîne de sessions programmées à deux, et ce qui attend. L'heure et la branche l'identifient. Elle l'enregistre en dernier (un commit), l'envoie sur GitHub (un push), puis vérifie qu'une session neuve la trouverait. `socle handoff write` remplace `socle handoff prompt`.
- **« reprends ».** En premier message d'une session neuve, l'agent rapatrie les branches de GitHub (`git fetch`), puis lance `socle handoff check` : la commande prend la passation la plus récente, toutes branches confondues, et juge sa garde. La tâche programmée (le message envoyé à l'heure dite à la session programmée) écrit « reprends — session programmée », pour que la session sache que le mot ne vient pas de vous et compte ses lots sans vous.
- **La garde**, la vérification qui empêche deux sessions de faire le même travail. Vos trois points du 24 novembre : elle part du dernier commit qui a écrit la passation et de son heure ; la session neuve, acceptée, retire la passation dans son premier commit, envoyé aussitôt ; sans passation, « reprends » fait ce que fait une session neuve, et le dit. Elle refuse, comme aujourd'hui, si la branche a bougé depuis ou si une autre session a écrit la mémoire depuis ; et, nouveau, si une session a repris la passation sans que son travail soit encore entré dans `main`, la branche principale.
- **Ce qu'elle laisse passer.** Deux « reprends » quasi simultanés, avant que l'un ait envoyé son retrait : toutes deux reprennent, comme le même texte collé deux fois aujourd'hui ; au pire, un lot fait en double, si vous ouvrez deux sessions à la fois. Un second « reprends » après que la pull request de la session qui a repris est fusionnée dans `main`, pendant qu'elle travaille encore : il fait ce que fait une session neuve, comme une session ouverte sans texte aujourd'hui. Et une pull request fusionnée par squash ou rebase (ses commits réécrits), sa branche supprimée, que la garde refusait : la session repart de `main`, qui porte le travail ; la mémoire écrite ailleurs depuis la passation la fait toujours refuser.
- **D'un autre compte**, la session voit les mêmes branches, celles du dépôt sur GitHub ; si elle ne trouvait aucune passation, elle le dirait dès son premier message.
- **L'état**, le résumé que l'agent lit au démarrage, dit la passation qui attend. Le hook de l'agent, le programme qui filtre ses commandes, ne change pas.

**Les tests que `valider` autorise à changer ou retirer**, parce qu'ils lisent le texte d'aujourd'hui, la commande `handoff prompt` ou le refus d'un squash : dans `tests/test_passation.py`, `test_il_refuse_tant_que_la_tete_locale_n_est_pas_poussee`, `test_il_nomme_la_tete_distante_et_l_heure_puis_le_prompt_d_une_session_neuve`, `test_apres_une_fusion_la_garde_nomme_la_branche_par_defaut`, `test_les_bornes_d_une_session_programmee`, `test_le_lot_de_l_etat`, `test_la_commande_ecrit_le_prompt_puis_juge_sa_garde`, `test_ses_refus_d_usage`, `test_le_prompt_ne_prend_plus_le_lien_de_la_session_qui_part`, `test_le_prompt_dans_la_langue_de_la_memoire` ; dans `tests/test_skills.py`, qui lisent les consignes de l'agent (ses skills), `test_changer_de_session_range_puis_renvoie_a_socle_handoff`, `test_il_dit_la_consommation_le_changement_de_session_et_l_apres_fusion`, `test_il_est_pose_protege_sous_son_budget_et_passe_ses_controles`, `test_ses_commandes_sont_celles_du_moteur`, `test_les_deux_modes_et_leur_commutateur`, `test_le_moment_ses_seuils_et_les_bornes`, `test_en_session_programmee_le_rangement_programme_la_session_neuve`, `test_la_garde_la_pull_request_voir_et_arreter_et_l_ancienne_session`, `test_les_instructions_et_le_guide_le_disent` ; dans l'auto-test du moteur (des erreurs commises exprès pour vérifier qu'un contrôle les attrape, et des témoins sains), les défauts `passation-non-poussee`, `passation-non-commitee`, `passation-borne-de-la-chaine`, `passation-sans-tache-prete`, `passation-squash-collee-tard` et `passation-squash-programmee`, et le témoin « une session programmée, une tâche prête et un lot mené sans message de l'humain, reçoit son prompt ». `valider` vous engage sur ces changements ; la CI les comptera quand ils seront faits, plus tard, si vous retenez la piste B de D-0189 (votre accord donné avant un lot couvre ses tests) et qu'elle est faite avant ; sinon, l'agent vous redemandera une confirmation courte à ce lot.

## Éléments cités

Plus bas : `B-`, un besoin ; `T-`, une tâche ; `L-`, un lot ; `D-`, une demande ou une décision ; `J-`, une entrée du journal ; après @, l'empreinte de la version lue.

- B-0346@0cc7064f — le besoin : la session neuve reprend sur « reprends » seul, la passation écrite dans le dépôt.
- T-0180@ec227028 — la tâche qui vous soumet cette spécification ; votre réponse la clôt.
- L-0038@3287cadb — le lot de cette seule tâche, au jalon en cours, l'ensemble des corrections d'avant chess.
- D-0174@95b3c303 — votre validation du 24 novembre de la passation programmée ; cette spécification en remplace « Le prompt et sa garde ».
- D-0177@4e9a5869 — vos trois points du 24 novembre : la tête de la garde, le retrait par la session neuve, « reprends » sans passation.
- D-0185@0953ba62 — votre décision : ce chantier passe avant la mise à jour de chess.
- D-0173@163bc9a2 — votre décision : ce dépôt reste au prompt à copier, qui devient « reprends ».
- J-2026-11-24-AF@1eb7df79 — votre question du 24 novembre : le prompt est-il utile ?
- D-0189@95adb0f5 — la demande en attente qui règle si votre réponse couvre des tests changés plus tard.

## Où regarder

- [La spécification](https://github.com/theodubus/memory/blob/0ebe650b9beef7535972c0246bff6c89019175fc/docs/fabrication/reprends-specification.md) : « La trouver », « La garde », « Reprendre, ou rien à reprendre » et « Modèle de menace » (ce que la garde arrête et laisse passer). Vérifier que ce qu'elle laisse passer vous convient.

## Options

- **La spécification telle qu'écrite** (recommandée). Effort : une ou deux tâches menées par un agent auxiliaire, de 3 à 4 points de la semaine chacune (un point : 1 % de votre limite d'usage hebdomadaire), puis une demande courte : les skills de l'agent ont une copie dans le projet, protégée pour qu'il ne change pas ses propres règles, que l'installeur remet et que vous seul approuvez. Risque faible : la garde d'aujourd'hui reste, et la session neuve s'arrête au moindre doute. Réversible : le texte à copier revient par une tâche.
- **Avec vos changements** (répondre `refuser`, en disant ce qui change). Une réécriture et une demande nouvelle ; d'ici là, le texte à copier reste.

## Conséquences

Si vous validez : T-0180 se ferme ; les tâches qui l'appliquent s'ouvrent (le moteur, les skills, le guide `HELP.md`, la note de version qui dit le changement aux projets), et changent les tests nommés ; chess reçoit « reprends » à sa mise à jour ; ici, à la fin de chaque lot, l'agent vous dira d'écrire « reprends » dans une session neuve. Si vous refusez : la spécification se réécrit sur ce que vous dites et revient en demande. Sans réponse : rien ne change, et le texte à copier reste.

## Recommandation

La spécification telle qu'écrite. Vérifié : le clone de ce dépôt rapatrie toutes les branches de GitHub ; la garde d'aujourd'hui et ses tests ; vos trois points ; les cas de fusion où la règle d'avant, sans estampille, échouait, que la relecture du lot a reproduits avec git. Supposé : que l'estampille les règle tous, et qu'une session d'un autre compte rapatrie de même toutes les branches ; les tests de la tâche le vérifieront avec git, le reste au premier usage réel.

## Réponses possibles

- `valider` — la spécification telle qu'écrite, et le changement ou le retrait des tests, défauts et témoin nommés plus haut.
- `refuser` — elle ne convient pas : dites ce qui change ; elle se réécrit et revient en demande.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
