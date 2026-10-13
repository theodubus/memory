# La passe de recul : relevé et propositions

B-0041, à la demande de Théo : « une passe de ta part sur tout le code et
prendre du recul pour voir ce qu'on pourrait modifier/ajouter (que ce soit
sur des points techniques ou alors de façon beaucoup plus macro sur le
fonctionnement lui même en réfléchissant à ce que l'outil est censé
faire) ». Relevé le 2026-10-12.

**Comment.** Le moteur (environ 9 000 lignes) a été relu en cinq parts, par
cinq relecteurs en parallèle, chacun avec des essais sur des dépôts
jetables : la mémoire et ses contrôles ; les hooks, l'état et les liens ;
les contrôles de tests et les adaptateurs ; l'installeur, la mémoire privée,
la configuration et la ligne de commande ; l'auto-test et la couverture.
Le recul sur le fonctionnement part du cadrage
(`memory/archives/cadrage-2026-10-10.md`) et des rapports des bancs
(`banc/rapports/`). Les constats marqués **(v)** ont été revérifiés à la
main en écrivant ce relevé ; les autres reposent sur l'essai du relecteur.

**Déjà corrigé.** Deux constats visaient du code livré la veille pour le
parcours, et l'ont été tout de suite (J-2026-10-12-D) : le hook avant
commit plantait dès qu'un fichier protégé changeait, et deux tests de
l'avertissement au commit ne tournaient jamais.

## En bref

- Sur ce qu'ils mesurent, les bancs sont bons : les quatorze scénarios
  passent, et les fautes tentantes sont attrapées ou jamais tentées.
- La relecture trouve pourtant une vingtaine de défauts graves, en quatre
  familles : des **pertes de données** à l'installation et à la migration,
  des **contournements** du hook de l'agent, des **fuites** possibles de la
  mémoire privée, et des **contrôles qui laissent passer** ce qu'ils
  annoncent attraper.
- Trois causes reviennent :
  1. des contrôles qui lisent du **texte par motifs** au lieu de sa
     structure : le hook de l'agent sur la commande brute, les valeurs
     attendues ligne par ligne, les termes privés mot à mot ;
  2. l'installeur et la mémoire privée, **peu essayés sur des cas réels**
     (fichiers non commités, un `CLAUDE.md` existant, un sous-dossier, un
     mode chiffré verrouillé) ;
  3. la règle du dépôt, « tout contrôle a son défaut injecté », que **rien
     ne fait respecter** : 8 contrôles sur 33 n'ont jamais été vus échouer,
     et des refus du hook non plus.

## 1. Le fonctionnement : ce que l'outil doit faire, et où il en est

Les six problèmes du cadrage, et la réponse du socle aujourd'hui :

| # | Problème du cadrage | Réponse aujourd'hui | Ce qui manque |
| --- | --- | --- | --- |
| 1 | Reprise sans contexte | état dérivé au démarrage, consignes écrites en mémoire ; s1, s12, s13, s14 passent 12 fois sur 12 | — |
| 2 | Doc périmée, copies divergentes | valeurs liées, références vivantes, correspondance code ↔ doc, copies refusées ; s2 passe | la correspondance ne vaut que pour les liens déclarés à la main, et une seule dispense couvre toute une plage |
| 3 | Faux sentiment de preuve | tests creux, valeurs attendues, régression rejouée, trace des hooks | **la mutation ne tourne nulle part** : le plafond existe, aucun workflow ne lance le balayage (B-0005) ; et un contrôle qui plante comptait comme un contrôle qui attrape |
| 4 | Complétion de tête | SHA, identifiants et références inventés refusés ; s10 : jamais tentée | — |
| 5 | Croissance non bornée | budgets par couche, archivage | l'archivage tronque une entrée qui a des sous-titres |
| 6 | Décision humaine sans contexte | contrat des demandes, lint, lien obligatoire ; s5 passe | — |

Ce que le recul ajoute :

