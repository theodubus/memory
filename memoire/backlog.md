<!-- socle: couche=backlog zone=publique -->
# Backlog

Les sujets à traiter. Chacun a un statut (ouvert, en cours, bloqué, fait,
abandonné) et une origine ; un sujet clos porte la référence de ce qui l'a
clos, puis s'archive dans le journal (`python3 .socle/socle archive`).

## B-0001 — Jalon 6 : second adaptateur sur un projet jetable, langage dynamique

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

L'adaptateur Python existe et sert à ce dépôt ; il reste à l'éprouver sur un
projet jetable avec un outil de mutation (mutmut), dont le lecteur de
résultats est écrit mais jamais exécuté. Porte : noyau inchangé.

## B-0002 — Jalon 7 : mémoire privée, en dépôt compagnon et chiffrée, et contrôles de fuite

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Déjà en place : les identifiants privés préfixés de `P`, refusés dans tout
fichier public même sans accès à la zone privée. Restent les deux modes, le
verrou du dépôt compagnon, la liste de termes refusés, le signal « mémoire
privée indisponible » éprouvé par l'auto-test, et les arbitrages sur les
fuites listés par le cadrage.

## B-0003 — Jalon 8 : initialisation depuis un cadrage, depuis rien ou depuis un dépôt existant

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

L'installeur pose déjà le dispositif, gère l'adoption et se relance. Restent
les trois entrées d'initialisation et leur confrontation, les questions
plafonnées, les migrations de format scriptées, l'affichage du diff de
politique à la mise à jour. Attend D-0002.

## B-0004 — Jalon 9 : banc d'évaluation sur un agent réel

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Les six scénarios du cadrage et les métriques : part des défauts attrapés par
étage, faux positifs, durée de `verify`, coût en jetons du démarrage.

## B-0005 — Workflow de mutation hebdomadaire générique, et alerte quand il cesse de tourner

> statut : ouvert · origine : J-2026-10-10-D

Le verdict existe (`socle mutation-verdict`) ; manquent le gabarit de
workflow planifié et l'équivalent de `chess:tools/balayage-vivant.sh`, qui
voit un cliquet endormi par GitHub.

## B-0006 — Vérifier l'empreinte du moteur contre la version publiée en amont

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Aujourd'hui, la CI compare le moteur au verrou local. Le cadrage demande la
comparaison avec la version publiée, que le verrou seul ne garantit pas si
moteur et verrou changent ensemble.

## B-0007 — Le hook pre-commit contrôle l'arbre de travail, pas l'index

> statut : ouvert · origine : J-2026-10-10-E

Un commit partiel peut être jugé sur des fichiers qu'il ne contient pas. La
CI, elle, juge le commit réel.

## B-0008 — Les chemins qui n'existent que dans une rustine sont pris pour des liens morts

> statut : ouvert · origine : J-2026-10-10-F

25 cas sur chess, tous des lecteurs de sondes contenus dans les rustines de
l'attic. Une notation pour « chemin dans une rustine », ou une exclusion
déclarée par le projet.

## B-0009 — Adoption : importer l'existant que le socle sait lire

> statut : ouvert · origine : J-2026-10-10-F

Les plafonds de mutation de chess ont été repris à la main
(`docs/chess/mutation-caps.toml`). L'adoption pourrait proposer cette
reprise, et celle des tables « Ce qui tourne tout seul ».

## B-0010 — Calibrer les budgets de taille et de jetons du démarrage

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Question ouverte du cadrage. Les valeurs par défaut des garde-fous sont des
hypothèses ; chess donne un point de mesure (F-0005).

## B-0011 — Audit périodique de l'adaptateur

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Détecter un outil ou un langage nouveau dans le projet et émettre une
demande. Fréquence à décider (question ouverte du cadrage).

## B-0012 — Une copie non marquée d'une valeur liée n'est qu'un avertissement

> statut : ouvert · origine : J-2026-10-10-E

`docs.valeurs` refuse une valeur marquée fausse, mais ne fait qu'avertir sur
une copie non marquée de la valeur courante : elle pourrait être une
coïncidence. Mesurer les faux positifs avant de durcir.

## B-0014 — Exiger un test pour du code nouveau, et pour du code existant qu'on découvre non testé

> statut : ouvert · origine : J-2026-10-10-J

Demandé par Théo. Le cadrage ne l'impose pas : il exige un test de
régression pour un correctif, et compte sur la mutation pour voir le code
qu'aucun test ne vérifie — or la mutation est hebdomadaire et absente pour
Python. À concevoir : un contrôle sur le diff, par exemple « une fonction
publique ajoutée ou modifiée est nommée par au moins un test », avec une
dispense motivée comme pour la doc ; et, quand l'agent découvre en route du
code existant sans test, la règle de l'écrire tout de suite s'il est dans le
périmètre, sinon de l'inscrire au backlog.

## B-0015 — La trace des hooks ignore les worktrees git

> statut : ouvert · origine : J-2026-10-10-L

Les hooks de l'agent écrivent la trace dans `.socle/trace/` du dépôt
principal ; un commit fait dans un autre worktree la cherche dans le sien, ne
la trouve pas, et part avec `Socle-Hooks: aucun` — la CI le refuse. Placer la
trace dans le répertoire git commun (`git rev-parse --git-common-dir`),
partagé par tous les worktrees, avec un défaut injecté dans l'auto-test.
