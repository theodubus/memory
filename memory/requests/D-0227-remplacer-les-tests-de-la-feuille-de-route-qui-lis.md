<!-- socle: couche=demandes zone=publique -->
# D-0227 — Remplacer les tests de la feuille de route qui lisent les formats compact et détaillé ou l'option --by par ceux de la forme unique

> date : 2026-11-27

## Décision demandée

Dans `tests/test_suite_du_projet.py` (les tests de « la suite du
projet », la feuille de route), supprimer les 22 tests qui lisent ses
formats compact et détaillé ou son option `--by`, en changer 5 et en
déplacer 1, au profit de 19 tests nouveaux de la forme unique que tu as
validée.

## Contexte

**Le projet.** Le socle est l'outil que ce dépôt, memory, fabrique et
que chess, ton projet de moteur d'échecs, reçoit à chaque mise à jour :
la mémoire, les contrôles et les hooks qui encadrent un agent de code.
Son backlog range le travail en besoins (`B-`), tâches (`T-`), lots de
tâches (`L-`) et jalons de besoins (`JA-`). Sa commande `socle roadmap`
en calcule la suite, ce qui vient ensuite, pour que l'humain pilote.

**Le chantier.** Le 26 novembre, tu as jugé la feuille de route
illisible sur ton téléphone : le format compact, une ligne en colonnes
par jalon et par lot, et le détaillé (`--format markdown`), un tableau de
tâches par lot sous une légende de huit symboles ; `--by need` les lisait
par besoin. Tu as décidé que la forme retenue remplacerait partout les
deux formats, puis validé la maquette A2-d : « Maintenant », les lots en
cours ; les jalons, ou étapes, en `X. [K/N] titre` (`K` besoins clos sur
`N`), alignés, seul le suivant déplié en ses besoins ; « Pour toi » ; la
réserve, les besoins d'aucun jalon, comptés. Ce matin, tu as demandé de
la faire maintenant, puis jugé le Markdown rendu illisible : la forme
est un texte aligné, chaque titre suivi de son identifiant, que
`--format markdown` met dans un bloc de code pour la conversation et la
CI. Le code est écrit, avec le guide, la ligne de l'état, `FORMAT.md` et
la note de version.

**La question.** La politique interdit à l'agent de supprimer un test ou
d'en changer une valeur attendue sans ta validation écrite qui le nomme.
Or 22 tests lisent un rendu qui disparaît, et 6 autres changent. Rien de
ce code n'est commité ni poussé avant ta réponse.

Valider, c'est aussi valider ce que la forme cesse de montrer, que la
spécification en déduit sans que tu l'aies tranché : la lecture par
besoin et l'option `--by` ; les lots à venir, au-delà des lots en cours
(le compact en montrait trois, sa « fenêtre ») ; le lien entre un lot et
la demande qu'il attend, la demande restant sous « Pour toi ». Le calcul
de la suite (l'ordre des lots et des jalons, l'avancement, l'alerte de
deux lots sans ordre entre eux) ne change pas : ses tests restent.
Chaque test supprimé, et ce qui le remplace :

- `test_le_format_compact_une_ligne_par_jalon_et_par_lot_le_lot_en_cours_marque`,
  `test_le_format_compact_aligne_en_colonnes_comme_l_exemple_valide` :
  `test_la_forme_comme_la_maquette_validee_dans_le_terminal`,
  `test_les_parties_dans_leur_ordre_et_l_alerte_d_une_entree_bloquee`,
  `test_les_crochets_ont_la_meme_largeur_et_les_titres_s_alignent_un_total_a_deux_chiffres_compris`.
- `test_le_format_detaille_par_lot`,
  `test_le_format_detaille_un_tableau_par_lot_comme_l_exemple_valide` :
  `test_le_bloc_de_code_porte_le_texte_du_terminal`.
- `test_le_format_compact_ne_nomme_aucune_demande`,
  `test_le_format_detaille_donne_le_lien_de_chaque_demande_et_de_ce_qui_revient_a_l_humain` :
  `test_aucun_rendu_ne_nomme_une_demande_par_son_identifiant` ; les liens
  partent avec le Markdown rendu.
- `test_le_format_detaille_suit_le_lot_en_cours_et_les_deux_suivants_all_les_suit_tous` :
  `test_seul_le_premier_jalon_est_deplie_all_les_deplie_tous` et
  `test_un_lot_en_cours_nomme_trois_taches_ouvertes_au_plus_puis_compte_les_autres`.
