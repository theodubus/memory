<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

B-0032, les chemins en anglais (feu vert de Théo pour B-0029 à B-0032) :
fait, mais pas commité. Le renommage change la valeur attendue de quatorze
tests ; D-0011, poussée, demande à Théo de le valider. En attendant, le
travail est remisé dans `git stash` (« B-0032 travail, attend D-0011 »),
avec sa décision (chemins en anglais) et son entrée de journal : les
hooks refusent de le commiter ou de le laisser dans l'arbre (B-0033).

## Prochaines étapes

1. À la réponse de Théo sur D-0011 : la consigner (`socle answer
   --relayed`), restaurer le stash, commiter avec la dispense de test des
   dix fonctions modifiées que l'auto-test exerce, `socle ci`, pousser ;
   puis donner à Théo les trois commandes qui migrent ce dépôt.
2. B-0029 (privé couche par couche, bascule de l'existant), puis B-0031
   (langue de la mémoire), puis B-0030 (autres adaptateurs).
