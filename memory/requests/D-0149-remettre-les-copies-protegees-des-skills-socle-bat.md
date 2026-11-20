<!-- socle: couche=demandes zone=publique -->
# D-0149 — Remettre les copies protégées des skills socle-batch, socle-review et socle-request sur leurs gabarits que le lot L-0006 a changés, et supprimer quatre tests et en changer un qui fixaient l'ancien texte

> date : 2026-11-20

## Décision demandée

Autoriser l'agent à remettre les copies protégées de ce dépôt des skills `socle-batch`, `socle-review` et `socle-request` sur le texte exact de leurs gabarits, changés par le lot L-0006, et ratifier la suppression de quatre tests et le changement d'un cinquième, qui fixaient l'ancien texte. Vous répondrez une fois la pull request du lot ouverte, après sa revue, son lien donné dans la conversation.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code tenu par un agent d'IA : il garde la mémoire du projet (décisions, journal, backlog des besoins, ces résultats à atteindre, et des tâches), vérifie ce que l'agent produit, et vous pose en demandes les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote ; le dépôt `theodubus/socle` distribue le moteur seul.

**Le chantier.** Le lot L-0006 (des tâches menées et relues ensemble) corrige les skills du produit, ces procédures écrites que l'agent charge quand elles servent. Il y écrit des décisions que vous aviez prises et qu'aucun lot n'avait encore portées dans les textes : le 15 novembre, sur Fable, le modèle le plus capable et le plus cher, au-dessus d'Opus ; le 17, retirer la procédure des formes du shell (plus bas) et ajouter une ligne d'économie à la consigne des sous-agents, ces agents que lance celui qui mène le lot ; le 20, retirer le recul, un paragraphe de réflexion exigé après chaque passe de revue. L'implémentation est faite ; restent la revue du lot par un relecteur sans contexte, la pull request et la fusion.

**La question.** Chaque skill a deux textes : le gabarit, que le produit installe dans chaque projet, et, dans ce dépôt, une copie, celle que charge l'agent d'ici, protégée pour qu'il ne récrive pas ses propres règles : seul votre accord la change. Les trois copies ont le texte de vos accords du 19 novembre ; l'état du dépôt (le résumé que le socle calcule et donne à l'agent au démarrage) signale qu'elles diffèrent de leurs gabarits. Cinq tests fixaient aussi mot pour mot des textes que le lot retire ; le socle refuse qu'un test soit supprimé ou change sans une demande validée qui le nomme. Ils sont commités et poussés sous cette demande, comme vous l'avez permis le 20 novembre : la vérification de la pull request les refuse jusqu'à votre réponse.

**Les formes du shell.** Le hook de l'agent, le programme qui juge chaque commande avant qu'elle parte, ne sait pas lire toutes les écritures possibles d'une commande. Un relecteur qui trouvait une écriture qu'aucun agent n'emploie et qui échappait au hook l'écartait, et elle s'inscrivait dans une liste du guide (le manuel de l'humain, installé avec le moteur) ; ailleurs que dans ce dépôt, l'agent proposait de la signaler à `theodubus/socle`. Le 17 novembre, vous avez retiré du produit cette procédure et la liste ; le guide garde ce que le hook arrête et ce qu'il ne modélise pas, que rattrape le contrôle des fichiers protégés. Le hook ne change pas.

**Ce qui change**, de chaque copie à son gabarit, avec son origine.

`socle-batch`, la conduite d'un lot :

