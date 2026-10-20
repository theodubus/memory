<!-- socle: couche=demandes zone=publique -->
# D-0033 — Retirer le code de compatibilité avec les versions antérieures du socle, et ses tests

> date : 2026-10-20 · lu : decisions@71682948

## Décision demandée

Valider que je retire du moteur tout le code qui ne sert qu'aux projets
installés par une version antérieure du socle, en supprimant les tests qui
ne portent que sur lui et en réécrivant au format courant ceux qui s'en
servent comme décor ; et, si tu le veux aussi, que je remplace le
vocabulaire des échecs dans les données des tests.

## Contexte

Tu as demandé si du code ne sert qu'à s'adapter aux versions antérieures
du socle, et dit que si oui, il ne sert à rien : aucun projet n'est équipé
du socle. L'inventaire, fait ce jour sur tout le dépôt, en trouve environ
600 lignes dans le moteur, 520 dans les tests et 75 dans la documentation :

- **les formats 1 et 2 de la mémoire** : le moteur lit encore les noms
  français d'avant (`memoire/`, `politique.toml`…), le backlog en un seul
  fichier (`memory/backlog.md`), et migre un projet de l'un à l'autre à la
  mise à jour (`migrations.py`, 211 lignes, et les tables de traduction de
  chemins de `config.py`) ; une base de CI à l'ancien format se relit sous
  les nouveaux noms ;
- **l'archivage du backlog dans le journal**, qui ne sert qu'au format 2 ;
- **les anciens noms des commandes et des options** (`aide`, `prive`,
  `relu`, `--oui`, `--depot`…), que la décision de passer en anglais ne
  gardait « qu'une version » ;
- l'ancien emplacement de la trace des hooks, et un dossier du moteur lu à
  travers un lien, qui n'existe plus.

Retirer ce code, c'est aussi retirer les tests qui le prouvent. La
politique (point 2) l'interdit sans une demande validée qui nomme les
tests : d'où celle-ci. Rien n'est retiré ; j'attends ta réponse.

Deux choses restent, parce qu'elles servent encore : la lecture des sujets
imbriqués dans le journal (ce dépôt en a), et le repli vers la section
`[code]` de l'adaptateur maintenu quand celui d'un projet n'en a pas,
parce que l'adaptateur de ce dépôt n'en a pas. Ce fichier est protégé :
seul toi peux y ajouter cette section ; je l'ai mis au backlog pour toi, et
le repli partira après. Deux demandes déjà répondues (D-0007, D-0009)
pointent vers une ancre d'avant le changement de titre ; elles sont gelées,
donc au lieu de garder la table des anciennes ancres, une couche gelée ne
verra plus ses ancres vérifiées, seulement ses fichiers.

## Éléments cités

- J-2026-10-19-A@2f14ec50 — ta consigne : pas de rétro-compatibilité avec
  une version antérieure du socle, « le projet est EN DEV ».
- J-2026-10-20-Q@d907f682 — ta question de ce jour, texte exact : « si oui
  ce code ne sert à rien », et celle sur les échecs.
- ADR-0018@61948166 — la décision qui a passé les chemins d'un projet en
  anglais (format 2), d'où les tables de traduction.
- ADR-0025@f97acbb5 — la décision du backlog en un fichier par sujet
  (format 3), d'où la migration du format 2.
- ADR-0027@a8288770 — la décision qui a mis les commandes en anglais, en
  gardant les anciens noms une version.
- D-0007@b1d5c5f6 — ta réponse sur la liste des termes privés, gelée, dont
  un lien vise une ancre d'avant le changement de titre.
- D-0009@52085783 — ta réponse sur les sessions du banc sur un vrai agent,
  gelée, avec un lien de même sorte.

## Où regarder

