<!-- socle: couche=demandes zone=publique -->
# D-0125 — Changer vingt tests que la structure du backlog en quatre formes fait changer, et remettre trois copies protégées de skills à leurs gabarits

> date : 2026-11-16

## Décision demandée

Autoriser l'agent à changer les valeurs attendues des vingt tests nommés plus bas, que la structure du backlog en quatre formes, dont vous avez validé la spécification le 16 novembre, fait changer, et à remettre les copies protégées de ce dépôt des skills `socle-batch`, `socle-review` et `socle-resume` au texte exact de leurs gabarits.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code entretenu par un agent d'IA : il garde la mémoire du projet, dont le backlog (la liste du travail à faire), vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote.

**Le chantier.** Le 16 novembre, vous avez validé la spécification d'un backlog en quatre formes, chacune avec son préfixe : un besoin (`B-`), un défaut à corriger ou une fonction à ajouter ; une tâche (`T-`), un livrable fait en un commit, qui nomme son besoin ; un lot (`L-`), des tâches menées et relues ensemble ; un jalon (`JA-`), des besoins qui servent un même but. Jusqu'ici, toute entrée était un `B-`, un lot ou un jalon marqué d'un champ `forme`, et l'entrée s'appelait « sujet ». Elle est écrite : le moteur, ses contrôles, les textes du produit, et la migration de ce dépôt, où 13 lots et 5 jalons ont pris leur préfixe et 48 tâches ont été posées ; un lot ou un jalon y perd sa priorité, qui ne changeait déjà aucun ordre. Un relecteur sans contexte, un autre agent qui n'a pas la conversation et cherche à prendre le travail en défaut, l'a relue : trois défauts qu'il juge bloquants sont corrigés avant la livraison, six autres vont au backlog. Restent, pour une session suivante, le découpage des besoins à plusieurs livrables, et des textes qui disent encore « sujet » (le dossier que reçoit le relecteur, par exemple) : d'autres tests les lisent mot pour mot, et une autre demande les nommera.

**La question.** La politique du projet interdit à l'agent de changer la valeur attendue d'un test, ce qu'un test exige du code, sans un accord de vous qui le nomme ; votre validation de la spécification n'en nommait aucun. Vingt tests attendent l'ancien vocabulaire ou l'ancienne forme des entrées : sans ce changement, ils échouent, et la structure ne se livre pas. Trois skills, les procédures écrites que l'agent suit, ont deux textes : le gabarit, que le produit installe dans chaque projet, et dans ce dépôt une copie, celle que suit son agent, protégée pour qu'il ne récrive pas ses propres règles : seul votre accord permet de la changer.

**Les tests, dans `tests/`.** Chacun garde ce qu'il prouvait : seuls les identifiants et les mots suivent la structure.

