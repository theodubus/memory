<!-- socle: couche=demandes zone=publique -->
# D-0051 — Valider le plan de retrait de BMAD : ce qui part, les tests supprimés, la documentation, la mémoire et les tâches qui reviennent

> date : 2026-10-30 · lu : decisions@828266d1 · lu : backlog@aa365018

## Décision demandée

Valider le plan complet de retrait de BMAD Method du socle : ce qui part du
moteur, les tests supprimés (nommés plus bas), la documentation, la
mémoire, et les tâches qui reviennent, avant de le lancer.

## Contexte

Théo a validé le principe du retrait (D-0050@def47d1d) : le pilote a montré que les
workflows de planification de BMAD sont des coachs par conception, qu'il
ajoute une seconde mémoire à côté de celle du socle, et que sa répartition
du travail entre agents fait tourner tous les sous-agents au modèle de la
session. Il demande de fixer d'abord tout ce que le retrait implique.

**Ce que BMAD avait fait écarter.** Aucune partie existante du socle n'a
été retirée pour BMAD. Deux choses n'ont pas été faites parce que BMAD les
faisait : la planification, confiée à BMAD par ADR-0032 (« Planifier
revient à BMAD »), et le mode multi-agent, B-0055, abandonné le 19
octobre parce que BMAD répartissait déjà le travail. B-0071, le choix du
modèle et de l'effort par tâche, est resté ouvert en se définissant par
ce que BMAD ne fait pas. Les trois autres sujets abandonnés du backlog le
sont pour d'autres raisons.

**1. Ce qui part du moteur.**
- Les modules `bmad.py` et `checks_bmad.py`, et leurs trois contrôles :
  `bmad.reports`, `bmad.approbation`, `bmad.lectures`.
- Leurs quatre défauts injectés : `report-bmad-hors-backlog`,
  `spec-approuvee-sans-trace`, `intention-changee-apres-approbation`,
  `decision-bmad-lue-perimee`.
- Dans l'installeur : `--with-bmad`, `--bmad-version`, l'installation de
  BMAD par npx, la personnalisation de ses skills, et la reconnaissance de
  BMAD comme outil tiers.
- Dans la ligne de commande : `socle bmad-import`, la lecture d'une
  décision `AD-n` par `socle show`, l'empreinte de l'intention d'une spec
  de BMAD dans `socle decision --about`, qui garde le chemin seul.
- Dans l'état : la ligne de BMAD ; les gabarits `bmad-custom` ; les
  messages et mots-clés qui ne servent qu'à lui.

**2. Ce qui reste.** La déclaration de fichiers tiers (ADR-0031), ses
contrôles, ses deux défauts et la fonction qui écrit cette liste : elle
sert à tout outil. Les décisions prises en séance (`socle decision`) et
leur défaut `decision-sans-relais` : elles sont au socle, pas à BMAD.

**3. Les tests.** Supprimés, 39 :
- dans le fichier des tests de BMAD, 33 tests :
  `test_en_tete_lit_les_cles_sans_guillemets_ni_commentaires`,
  `test_spec_reconnait_une_spec_et_son_intention_figee`,
  `test_l_empreinte_de_l_intention_ignore_les_espaces_pas_le_texte`,
  `test_une_spec_courte_ou_en_brouillon_n_est_pas_approuvee`,
  `test_reports_lit_chaque_entree`, `test_sprint_lit_les_statuts`,
  `test_dossiers_suit_la_configuration_de_bmad`,
  `test_specs_trouve_les_specs_du_dossier_d_implementation`,
  `test_un_report_hors_du_backlog_fait_echouer_le_controle`,
  `test_importer_fait_entrer_chaque_report_une_fois`,
  `test_la_commande_dit_ce_qu_elle_pose`,
  `test_reports_a_entrer_ignore_un_doublon_et_un_projet_sans_bmad`,
  `test_l_etat_montre_les_specs_le_sprint_et_les_reports`,
  `test_sans_bmad_l_etat_n_en_dit_rien`,
  `test_une_spec_approuvee_sans_trace_est_refusee`,
  `test_une_spec_approuvee_et_consignee_passe`,
  `test_une_intention_changee_apres_l_approbation_est_refusee`,
  `test_une_spec_courte_n_a_pas_besoin_d_approbation`,
  `test_la_commande_cmd_decision_cite_l_intention_de_la_spec`,
  `test_personnalisations_bmad_lit_la_table_de_chaque_skill`,
  `test_l_installeur_pose_la_personnalisation_dans_la_langue_du_projet`,
  `test_poser_bmad_garde_une_personnalisation_du_projet`,
  `test_poser_bmad_regenere_ce_qu_il_a_pose_et_parle_anglais`,
  `test_l_etat_signale_un_skill_sans_personnalisation`,
  `test_commande_bmad_suit_la_langue_et_la_version`,
  `test_une_commande_installe_bmad_puis_le_socle_qui_le_reconnait`,
  `test_installer_bmad_garde_un_bmad_deja_la`,
  `test_sans_npx_l_installation_s_arrete_avec_le_remede`,
  `test_un_echec_de_bmad_arrete_l_installation`,
  `test_decisions_architecture_lit_chaque_ad_hors_des_blocs_de_code`,
  `test_l_etat_et_show_donnent_les_decisions`,
  `test_une_citation_a_jour_passe`,
  `test_une_citation_perimee_ou_inconnue_est_refusee` ;
