<!-- socle: couche=backlog zone=publique -->
# B-0089 — Sur un projet qui n'a pas encore de code, verify échoue avec tout adaptateur sauf python

> statut : ouvert · origine : J-2026-10-29-L · lu : backlog@b8f4fad9

Un projet neuf s'installe avant d'avoir du code : avec BMAD Method, la
planification dure avant la première story. Sur un tel projet, `verify`
lance pourtant la commande de test de l'adaptateur, et toutes échouent,
sauf celle de `python`, qui reconnaît « aucun test » (B-0026) : pytest rend
5, cargo, go et maven ne trouvent pas de manifeste, bundler pas de Gemfile,
phpunit pas de `vendor/`, vitest n'est pas installé. Le hook de fin de tour
refuse alors de conclure, et la première CI du projet est rouge.

Un projet sans aucun fichier source à lui (les motifs `sources` de
l'adaptateur, hors du dossier du socle et des fichiers tiers) n'a rien à
compiler ni à tester : ses étapes s'annoncent en avertissement, non
lancées, jusqu'au premier fichier. L'adaptateur `python-pytest` reconnaît
aussi « no tests ran », comme `python` le fait pour unittest.