- `test_cli.py`, `test_new_request_questions_pose_des_questions_de_cadrage`, et `test_renommages.py`, `test_l_etat_l_identifiant_l_empreinte_et_l_archivage` : la commande qui crée une entrée, `socle new`, reçoit le type « need » au lieu de « backlog », qui disparaît (`task`, `batch` et `milestone` créent les autres formes) ; le refus attendu (des questions de cadrage hors d'une demande) et le numéro attendu restent.
- `test_format_3.py`, `test_un_sujet_clos_se_range_avec_les_clos` et `test_un_sujet_rouvert_revient_parmi_les_ouverts` : les messages disent « entrées ouvertes », « entrée(s) rangée(s) » et « entrées closes » au lieu de « sujets ouverts », « sujet(s) rangé(s) » et « sujets clos ».
- `test_hooks.py`, `test_exiger_recap_rappelle_l_ordre_du_backlog` : le rappel que l'agent reçoit en fin de tour attend « prochain jalon : JA-… ; besoins ouverts : B-… » et « tâche prête : T-… », au lieu de « prochain jalon : B-… ; reste : B-… » et « prêt : B-… ».
- `test_demarrage.py`, `test_les_listes_de_l_etat_derive_sont_plafonnees_et_ses_lignes_bornees` : ses 21 entrées d'essai deviennent 21 tâches d'un même besoin, puisque seule une tâche, jamais un besoin, peut être prête (à prendre maintenant) ; le plafond des listes reste vérifié ; « prêt : B-… » devient « tâche prête : T-… », « autre(s) prêt(s) » « autre(s) tâche(s) prête(s) », « prêts aussi » « prêtes aussi ».
- `test_ordre.py`, l'ordre du backlog : ses entrées d'essai prennent leur forme par leur préfixe, le champ `forme` disparaissant. Quatorze tests y changent leurs attentes de la même façon : `B-` devient `JA-`, `L-` ou `T-` selon la forme ; « prêt » devient « tâche prête » ; « reste : » « besoins ouverts : » ; « 3 clos sur 3 » « 3 close(s) sur 3 » ; « sujet(s) attendent un sujet ouvert » « entrée(s) attendent une entrée ouverte du backlog ». Le vingtième, `test_un_jalon_clos_sur_une_tache_ouverte_est_refuse`, passe encore, son jalon lu comme un besoin : changé, il juge un vrai jalon. Ce sont `test_ordre_donne_les_prets_le_prochain_jalon_et_ce_qui_lui_reste`, `test_un_jalon_dont_tout_est_clos_se_dit_a_clore`, `test_au_dela_du_plafond_les_prets_se_comptent`, `test_un_jalon_clos_sur_une_tache_ouverte_est_refuse`, `test_les_prets_se_rangent_par_priorite_et_les_basses_restent_a_part`, `test_un_sujet_qui_attend_une_demande_est_pret_a_sa_reponse`, `test_un_jalon_qui_attend_un_sujet_qui_attend_une_demande`, `test_l_etat_dit_ce_qu_attendent_ses_sujets_un_sujet_ou_une_demande`, `test_les_criteres_se_lisent_dans_leur_section`, `test_un_sujet_fait_avec_un_critere_non_coche_est_refuse`, `test_est_lot_se_lit_dans_les_deux_langues`, `test_la_memoire_relie_le_lot_a_ses_sujets_et_l_etat_montre_le_prochain`, `test_un_lot_dont_tout_est_clos_se_dit_a_clore` et `test_le_lot_en_cours_passe_devant_et_un_lot_fait_avant_ses_sujets_est_refuse`.

Le même push porte ces six fichiers entiers : deux autres tests n'y changent que leurs données d'essai, pas leurs attentes (`test_dependances_et_est_jalon_se_lisent_dans_les_deux_langues`, `test_l_essentiel_tient_dans_les_2000_premiers_octets_d_un_etat_qui_les_depasse`). Cinq autres, déjà dans le commit de la structure, ne changent que la commande qu'ils lancent ou le squelette qu'ils remplissent, pas leurs attentes : `test_new_ecrit_le_sujet_meme_si_sa_sortie_est_coupee`, `test_un_sujet_nouveau_a_son_fichier`, `test_un_identifiant_neuf_saute_ceux_des_branches_poussees`, `test_new_ecrit_dans_la_langue_du_projet`, `test_une_memoire_anglaise_remplie_passe_les_controles`. La politique ne réserve pas ces sept-là à votre accord ; ils sont dits pour que vous les voyiez.

**Les trois skills.** Leurs gabarits, le texte que reçoit chaque projet équipé, disent désormais « tâche », « besoin » et `socle new batch` ; la copie de `socle-batch` fait encore écrire `socle new backlog`, une commande qui n'existe plus. Les copies sont aussi en retard sur des changements de leurs gabarits déjà livrés aux projets : pour `socle-review`, vos décisions des 14, 15 et 16 novembre (le tri des constats du relecteur, son modèle d'IA, les formes du shell que le hook ne juge pas) et le point de départ du diff qu'il juge ; pour `socle-resume`, la reprise après une limite quand manque l'outil de Claude Code qui lit les événements de la session. Chaque copie devient son gabarit, octet pour octet.

## Éléments cités

- .claude/skills/socle-batch/SKILL.md sha256:d84357a103ecb244
- .claude/skills/socle-review/SKILL.md sha256:ffce8d6c84cf4196
- .claude/skills/socle-resume/SKILL.md sha256:3746f4f208284a39