- dans le fichier des tests des fichiers tiers, 6 tests :
  `test_outils_tiers_reconnait_bmad_par_son_dossier`,
  `test_outils_tiers_reconnait_bmad_par_ses_skills`,
  `test_outils_tiers_ne_voit_rien_sans_outil`,
  `test_une_installation_avec_bmad_declare_ses_fichiers_et_passe`,
  `test_garde_fous_initiaux_laissent_l_outil_hors_du_cliquet_de_mutation`,
  `test_une_mise_a_jour_declare_un_outil_venu_depuis_et_le_dit_a_approuver`.

Déplacés tels quels dans les tests des demandes, parce qu'ils jugent les
décisions en séance : `test_ecrire_seance_pose_la_question_et_sa_reponse`,
`test_une_seance_relayee_sans_citation_est_refusee`,
`test_une_seance_sans_reponse_est_hors_contrat`,
`test_le_hook_refuse_une_decision_que_l_agent_ne_relaie_pas`.

**4. La documentation.** Le README (sa section sur BMAD, l'option
`--with-bmad`, Node et uv dans les prérequis) ; le guide, en français et
en anglais (sa section sur BMAD, l'exemple d'une spec à approuver) ; le
format de la mémoire (les reports de BMAD au backlog, ses décisions
`AD-n`) ; l'architecture de l'atelier (les lignes des modules de BMAD, de
l'installeur, et deux exigences) ; les gabarits des instructions (la spec
de BMAD, le préfixe `bmad-` des skills) ; les instructions de ce dépôt ;
le commentaire des garde-fous qui nomme BMAD.

**5. La mémoire.** Une ADR nouvelle, le retrait, qui remplace ADR-0032.
Les faits F-0022, F-0023 et F-0024, qui décrivent l'intégration de BMAD,
s'archivent au journal, comme le format le permet. B-0099, le profil de
BMAD, est abandonné. B-0071 se fond dans B-0055, rouvert.

**6. Les tâches qui reviennent.**
- **La planification, à la manière du socle** (sujet nouveau) : depuis le
  cadrage, une spécification et une architecture courtes dans la
  documentation du projet ; chaque choix en ADR, chaque question ouverte
  en demande, chaque tâche en sujet du backlog avec ses critères
  d'acceptation ; l'approbation d'une spécification consignée en séance ;
  un skill du socle qui décrit la procédure, au ton formel et technique.
- **La répartition entre agents** (B-0055 rouvert, avec B-0071) : un agent
  maître qui confie chaque tâche à un sous-agent dans son worktree, avec
  le seul contexte de la tâche, en choisissant le modèle et l'effort ; des
  relecteurs sans contexte ; les contrôles du socle sur le travail rendu
  avant sa reprise ; mesuré au banc.
- **Le pilote** : un dépôt neuf, installé sans BMAD, avec le cadrage ; la
  planification s'y fait d'abord à la main, sous la consigne de ton de
  Théo, puis avec le skill.

**L'ordre.** Le retrait (points 1 à 5), dans une PR ; puis le pilote
neuf ; puis la planification ; puis la répartition entre agents, quand le
pilote écrira du code.

## Éléments cités

