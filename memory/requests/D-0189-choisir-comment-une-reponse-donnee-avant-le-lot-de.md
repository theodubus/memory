<!-- socle: couche=demandes zone=publique -->
# D-0189 — Choisir comment une réponse donnée avant le lot de son changement couvre ce changement : une validation déjà poussée compte tant que ce qu'elle nomme n'a pas changé sur la branche par défaut (piste B), ou la règle des skills (piste A)

> date : 2026-11-25

## Décision demandée

Choisir comment une validation que vous donnez avant le lot qui change le test qu'elle nomme couvre ce changement, fait plus tard dans une autre session : la piste B, où le contrôle compte une validation déjà poussée tant que ce qu'elle nomme n'a pas changé sur la branche par défaut, ou la piste A, deux règles des skills sans toucher au contrôle.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet, vérifie le travail de l'agent et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Chess, votre jeu d'échecs, recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Le jalon en cours corrige et stabilise le produit avant cette mise à jour de chess. Le 24 novembre, vous y avez rangé trois corrections laissées hors de tout jalon ; celle-ci est la dernière. Sa conception n'étant pas tranchée, sa spécification vous est soumise avant tout code.

**La question.** Changer la valeur attendue d'un test, ou le supprimer, exige votre validation qui le nomme : une demande écrite, ou une question courte dans la conversation. Deux règles se contredisent. Le 19 novembre, vous avez retenu qu'une telle demande se pose dès que la tâche s'écrit, avant son lot, pour que le lot ne s'arrête pas en route. Depuis le 14 novembre, votre réponse se pousse avec le test qu'elle autorise, jamais avant : les contrôles automatiques de GitHub (la CI) ne comptent que les validations ajoutées par le push ou la pull request qu'ils jugent (leur plage). Or l'agent mène un lot par session et fusionne sa pull request à la fin du lot : une réponse donnée avant le lot de son changement n'a nulle part où attendre. Gardée dans le conteneur de la session, elle disparaît avec lui ; poussée, elle est fusionnée avec sa session, et la CI du lot suivant ne la compte plus.

**Vu trois fois.** Le 24 novembre, votre validation d'un test d'une tâche, donnée un lot trop tôt, a dû vous être redemandée ; le même jour, une réponse a dû partir dans un dossier de passation pour rester avec ses deux tests ; avant, trois réponses poussées trop tôt ont dû être consignées une seconde fois. L'autre face, vue sur chess : une réponse donnée mais pas encore enregistrée dans le dépôt reste affichée « en attente », et l'agent vous la redemande.

**La piste B.** Une validation déjà poussée, même dans une pull request fusionnée, couvre le changement de ce qu'elle nomme (un test, un fichier de cas, une clé des garde-fous, un fichier protégé) tant que la branche par défaut ne l'a pas encore reçu : ce qu'elle nomme y est encore tel que vous l'aviez sous les yeux en répondant. Une fois ce changement fusionné, elle est épuisée ; un nouveau changement de la même chose demande une nouvelle validation. Votre réponse s'enregistre et se pousse aussitôt, n'est jamais redemandée, et la règle du 19 novembre reste. L'avertissement qui dit aujourd'hui « poussée seule, elle ne couvrira pas ce changement » dirait faux : il se retire, avec ses tests.

**La piste A.** Aucun contrôle ne change. Une réponse donnée dans la conversation s'écrit au journal du projet, et le lot qui change le test l'enregistre de là, dans le même push que lui. Une demande écrite ne se pose plus dès la tâche écrite, mais à l'annonce du lot qui change le test, dans sa session.

**Les tests que `valider` retire**, dans `tests/test_reponse_seule.py` : `test_la_reponse_seule_avertit_dans_l_arbre_au_commit_et_avant_le_push`, `test_avec_le_changement_qu_elle_autorise_rien_a_dire`, `test_un_test_deja_change_sur_la_branche_sous_une_validation_d_avant_ne_fait_pas_taire`, `test_une_reponse_deja_poussee_est_hors_de_la_plage`, `test_une_demande_qui_ne_nomme_ni_test_ni_fichier_ne_dit_rien`, `test_un_fichier_protege_cite_avec_son_empreinte`, `test_un_fichier_protege_cite_sans_empreinte_ne_compte_pas`, `test_un_fichier_deja_pousse_sous_la_demande_en_attente_precede_sa_reponse`, `test_un_fichier_de_cas_cite`, `test_une_cle_des_seuils_nommee_est_suivie_comme_un_test`, `test_une_cle_que_la_demande_ne_nomme_pas_ne_compte_pas`, `test_une_exception_du_controle_n_est_qu_un_avertissement`, `test_la_base_non_poussee` et `test_un_depot_sans_commit_n_a_pas_de_base` ; et deux défauts injectés de l'auto-test du moteur, `reponse-poussee-seule` et `reponse-poussee-sans-sa-cle`. Le test qui vérifie qu'une réponse enregistrée n'est plus « en attente » reste.

