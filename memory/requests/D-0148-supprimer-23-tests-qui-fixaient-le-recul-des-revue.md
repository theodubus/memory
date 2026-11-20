<!-- socle: couche=demandes zone=publique -->
# D-0148 — Supprimer 23 tests qui fixaient le recul des revues, retiré le 20 novembre, et ajuster ceux qui le citaient ?

> date : 2026-11-20

## Décision demandée

Les tests qui fixaient le recul des revues, que vous avez fait retirer le 20 novembre, peuvent-ils être supprimés (23) ou ajustés (14), comme la liste ci-dessous les nomme et le justifie ?

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui rend fiables la mémoire, la documentation et les tests d'un projet tenu par un agent de code, et qui ne laisse à l'humain que ce qu'aucun contrôle ne tranche. Les projets qui l'installent reçoivent aussi ce changement.

**Le chantier.** Avant de livrer un lot de tâches, l'agent le fait relire par un relecteur, un sous-agent sans contexte, qui reçoit un dossier (le texte qui lui dit quoi relire) et rend ses constats ; les bloquants doivent être corrigés avant la livraison, et chaque passe s'inscrit dans une section « Revues » du fichier du lot. Le 20 novembre, sur la mesure que le recul n'avait jamais arrêté un lot, vous avez retiré l'obligation du recul : son paragraphe de réflexion, exigé avant chaque passe au-delà de la première et à la clôture, les refus qui l'exigeaient, les marques « même cause / cause nouvelle » que le relecteur posait sur chaque bloquant, et l'arrêt du lot par une demande. Vous avez gardé l'historique des passes et de leurs bloquants, et le tri des constats en bloquant, backlog ou écarté.

**La question.** Le retrait est codé, avec six tests nouveaux qui échouent sur le code d'avant. Les tests qui fixaient l'ancienne règle échouent désormais, et le socle refuse qu'un test soit supprimé ou que sa valeur attendue change sans une demande validée qui le nomme. Ils attendent, non commités, dans le conteneur de l'agent.

Le détail. Avec ces changements, la suite complète passe ; seul le contrôle des valeurs attendues (`tests.attendus`) attend cette réponse. Le tri des constats n'est pas touché : ses tests, dans un autre fichier, ne changent pas. Un point dépasse la lettre de votre décision : le dossier d'une deuxième passe redonnait au relecteur les bloquants des passes d'avant, pour qu'il marque chacun « même cause » ou « cause nouvelle ». Sans les marques, il ne les redonne plus ; l'historique reste lisible dans la section « Revues » du lot. L'option `garder-le-rappel` le garde.

**Les 23 tests supprimés** (dans `tests/test_historique_des_revues.py`), par ce qu'ils fixaient :

- le paragraphe du recul et sa forme : `test_les_passes_leurs_commits_leurs_bloquants_et_leur_recul` (sa lecture des passes et de leurs bloquants est reprise par un test nouveau), `test_le_recul_commence_par_recul_a_soixante_mots_et_finit_par_sa_decision`, `test_un_recul_trop_court_est_refuse_comme_un_recul_absent` ;
- le refus d'une passe sans recul et ce que ce refus montrait (les entrées ouvertes et closes, les lots voisins, trois questions) : `test_une_deuxieme_passe_sans_recul_est_refusee_et_montre_l_historique`, `test_la_commande_refuse_la_passe_sur_sa_sortie_d_erreur`, `test_le_refus_donne_les_entrees_ouvertes_et_closes_et_les_lots_voisins` ;
- les marques du relecteur et la règle qui refusait de continuer quand une même cause revenait : `test_avec_son_recul_la_deuxieme_passe_donne_au_relecteur_les_causes_d_avant`, `test_a_partir_de_la_deuxieme_passe_chaque_bloquant_porte_le_regard_du_relecteur`, `test_continuer_apres_deux_passes_ou_une_meme_cause_revient_est_refuse`, `test_une_seule_passe_ou_la_cause_revient_laisse_continuer` ;
- l'arrêt du lot par une demande : `test_un_arret_nomme_sa_demande`, `test_un_arret_attend_la_reponse_a_sa_demande`, `test_une_demande_ancienne_repondue_qui_ne_cite_pas_le_lot_ne_leve_pas_l_arret`, `test_une_demande_du_lot_retiree_ne_leve_pas_l_arret_meme_repondue`, `test_parmi_les_demandes_du_recul_une_du_lot_repondue_suffit`, `test_un_arret_sans_sa_demande_est_refuse` ;
- le refus de clore un lot sans recul : `test_le_refus_de_la_cloture_montre_ce_que_montre_celui_d_une_passe`, `test_un_lot_clos_sans_le_recul_de_sa_derniere_passe_est_refuse`, `test_avec_son_recul_ou_sans_passe_il_se_clot`, `test_continuer_apres_deux_passes_ou_une_meme_cause_revient_ne_clot_pas`, `test_un_bloquant_sans_le_regard_du_relecteur_ne_clot_pas`, `test_un_arret_ne_clot_qu_apres_la_reponse_a_la_demande_du_lot` ;
- la fonction unique qui jugeait le recul à la passe et à la clôture, retirée : `test_une_fonction_pour_la_passe_et_la_cloture`.

**Les 6 tests dont une assertion change :**

