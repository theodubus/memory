<!-- socle: couche=decisions zone=publique -->
# ADR-0035 — En session cloud, le hook de démarrage installe les outils de l'adaptateur

> statut : acceptée · date : 2026-10-29 · source : D-0048@a6311d88 · lu : decisions@d14040a2

## Contexte

La session cloud du pilote n'avait pas pytest : la CI que pose le socle
l'installe, mais le conteneur de l'agent repart de zéro à chaque session.
B-0090@97cfaf07 a fait dire l'outil manquant, à l'installation et dans `verify` ;
restait un geste à refaire dans chaque environnement, le script
d'installation, ou une installation par l'agent à chaque session. Théo a
répondu « oui » à la proposition de rendre cette installation automatique
(D-0048), en notant que Claude Code installe d'ordinaire ses outils de
lui-même.

## Décision

- **En session cloud seulement** (Claude Code y pose
  `CLAUDE_CODE_REMOTE=true`), le hook de démarrage du socle lance, avant
  d'imprimer l'état, les commandes que la CI lance pour les outils de
  l'adaptateur : ses étapes `ci_setup`, déjà maintenues pour la CI. Sur la
  machine de l'humain, rien ne s'installe.
- **Une fois par conteneur** : une marque, dans le répertoire git commun à
  côté de la trace des hooks, garde l'empreinte des commandes réussies ;
  une reprise ou un compactage ne les relance pas, une session neuve si.
- **Un échec ne bloque pas le démarrage** : l'agent lit la commande, son
  code et la fin de sa sortie, sous l'état ; la commande se retente à la
  session suivante.
- Le délai du hook de démarrage passe de 30 à 300 secondes, les commandes
  ayant 270 secondes en tout.
- Ce qui dépend de l'agent reste dans les hooks, ce qui dépend du langage
  dans l'adaptateur : le moteur n'apprend ni l'un ni l'autre.

## Conséquences

- Mesuré : `pip install pytest mutmut` sans cache prend environ sept
  secondes dans un conteneur cloud ; c'est le coût d'une session neuve
  pour un projet sous `python-pytest`.
- La session qui installe le socle n'a pas eu ce démarrage : elle installe
  les outils elle-même, et l'installeur le dit.
- Une commande qui dépend du projet (`npm ci`, `composer install`) échoue
  tant que le projet n'a pas son manifeste ; elle le dit à chaque session
  neuve, sans rien bloquer.
- Défaire : retirer l'appel du hook de démarrage, et remettre son délai.
