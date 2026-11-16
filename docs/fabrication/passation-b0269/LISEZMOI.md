# Passation du lot B-0269, le 16 novembre

La session du 16 novembre (J-2026-11-16-T) s'est arrêtée sur la limite
d'usage : la semaine à 89 %, la fenêtre de cinq heures à 94 %. Le travail
de B-0265 est fait, mais pas relu. Il est rangé ici, en deux correctifs,
pour qu'une session neuve le reprenne du dépôt seul. Ce dossier se retire
dans le commit qui les intègre.

## Ce qu'il contient

- b0265-structure.patch.gz : le commit de B-0265, fait par un sous-agent sur
  le modèle de la session, à partir de 42c246b. Il livre les points 1 à 9
  de D-0123, sauf la seconde moitié du point 8 :
  - une ADR nouvelle, la spécification, avec `validation : D-0123` ;
  - les préfixes `T-`, `L-` et `JA-` dans `engine/socle/memory.py` ;
  - l'ancien numéro (`ancien`), résolu par `socle show` et par les
    contrôles des références ;
  - le contrôle nouveau `memoire.formes`, et ses 13 défauts injectés ;
  - les commandes `socle new need|task|batch|milestone` ;
  - la migration, un module nouveau que la mise à jour de l'installeur
    appelle, appliquée à ce dépôt : 13 lots deviennent L-0001 à L-0013,
    5 jalons JA-0001 à JA-0005, avec 48 tâches pour les 8 lots ouverts ;
  - les textes en français et en anglais, les notes de version
    (`2026-11-16-f`), le point 12 du prompt de chess ;
  - 20 tests nouveaux, qui échouent sur le commit parent ;
  - une entrée de journal, la suivante du 16 novembre.
- b0265-tests-attendus.patch.gz : les 20 tests existants dont la nouvelle
  structure change la valeur attendue. `tests.attendus` refuse de les
  commiter sans une demande validée qui les nomme. Dans le sous-agent,
  `verify --fast` passait, la suite entière comprise, sauf
  `tests.attendus`.

## La reprise, dans l'ordre

1. `gunzip -c` puis `git am -3` du premier correctif, puis `git apply`
   du second, qui reste dans l'arbre. Ils sont compressés : le contrôle
   `memoire.prive` lirait sinon, dans un test qu'ils portent, l'identifiant
   privé d'exemple que le dossier des tests a le droit d'écrire. Le chantier actif peut entrer en conflit : il
   garde la version du correctif, ses citations récrites (B-0269 devient
   L-0013, B-0224 devient JA-0005).
2. La revue du lot (skill `socle-review`), contre le « Fait quand » de
   B-0265 et contre D-0123. Elle juge aussi les sept choix que la
   spécification ne tranchait pas, écrits dans l'ADR du correctif. Parmi
   eux : la tâche de migration renvoie aux critères de son besoin au lieu
   de les copier, et un jalon attend tous les besoins de ses lots, clos
   compris (JA-0005 en attend 57).
3. La demande qui nomme les tests ci-dessous, relue à froid, poussée, son
   lien donné à Théo. Elle part après la revue, si la revue change la
   liste. Elle cite aussi les copies protégées des skills `socle-batch`,
   `socle-review` et `socle-resume` (sous `.claude/skills/`) à remettre
   depuis leurs gabarits : celle de `socle-batch` dit encore
   `socle new backlog`, une commande que la structure retire.
4. À la réponse de Théo : le commit des tests et de la réponse, le push,
   la CI, la fusion. Puis B-0263 (D-0124 validée), puis B-0270.

Restent au backlog, dans le correctif : T-0049, la seconde moitié du
point 8 (découper les besoins, récrire leurs critères, refaire les lots
de JA-0005), et T-0050, les textes que des tests lisent mot pour mot et
qui disent encore « sujet » (le dossier de `socle review`, les questions
de départ, la règle du hook dans le guide, qui reprend les mots de
D-0120 : à demander à Théo).

## Les tests à nommer dans la demande

Fichier par fichier, ce qui change et pourquoi.

- tests/test_cli.py, `test_new_request_questions_pose_des_questions_de_cadrage` :
  `type="backlog"` devient `type="need"`, la valeur « backlog »
  n'existant plus.
- tests/test_renommages.py, `test_l_etat_l_identifiant_l_empreinte_et_l_archivage` :
  `cmd_next_id(type="backlog")` devient `type="need"`, toujours B-0002.
- tests/test_format_3.py, `test_un_sujet_clos_se_range_avec_les_clos` et
  `test_un_sujet_rouvert_revient_parmi_les_ouverts` : « sujets ouverts »,
  « sujet(s) rangé(s) » et « sujets clos » deviennent « entrées
  ouvertes », « entrée(s) rangée(s) » et « entrées closes » (le
  vocabulaire, point 9).
- tests/test_hooks.py, `test_exiger_recap_rappelle_l_ordre_du_backlog` :
  « prochain jalon : B-0002 … ; reste : B-0001 » et « prêt : B-0001 »
  deviennent « prochain jalon : JA-0002 … ; besoins ouverts : B-0001 »
  et « tâche prête : T-0001 ».
- tests/test_demarrage.py,
  `test_les_listes_de_l_etat_derive_sont_plafonnees_et_ses_lignes_bornees` :
  la fixture passe de 21 besoins à 21 tâches du besoin B-0100. « prêt :
  B-0003 » devient « tâche prête : T-0003 », « autre(s) prêt(s) »
  devient « autre(s) tâche(s) prête(s) ».
- tests/test_ordre.py, le fichier entier, sous les quatre formes : sa
  fonction `sujet()` perd `forme`, et sa version actuelle échoue contre
  le moteur nouveau. Quatorze tests y changent une valeur attendue :
  - `test_ordre_donne_les_prets_le_prochain_jalon_et_ce_qui_lui_reste` ;
  - `test_un_jalon_dont_tout_est_clos_se_dit_a_clore` ;
  - `test_au_dela_du_plafond_les_prets_se_comptent` ;
  - `test_un_jalon_clos_sur_une_tache_ouverte_est_refuse` ;
  - `test_les_prets_se_rangent_par_priorite_et_les_basses_restent_a_part` ;
  - `test_un_sujet_qui_attend_une_demande_est_pret_a_sa_reponse` ;
  - `test_un_jalon_qui_attend_un_sujet_qui_attend_une_demande` ;
  - `test_l_etat_dit_ce_qu_attendent_ses_sujets_un_sujet_ou_une_demande` ;
  - `test_les_criteres_se_lisent_dans_leur_section` ;
  - `test_un_sujet_fait_avec_un_critere_non_coche_est_refuse` ;
  - `test_est_lot_se_lit_dans_les_deux_langues` ;
  - `test_la_memoire_relie_le_lot_a_ses_sujets_et_l_etat_montre_le_prochain` ;
  - `test_un_lot_dont_tout_est_clos_se_dit_a_clore` ;
  - `test_le_lot_en_cours_passe_devant_et_un_lot_fait_avant_ses_sujets_est_refuse`.

  Ce qui y change : les identifiants (B- devient JA-, L- ou T- selon la
  forme), « prêt » qui devient « tâche prête », « reste : » qui devient
  « besoins ouverts : », « 3 clos sur 3 » qui devient « 3 close(s) sur
  3 », et « sujet(s) attendent un sujet ouvert » qui devient « entrée(s)
  attendent une entrée ouverte du backlog ». Le second correctif donne
  chaque ligne.
