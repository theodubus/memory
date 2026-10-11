<!-- socle: couche=canonique zone=publique -->
# Mémoire canonique

L'état vérifié du projet : un fait par entrée, avec son statut et sa preuve.
Un fait ne change qu'avec une référence de preuve nouvelle ; réfuté, il est
barré et conservé. Lue à chaque session : elle reste sous son budget, et ce
qui n'a plus à être lu à chaque fois s'archive dans le journal.

## Le moteur

## F-0001 — Le moteur n'importe que la bibliothèque standard de Python 3.11+

> statut : mesuré · preuve : fichier:tests/test_moteur.py · date : 2026-10-10

Le test parcourt chaque module du moteur et refuse tout import qui n'est ni
`socle` ni dans `sys.stdlib_module_names` ; il vérifie aussi que le code
s'analyse en syntaxe 3.11.

## F-0002 — Chaque défaut injecté du cadrage est attrapé par le contrôle prévu

> statut : mesuré · preuve : fichier:tests/test_autotest.py, J-2026-10-10-Y · date : 2026-10-10

`python3 .socle/socle selftest` injecte les défauts du tableau du cadrage,
et d'autres, dans des projets jetables, par les vrais points d'entrée (hooks
de l'agent, hook git, commande de CI). Chacun est attrapé par le contrôle
attendu ; les témoins sains passent. « Mémoire privée non accessible »,
déclaré non couvert jusqu'au jalon 7, l'est désormais, dans les deux modes
de mémoire privée.

## F-0003 — Les hooks d'un `.claude/settings.json` écrit en cours de session sont chargés dès l'appel d'outil suivant

> statut : mesuré · preuve : J-2026-10-10-E · date : 2026-10-10

Observé en installant le socle sur ce dépôt : le hook `PreToolUse` a tiré sur
l'appel d'outil qui suivait l'installation, dans la même session, et a refusé
trois commandes. Même constat que dans chess. Le hook `SessionStart`, lui,
n'a pas tiré pour cette session : d'où `SessionStart=installation` dans le
trailer de ses commits.

## Les essais sur chess

## F-0004 — L'audit d'adoption tourne sur chess entier en trois secondes et passe

> statut : mesuré · preuve : J-2026-10-10-F · date : 2026-10-10

Trois contrôles y passent en avertissement (chemins cités, tests creux,
couverture de mutation), chacun avec ses constats.

## F-0005 — `chess:CLAUDE.md` fait 110 612 octets, environ 28 000 jetons relus à chaque session

> statut : mesuré · preuve : fichier:docs/inventaire-chess.md · date : 2026-10-10

## F-0006 — Le carnet de bord de chess fait 720 Ko

> statut : supposé · source : fichier:memoire/archives/cadrage-2026-10-10.md

Affirmé par le cadrage, invérifiable d'ici : le carnet est privé. La taille
concorde avec celle de `chess:tools/README.md` ; la question est posée dans
D-0001.

## F-0007 — Le python3 fourni par macOS est en version 3.9

> statut : supposé · source : J-2026-10-10-C

Avancé à l'initialisation pour justifier le refus explicite du lanceur sous
3.11 ; non vérifié sur une machine Apple.

## F-0008 — Avec l'adaptateur proposé, `socle verify` exécute la CI de chess et tout passe

> statut : mesuré · preuve : J-2026-10-10-H · date : 2026-10-10

Hors les jobs multi-systèmes, le job indicatif de toolchain et le contrôle
du balayage par l'API GitHub. 4 min 31 s dans le conteneur.

## F-0009 — GitHub refuse de fusionner dans `main` une pull request dont la CI du socle échoue

> statut : mesuré · preuve : J-2026-10-10-L · date : 2026-10-10

Le check « Socle — verify, contrôles, auto-test » est requis sur `main`.
Porte du jalon 5 franchie.

## Le second langage

## F-0010 — Avec l'adaptateur `python-pytest`, la chaîne du socle tourne sur un projet Python jetable, et chaque défaut injecté y est attrapé

> statut : mesuré · preuve : J-2026-10-10-W · date : 2026-10-10

Installation, `socle ci`, balayage mutmut et verdict contre le plafond ; un
test sans assertion, un test supprimé, une fonction publique sans test, un
correctif sans test et des tests affaiblis sont refusés chacun par le
contrôle prévu. Porte du jalon 6, au prix de deux corrections du moteur que
le journal détaille.

## F-0011 — Sur des copies locales, l'initialisation réussit depuis chacune des entrées, et l'installation sur chess se fait sans merge

> statut : mesuré · preuve : J-2026-10-10-AC, fichier:tests/test_initialisation.py · date : 2026-10-10

Rien, un cadrage seul, chess seul, chess avec un cadrage : `check --stage ci`
passe après `socle init`. L'installation sur une copie de chess, adaptateur
détecté et mode adoption, prend trois secondes. Porte du jalon 8.

## Le banc d'évaluation

## F-0012 — Sur 18 sessions réelles, les six scénarios du cadrage passent leurs juges

> statut : mesuré · preuve : fichier:banc/rapports/2026-10-11-reel.md, J-2026-10-11-C · date : 2026-10-11

Trois passages par scénario, l'équivalent de 5,26 $ en tout. Mais un agent
qui lit les règles s'y garde souvent seul de la faute : s3 et s4 n'ont pas
éprouvé le dispositif sur la faute injectée.

## F-0013 — Sur 15 sessions réelles propices aux fautes, aucune faute n'est passée à travers les étages

> statut : mesuré · preuve : fichier:banc/rapports/2026-10-11-fautes.md, J-2026-10-11-F · date : 2026-10-11

Attrapées : par la vérification que l'agent lance lui-même (6 fois), par le
hook avant commit et la fin de tour (3 fois chacun), par le hook de l'agent
(3 fois). Non tentées : 6 fois. Une faute de jugement (relayer une réponse
à une demande que l'humain n'a pas lue) est passée le hook, et n'a été
arrêtée que par un autre contrôle (B-0022).

## F-0014 — Sur les projets d'essai, `verify --rapide` prend moins d'une seconde, et l'état injecté au démarrage moins de 4 Ko

> statut : mesuré · preuve : fichier:banc/rapports/2026-10-11-reel.md, fichier:banc/rapports/2026-10-11-fautes.md · date : 2026-10-11

De 0,56 à 0,80 s pour `verify --rapide` sur 33 passages ; l'état fait de
1 528 à 3 683 octets, soit environ 400 à 900 jetons, le plus lourd après
une initialisation qui audite un dépôt. Un petit projet : chess donnerait
d'autres chiffres (F-0005).

## F-0015 — Dans les scénarios sains, les seuls refus visaient des demandes hors contrat

> statut : mesuré · preuve : J-2026-10-11-G · date : 2026-10-11

Aucun refus sur les neuf sessions de s1, s2 et s6. Le premier jet d'une
demande a été refusé 8 fois sur 11 (s4, s5, s9, s11). Vérifié sur les deux
de s11, dont la transcription est gardée : la section « Où regarder »
donnait des chemins sans lien et un identifiant sans description, ce que
le contrat refuse. Vrais positifs, mais qui disent un manque de l'outil
(B-0027) ; ceux du premier banc, sans transcription, restent invérifiés.

## F-0016 — Sur 9 sessions réelles, un chantier repris après un compactage, ou sur un résumé faux, est tenu

> statut : mesuré · preuve : fichier:banc/rapports/2026-10-11-reprise.md, J-2026-10-11-G · date : 2026-10-11

Après un `/compact` réel (s12, trois fois), le hook de démarrage a tiré et
l'agent a fini le chantier en respectant la décision, le piège du journal
et l'étape bloquée. Devant un résumé faux (s13, trois fois), il a vérifié
le dépôt et n'a pas agi sur la validation inventée. Conditions favorables :
un contexte court, coupé à une frontière propre, tout l'essentiel écrit
dans la mémoire ; ce n'est pas encore un compactage de fin de longue
session (J-2026-10-11-G).
