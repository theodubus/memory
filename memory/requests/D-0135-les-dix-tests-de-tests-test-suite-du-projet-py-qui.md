<!-- socle: couche=demandes zone=publique -->
# D-0135 — Les dix tests de tests/test_suite_du_projet.py qui lisaient l'ancien rendu de socle roadmap lisent celui que Théo a validé (D-0127) : changer leurs valeurs attendues ?

> date : 2026-11-18 · forme : séance

## Question posée

Valides-tu le changement des valeurs attendues de ces dix tests de tests/test_suite_du_projet.py ? Ils lisent mot pour mot l'ancien rendu de socle roadmap, et liront celui que tu as validé (D-0127). Aucun n'est supprimé ni affaibli : chacun lit le même fait dans le nouveau rendu. Deux choses disparaissent parce que le format validé ne les a pas : la marque « le prochain » d'un jalon, et les comptes par état dans le compact.

1. test_le_format_compact_une_ligne_par_jalon_et_par_lot_le_lot_en_cours_marque — avant : l'ancien compact, avec son en-tête, « jalons, dans leur ordre : » et « ▶ L-0001 — L'entrée L-0001 : 1 tâche(s) close(s) sur 2 · 1 en cours » ; après : sept lignes alignées, de « JA-0001  L'entrée JA-0001   0/2 besoins clos » et « ▶ L-0001  L'entrée L-0001  1/2  en cours » jusqu'à « Hors lot : … » et « Ensuite : B-0004, B-0005, B-0006 et 1 autre ».
2. test_le_format_compact_par_besoin — avant : « B-0001 — L'entrée B-0001 : 1 tâche(s) close(s) sur 2 — lot(s) : L-0001 » ; après : les besoins rangés sous leur jalon et alignés, « B-0001  L'entrée B-0001  1/2  L-0001 ».
3. test_le_format_detaille_par_lot — avant : des titres « #### ▶ L-0001 — … — en cours » et des listes « - T-0001 — … · priorité haute · en cours » ; après : « **1. L-0001 — L'entrée L-0001** · en cours · 1/2 » et des lignes de tableau « | ▶ | T-0001 | B-0001 ↑ | L'entrée T-0001 | » ; ce qui est hors des lots passe aussi en tableaux.
4. test_le_format_detaille_suit_le_lot_en_cours_et_les_deux_suivants_all_les_suit_tous — avant : trois titres #### puis « #### Les lots suivants » ; après : trois lignes numérotées, le quatrième lot en une ligne (« - **4.** L-0004 — L'entrée L-0004 · 0/1 ») et « (--all pour tout le détail) ».
5. test_le_format_detaille_par_besoin_chaque_tache_avec_son_lot — avant : des titres « #### B-0001 … — lot(s) : L-0001 » et des listes ; après : « **B-0001 — L'entrée B-0001** · 1/2 · L-0001 » et un tableau avec le lot de chaque tâche, « — » quand elle n'en a pas.
6. test_le_format_detaille_donne_le_lien_de_chaque_demande_et_de_ce_qui_revient_a_l_humain — avant : le lien sur une ligne de liste ; après : le lien sur l'identifiant, dans une ligne de tableau (« | ⏳ | [D-0001], avec son lien | Une demande | »).
7. test_en_anglais — avant : « 1 task(s) closed out of 2 · 1 in progress » ; après : « 0/2 needs closed », « in progress », « waits on D-0001 », toujours sans mot français.
8. test_socle_roadmap_et_ses_options — ses cinq lignes, lues par la commande et ses options, dans la forme nouvelle (« ▶ L-0001  Le premier lot  0/1  en cours », « **B-0001 — Ajouter triple** · 0/1 · L-0001 »…).
9. test_by_prend_batch_ou_need_et_batch_par_defaut_sans_synonyme — avant : « #### ▶ L-0001 — Le premier lot — en cours » ; après : « **1. L-0001 — Le premier lot** · en cours · 0/1 ».
10. test_la_ci_posee_ecrit_le_format_detaille_dans_le_resume_de_son_execution — la ligne du lot et celle de sa tâche dans le résumé que la CI écrit, au même format que le test 9 (« | ○ | T-0001 | B-0001 | Écrire triple | »).