- `test_une_section_anglaise_se_lit_de_meme` — un bloquant lu n'est plus une cause et sa marque, mais sa cause seule.
- `test_la_premiere_passe_garde_le_dossier_d_avant_et_s_ecrit_a_la_fin_du_lot` — une passe lue ne porte plus de recul.
- `test_la_meme_passe_se_reconnait_sur_un_arbre_sale` (des changements non commités) — une deuxième passe sans recul n'est plus refusée : elle s'écrit, et la commande le dit.
- `test_une_ligne_de_bloquant_mal_ecrite_est_refusee_a_tout_statut` — le refus reste ; son message ne cite plus les règles retirées, mais la forme attendue, une ligne `- Bloquant : <sa cause>` par bloquant.
- `test_l_historique_se_lit_d_une_session_neuve` — le bloquant est sa cause seule, et le dossier ne redonne plus les causes d'avant (inchangé sur ce point avec `garder-le-rappel`).
- `test_la_passe_ecrite_se_commite_et_le_dossier_se_produit_sur_la_branche_d_integration` (dans `tests/test_skills.py`) — il n'attend plus dans le skill de revue la phrase sur la clôture refusée, qui en sort.

**Les 8 tests ajustés sans assertion changée** : des valeurs d'exemple qu'ils partagent (une fonction d'aide qui écrivait un recul, des demandes d'exemple retirées) changent, et le contrôle les signale : `test_la_commande_ecrit_la_passe_et_le_dit_sur_sa_sortie_d_erreur` (déplacé tel quel dans un autre groupe de tests), `test_la_meme_passe_se_redonne_sans_s_ecrire_deux_fois`, `test_un_projet_anglais_ecrit_la_section_dans_sa_langue`, `test_une_ligne_de_bloquant_ecrite_autrement_se_releve_avec_sa_ligne`, `test_une_ligne_de_bloquant_sans_puce_se_releve_aussi`, `test_une_passe_garde_l_empreinte_de_l_arbre_de_travail_qu_elle_a_relu`, `test_une_section_qui_existe_recoit_la_passe_a_sa_fin_avant_la_section_suivante`, `test_une_section_qui_n_est_pas_la_derniere_finit_au_titre_suivant`.

## Éléments cités

Chaque renvoi porte le numéro de l'entrée (D- une décision humaine, ADR- une décision d'architecture, T- une tâche, B- un besoin, L- un lot), suivi de l'empreinte de la version lue.

- D-0144@3ca5d3d1 — votre décision du 20 novembre : retirer l'obligation du recul, garder l'historique des passes et le tri des constats.
- L-0006@7bbb0f14 — le lot en cours, sur les skills et leurs copies protégées (la copie qu'un projet reçoit, qui ne change qu'avec votre accord).
- ADR-0084@df557d83 — la décision du 16 novembre qui avait posé le recul ; une décision nouvelle, écrite par l'agent sur votre validation, la remplace.
- B-0309@3c791fc4 — le besoin : le recul n'a jamais arrêté un lot ; il se ferme avec le commit de ces tests.

## Où regarder

- [Les tests d'aujourd'hui](https://github.com/theodubus/memory/blob/6ba36d7c555d346323193a13774bca038f5a7017/tests/test_historique_des_revues.py) : ceux qu'on supprimerait, chacun dans son groupe ci-dessus.
- [Votre décision du 20 novembre](https://github.com/theodubus/memory/blob/6ba36d7c555d346323193a13774bca038f5a7017/memory/requests/D-0144-retirer-l-obligation-du-recul-au-lot-l-0006-garder.md) : ce qui est retiré, ce qui est gardé.

## Options

- **Valider.** Les tests nommés se suppriment ou s'ajustent, et se commitent avec votre réponse. Risque : un test supprimé qui garderait autre chose que le recul ; la revue du lot le vérifie, et un comportement découvert sans test en reçoit un nouveau dans le lot, ce qu'aucune demande n'exige. Réversible : l'historique du dépôt garde chaque test.
- **Garder le rappel (`garder-le-rappel`).** Comme valider, mais le dossier d'une passe redonne encore au relecteur les bloquants des passes d'avant, sans lui demander de marque. Effort : quelques lignes, et `test_l_historique_se_lit_d_une_session_neuve` garde son assertion d'avant sur ce point. Coût : un dossier un peu plus long à partir de la deuxième passe.
- **Refuser.** Les tests restent, et le retrait du recul doit se défaire. Réversible.

## Conséquences

Si vous validez, ou gardez le rappel : les tests se commitent avec votre réponse, B-0309 se ferme, et le lot continue. Si vous refusez : le commit du retrait se retire du lot, et le recul reste exigé. Sans réponse : les tests attendent dans le conteneur ; le lot avance sur ses autres tâches, mais ne se livre pas sans eux.

## Recommandation

Valider. Vérifié : avec ces changements, la suite complète passe, et les six tests nouveaux échouent sur le code d'avant ; chaque test supprimé porte sur l'une des règles retirées, ci-dessus. Supposé : que le rappel des causes d'avant ne sert plus au relecteur sans les marques.

## Réponses possibles

- `valider` — les tests nommés se suppriment ou s'ajustent, et se commitent avec votre réponse.
- `garder-le-rappel` — de même, et le dossier d'une passe redonne au relecteur les bloquants d'avant.
- `refuser` — les tests restent ; le retrait du recul se retire du lot.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
