<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

B-0030, cinq adaptateurs de plus (JavaScript et TypeScript, Go, Java, Ruby,
PHP) : fait et éprouvé sur leurs vrais outils par un banc, mais pas commité.
Le test qui figeait la liste des trois adaptateurs maintenus change de
valeur attendue : D-0013, poussée, demande à Théo de le valider. En
attendant, tout le travail (adaptateurs, lecteurs de mutation, banc, tests,
décision, journal, fait mesuré, deux sujets nouveaux) est remisé dans
`git stash` (« B-0030 travail, attend D-0013 ») : les hooks refusent de le
commiter ou de le laisser dans l'arbre (B-0033).

## Prochaines étapes

1. À la réponse de Théo sur D-0013 : la consigner (`socle answer
   --relayed`), restaurer le stash, commiter avec la dispense de test
   d'`eprouver` (il lance les vrais outils ; le banc l'exerce), `socle ci`,
   pousser.
2. Les sujets que Théo a ouverts pour plus tard : B-0035 (la documentation
   du projet), précédé de B-0034 (le parcours de l'utilisateur) ; puis
   B-0033, B-0037 et B-0038.
