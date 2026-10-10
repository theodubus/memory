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

## F-0002 — Chaque défaut injecté du cadrage est attrapé par le contrôle prévu, sauf la mémoire privée

> statut : mesuré · preuve : fichier:tests/test_autotest.py · date : 2026-10-10

`python3 .socle/socle selftest` injecte les défauts du tableau du cadrage,
et d'autres, dans un projet jetable, par les vrais points d'entrée (hooks de
l'agent, hook git, commande de CI). Chacun est attrapé par le contrôle
attendu ; les témoins sains passent. « Mémoire privée non accessible » est
déclaré non couvert avant le jalon 7, jamais en silence.

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