- D-0050@def47d1d — la décision en séance où Théo valide le principe du retrait.
- ADR-0031@ded211d6 — la déclaration des fichiers d'un outil tiers, que
  tous les contrôles ignorent : elle reste.
- ADR-0032@294aa890 — le mariage du socle et de BMAD : un propriétaire par
  nature d'information, la planification à BMAD ; remplacée.
- ADR-0034@84d4c527 — les skills du socle et ceux du projet : la règle du
  préfixe `bmad-` en disparaît.
- B-0055@ba80a4b6 — le mode multi-agent, abandonné le 19 octobre parce que
  BMAD répartissait le travail : rouvert.
- B-0071@a3183a30 — le choix du modèle et de l'effort par tâche : fondu
  dans B-0055.
- B-0099@ea38280e — le profil de BMAD perdu en session cloud : abandonné.
- B-0095@9f5a38aa — l'adaptateur Dart du pilote : inchangé.
- F-0022@160bec31 — les quatre contrôles qui refusaient les fichiers de
  BMAD avant la déclaration des fichiers tiers : archivé.
- F-0023@b8b44547 — la personnalisation de BMAD qui portait la mémoire du
  socle dans ses workflows : archivé.
- F-0024@e64e3740 — la session réelle sous le mariage, sans refus :
  archivé.

## Où regarder

- [les tests de BMAD](https://github.com/theodubus/memory/blob/27eee5a888183bfd1159ce05d3da0891a08131d0/tests/test_bmad.py) :
  les 33 tests supprimés et les 4 déplacés.
- [les tests des fichiers tiers](https://github.com/theodubus/memory/blob/27eee5a888183bfd1159ce05d3da0891a08131d0/tests/test_tiers.py) :
  les 6 tests supprimés, et ceux qui restent sur la déclaration générique.
- [les contrôles de BMAD](https://github.com/theodubus/memory/blob/27eee5a888183bfd1159ce05d3da0891a08131d0/engine/socle/checks_bmad.py) :
  ce qui part.
- [le README](https://github.com/theodubus/memory/blob/27eee5a888183bfd1159ce05d3da0891a08131d0/README.md),
  sa section « Avec BMAD Method » : ce qui disparaît de la documentation.
- [ADR-0032](https://github.com/theodubus/memory/blob/27eee5a888183bfd1159ce05d3da0891a08131d0/memory/decisions/ADR-0032-le-socle-et-bmad-maries-un-proprietaire-par-nature.md) :
  le mariage que le retrait défait.

## Options

- **Valider le plan tel quel** : je fais le retrait (points 1 à 5) dans une
  PR, j'ouvre le sujet de la planification et je rouvre B-0055. Effort :
  une demi-journée pour le retrait. Risque faible : chaque contrôle qui
  part emporte son défaut injecté, l'auto-test le vérifie. Réversible.
- **Valider avec des changements** : le plan modifié selon votre réponse,
  puis réécrit en une demande qui remplace celle-ci.
- **Refuser** : BMAD reste ; rien ne change.

## Conséquences

- Si Théo valide : le retrait se fait dans une PR, les 39 tests nommés
  partent, les 4 tests de séance sont déplacés tels quels, et les deux
  tâches reviennent au backlog ; le pilote repart d'un dépôt neuf.
- S'il demande des changements : la demande se réécrit.
- S'il refuse : BMAD reste dans le socle, avec ses défauts relevés.
- Sans réponse : rien ne bouge ; le pilote attend.

## Recommandation

Valider le plan tel quel.

Vérifié : aucune partie existante du socle n'a été retirée pour BMAD ;
B-0055 est le seul sujet abandonné à cause de lui ; les 37 tests de son
fichier sont relevés un à un, dont 4 qui jugent les décisions en séance ;
6 tests des fichiers tiers dépendent de la reconnaissance de BMAD.

Supposé : qu'aucun autre test ne dépende de BMAD sans le nommer ; la suite
entière le dira au retrait.

## Réponses possibles

- `valider` — le plan tel quel : le retrait dans une PR, les 39 tests nommés supprimés, les 4 tests de séance déplacés, les tâches au backlog.
- `modifier` — le plan change selon la réponse, et se réécrit en une demande qui remplace celle-ci.
- `refuser` — BMAD reste dans le socle.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
