<!-- socle: couche=demandes zone=publique -->
# D-0004 — Accepter qu'une assertion tautologique passe quand une raison écrite l'accompagne

> date : 2026-10-10 · bloque : rien, l'échappatoire est en place et visible en attendant

## Décision demandée

Garder ou retirer l'échappatoire « `socle: voulu — <raison>` » qui laisse
passer une assertion du type `f(x) == f(x)` quand un commentaire en donne la
raison.

## Contexte

Le cadrage classe parmi les tests creux « l'assertion tautologique du type
f(x) == f(x) ». En essayant le socle sur chess, le contrôle a signalé le test
`la_recherche_est_deterministe`, qui appelle deux fois la recherche sur la
même position et compare les deux coups : c'est exactement `f(x) == f(x)`, et
c'est un vrai test, puisqu'une recherche non déterministe le ferait échouer.

J'ai donc ajouté une échappatoire, sur le modèle de la règle des tests
désactivés : la tautologie passe si la ligne, ou celle d'avant, porte un
commentaire « socle: voulu — » suivi d'une raison. C'est un assouplissement
d'une règle du cadrage, donc il te revient (point 1 de la politique). Il est
en place, mais visible : dans le code, dans le message du contrôle, et dans
un témoin de l'auto-test.

## Éléments cités

- `la_recherche_est_deterministe` — le test de chess, dans le module de recherche, qui compare deux recherches identiques.
- `moteur/socle/controles_tests.py` — le module du moteur qui détecte les tests creux et porte l'échappatoire.

## Options

- **Garder l'échappatoire** : effort nul ; risque faible, un agent pourrait
  justifier une vraie tautologie, mais la raison est écrite et visible en
  revue ; réversible en retirant une ligne.
- **La retirer** : effort de dix minutes ; risque nul pour le cadrage, mais
  chess devra réécrire son test de déterminisme sous une autre forme, par
  exemple en comparant à un coup attendu fixé ; réversible.
- **La garder sous condition** : par exemple, exiger que le nom du test
  contienne « determin » ; effort d'une heure ; risque de rigidité ;
  réversible.

## Conséquences

Si tu valides, l'échappatoire reste et la règle des tests creux du cadrage
est précisée en ce sens. Si tu refuses, je la retire, avec son témoin, et je
note dans l'inventaire que le test de chess doit changer. Sans réponse,
l'échappatoire reste en place, signalée par cette demande dans l'état
dérivé à chaque démarrage.

## Recommandation

Garder l'échappatoire. Vérifié : le test de chess est légitime, et
l'auto-test montre qu'une tautologie sans raison reste refusée alors qu'une
tautologie avec raison passe. Supposé : qu'un agent n'abuse pas de
l'échappatoire — rien ne le mesure, seule la revue le voit.

## Réponses possibles

- `valider` — l'échappatoire reste.
- `refuser` — je la retire.
- `conditionner` — le texte de ta réponse dit la condition.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit.