- **R1. La garantie « seule la CI est incontournable » repose sur une
  branche protégée que rien ne pose ni ne vérifie (v).** Sans elle, la CI
  dit rouge et rien n'empêche de fusionner. Ni le guide, ni « Et
  maintenant », ni l'état n'en parlent. Proposition : une étape « protéger
  la branche par défaut » (exiger la CI et la revue du propriétaire), avec
  le lien de la page GitHub, et une ligne de l'état qui dit si elle l'est.
- **R2. La mutation ne tourne nulle part (v).** Le cadrage en fait la
  réponse principale au problème 3. Proposition : un workflow hebdomadaire
  posé par l'installeur, qui lance la commande de l'adaptateur puis
  `socle mutation-verdict --poser`, et une alerte quand il cesse de
  tourner (B-0005).
- **R3. Le hook de l'agent juge le texte brut de la commande.** Sur 40 cas
  essayés, 25 contournements simples passent (lanceur entre guillemets,
  `git -C . push --force`, `push -fu`, `push origin :branche`, réglages
  locaux de Claude Code qui coupent tous les hooks…), et 6 commandes qui ne
  font que citer un motif sont refusées. Proposition : découper chaque
  commande avec `shlex` et juger son argv ; en défense en profondeur, que
  les commandes réservées à l'humain refusent d'elles-mêmes quand elles
  tournent dans une session d'agent.
- **R4. La lecture prouvée est la mécanique la plus fragile.** Quatre
  correctifs en trois jours (J-2026-10-10-U, J-2026-10-11-R,
  J-2026-10-12-A, et deux constats de plus ici), une fonction de 90
  lignes écrite deux fois (contrôle et hook), et 7 s sur 11 de la fin de
  tour. Proposition : une seule fonction, qui accepte toute version de
  l'index présente dans la plage, plus simple et presque aussi forte.
- **R5. La boucle de travail est lente.** Une fin de tour qui touche du
  code relance toute la suite de tests de ce dépôt, banc et auto-test
  compris : jusqu'à 5 minutes, et à chaque nouvel essai tant qu'un contrôle
  sans rapport échoue. Proposition : sortir le banc et l'auto-test de la
  suite rapide (la CI les garde), paralléliser l'auto-test (deux fois plus
  rapide, mesuré), ne plus le lancer deux fois en CI.
- **R6. Rien n'est encore éprouvé hors de ce dépôt.** Ni un projet réel
  (`chess` n'a servi que de copie jetable), ni un autre agent que Claude
  Code, que le cadrage vise pourtant. Le premier risque du cadrage, des
  faux positifs qui poussent à contourner, ne se mesure que là.
  Proposition : installer le socle sur `chess` pour de vrai, en adoption,
  et relever ses refus pendant une semaine ; puis un banc sans les hooks de
  l'agent, pour mesurer ce que git et la CI attrapent seuls.
- **R7. La mémoire privée concentre les risques** : un tiers des constats
  graves. Proposition : la durcir avant tout nouvel usage, et dire dans le
  guide que le mode chiffré est le moins éprouvé.
- **R8. La distribution** : le moteur est copié dans chaque projet ;
  l'empreinte n'est pas comparée à une version publiée (B-0006), et
  l'installation passe par un clone (B-0042).

## 2. La technique, par gravité

### A. Pertes de données et casse sur un vrai projet

| Constat | Où |
| --- | --- |
| La migration du format 1 au format 2 efface les fichiers de mémoire pas encore commités : `git mv -k` les saute, puis le dossier est supprimé **(v)** | `moteur/socle/migrations.py` |
| L'installation relancée depuis le projet (`python3 .socle/socle install`) efface son propre moteur : la source est la destination, supprimée avant la copie **(v)** ; le message de `prive installer` conseille justement cette commande | `moteur/socle/installeur.py` |
| Un CLAUDE.md existant est remplacé par la seule ligne d'import dès qu'un AGENTS.md existe, à chaque mise à jour | `moteur/socle/installeur.py` |
| Relancer `--adoption` écrit une seconde table `[adoption]` : les garde-fous deviennent illisibles | `moteur/socle/installeur.py` |
| Installé dans un sous-dossier d'un dépôt, les hooks git ne tirent pas et le workflow est posé où GitHub ne le lit pas, sans message | `moteur/socle/installeur.py`, `moteur/socle/outils.py` |
| Un `*.lock` du .gitignore du projet empêche de commiter le verrou ; un fichier parasite du clone source entre dans l'empreinte | `moteur/socle/installeur.py`, `moteur/socle/empreinte.py` |
| Un second `init --cadrage` écrase l'archive « telle quelle » ; un nom avec espace casse la référence | `moteur/socle/initialisation.py` |
| L'archivage du backlog tronque une entrée qui a des sous-titres et casse ses ancres | `moteur/socle/archivage.py` |

### B. Contournements des garde-fous par l'agent

| Constat | Où |
| --- | --- |
| Un réglage local de Claude Code, écrit par l'agent, coupe tous ses hooks ; la trace des hooks compte une session ancienne, et la CI ne voit rien | `moteur/socle/hooks.py`, gabarit de la politique |
| Réponse ou approbation à la place de l'humain : lanceur entre guillemets, `cd .socle`, drapeaux cherchés dans toute la commande **(v)** | `moteur/socle/hooks.py`, `moteur/socle/cli.py` |
| Pushes irréversibles qui passent : `-C`, `-c`, `-fu`, `:branche`, `HEAD:refs/heads/main` ; motifs morts (`twine publish`, `gem publish`) ; `gh api -X DELETE` ; deux outils GitHub d'écriture | `moteur/socle/hooks.py` |
| Un renommage efface le chemin d'origine des fichiers changés : un fichier protégé ou un test renommés passent tous les étages | `moteur/socle/outils.py` |
| Un fichier protégé s'écrit par le shell (`git rm`, `mv` d'un dossier, `1>`, `sed --in-place`…), et ce refus n'a pas de défaut injecté | `moteur/socle/hooks.py` |
| Le cliquet ne voit ni l'élargissement des docs d'une correspondance code ↔ doc, ni un plafond de mutation inventé à la main | `moteur/socle/controles_cliquet.py` |

