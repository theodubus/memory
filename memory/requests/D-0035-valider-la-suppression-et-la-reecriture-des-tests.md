<!-- socle: couche=demandes zone=publique -->
# D-0035 — Valider la suppression et la réécriture des tests que demande le retrait du code de compatibilité (D-0033)

> date : 2026-10-20 · lu : decisions@2a93e7ab

## Décision demandée

Valider que je supprime, raccourcis ou réécris les tests nommés plus bas,
comme le retrait du code de compatibilité que tu as choisi le demande.

## Contexte

Tu as répondu « Et oui tout retirer » à la demande sur le code de
compatibilité : j'ai consigné la réponse `tout`. Le retrait est fait dans
mon arbre de travail, pas encore commité : le moteur ne lit plus que le
format courant de la mémoire, les anciens noms des commandes sont partis,
et les données des tests n'ont plus de vocabulaire des échecs. Toute la
suite de tests et l'auto-test passent.

Mais le contrôle qui protège les tests (`tests.attendus`, le point 2 de la
politique) ne reconnaît comme validation qu'une demande répondue
`valider` qui nomme chaque test. Celle-ci offrait deux réponses positives
(`tout`, `compatibilite-seule`) et `refuser`, aucune ne s'appelait
`valider` : ta réponse ne débloque donc rien, et c'est une faute de
rédaction de la demande. Je ne contourne pas le contrôle ; je te demande de valider la
même chose, test par test. Le défaut de l'outil (une demande à plusieurs
réponses positives ne peut rien valider) va au backlog.

Ce qui change, test par test. Supprimés, parce qu'ils ne prouvaient que la
compatibilité :

- `tests/test_formats.py` entier : `test_traduire_un_chemin_dans_les_deux_sens`,
  `test_un_chemin_qui_mele_les_deux_formats`, `test_le_miroir_prive`,
  `test_la_memoire_se_reconnait_sous_ses_deux_noms`,
  `test_une_reponse_a_cote_de_sa_demande`,
  `test_les_garde_fous_se_traduisent_cle_et_valeur`,
  `test_une_ancre_ecrite_avant_la_migration`, `test_les_chemins_d_un_texte`,
  `test_un_projet_neuf_est_au_format_3`, `test_un_projet_d_avant_se_lit_au_format_1`,
  `test_la_migration_renomme_et_la_ci_lit_la_base_sous_les_noms_de_la_tete`,
  `test_un_fichier_protege_deplace_par_la_migration_est_juge_sous_son_nom_nouveau`,
  `test_la_migration_garde_la_memoire_pas_encore_commitee`,
  `test_une_validation_d_avant_la_migration_n_est_pas_nouvelle`,
  `test_l_ancien_chemin_d_une_entree_gelee_reste_valide` ;
- `tests/test_format_3.py` : `test_un_fichier_par_sujet_sans_rien_perdre`,
  `test_relancee_elle_ne_fait_rien`, `test_la_memoire_migree_passe_les_controles`,
  `test_un_lien_vers_un_sujet_qui_n_existe_pas_reste_mort`,
  `test_la_bascule_d_un_sujet_a_sous_titres_juste_apres_la_migration`,
  `test_la_mise_a_jour_range_un_projet_existant`,
  `test_la_mise_a_jour_d_un_backlog_vide`, `test_un_sujet_de_plus_au_format_2` ;
- `tests/test_renommages.py` : `test_le_dossier_du_moteur_se_lit_a_sa_cible`,
  `test_la_commande_son_action_et_ses_options_sous_leur_nom_anglais`,
  `test_une_commande_de_l_humain_l_est_sous_ses_deux_noms` (remplacé par un
  test des seuls noms anglais), `test_le_guide_sous_ses_deux_noms` ;
- `tests/test_initialisation.py` : `test_les_migrations_s_appliquent_dans_l_ordre` ;
- `tests/test_lectures.py` : `test_un_sujet_archive_garde_sa_lecture`,
  `test_un_sujet_archive_garde_ses_sous_titres_et_son_ancre`,
  `test_un_sujet_cree_puis_archive_sur_la_branche_garde_sa_lecture`,
  `test_une_lecture_inventee_reste_refusee_meme_archivee` ;
- `tests/test_langue.py` : `test_l_archive_du_backlog_est_en_anglais`.

Raccourcis, la partie de compatibilité seule : `test_le_verrou_note_le_format`
(le format se lit désormais dans la configuration, plus dans la migration)
et `test_trace_commune_aux_worktrees` (plus d'ancien emplacement de la
trace) ; `test_une_installation_au_format_3` perd la ligne qui lisait le
format détecté, qui n'existe plus.

