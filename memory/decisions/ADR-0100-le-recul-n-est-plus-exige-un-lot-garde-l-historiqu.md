<!-- socle: couche=decisions zone=publique -->
# ADR-0100 — Le recul n'est plus exigé : un lot garde l'historique de ses passes et leurs bloquants, sans recul, sans marque de cause ni arrêt par demande

> statut : acceptée · date : 2026-11-20 · validation : D-0144 · source : ADR-0084@df557d83, D-0144@3ca5d3d1, B-0309@3c791fc4, T-0110@e02d5335, J-2026-11-20-C@5af55283, J-2026-11-20-D@f3bd4040, ADR-0098@3081a5ed, D-0128@fd7c9ad7, T-0060@4ff7dafb · lu : decisions@1bc25f37

## Contexte

ADR-0084@df557d83 a posé l'historique des passes de revue d'un lot dans
sa section `## Revues`, et un recul écrit avant chaque passe au-delà de
la première et à la clôture, avec le regard du relecteur sur chaque
bloquant et l'arrêt sur une demande. Mesuré le 20 novembre
(J-2026-11-20-C@5af55283) : quatorze passes sur neuf lots, quatorze
reculs, tous « continuer », aucun arrêt ; celui de L-0019@4a8f5475 a décrit la
boucle du hook et conclu « continuer ». Par construction, le recul pose
la question à l'agent qui veut finir son lot, pour une passe de plus, et
une boucle d'un lot à l'autre lui échappe (ADR-0098@3081a5ed). Il coûte
un paragraphe de soixante mots à chaque passe et à chaque clôture,
refusé par l'outil s'il manque, environ 120 lignes du moteur dans neuf
modules, et il part dans chaque projet installé (B-0309@3c791fc4). Théo
a validé son retrait (D-0144@3ca5d3d1, J-2026-11-20-D@f3bd4040).

## Décision

ADR-0084 telle qu'écrite, sauf ce qui suit.

1. *Plus de recul.* `socle review` écrit la passe suivante sans exiger
   de la précédente un paragraphe « Recul : », et le contrôle du backlog
   laisse se clore `fait` un lot relu sans lui. Les points 3 à 6
   d'ADR-0084 se retirent : le recul, sa forme et sa décision, la règle
   des deux passes où une même cause revient, et l'arrêt sur une
   demande, que levait seule la réponse de l'humain.
2. *Plus de marque de cause.* Aucun bloquant n'a à porter le regard du
   relecteur (`· même cause`, `· cause nouvelle`). Le dossier d'une passe
   au-delà de la première est celui de toute passe : il ne donne plus au
   relecteur les causes des passes d'avant, ni la consigne de les
   comparer (le point 8 d'ADR-0084, pour sa part du second regard).
3. *Ce qui reste d'ADR-0084.* La section `## Revues`, la dernière de
   l'entrée du lot ; une passe par dossier de `socle review`, son titre,
   sa date et sa ligne `Commits`, avec l'empreinte de l'arbre de travail
   qu'elle a relu ; la même passe redonnée tant que rien ne change hors
   de la mémoire ; le lot en cours ou celui que `--batch` nomme (point
   7) ; les lignes `- Bloquant : <sa cause>` et `- Ouvre : <les entrées
   que la passe ouvre>` que l'agent consigne, qui servent à une session
   neuve qui reprend le lot. Le contrôle du backlog refuse encore, à tout
   statut, une ligne qui se donne pour un bloquant sans cette forme :
   l'historique ne la compterait pas parmi les bloquants de sa passe.
4. *Ce qu'un lot a déjà écrit.* Un paragraphe de recul et une marque de
   cause écrits avant cette décision restent dans le lot et se lisent
   comme du texte ; une marque fait alors partie de la cause du bloquant.
5. *Le tri des constats* bloquant, pour le backlog ou écarté ne change
   pas. Sa catégorie des formes du shell sort du produit par
   T-0060@4ff7dafb, selon D-0128@fd7c9ad7, hors de cette décision.
6. Rien ne remplace le recul : contre une boucle d'un lot à l'autre, la
   protection est la règle de preuve d'ADR-0098.

## Modèle de menace

Ce que le garde-fou retiré arrêtait, et qui passe désormais : une passe
de plus, ou la clôture `fait`, sans recul écrit ; un « continuer » après
deux passes où le relecteur a vu une même cause revenir ; une passe ou
une clôture pendant qu'un arrêt attend la réponse de l'humain. Mesuré,
il n'en a arrêté aucun en quatorze reculs. Ce qui reste arrêté : une
ligne de bloquant que l'historique ne lit pas ; un lot qui livre du code
sans revue, que le skill `socle-batch` exige. Un agent hostile n'est pas
dans le modèle.

## Conséquences

Se retirent : les fonctions du recul dans `engine/socle/memory.py`
(`refus_de_la_suite`, `refus_du_recul`, `decision_du_recul`,
`leve_l_arret`, et leurs aides), le refus de `socle review` et le
contrôle de la clôture, le second regard du dossier, ce que montrait le
refus (les entrées ouvertes et closes depuis le début du lot, les lots
voisins, les trois questions), les cinq mots du vocabulaire de la
section (`meme-cause`, `cause-nouvelle`, `recul`, `continuer`,
`s-arreter`), leurs messages, huit défauts injectés et quatre témoins.
Les skills `socle-review` et `socle-batch`, le guide et le format ne le
disent plus, dans les deux langues ; les copies protégées de ce dépôt
attendent leur remise (T-0072@f84a75da), chess le reçoit à sa mise à
jour. Les
tests qui fixaient le recul ne se retirent ou ne changent que sous une
demande validée qui les nomme. Défaire : une décision qui rétablit
ADR-0084 ; les passes écrites d'ici là n'ont pas de recul, et la
première passe d'après se jugerait sur lui.