### C. Fuites possibles de la mémoire privée

| Constat | Où |
| --- | --- |
| Les termes privés ne se trouvent que mot pour mot : « acme_corp », « AcmeCorp », un terme coupé en fin de ligne, un nom de fichier ou de branche passent | `moteur/socle/prive.py`, `moteur/socle/hooks.py` |
| En mode chiffré, la liste des termes part en clair quand le filtre manque, et rend la mémoire « indisponible » quand il est là | `moteur/socle/prive.py` |
| Le cadrage est archivé en public même avec une mémoire privée, et les archives échappent au contrôle des fuites | `moteur/socle/initialisation.py`, `moteur/socle/prive.py` |
| Ajouter un terme à une liste illisible l'écrase | `moteur/socle/prive.py` |
| `socle new` écrit une entrée privée quand la mémoire privée est indisponible : identifiant deviné, texte clair accolé au fichier chiffré | `moteur/socle/cli.py`, `moteur/socle/memoire.py` |
| Un identifiant privé dans un bloc de code d'un fichier public n'est attrapé ni au commit ni en CI | `moteur/socle/controles_memoire.py` |
| Le corps d'une pull request écrit dans un fichier hors du dépôt, puis passé par `--body-file`, n'est pas lu | `moteur/socle/hooks.py` |
| La mémoire privée n'est jamais relue à une révision : « ajout seul » ne la protège pas | `moteur/socle/memoire.py`, `moteur/socle/controles_memoire.py` |

### D. Contrôles qui laissent passer

