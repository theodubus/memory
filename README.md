# memory — l'atelier du socle

Ce dépôt fabrique le **socle** : mémoire et garde-fous pour les agents de
code qui entretiennent un projet dans la durée. Ce qu'il est, comment il
fonctionne et comment l'installer : [sa page d'accueil](engine/README.md),
publiée comme README du dépôt public
[theodubus/socle](https://github.com/theodubus/socle).

## Les deux parts du dépôt

**Le produit**, `engine/socle/`, est la seule partie copiée dans un projet ;
le workflow `distribution.yml` le publie, avec sa page d'accueil et sous
licence MIT, dans le dépôt public à chaque fusion sur `main` qui le change. **L'atelier**
est tout le reste : les tests (`tests/`), les bancs (`bench/`), la
documentation de fabrication (`docs/fabrication/`) et la mémoire
(`memory/`). Ce dépôt est lui-même équipé du socle, en mode amont : sa
mémoire est l'historique de la fabrication.

## État

L'atelier fabrique la version <!-- valeur:version -->0.1.0<!-- /valeur -->,
en développement. Où en est le travail se calcule :
`python3 .socle/socle state`.

## Documentation

| Document | Portée |
| --- | --- |
| [La page d'accueil du socle](engine/README.md) | ce qu'est le socle, son fonctionnement, son installation : le README du dépôt public |
| [Le guide d'utilisation](engine/socle/HELP.md) | l'usage d'un projet équipé, étape par étape, et la référence des commandes |
| [Le format de la mémoire](engine/socle/FORMAT.md) | la spécification de la mémoire |
| [L'atelier](docs/fabrication/README.md) | la fabrication : architecture, bancs, relevés |
| [Les instructions de ce dépôt](AGENTS.md) | comment l'agent y travaille, et les commandes de l'atelier |
