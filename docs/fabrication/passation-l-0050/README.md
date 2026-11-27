# Passation du lot L-0050, en attente de D-0227

`l-0050.patch` porte le travail du lot L-0050 (B-0364) qui ne se commite
qu'après la réponse de Théo à D-0227 : le rendu A2-d de
`engine/socle/roadmap.py`, ses tests dans `tests/test_suite_du_projet.py`,
et ce qui le dit (T-0208), soit 22 tests supprimés, 5 changés, 1 déplacé
et 19 nouveaux. Le garder ici le met à l'abri si la session perd son
conteneur.

D-0227 validée, depuis la racine du dépôt :

```sh
git apply docs/fabrication/passation-l-0050/l-0050.patch
```

Puis ce dossier se retire dans le commit qui livre le code et les tests.
