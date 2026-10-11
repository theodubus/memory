<!-- socle: couche=decisions zone=publique -->
# ADR-0018 — Les chemins d'un projet sont en anglais, au format 2 de la mémoire

> statut : acceptée · date : 2026-10-11 · source : J-2026-10-11-N@b7c42180 · lu : decisions@50eefafa

## Contexte

Les chemins d'un projet étaient en français (`memoire/`, `canonique.md`,
`.socle/politique.toml`…). Théo a demandé des noms en anglais pour tous les
projets, quelle que soit la langue de la mémoire (B-0032@e0e327b1). Un chemin est un
identifiant, et ADR-0002@5b36d00d veut les identifiants en anglais ; un seul jeu de
chemins évite d'en traduire par langue quand la langue de la mémoire
deviendra un choix (B-0031@bf3363d3). Mais des projets existent déjà au format 1, et
leur mémoire, en ajout seul, cite les anciens chemins.

## Décision

Le format 2 de la mémoire renomme les chemins en anglais : memory/,
canonical.md, active.md, requests/, private/, terms.txt, les réponses en
`.answer.toml`, et sous `.socle/` policy.toml, guardrails.toml,
adapter.toml, engine/ et engine.lock. Le contenu ne change pas : titres,
statuts et mots-clés restent ceux de la langue de la mémoire.

Le moteur lit les deux formats. La table des chemins se choisit par projet
et par révision : le verrou du moteur, sinon la politique, sinon le dossier
de mémoire. Tout ce qui reconnaît un fichier de mémoire accepte les deux
noms ; tout ce qui en écrit un suit le format du projet.

La migration du format 1 au 2 renomme avec `git mv` et traduit les chemins
dans la configuration et dans la documentation hors mémoire. Elle ne
réécrit jamais la mémoire : un ancien chemin ou une ancienne ancre cités
dans une entrée gelée restent des références valides. En CI, une plage qui
migre lit la base sous les noms de la tête, pour que le cliquet, l'ajout
seul et les références comparent un fichier à lui-même.

## Conséquences

Une installation neuve est au format 2. Une mise à jour d'un projet au
format 1 le migre, et renomme des fichiers protégés : l'humain l'approuve
(`socle approve`), comme toute mise à jour de la politique. Les permaliens
déjà donnés restent valides, puisqu'ils visent un commit. Le moteur garde la
table du format 1 tant qu'un projet peut en être.

Pour défaire : poser `FORMAT_ACTUEL = FORMAT_1` dans
`moteur/socle/config.py` et retirer la migration 1 → 2 de
`moteur/socle/migrations.py` ; un projet déjà migré se renomme à rebours
par `config.traduire(chemin, vers=1)`. Les tests de
`tests/test_formats.py` diront ce qui casse.