## Éléments cités

Plus bas : `B-`, un besoin ; `T-`, une tâche ; `L-`, un lot ; `D-`, une demande ou une décision ; `J-`, une entrée du journal ; après @, l'empreinte de la version lue.

- B-0347@886a118c — le besoin : une réponse donnée avant le lot de son changement le couvre, plus tard, dans une autre session.
- T-0179@b553c61e — la tâche qui vous soumet cette spécification ; votre réponse la clôt.
- L-0037@d136cee1 — le lot de cette seule tâche, au jalon en cours.
- D-0141@284ef820 — votre décision du 19 novembre : la demande d'un test se pose avant son lot.
- B-0142@1d182ddf — le besoin du 14 novembre : la réponse se pousse avec son changement, et l'avertissement qui le rappelle.
- D-0147@ffd624cc — votre décision du 20 novembre : un test se pousse sous sa demande en attente, la CI rouge jusqu'à votre réponse.
- D-0184@1d7b6a57 — la validation du 24 novembre qui a dû vous être redemandée.
- J-2026-11-24-AG@994b67c1 — l'entrée du journal qui relève ce cas.
- J-2026-11-24-Z@68d28ccd — la réponse partie en correctif pour rester avec ses tests.
- D-0092@42266c33 — votre décision : l'agent fusionne lui-même sa pull request.

## Où regarder

- [La spécification](https://github.com/theodubus/memory/blob/c46f7b60d53b5435e54e54a7cf41f76c7f08f20d/docs/fabrication/reponse-avant-le-lot-specification.md) : « La règle » et son tableau de cas, puis « Modèle de menace » (ce que le contrôle arrête, ce qu'il laisse passer, ce qu'il ne voit pas). Vérifier que l'assouplissement vous convient : une validation de plusieurs semaines couvre encore son premier changement.
- La même, « Piste A » : « Ce qui reste », pour comparer.

## Options

- **Piste B** (recommandée). Effort : une tâche menée par un sous-agent, de 3 à 4 points de la semaine, puis une demande pour remettre la copie protégée du skill des demandes. Risque faible : la règle est bornée, une validation par changement ; c'est un assouplissement d'un garde-fou, que seule votre validation permet. Réversible : rétablir l'ancienne règle est une tâche.
- **Piste A**. Effort : du texte dans deux skills, de 1 à 2 points. Risque moyen : la réponse attend au journal, que rien ne vérifie ; une session qui ne suit pas la règle vous la redemande ; un lot peut de nouveau s'arrêter en route. Réversible.

## Conséquences

Si vous validez : une tâche implémente la piste B dans un lot neuf du jalon, après celui de la reprise sur « reprends » seul ; elle retire les tests nommés plus haut ; le prompt de mise à jour de chess le dira. Avec `piste-a` : une tâche écrit les deux règles, au même endroit. Si vous refusez : la spécification se réécrit sur ce que vous dites et revient en demande ; rien ne change d'ici là. Sans réponse : rien ne change, ce lot attend, et l'agent passe au suivant.

## Recommandation

La piste B. Vérifié : les trois cas cités, dans le journal ; le contrôle d'aujourd'hui ne lit que les validations de sa plage, et le seul contrôle qui le rappelle est l'avertissement retiré. Supposé : que la comparaison à la branche par défaut tienne dans la CI de chess comme ici (elle tire tout l'historique) ; les tests de la tâche le vérifieront.

## Réponses possibles

- `valider` — la piste B, et le retrait des tests et des défauts injectés nommés plus haut.
- `piste-a` — la piste A, sans toucher au contrôle ni aux tests.
- `refuser` — aucune des deux : dites ce qui change ; la spécification se réécrit et revient en demande.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
