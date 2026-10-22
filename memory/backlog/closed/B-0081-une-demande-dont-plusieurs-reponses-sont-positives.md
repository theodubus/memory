<!-- socle: couche=backlog zone=publique -->
# B-0081 — Une demande dont plusieurs réponses sont positives ne valide rien

> statut : fait · origine : J-2026-10-20-U · ref : D-0040 · lu : backlog@09b7dcc5

D-0033 offrait `tout`, `compatibilite-seule` et `refuser` ; Théo a répondu
`tout`, qui autorise la suppression des tests qu'elle nomme, mais le moteur
ne reconnaît comme validée qu'une demande répondue `valider`
(`Demande.validee`). La réponse ne débloquait donc ni `tests.attendus`, ni
le cliquet, ni les fichiers protégés, et il a fallu reposer la question
(D-0035). Deux voies : le lint d'une demande refuse des réponses possibles
dont aucune n'est `valider` quand elle annonce un geste que seule une
validation autorise (suppression de test, assouplissement) ; ou une
demande déclare lesquelles de ses réponses valident. La seconde touche à
ce qui autorise l'agent : elle se décide avec Théo.
