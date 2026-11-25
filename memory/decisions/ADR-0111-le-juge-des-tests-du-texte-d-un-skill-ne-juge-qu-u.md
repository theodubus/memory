<!-- socle: couche=decisions zone=publique -->
# ADR-0111 — Le juge des tests du texte d'un skill ne juge qu'un test qui lit un skill, assertion par assertion, contre les chaînes assemblées du moteur

> statut : acceptée · date : 2026-11-25 · source : ADR-0110@5263f8fb, L-0041@96f53ba2, D-0196@282f8a66, D-0197@490ec951, L-0039@7483c5d1 · lu : decisions@32581597

## Contexte

ADR-0110 laisse passer, en mode amont, un test qui ne perd que des
phrases qu'un gabarit de skill du produit a quittées, et donne pour
fermée la menace (b) : affaiblir le test d'un comportement du moteur sous
couvert du texte d'un skill. La revue adversariale de L-0041 la montre
ouverte de trois façons, chacune éprouvée :

1. Le juge recevait les phrases de toutes les assertions perdues d'un
   test ensemble : une assertion sans phrase (`assertEqual(comportement(),
   2)` passée à 3) passait avec la phrase d'une autre assertion du même
   test, et un test supprimé entier de même.
2. Une phrase d'un gabarit qui sert d'entrée à un test de comportement
   n'est dans aucun module : `tests/test_renommages.py:139` éprouve le
   motif du hook sur la commande `private lock`, que le gabarit de
   `socle-private-memory` cite. Le gabarit changé, ce test se supprimait
   sans validation.
3. Une phrase du moteur se cherchait dans le texte brut de ses modules :
   un message écrit en littéraux concaténés, ou coupé par un paramètre
   (`{x}`), ne s'y retrouvait pas.

## Décision

Le point 3 d'ADR-0110 se précise ainsi :

1. **Le test lit un skill.** Seul un test dont le corps, ou une aide de
   son fichier qu'il nomme, nomme un skill (`SKILL`, `skills`) se juge sur
   le texte des skills. Un test de comportement qui ne lit aucun skill
   garde la règle commune, quelles que soient ses phrases.
2. **Assertion par assertion.** Chaque assertion perdue doit porter ses
   propres phrases, que le juge accepte seules ; une assertion sans phrase
   refuse le test. Un test supprimé : chacune de ses assertions de même,
   puis les phrases de tout son corps ensemble. Les valeurs changées hors
   des assertions ne se taisent que si toutes sont des phrases que le juge
   accepte.
3. **Les chaînes du moteur.** Une phrase est du moteur si elle contient,
   ou est contenue dans, un morceau d'au moins douze caractères d'une
   chaîne d'un module Python du moteur, lue par `ast` : concaténations
   assemblées, f-strings comprises, coupées à leurs paramètres. Un module
   qui ne se lit pas compte en entier. Le moteur est écrit en Python : ce
   n'est pas le langage d'un projet.

## Modèle de menace

La menace (b) d'ADR-0110, telle que la revue l'a ouverte :

Fermé : une valeur de comportement qui accompagne une phrase de skill
dans un même test (refusée, point 2) ; un test de comportement qui ne lit
aucun skill, même si son entrée est une phrase de gabarit (point 1) ; un
message du moteur écrit en plusieurs littéraux ou avec des paramètres
(point 3).

Laissé ouvert, et pourquoi c'est accepté :

- Un test qui lit un skill et qui, dans une même assertion, juge aussi
  un comportement avec une phrase du gabarit : l'assertion porte le texte
  du skill, dont Théo a confié le jugement à l'expérience (D-0197).
- Une aide qui nomme un skill dans un commentaire sans en lire : le test
  doit encore ne perdre que des phrases qu'un gabarit a quittées.
- Une phrase qui chevauche deux morceaux d'un message sans en contenir
  aucun entier : rare, et toute phrase qui contient une commande du moteur
  est déjà tenue pour du moteur, du côté strict.

## Conséquences

Plus strict qu'ADR-0110 : les tests de texte dont une valeur perdue n'est
pas une phrase gardent leur avertissement ou leur refus, et demandent la
validation de Théo comme avant. Rejouée sur la plage de L-0039, la
suppression du test de `socle-batch` que D-0196 avait fait valider passe
toujours seule. Pour défaire : revenir au juge d'ADR-0110.