| Constat | Où |
| --- | --- |
| Une valeur attendue placée hors de la ligne d'assertion (assertion sur plusieurs lignes, variable, constante, tables de Go, paramètres) change sans bruit | `moteur/socle/controles_tests.py` |
| Un test sans assertion passe si un commentaire, une docstring ou du code de production contient « assert » | `moteur/socle/tests_lecture.py` |
| Un groupe entier de tests se désactive sans raison (classe, `describe.skip`, `@Disabled`) | `moteur/socle/controles_tests.py`, adaptateurs |
| Un test de régression qui échoue sur le parent pour une mauvaise raison (import manquant) fait foi | `moteur/socle/controles_tests.py` |
| Des noms cherchés comme sous-chaînes : un commentaire suffit à « tester » une fonction, une validation qui nomme `test_double_negatif` couvre `test_double` | `moteur/socle/controles_tests.py` |
| Une seule `Dispense-doc` couvre toute la plage et toute la table de correspondance | `moteur/socle/controles_docs.py` |
| Une lecture d'index recopiée d'un sujet plus ancien du même fichier passe | `moteur/socle/controles_memoire.py`, `moteur/socle/hooks.py` |
| Une décision se réécrit dans ses lignes en citation ; le journal accepte un ajout au milieu d'une phrase ; un titre mal formé fait disparaître l'entrée | `moteur/socle/controles_memoire.py`, `moteur/socle/memoire.py` |
| Pendant une migration, une ancienne validation compte comme nouvelle | `moteur/socle/demandes.py` |

### E. Refus à tort et friction

| Constat | Où |
| --- | --- |
| Une assertion reformatée à valeur égale, ou deux tests homonymes dans deux classes, sont lus comme une valeur attendue changée (vécu en CI le 2026-10-12) | `moteur/socle/controles_tests.py` |
| Un texte qui cite une commande dangereuse ou réservée est refusé comme si elle était lancée (vécu plusieurs fois pendant B-0034) | `moteur/socle/hooks.py` |
| Le verdict des lectures prouvées dépend de la base choisie | `moteur/socle/controles_memoire.py` |
| Le lint d'une demande prend un extrait de code ou un « < 5 » pour un trou du gabarit | `moteur/socle/demandes.py` |
| Une référence suivie d'un point ou d'une parenthèse, ou un lien avec `%20`, est déclarée morte (B-0020) | `moteur/socle/memoire.py` |
| « **Pour toi** : » en gras n'est pas reconnu comme récap ; un lien vers une étiquette est déclaré mort | `moteur/socle/humain.py`, `moteur/socle/liens.py` |
| La virgule décimale française confond 3,5 et 35 | `moteur/socle/controles_docs.py` |

### F. Autres défauts

| Constat | Où |
| --- | --- |
| L'empreinte de l'arbre, qui décide de relancer les tests en fin de tour, ignore le contenu des fichiers non suivis | `moteur/socle/hooks.py` |
| Le compteur d'échecs de fin de tour survit d'une session à l'autre : la nouvelle session escalade dès son premier échec | `moteur/socle/hooks.py` |
| `prepare-commit-msg` met le diff de `git commit -v` dans le message | `moteur/socle/hooks.py` |
| `mutation-verdict --poser` annonce un plafond qu'il n'écrit pas pour certaines formes de clé ; mutmut lit mal un module dont le nom commence par `x_` | `moteur/socle/mutation.py` |
| La lecture des tests par motifs casse sur des formes courantes : une flèche sans accolades en JavaScript, `if … end` en Ruby, un type `[u8; 4]` en Rust, un test Python sur une ligne | `moteur/socle/tests_lecture.py`, adaptateurs |

### G. L'auto-test

- **8 contrôles sur 33 n'ont aucun défaut injecté** : `adaptateur.capacites`,
  `demandes.reponses`, `hooks.configuration`, `instructions.source-unique`,
  `memoire.format`, `memoire.peremption`, `mutation.couverture` (impossible :
  l'adaptateur du projet jetable n'a pas de mutation), `prive.acces` ; deux
  autres (`memoire.preuves`, `demandes.contrat`) ne sont vus qu'à travers le
  hook de l'agent. Un défaut simple a été essayé pour chacun : aucun n'est
  muet, mais rien ne les éprouve.
- Des refus du hook jamais vus : 7 motifs irréversibles sur 8, les outils
  externes, l'écriture protégée par le shell, la référence inventée,
  l'escalade après trois échecs.
- Aucun témoin ne vérifie qu'un changement validé passe (seuil relâché,
  fichier protégé, valeur attendue, sous une demande validée).
- Proposition : un test qui exige que chaque contrôle du registre ait au
  moins un défaut injecté, ou une exemption écrite ; et une mutation
  factice dans l'adaptateur du projet jetable.

### H. Performance