L'empreinte de ces trois lignes est celle que la copie aura, celle de son gabarit : votre accord porte sur ce texte exact. Plus bas : `D-`, une demande comme celle-ci ; `ADR-`, une décision que l'agent écrit seul quand elle est réversible ; après @, l'empreinte de la version lue.

- D-0123@61a56e15 — votre validation du 16 novembre de la spécification de la structure.
- ADR-0083@512e719c — la décision de l'agent qui écrit cette spécification et tranche ce qu'elle laissait ouvert.
- B-0265@f07750af — le besoin : un mot pour une chose dans le backlog, et sa structure en quatre formes.
- T-0046@9749df37 — la tâche faite de ce besoin : le commit qui écrit la structure et migre ce dépôt.
- L-0013@e9926abe — le lot en cours, qui réunit ce travail et deux autres.
- B-0218@249d6b52 — le besoin des copies protégées en retard sur leurs gabarits, que cette remise règle pour les skills.

## Où regarder

- [Les tests de l'ordre du backlog, avant leur changement](https://github.com/theodubus/memory/blob/51fed60776508eaf30bc5331469b7332a57f04b0/tests/test_ordre.py) : les attentes que le détail plus haut remplace ; les autres fichiers sont dans le même dossier.
- [Le gabarit de `socle-batch`, le texte nouveau](https://github.com/theodubus/memory/blob/51fed60776508eaf30bc5331469b7332a57f04b0/engine/socle/templates/skills/socle-batch/SKILL.md) et [sa copie actuelle, à remplacer](https://github.com/theodubus/memory/blob/51fed60776508eaf30bc5331469b7332a57f04b0/.claude/skills/socle-batch/SKILL.md) : l'étape 1, `socle new batch` au lieu de `socle new backlog`.
- [Le gabarit de `socle-review`](https://github.com/theodubus/memory/blob/51fed60776508eaf30bc5331469b7332a57f04b0/engine/socle/templates/skills/socle-review/SKILL.md) et [celui de `socle-resume`](https://github.com/theodubus/memory/blob/51fed60776508eaf30bc5331469b7332a57f04b0/engine/socle/templates/skills/socle-resume/SKILL.md) : les textes que prendront leurs copies.
- [La spécification écrite, ADR-0083](https://github.com/theodubus/memory/blob/51fed60776508eaf30bc5331469b7332a57f04b0/memory/decisions/ADR-0083-le-backlog-en-quatre-formes-chacune-avec-son-prefi.md) : ce que la structure tranche, dont la priorité qu'un lot ou un jalon perd à la migration.

## Options

- Valider : effort faible, les tests et les copies changent avec le code ; risque faible, chaque test garde ce qu'il prouvait ; réversible par une demande nouvelle.
- Les tests seuls : la structure se livre ; les trois copies restent en retard, et celle de `socle-batch` cite une commande disparue, jusqu'à une demande nouvelle.
- Refuser : la structure ne se livre pas ; l'agent vous demande ce qui doit changer.

## Conséquences

Si vous validez : l'agent commite ces vingt tests, eux seuls, les trois copies et votre réponse dans un même push, puis livre la structure par la pull request de la branche, une fois la CI verte. Les tests seuls : de même, sans les copies. Si vous refusez : rien de la structure ne fusionne, et l'agent revoit avec vous ce qui doit changer. Sans réponse : la structure reste sur la branche, sa CI (les vérifications que GitHub lance à chaque envoi) en échec sur ces vingt tests ; l'agent avance sur l'entrée suivante du lot, l'arrêt d'un chantier qui tourne en rond, dont vous avez validé la spécification le même jour.

## Recommandation

Valider. Vérifié : avec le code de la structure et ces changements, la suite entière passe ; sans eux, 21 tests échouent : 19 des vingt nommés, et deux dont seules les données d'essai changent, pas les attentes, que la politique ne réserve donc pas à votre accord ; le vingtième passe encore, mais attend l'ancien identifiant d'un jalon. Les empreintes citées sont celles des gabarits relus. Supposé : rien.

## Réponses possibles

- `valider` — les vingt tests changent comme décrit, et les trois copies deviennent leurs gabarits.
- `tests-seuls` — les vingt tests changent ; les trois copies restent telles quelles.
- `refuser` — rien de cela ne change ; la structure ne se livre pas.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
