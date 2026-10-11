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

## Installer

Python 3.11 ou plus récent, dans un dépôt git :

```sh
git clone https://github.com/theodubus/memory /tmp/socle
PYTHONPATH=/tmp/socle/moteur python3 -m socle install --target . --adapter auto --owner @moi
# projet existant : ajouter --adoption ; mémoire privée : --private compagnon|chiffre
python3 .socle/socle init --cadrage cadrage.md --depot   # l'une, l'autre, les deux, ou rien
python3 .socle/socle state
python3 .socle/socle verify --rapide
```

`--adapter auto` choisit l'adaptateur d'après le dépôt. Adaptateurs
maintenus : `rust`, `python` (`unittest`), `python-pytest` (pytest et
mutmut) ; un autre langage se déclare dans un fichier `.toml` passé à
`--adapter`. Relancer l'installeur met le socle à jour : il remplace le
moteur, migre les formats, et montre le diff de la politique sans la
toucher.

## Lire la suite

- `AGENTS.md` — comment travailler dans ce dépôt, et ce que le socle impose.
- `docs/architecture.md` — où chaque exigence du cadrage est appliquée.
- `moteur/socle/FORMAT.md` — le format de la mémoire.
- `docs/inventaire-chess.md` — ce qui vient du dépôt chess.
- `memoire/archives/cadrage-2026-10-10.md` — le cadrage fondateur, tel quel.