Réécrits sur un projet au format courant, ce qu'ils prouvent ne change pas,
leurs chemins attendus suivent (un sujet du backlog dans son propre fichier
au lieu du fichier unique `memory/backlog.md`, les noms anglais au lieu
des noms français d'avant) : `test_un_sujet_basculé_garde_son_identifiant_et_perd_son_texte`,
`test_show_donne_l_empreinte`, `test_url_donne_le_permalien`,
`test_new_ecrit_dans_la_langue_du_projet`, `test_une_bascule_en_anglais`,
`test_le_hook_juge_la_recopie_comme_le_controle`, `test_les_fonctions`,
`test_cmd_answer_refuse_de_relayer_une_reponse_a_une_demande_non_lue`,
`test_couche_imposee_par_l_emplacement`, `test_zone_et_lisibilite`,
`test_le_hook_la_refuse_a_l_agent`, et `test_un_sujet_clos_se_range_avec_les_clos`,
qui dit désormais qu'un document qui lie un sujet doit suivre son
déplacement parmi les clos, comme pour tout fichier.

Les données tirées des échecs prennent un vocabulaire neutre, valeurs et
assertions équivalentes : `test_un_depot_que_le_projet_lie_est_connu` et
`test_un_depot_declare_passe` (un dépôt nommé « outil » au lieu de
« chess »), `test_metadonnees_et_commande_avec_virgule` et
`test_fait_barre_et_meta_sur_deux_lignes` (des lignes lues au lieu de
nœuds, une copie de tampons au lieu du copy-make),
`test_une_valeur_libre_ne_se_confond_pas` (des kilos au lieu d'Elo),
`test_tests_reconnus` et `test_assertion_par_aide` (un test Rust nommé
`produit_un` au lieu de `perft_un`), et les modules d'exemple du verdict
de mutation (`src/parse.rs`, `src/table.rs`, `src/score.rs` au lieu de
ceux d'un moteur d'échecs) dans `test_module_jamais_balaye_casse`,
`test_lecteur_inconnu_casse`, `test_un_module_a_mesurer_ne_casse_pas`,
`test_poser_ecrit_le_plafond_mesure`, `test_cmd_mutation_verdict_avec_poser`,
`test_poser_plafonds_ne_touche_que_les_modules_a_mesurer`,
`test_poser_les_autres_formes_de_cle`, `test_un_plafond_non_ecrit_est_dit`.

## Éléments cités

- D-0033@43487fd4 — la demande sur le code de compatibilité, à laquelle tu
  as répondu `tout` ; elle nommait déjà la plupart de ces tests.
- J-2026-10-20-S@5844ec0a — ton message, texte exact, avec « Et oui tout
  retirer ».
- ADR-0017@9e0e51eb — la décision qui veut qu'une valeur attendue ne change
  que sur une validation humaine ou une spécification écrite par toi.

## Où regarder

- [la demande D-0033](https://github.com/theodubus/memory/blob/3d1b1d77ae3999233c6705ec93eb31c369ecff60/memory/requests/D-0033-retirer-le-code-de-compatibilite-avec-les-versions.md) :
  vérifier que les tests ci-dessus sont ceux qu'elle annonçait, et que rien
  d'autre ne s'y ajoute que les cas dits ici.
- [les tests des formats](https://github.com/theodubus/memory/blob/3d1b1d77ae3999233c6705ec93eb31c369ecff60/tests/test_formats.py), [ceux du format 3](https://github.com/theodubus/memory/blob/3d1b1d77ae3999233c6705ec93eb31c369ecff60/tests/test_format_3.py)
  et [ceux des renommages](https://github.com/theodubus/memory/blob/3d1b1d77ae3999233c6705ec93eb31c369ecff60/tests/test_renommages.py), dans leur version
  poussée : ce qui en part. Les versions nouvelles ne sont pas poussées :
  elles ne peuvent l'être qu'après ta réponse.

## Options

- **Valider** : je commite et pousse le retrait avec ses tests, après
  `verify`, l'auto-test et la CI. Effort : quelques minutes. Risque faible :
  toute la suite passe déjà dans l'arbre. Réversible : un commit qui se
  défait.
- **Refuser** : je remets les tests et le code tels qu'ils sont poussés ;
  ta réponse à D-0033 reste sans effet. Effort : quelques minutes. Risque
  nul. Réversible.

## Conséquences

- Si tu valides : le retrait est commité et poussé, puis je te soumets le
  plan de la documentation.
- Si tu refuses : rien ne change dans le dépôt ; le code mort reste.
- Sans réponse : le retrait reste dans mon arbre de travail, non commité ;
  si la session se perd, il est à refaire (quelques heures). Je te soumets
  quand même le plan de la documentation, qui n'en dépend pas.

## Recommandation

Valider. Vérifié : la suite complète des tests et l'auto-test passent dans
l'arbre ; les seuls refus restants sont ceux du contrôle des tests, sur la
liste ci-dessus, et ceux de quelques fonctions modifiées que je dispenserai
nommément. Supposé : que la CI de GitHub juge comme ce conteneur.

## Réponses possibles

- `valider` — je commite et pousse le retrait avec ces tests.
- `refuser` — je remets tout tel que c'est poussé.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
