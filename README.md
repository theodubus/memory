# Socle — mémoire, documentation et tests fiables pour agents de code

Version <!-- valeur:version -->0.1.0<!-- /valeur -->. Un moteur Python,
bibliothèque standard seule, à installer dans n'importe quel projet de code
entretenu par un agent. L'agent écrit la mémoire, la documentation et les
tests ; des contrôles automatiques attrapent les erreurs, à trois étages
(hooks de l'agent, hooks git, CI) ; l'humain n'arbitre que ce qu'aucun
contrôle ne peut trancher.

- **Mémoire** en cinq couches lisibles par script — canonique, actif,
  décisions, journal, backlog — plus une file de demandes humaines au
  contrat vérifié. L'état du projet se calcule depuis git, il ne s'écrit pas.
- **Garde-fous** doc ↔ code et tests : références vivantes, valeurs liées à
  leur source, pas de copie, tests creux, valeurs attendues, régression
  rejouée sur le commit parent, cliquet sur tous les seuils.
- **Auto-test** : chaque défaut connu est injecté dans un projet jetable et
  doit être attrapé par l'étage prévu.

## Commencer

Python 3.11 ou plus récent, dans un dépôt git :

```sh
git clone https://github.com/theodubus/memory /tmp/socle
PYTHONPATH=/tmp/socle/engine python3 -m socle install --target . --owner @moi
```

Avec BMAD Method, qui planifie pendant que le socle prouve et retient,
ajouter `--with-bmad` : la même commande installe les deux.

L'installation finit par « Et maintenant » : tes étapes suivantes, dans
l'ordre, chacune avec sa commande (décrire le projet à l'agent, commiter,
ouvrir l'agent). Ensuite, `python3 .socle/socle help` donne tes gestes :
répondre aux demandes de l'agent, approuver tes propres changements
protégés, relire avant publication si tu l'as choisi, commiter toi-même. Ce
guide se lit aussi dans `engine/socle/HELP.md`.

L'adaptateur se déduit du dépôt (`--adapter <nom>` le force). Adaptateurs
maintenus : `rust`, `python` (`unittest`), `python-pytest` (pytest et
mutmut), `javascript` (vitest et Stryker), `go` (go test et gremlins),
`java` (Maven, JUnit 5 et PIT), `ruby` (RSpec et mutant), `php` (PHPUnit et
Infection), `csharp` (dotnet test et Stryker.NET) ; un autre langage se déclare dans un fichier `.toml` passé à
`--adapter`. Options : `--private compagnon|chiffre` (une mémoire privée),
`--review lots|chaque-push` (relire avant publication), `--language en`
(une mémoire en anglais), `--adoption` (un projet existant dont des
contrôles échouent). Relancer l'installeur met le socle à jour : il
remplace le moteur et montre le diff de la politique
sans la toucher.

## Lire la suite

- `docs/socle.md` — ce que fait le socle et comment il est fait : la mémoire, les contrôles, les trois étages, la politique, les demandes, et que faire quand un contrôle refuse.
- `engine/socle/HELP.md` — le guide de l'humain : ses gestes, chacun avec sa commande.
- `AGENTS.md` — comment travailler dans ce dépôt, et ce que le socle impose.
- `docs/architecture.md` — où chaque exigence du cadrage est appliquée.
- `docs/parcours.md` — le parcours de l'utilisateur, relevé, et ce qui le simplifiera.
- `docs/recul.md` — la passe de recul sur le code et le fonctionnement : constats et propositions.
- `engine/socle/FORMAT.md` — le format de la mémoire.
- `docs/inventaire-chess.md` — ce qui vient du dépôt chess.
- `memory/archives/cadrage-2026-10-10.md` — le cadrage fondateur, tel quel.