- un sous-agent ne reçoit jamais Fable, sauf si vous le voulez (vous, le 15 novembre) ;
- la consigne des sous-agents porte « Économie : lire ce qui sert, pas les fichiers entiers ; pas de suite complète relancée sans raison » (vous, le 17) ;
- la clôture d'un lot n'exige plus le recul (vous, le 20) ;
- la revue renvoie au tri des constats du relecteur que fait `socle-review` (bloquant, au backlog ou écarté), au lieu de « le reste va au backlog », qui le contredisait ;
- un ensemble de tâches qu'une session ne mène pas se forme en jalon, un groupe de besoins, ses lots dessous, plutôt qu'en un lot trop long (un choix de l'agent) ;
- le réveil programmé d'une attente (`send_later`) n'est nommé qu'en session cloud, sur les serveurs d'Anthropic, seul endroit où il existe ; ailleurs, la fin du récap (le résumé de fin de tour de l'agent) dit l'attente, et vous relancez l'agent ;
- pour tenir sous le plafond de 8 000 octets d'un skill, des redites retirées sans règle perdue ; le texte à copier pour ouvrir une session neuve dit de lire l'état et ce que sa ligne « !! coupé » y dit manquer, faute de place.

`socle-review`, la revue d'un lot :

- le recul retiré : chaque passe, une relecture, garde dans le fichier du lot une ligne par bloquant et une ligne des entrées qu'elle ouvre au backlog, et rien d'autre n'est exigé (vous, le 20) ;
- un lot implémenté sur Fable fait vous demander, avant la revue, si vous voulez aussi Fable pour le relecteur (vous, le 15) ;
- la règle des formes du shell sort (vous, le 17).

`socle-request`, les demandes :

- le relecteur à froid d'une demande, un sous-agent qui la lit à votre place avant qu'elle parte, reçoit le modèle le plus capable jusqu'à Opus, et non celui de la session ; Fable seulement si vous le demandez ; le récap nomme ce modèle (un choix de l'agent, qui étend votre règle du 15 novembre pour le relecteur d'un lot) ;
- une décision que vous donnez de vous-même se consigne par `socle decision --unprompted`, son texte exact, sans question inventée, ce que l'agent de chess faisait.

**Les tests**, dans `tests/test_skills.py` et `tests/test_revue.py` :

1. `test_il_ne_renvoie_pas_a_l_atelier`, changé : il interdit dans `socle-batch` les mots propres à ce dépôt (numéros de la mémoire, « chess », « Théo », noms de modèles) ; avant, Fable compris ; après, sans Fable, que le skill nomme pour l'interdire aux sous-agents.
2. `test_une_forme_du_shell_qu_un_agent_n_ecrit_pas_s_ecarte_pour_la_liste`, supprimé : la règle des formes dans `socle-review`.
3. `test_dans_un_projet_equipe_la_forme_se_signale_au_depot_du_socle`, supprimé : leur signalement à `theodubus/socle`.
4. `test_une_forme_qu_aucun_agent_n_ecrit_ne_bloque_pas_et_va_a_la_liste`, supprimé : la même règle dans la consigne que `socle review` écrit en tête du dossier du relecteur, d'où le lot la retire aussi.
5. `test_le_guide_dit_la_regle_et_chaque_forme_cite_sa_note`, supprimé avec sa classe `TestLesFormesConnuesDuGuide` : le paragraphe du guide que vous aviez validé le 16 novembre, et la liste, que votre décision du 17 retire. Deux tests nouveaux montrent qu'aucun texte posé ne dit plus la procédure ni la liste, et que le guide garde ce que le hook arrête.

## Éléments cités

- .claude/skills/socle-batch/SKILL.md sha256:4613921ec80e935f
- .claude/skills/socle-review/SKILL.md sha256:619553ba785b3bca
- .claude/skills/socle-request/SKILL.md sha256:04451ba730e5c9d2

L'empreinte de ces trois lignes est celle de chaque gabarit, que la copie prendra octet pour octet : votre accord porte sur ce texte exact. Plus bas : `D-`, une de vos décisions ; `L-`, un lot ; `T-`, une tâche ; `B-`, un besoin ; après @, l'empreinte de la version lue.

- L-0006@7bbb0f14 — le lot en cours, sur les skills et leurs copies protégées.
- T-0072@f84a75da — sa dernière tâche, qui remet les copies en retard.
- B-0218@fd498240 — le besoin des copies protégées en retard, que rien ne signalait.
- D-0137@8a882c42 — votre accord du 19 novembre qui a remis pour la dernière fois les copies de `socle-batch` et de `socle-request`.
- D-0138@f8ca9924 — votre accord du même jour pour celle de `socle-review`.
- D-0117@0e7cde01 — votre règle du 15 novembre : le relecteur d'un lot sur le modèle le plus capable.
- D-0119@c39e11d7 — votre décision du 15 novembre sur Fable.
- D-0120@f10e0e80 — votre validation du 16 novembre du paragraphe du guide sur les formes du shell.
- D-0128@fd7c9ad7 — votre décision du 17 novembre qui retire cette procédure et la liste.
- D-0144@3ca5d3d1 — votre décision du 20 novembre qui retire le recul.
- D-0147@ffd624cc — votre accord du 20 novembre : un test changé se pousse sous sa demande en attente.

## Où regarder

- Les copies actuelles, à remplacer : [`socle-batch`](https://github.com/theodubus/memory/blob/d34e0418f5d8c4946cd6b6f37b77f26bd7159b7a/.claude/skills/socle-batch/SKILL.md), [`socle-review`](https://github.com/theodubus/memory/blob/d34e0418f5d8c4946cd6b6f37b77f26bd7159b7a/.claude/skills/socle-review/SKILL.md), [`socle-request`](https://github.com/theodubus/memory/blob/d34e0418f5d8c4946cd6b6f37b77f26bd7159b7a/.claude/skills/socle-request/SKILL.md).
- Le texte nouveau : les gabarits `engine/socle/templates/skills/socle-batch/SKILL.md`, `engine/socle/templates/skills/socle-review/SKILL.md` et `engine/socle/templates/skills/socle-request/SKILL.md`, dans la pull request du lot ; y vérifier les changements dits plus haut.
- [Le paragraphe du guide et la liste](https://github.com/theodubus/memory/blob/d34e0418f5d8c4946cd6b6f37b77f26bd7159b7a/engine/socle/HELP.md#L386), que le lot retire.
- Les tests : [le premier](https://github.com/theodubus/memory/blob/d34e0418f5d8c4946cd6b6f37b77f26bd7159b7a/tests/test_skills.py#L326), [le deuxième](https://github.com/theodubus/memory/blob/d34e0418f5d8c4946cd6b6f37b77f26bd7159b7a/tests/test_skills.py#L594), [le troisième](https://github.com/theodubus/memory/blob/d34e0418f5d8c4946cd6b6f37b77f26bd7159b7a/tests/test_skills.py#L613), [le quatrième](https://github.com/theodubus/memory/blob/d34e0418f5d8c4946cd6b6f37b77f26bd7159b7a/tests/test_revue.py#L149), [le cinquième](https://github.com/theodubus/memory/blob/d34e0418f5d8c4946cd6b6f37b77f26bd7159b7a/tests/test_revue.py#L613).

## Options

- Valider : les trois copies deviennent leurs gabarits, octet pour octet, et les tests sont ratifiés ; effort faible ; risque faible, ce sont les textes que chess recevra, relus par la revue ; réversible par une demande nouvelle.
- Refuser : copies et tests restent ; pour que les tests passent, une correction rend aux gabarits la règle des formes du shell et retire de `socle-batch` l'interdiction de Fable, contre vos décisions du 15 et du 17 novembre, et chess le recevrait ; les autres changements restent dans les gabarits ; effort moyen ; risque moyen ; réversible.

Aucune réponse partielle : seule `valider` autorise un test changé, et garder les copies d'avant laisserait l'agent d'ici suivre d'anciennes règles, dont le recul.

## Conséquences

Si vous validez : la vérification de la pull request passe ; l'agent pose les trois copies par l'installeur (la commande qui installe ou met à jour le socle), les commite avec votre réponse, puis fusionne. Si vous refusez : la correction ci-dessus, avant la fusion. Sans réponse : la vérification reste rouge, et le lot ne se fusionne pas. Si la revue a changé l'un de ces gabarits, l'agent vous le dit avec le lien de la pull request, et une demande nouvelle remplace celle-ci pour sa copie.

## Recommandation

Valider. Vérifié : les empreintes citées sont celles des fichiers que pose l'installeur, relancé dans un clone jetable du dépôt, identiques octet pour octet aux gabarits ; seules ces trois copies changent (la CI, les autres skills et le fichier d'instructions de l'agent sont à jour) ; les différences sont celles dites plus haut, lues dans le diff de chaque copie à son gabarit ; avec les cinq tests changés, la suite passe, et seul le contrôle des valeurs attendues attend cette réponse. Supposé : que la revue ne changera pas ces gabarits.

## Réponses possibles

- `valider` — les trois copies deviennent leurs gabarits, et les tests sont ratifiés.
- `refuser` — copies et tests restent ; les textes que fixent les tests reviennent dans les gabarits avant la fusion.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