- `test_les_lots_d_aucun_jalon_sous_hors_des_jalons_a_leur_place_dans_l_ordre` :
  `test_le_travail_hors_jalon_est_sous_maintenant_et_nulle_part_ailleurs`.
- `test_un_lot_arrete_nomme_les_demandes_qu_il_attend_dans_le_detaille` :
  une entrée bloquée se dit sur une ligne « Attention : »
  (`test_les_parties_dans_leur_ordre_et_l_alerte_d_une_entree_bloquee`),
  et la demande qu'un lot attend, sous « Pour toi ».
- `test_chaque_tableau_markdown_est_bien_forme` :
  `test_ni_tableau_ni_legende_ni_ancien_format`.
- `test_un_backlog_sans_lot_ni_jalon` :
  `test_sans_lot_en_cours_la_premiere_tache_prete_sinon_rien_en_cours`.
- `test_en_anglais` : son rôle passe à
  `test_en_anglais_la_suite_ne_garde_aucun_mot_francais`, qui existait
  et change (plus bas).
- `test_le_format_compact_par_besoin`,
  `test_le_format_compact_par_besoin_une_ligne_alignee_par_besoin`,
  `test_le_format_detaille_par_besoin_chaque_tache_avec_son_lot`,
  `test_lu_par_besoin_chaque_besoin_a_le_tableau_de_ses_taches_et_le_lot_de_chacune`,
  `test_by_prend_batch_ou_need_et_batch_par_defaut_sans_synonyme` : la
  lecture par besoin et l'option `--by` disparaissent ;
  `test_l_option_by_et_les_anciens_formats_sont_refuses` vérifie qu'elles
  sont refusées.
- `test_les_lots_de_deux_jalons_qui_alternent_suivent_l_ordre_d_execution`,
  `test_la_fenetre_est_commune_a_tous_les_jalons_dans_le_compact`,
  `test_la_fenetre_est_commune_a_tous_les_jalons_dans_le_detaille` : la
  forme ne montre plus que les lots en cours, et ne découpe plus les lots
  en fenêtre ; l'ordre des lots reste vérifié par
  `test_l_ordre_d_execution_vient_des_apres_et_non_des_numeros`, inchangé.
- `test_la_ci_posee_ecrit_le_format_detaille_dans_le_resume_de_son_execution` :
  `test_la_ci_posee_ecrit_le_rendu_markdown_dans_le_resume_de_son_execution`.
- `test_le_guide_montre_les_deux_formats_et_une_note_de_version_le_dit` :
  `test_le_guide_montre_la_forme_et_une_note_de_version_le_dit`.

Les 6 autres tests nouveaux ne remplacent aucun test :
`test_les_trois_marques_d_un_besoin_dans_l_ordre_de_l_apres_du_jalon`,
`test_aucune_ligne_vide_de_pour_toi_ni_de_la_reserve`,
`test_une_ligne_longue_passe_a_la_suivante_sous_sa_colonne`,
`test_l_en_tete_nomme_le_projet_et_le_jour`,
`test_un_deux_points_entre_guillemets_ou_dans_du_code_ne_coupe_pas_le_titre`,
`test_format_md_ne_prend_plus_la_feuille_de_route_pour_exemple_de_consigne`.

Chaque test changé ou déplacé, et sa valeur avant et après :

- `test_un_besoin_pour_l_humain_ne_se_decoupe_pas` : le besoin pour
  l'humain se lisait sous « Pour l'humain » du format détaillé ; il se lit
  sous « Pour toi ».
- `test_deux_lots_qui_attendent_le_meme_lot_sans_ordre_entre_eux_sont_signales` :
  « !! ordre ambigu : … » devient « Attention : ordre ambigu : … ».
- `test_en_anglais_la_suite_ne_garde_aucun_mot_francais` : il lisait les
  deux anciens formats ; il lit les deux rendus.
- `test_socle_roadmap_et_ses_options` : il lisait les lignes des deux
  formats et `--by need` ; il lit celles de la forme, et `--all`.
- `test_l_etat_a_une_ligne_qui_renvoie_a_la_commande` : « la suite :
  `python3 .socle/socle roadmap` (détaillée : `--format markdown`) »
  perd sa parenthèse.
