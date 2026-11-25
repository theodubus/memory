<!-- socle: couche=demandes zone=publique -->
# D-0189 — Choisir comment une réponse donnée avant le lot de son changement couvre ce changement : une validation déjà poussée compte tant que la tâche qui la cite est ouverte et que ce qu'elle nomme n'a pas bougé (piste B), ou la règle des skills (piste A)

> date : 2026-11-25

## Décision demandée

Choisir comment votre accord pour changer un test, donné avant le lot qui le change, couvre ce changement quand il est fait plus tard, dans une autre session : la piste B, où le contrôle compte un accord déjà enregistré tant que la tâche qui fera le changement est ouverte et que le test n'a pas bougé dans la branche principale, ou la piste A, deux consignes écrites pour l'agent, sans toucher au contrôle.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet, vérifie le travail de l'agent et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Chess, votre jeu d'échecs, recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Le jalon en cours, un ensemble de corrections, stabilise le produit avant cette mise à jour de chess. Le 24 novembre, vous y avez rangé trois corrections laissées de côté ; celle-ci est la dernière. Sa conception n'étant pas tranchée, sa spécification vous est soumise avant tout code.

**La question.** Changer la valeur qu'un test attend, ou le supprimer, exige votre accord, qui nomme le test : une demande comme celle-ci, ou une question courte dans la conversation. Votre réponse devient un fichier du dépôt, que l'agent écrit mot pour mot (« consigner »), commite et envoie sur GitHub (« pousser »). Deux règles se contredisent. Le 19 novembre, vous avez retenu que la demande d'un test se pose dès que la tâche s'écrit, avant son lot (l'ensemble de tâches qu'une session mène, puis livre par une pull request). Mais les contrôles automatiques de GitHub (la CI) ne comptent que les accords ajoutés par le push ou la pull request qu'ils jugent ; d'où une règle du 14 novembre : la réponse se pousse avec le test qu'elle autorise, jamais avant. Or l'agent mène un lot par session, et fusionne sa pull request dans la branche principale (`main`) à la fin du lot. Votre réponse donnée avant le lot qui change le test n'a nulle part où attendre : gardée dans la machine de la session, elle disparaît avec elle ; poussée, elle part dans `main` avec la pull request de cette session, et la CI du lot suivant ne la compte plus.

**Déjà vu.** Le 24 novembre, votre accord sur un test, donné un lot trop tôt, a dû vous être redemandé ; le même jour, une réponse a dû être mise de côté, en correctif non appliqué, pour partir avec ses deux tests ; avant, trois réponses poussées trop tôt ont été consignées deux fois. Sur chess, l'inverse : une réponse donnée mais pas encore consignée reste « en attente » dans l'état du projet que l'agent vous montre, et il vous la redemande.

**Un exemple.** Session 1 : une tâche dit qu'un test doit attendre 6 au lieu de 4 ; vous validez. Session 2 : le lot change le test. Aujourd'hui, la CI le refuse, et l'agent vous redemande votre accord. Avec A, la session 1 écrit votre phrase au journal du projet (son registre daté) ; la session 2 la consigne de là, avec le test. Avec B, la session 1 consigne et pousse votre réponse, que la tâche cite ; la session 2 change le test, et la CI l'accepte.

**La piste B.** Un accord déjà poussé couvre le changement de ce qu'il nomme (un test ; un fichier de cas, une liste de valeurs attendues ; une clé des seuils de contrôle ; un fichier protégé, que seul vous pouvez faire changer). Poussé dans la même pull request, il le couvre toujours, comme la CI de la pull request le compte déjà. Fusionné dans `main` avec une pull request précédente, il le couvre à deux conditions : la tâche qui fera ce changement, et qui cite votre accord, est encore ouverte ; et ce qu'il nomme est encore tel que vous l'aviez sous les yeux en répondant. Le lot qui fait le changement clôt la tâche : une fois fusionné, l'accord est épuisé, et un nouveau changement du même test demande un nouvel accord. Le contrôle lit le nom, pas les valeurs : le relecteur du lot vérifie que le changement est celui que vous avez validé, comme aujourd'hui. Ce qu'elle laisse passer, mesuré sur ce dépôt : sur vos 149 accords, 4 sont cités par une tâche ouverte, et les 2 tests qu'ils nomment ont déjà changé depuis : aucun test n'est couvert aujourd'hui hors de sa pull request. Sans la condition de la tâche, 31 tests nommés par des accords anciens le redeviendraient : la relecture de la spécification l'a relevé. C'est un assouplissement d'un garde-fou (un contrôle qui refuse), que seul votre accord permet. L'avertissement qui dit aujourd'hui à l'agent, au commit et au push, « poussée seule, elle ne couvrira pas ce changement » dirait faux : il se retire, avec ses tests. La règle du 19 novembre reste ; celle du 20, qu'un test peut se pousser sous sa demande en attente, la CI rouge jusqu'à votre réponse, aussi.

**La piste A.** Aucun contrôle ne change. Votre réponse donnée dans la conversation s'écrit au journal, et le lot qui change le test la consigne de là. Votre décision du 19 novembre change : la demande d'un test ne se pose plus dès la tâche écrite, mais au début du lot qui le change, dans sa session ; sans votre réponse dans cette session, la pull request du lot finit rouge, l'agent ne peut la fusionner, et la session suivante la reprend. Rien ne vérifie le journal : une session qui ne suit pas la règle vous redemande.

