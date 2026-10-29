<!-- socle: couche=backlog zone=publique -->
# B-0090 — Un outil de l'adaptateur absent de l'environnement de l'agent ne se dit nulle part avant verify

> statut : fait · origine : J-2026-10-29-L · ref : J-2026-10-29-N · lu : backlog@b8f4fad9

La CI que pose le socle installe les outils de l'adaptateur (ses étapes
`ci_setup` : `pip install pytest mutmut`, `npm ci`, `composer install`…),
mais rien ne dit à l'humain ni à l'agent que l'environnement de l'agent en
a besoin aussi. Dans la session du pilote, l'installation et son audit
passent ; le premier `verify` échoue sur « No module named pytest ». En
session cloud, le conteneur repart de zéro à chaque session : installer
l'outil une fois ne suffit pas, il doit être dans le script d'installation
de l'environnement, un réglage que seul l'humain fait.

L'installation dit, parmi les étapes qui suivent, les commandes que la CI
lance pour ses outils, et où les mettre en session cloud. Un `verify` qui
échoue faute d'outil (code 127, ou « No module named ») le dit, avec ces
mêmes commandes.