- `test_un_titre_se_lit_jusqu_a_son_premier_deux_points_et_se_coupe_a_sa_colonne` :
  inchangé, il passe dans la classe des tests de la forme.

## Éléments cités

- B-0364@af10fb66 — le besoin : la feuille de route ne permet pas de piloter un projet.
- D-0212@6fc584aa — ta décision du 26 novembre : la forme retenue remplace les deux formats, partout.
- D-0214@982e025e — ta validation du 26 novembre de la maquette A2-d.
- D-0226@4430eeac — ta demande de ce matin de faire la feuille de route maintenant.
- D-0228@f958083b — ta remarque de ce matin : la feuille de route dans un bloc de texte, pas en Markdown rendu.
- L-0050@9340ee21 — le lot qui réunit les deux tâches de ce besoin.
- T-0207@7a227d44 — la tâche du rendu et de ses tests, que cette demande couvre.
- T-0208@f0f1baa6 — la tâche du guide, de l'état, de `FORMAT.md` et de la note de version.

## Où regarder

- [La spécification](https://github.com/theodubus/memory/blob/bce60489b991849bacf55919e086d40f61568b22/docs/fabrication/feuille-de-route-specification.md),
  section « Les tests » : ce que les tests nouveaux doivent prouver.
- [Les maquettes](https://github.com/theodubus/memory/blob/bce60489b991849bacf55919e086d40f61568b22/docs/fabrication/maquettes-feuille-de-route.md),
  section A2-d : celle que tu as validée.
- [Les tests d'aujourd'hui](https://github.com/theodubus/memory/blob/bce60489b991849bacf55919e086d40f61568b22/tests/test_suite_du_projet.py) :
  ceux que la liste supprime ou change.

Le texte sur le backlog de la maquette, un projet inventé, « Fou », tel
que le premier test nouveau le fixe ; la conversation et la CI le
reçoivent dans un bloc de code, comme ici :

```text
La suite de Fou — 27 novembre

Maintenant
 ▶ Finir l'adoption du socle (L-0001)
   reste : Passer CLAUDE.md dans
           AGENTS.md (T-0001)

Ensuite
1. [1/4] Embarquer le réseau N10 (JA-0001)
         ✓ Entraîner N10 sur les parties de
           novembre (B-0011)
         · Mesurer N10 contre N8 (B-0012)
         · Embarquer N10 dans le
           binaire (B-0013)
         · Situer le moteur sur la liste
           CCRL (B-0014)
2. [0/3] Régler la recherche par SPSA (JA-0002)
3. [0/2] Accélérer la recherche (JA-0003)
4. [0/3] Nouvelle architecture de
         réseau (JA-0004)

Pour toi : Copier les données d'entraînement sur
           un disque dur (B-0002)
En réserve : 12 besoins, dont 2 prioritaires
```

## Options

- **Valider** : les tests se remplacent comme la liste le dit, et le lot
  se livre aujourd'hui. Effort : aucun de ton côté. Risque : faible, la
  forme est celle que tu as validée. Réversible : un retour en arrière du
  commit les rend.
- **Refuser** : les anciens tests restent, et le nouveau rendu ne peut
  pas se livrer, puisqu'il les fait échouer : il faudrait garder un
  ancien format à côté de la forme, contre ta décision du 26 novembre.
  Le lot s'arrête. Réversible.

## Conséquences

- Si tu valides : l'agent commite le code et les tests, fait relire le
  lot par un relecteur sans contexte, puis ouvre la pull request et la
  fusionne une fois sa CI verte ; chess reçoit la forme à sa prochaine
  mise à jour.
- Si tu refuses : le travail reste sur la branche, non livré, et l'agent
  te demande quoi garder.
- Sans réponse : rien ne se livre ; le travail attend dans la session.
- Après la mise à jour de chess, revenir en arrière demanderait une
  mise à jour de plus.

## Recommandation

Valider. Vérifié : les 34 tests du fichier après le changement passent
(il en avait 37), la suite entière du dépôt aussi, et l'auto-test du
socle. Supposé : que la forme se lise sur ton
téléphone comme sur la maquette ; le rendu ci-dessus le laisse voir.

## Réponses possibles

- `valider` — les tests nommés se suppriment ou changent comme la liste le dit, et le lot se livre.
- `refuser` — les tests actuels restent, et le nouveau rendu ne se livre pas.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
