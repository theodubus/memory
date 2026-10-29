# La fabrication du socle

Ces documents s'adressent à qui fabrique le socle, pas à qui l'installe :
aucun n'est copié dans un projet. Pour comprendre l'outil et s'en servir,
[le README](../../README.md) et
[le guide d'utilisation](../../engine/socle/HELP.md) suffisent.

## D'où vient le socle

Le socle est né d'un projet d'échecs de Théo, `theodubus/chess` : un moteur
en Rust entretenu par un agent de code pendant des semaines. Pour qu'il
tienne, Théo y avait écrit à la main ses garde-fous : un `CLAUDE.md` de plus
de cent mille octets relu à chaque session, un carnet de bord, des scripts
de vérification et leurs auto-tests, des plafonds de mutation. Ils
marchaient, mais rien n'en était réutilisable, et l'agent passait une part
de chaque session à relire ce qu'il aurait dû pouvoir calculer.

Le [cadrage](../../memory/archives/cadrage-2026-10-10.md) a fixé le but : en
faire un outil générique, qui ne connaît ni le langage ni l'agent, et dont
chaque garde-fou a été vu échouer. Ce qui était générique dans chess a été
repris et généralisé ; ce qui lui était propre est resté là-bas. Le socle a
ensuite été éprouvé sur une copie de chess, puis sur des projets jetables
de huit langages. Les échecs ne sont plus que l'histoire : rien de ce
qu'un projet reçoit n'en parle.

## Les documents

| Document | Ce qu'il dit |
| --- | --- |
| [L'architecture](architecture.md) | où chaque exigence du cadrage est appliquée, module par module, et ce qui ne l'est pas encore |
| [Le banc d'évaluation](banc.md) | comment un agent réel est mis à l'épreuve sur des scénarios propices aux fautes, et quel étage attrape quoi |
| [Les adaptateurs](adaptateurs.md) | comment chaque adaptateur maintenu a été éprouvé, et ce que ces essais ont corrigé |
| [Le parcours de l'utilisateur](parcours.md) | ce que l'humain tape, lit et décide, relevé de l'installation à l'usage courant, et ce qui l'a simplifié |
| [La passe de recul](recul.md) | un relevé de tout le code et du fonctionnement : constats et propositions |
| [L'inventaire de chess](inventaire-chess.md) | ce que le projet d'échecs contenait de générique, et ce que chaque pièce est devenue |
| [L'essai sur une copie de chess](essai-chess.md) | la première mesure hors de ce dépôt : le socle installé en adoption, cinq tâches d'un agent |
| [Le matériel de l'essai sur chess](chess/README.md) | l'adaptateur et les plafonds de mutation préparés pour chess |

Les rapports des bancs sont dans `bench/reports/`. La mémoire de ce dépôt,
dans `memory/`, dit le reste : pourquoi chaque chose est ainsi (le journal),
ce qui a été décidé (les décisions), ce qui reste à faire (le backlog).

## Le travail dans ce dépôt

Ce dépôt est en mode amont : il fabrique le moteur qu'il utilise, et ce
moteur n'y est pas figé par une empreinte. Comment y travailler, et les
règles qui lui sont propres (un contrôle nouveau a son défaut injecté, la
bibliothèque standard seule) : [AGENTS.md](../../AGENTS.md).

```sh
python3 .socle/socle verify --fast       # compilation, tests, contrôles
python3 .socle/socle ci                  # tout, dont l'auto-test
python3 bench/bench.py --agent simule    # le banc, sur un agent simulé
python3 bench/adapters.py                # les adaptateurs, sur leurs vrais outils
```