**Les tests que `valider` retire** (la réponse qui retient la piste B), dans `tests/test_reponse_seule.py`, tous ceux de l'avertissement et de la fonction qui calcule ce qu'il juge, dont rien d'autre ne se sert : `test_la_reponse_seule_avertit_dans_l_arbre_au_commit_et_avant_le_push`, `test_avec_le_changement_qu_elle_autorise_rien_a_dire`, `test_un_test_deja_change_sur_la_branche_sous_une_validation_d_avant_ne_fait_pas_taire`, `test_une_reponse_deja_poussee_est_hors_de_la_plage`, `test_une_demande_qui_ne_nomme_ni_test_ni_fichier_ne_dit_rien`, `test_un_fichier_protege_cite_avec_son_empreinte`, `test_un_fichier_protege_cite_sans_empreinte_ne_compte_pas`, `test_un_fichier_deja_pousse_sous_la_demande_en_attente_precede_sa_reponse`, `test_un_fichier_de_cas_cite`, `test_une_cle_des_seuils_nommee_est_suivie_comme_un_test`, `test_une_cle_que_la_demande_ne_nomme_pas_ne_compte_pas`, `test_une_exception_du_controle_n_est_qu_un_avertissement`, `test_la_base_non_poussee` et `test_un_depot_sans_commit_n_a_pas_de_base` ; et deux défauts injectés, ces erreurs que l'auto-test du moteur commet exprès pour vérifier qu'un contrôle les attrape, `reponse-poussee-seule` et `reponse-poussee-sans-sa-cle`. La reconnaissance d'un test, d'une clé ou d'un fichier nommés reste vérifiée par les tests nouveaux de la règle B. Reste `test_une_reponse_consignee_mais_pas_commitee_n_est_plus_en_attente`.

## Éléments cités

Plus bas : `B-`, un besoin ; `T-`, une tâche ; `L-`, un lot ; `D-`, une demande ou une décision ; `J-`, une entrée du journal ; après @, l'empreinte de la version lue.

- B-0347@886a118c — le besoin : une réponse donnée avant le lot de son changement le couvre, plus tard, dans une autre session.
- T-0179@b553c61e — la tâche qui vous soumet cette spécification ; votre réponse la clôt.
- L-0037@d136cee1 — le lot de cette seule tâche, au jalon en cours.
- D-0141@284ef820 — votre décision du 19 novembre : la demande d'un test se pose avant son lot.
- B-0142@1d182ddf — le besoin du 14 novembre : la réponse se pousse avec son changement, et l'avertissement qui le rappelle.
- D-0147@ffd624cc — votre décision du 20 novembre : un test se pousse sous sa demande en attente, la CI rouge jusqu'à votre réponse.
- D-0184@1d7b6a57 — l'accord du 24 novembre qui a dû vous être redemandé.
- J-2026-11-24-AG@994b67c1 — l'entrée du journal qui relève ce cas.
- J-2026-11-24-Z@68d28ccd — la réponse mise de côté en correctif pour partir avec ses tests.
- D-0092@42266c33 — votre décision : l'agent fusionne lui-même sa pull request.

## Où regarder

- [La spécification](https://github.com/theodubus/memory/blob/bc8675c0846118b20624be54ee0d0050f0d6b2dd/docs/fabrication/reponse-avant-le-lot-specification.md) : « La règle » et son tableau de cas, puis « Modèle de menace » ; « Piste A », « Ce qui reste », pour comparer.

## Options

- **Piste B** (recommandée). Effort : une tâche menée par un agent auxiliaire, de 3 à 4 points de la semaine (un point : 1 % de la limite d'usage hebdomadaire de votre compte). Puis une demande courte : la piste B change le texte des skills des demandes et des lots (les consignes que l'agent suit), dont le projet garde une copie protégée que vous seul approuvez. Risque faible : l'accord ne vaut que pour une tâche ouverte. Réversible par une tâche.
- **Piste A**. Effort : du texte dans deux skills, de 1 à 2 points. Risque moyen : votre réponse attend au journal, que rien ne vérifie, et la pull request d'un lot peut rester rouge en attendant la vôtre. Réversible.

## Conséquences

Si vous validez : une tâche implémente la piste B dans le prochain lot du jalon, avant le code de la reprise sur « reprends » seul (la passation d'une session à la suivante, dont la spécification vous sera soumise ensuite, et dont les tests changeront sous votre réponse à venir) ; elle retire les tests nommés plus haut ; le guide de mise à jour de chess le dira, sans geste de votre part. Avec `piste-a` : une tâche écrit les deux consignes dans les skills des demandes et des lots. Si vous refusez : la spécification se réécrit sur ce que vous dites et revient en demande. Sans réponse : rien ne change, ce lot attend, et l'agent passe au suivant.

## Recommandation

La piste B. Vérifié : les cas cités, dans le journal ; le contrôle d'aujourd'hui ne lit que les accords de sa plage, et seul l'avertissement retiré le rappelle ; la mesure des accords anciens, sur ce dépôt. Supposé : que la comparaison à `main` tienne dans la CI de chess comme ici, qui lit tout l'historique du dépôt ; les tests de la tâche le vérifieront.

## Réponses possibles

- `valider` — la piste B, et le retrait des tests et des défauts injectés nommés plus haut.
- `piste-a` — la piste A, sans toucher au contrôle ni aux tests.
- `refuser` — aucune des deux : dites ce qui change ; la spécification se réécrit et revient en demande.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