- Fin de tour : jusqu'à 297 s sur ce dépôt, dont 264 s de suite de tests
  (banc 107 s, auto-test 87 s) et 7 s pour les lectures prouvées (près de
  2 000 appels à git).
- Auto-test : 76 s en série, 37 s sur quatre fils (prototype essayé) ; il
  tourne deux fois en CI.

### I. Dette

- `installer()` fait 180 lignes et six métiers ; `prive.py` (700 lignes)
  mêle chemins, verrou, termes, fuites, relecture, quatre contrôles, bascule
  et mise en place.
- Doublons : la règle des index permis (contrôle et hook), le calcul d'une
  ancre (B-0017), l'ajout au .gitignore, l'écriture d'un fichier.
- Code mort et docstrings périmées : anciens noms de fichiers du format 1
  dans des messages, un renvoi à un document qui n'existe pas (B-0016),
  « sept champs » au lieu de huit.

## 3. Propositions, par lots

| Lot | Contenu | Effort | Ce qu'il change |
| --- | --- | --- | --- |
| L1 | Pertes de données et casse (A) | faible | le socle s'installe et se met à jour sans rien perdre |
| L2 | Contournements (B), le hook par `shlex` et le refus des commandes humaines sous un agent (R3), la branche protégée (R1) | moyen | les garde-fous tiennent face à un agent qui cherche, et la CI devient réellement incontournable |
| L3 | Mémoire privée (C, R7) | moyen | la frontière du privé tient sur des formes réelles |
| L4 | L'auto-test (G) : chaque contrôle et chaque refus vus échouer, témoins de déverrouillage, mutation factice | moyen | la règle du dépôt se fait respecter seule |
| L5 | Contrôles qui laissent passer et refus à tort (D, E, F), dont les valeurs attendues comparées par littéraux et la lecture prouvée simplifiée (R4) | important | moins de faux négatifs, moins de friction ; deux choix de conception, chacun avec sa décision écrite |
| L6 | Performance (H, R5) | moyen | une fin de tour en secondes ; sortir le banc et l'auto-test de la suite rapide change l'adaptateur de ce dépôt, protégé : à toi |
| L7 | Dette (I) | moyen | un code plus facile à reprendre |
| R2 | Le workflow de mutation (B-0005) | moyen | la réponse principale au faux sentiment de preuve tourne enfin |
| R6 | `chess` pour de vrai, puis un banc sans les hooks de l'agent | moyen | la première mesure hors de ce dépôt |

Recommandation : L1, L2 et L3 d'abord, dans cet ordre, chaque constat avec
un test qui échoue sur le code actuel ; puis L4, pour que tout ce qui
précède soit vu échouer ; puis R6, la vraie mesure, avant L5, que ses
résultats aideront à prioriser ; L6, R2 et L7 ensuite.

## Suite donnée

Théo a validé l'ordre recommandé (D-0015) ; le sujet B-0044 suit les lots.

| Lot | Fait | Journal |
| --- | --- | --- |
| L1 | tout le lot | J-2026-10-12-G |
| L2 | tout le lot, dont R1 et R3 : la branche par défaut de ce dépôt exige déjà la CI par un ensemble de règles, sans revue des propriétaires du code | J-2026-10-12-H |
| L3 | tout le lot, et R7 : le guide dit que le mode chiffré est le moins éprouvé | J-2026-10-12-I |
| L4 | tout le lot : chaque contrôle et chaque refus ont leur défaut injecté, ce qu'un test exige ; mutation factice ; témoins de changements validés | J-2026-10-12-J |
| R6 | sur une copie du projet d'échecs (D-0016) : installation en adoption, cinq tâches sans un refus pendant les sessions, un refus à tort en CI, le banc sans les hooks de l'agent ; huit constats, relevé dans `docs/essai-chess.md` | J-2026-10-12-R |
| L5 | les sections D, E et F, et les trois constats de R6 qui en relevaient (B-0051, B-0049, B-0052) ; la deuxième ligne de E était réglée par L2 ; les deux choix de conception : la lecture prouvée en une seule fonction (ADR-0023), une valeur attendue hors des assertions dite sans être refusée (ADR-0024) | J-2026-10-13-A à J-2026-10-13-K |