- [la migration entre formats](https://github.com/theodubus/memory/blob/3b51e3daa3ed6a7d953297c86108400be2fbe660/engine/socle/migrations.py) : le fichier
  qui part en entier.
- [les formats 1 et 2 et leurs traductions](https://github.com/theodubus/memory/blob/3b51e3daa3ed6a7d953297c86108400be2fbe660/engine/socle/config.py#L70-L154) :
  ce qui part de la configuration.
- [les anciens noms des commandes](https://github.com/theodubus/memory/blob/3b51e3daa3ed6a7d953297c86108400be2fbe660/engine/socle/commands.py#L183-L212) :
  ce qui part de la ligne de commande.
- [les tests des formats](https://github.com/theodubus/memory/blob/3b51e3daa3ed6a7d953297c86108400be2fbe660/tests/test_formats.py) : le fichier de tests
  qui part en entier.
- [les tests du format 3](https://github.com/theodubus/memory/blob/3b51e3daa3ed6a7d953297c86108400be2fbe660/tests/test_format_3.py) : ce qui en part
  (la migration) et ce qui reste (le rangement, l'installation).

À vérifier : que chaque test ci-dessous ne prouve que de la compatibilité.

Tests supprimés :

- `tests/test_formats.py`, en entier : `TestChemins` (8 tests),
  `TestDetection` (2), `TestMigration` (5) ;
- `tests/test_format_3.py` : `TestMigration` (4 tests),
  `TestRangement.test_la_bascule_d_un_sujet_a_sous_titres_juste_apres_la_migration`,
  `TestRangement.test_la_mise_a_jour_range_un_projet_existant`,
  `TestInstallation.test_la_mise_a_jour_d_un_backlog_vide`,
  `TestInstallation.test_un_sujet_de_plus_au_format_2` ;
- `tests/test_renommages.py` : `TestAnciensNoms` (3 tests),
  `TestMoteurParUnLien.test_le_dossier_du_moteur_se_lit_a_sa_cible` ;
- `tests/test_initialisation.py` :
  `TestMiseAJour.test_les_migrations_s_appliquent_dans_l_ordre` ;
- `tests/test_lectures.py` : `TestArchivage.test_un_sujet_archive_garde_sa_lecture`,
  `TestArchivage.test_un_sujet_archive_garde_ses_sous_titres_et_son_ancre`,
  `TestArchivage.test_un_sujet_cree_puis_archive_sur_la_branche_garde_sa_lecture`,
  `TestArchivage.test_une_lecture_inventee_reste_refusee_meme_archivee` ;
- `tests/test_langue.py` : `TestProjetAnglais.test_l_archive_du_backlog_est_en_anglais`.

Tests raccourcis, la partie de compatibilité seule :
`TestMiseAJour.test_le_verrou_note_le_format` (`tests/test_initialisation.py`)
et `TestCommandes.test_trace_commune_aux_worktrees` (`tests/test_cli.py`).

Tests réécrits sur un projet au format courant, sans changer ce qu'ils
prouvent : ils installent aujourd'hui un projet au format 2 (un seul
fichier de backlog, d'anciens noms), et leurs chemins attendus changent
avec. Ce sont `tests/test_bascule.py`, `tests/test_identifiants.py`,
`tests/test_approbation.py`, `tests/test_langue.py`,
`tests/test_lectures.py`, `tests/test_cli.py`, `tests/test_liens.py`,
`tests/test_hooks.py`, `tests/test_renommages.py`, `tests/test_garde.py`,
`tests/test_format_3.py`, et un test de `tests/test_memoire.py` et de
`tests/test_prive.py`.

Si tu choisis aussi les échecs : les données de `tests/test_refus_texte.py`
(Elo, nœuds), `tests/test_memoire.py` (« 70 452 nœuds »),
`tests/test_demandes.py` (le plafond de mutation d'un moteur d'échecs),
`tests/test_tests_lecture.py` (perft), `tests/test_mutation.py` (des
modules d'un moteur d'échecs) et `tests/test_autres_depots.py` (un dépôt
nommé chess) prennent un vocabulaire neutre, à valeurs et assertions
équivalentes. Ce sont des tests de l'outil : rien de tout cela n'est
copié dans un projet.

## Options

- **Tout** : je retire le code de compatibilité et ses tests, je réécris
  les décors, et je neutralise le vocabulaire des échecs dans les tests.
  Effort : une grosse demi-journée. Risque moyen : une quinzaine de
  fichiers de tests changent ; la suite complète, l'auto-test et la CI le
  jugent avant le push. Réversible : des commits qui se défont.
- **Compatibilité seule** : la même chose, sans toucher aux données des
  tests tirées des échecs. Même effort, à une heure près ; même risque.
- **Refuser** : rien ne change ; le code mort reste, et la documentation
  devra continuer de l'expliquer ou le taire. Effort nul ; risque faible,
  mais du code qu'on lit et entretient pour rien.

## Conséquences

- Si tu valides (tout, ou compatibilité seule) : je le fais avant la
  documentation, pour qu'elle ne décrive que ce qui reste ; je consigne ta
  réponse, et je te donne le lien du résultat.
- Si tu refuses : rien ne change, et la documentation se fait avec ce
  code, sans le décrire.
- Sans réponse : rien n'est retiré ; je commence la documentation par ce
  qui ne dépend pas de ce choix.

## Recommandation

Tout. Vérifié : le moteur ne crée plus de projet aux formats 1 ou 2 par la
ligne de commande (seuls des tests le font, par un paramètre interne) ; le
code nommé n'est appelé que par la mise à jour d'un projet d'avant, par
ces tests, ou pour lire ce dépôt-ci, qui n'en dépend plus que par les
points traités plus haut. Supposé : que la réécriture des décors ne fasse
apparaître aucun défaut caché par le format 2 ; si elle en montre un, il
ira au backlog.

## Réponses possibles

- `tout` — je retire le code de compatibilité et ses tests, et je neutralise le vocabulaire des échecs dans les tests.
- `compatibilite-seule` — je retire le code de compatibilité et ses tests ; les données tirées des échecs restent.
- `refuser` — rien ne change.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
