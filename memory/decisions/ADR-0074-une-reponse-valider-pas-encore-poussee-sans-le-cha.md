<!-- socle: couche=decisions zone=publique -->
# ADR-0074 — Une réponse « valider » pas encore poussée sans le changement qu'elle autorise est signalée, pas refusée

> statut : acceptée · date : 2026-11-14 · source : B-0142@e05ad571, D-0071@9b06b40c, ADR-0024@699e330b · lu : decisions@2402f6cc

## Contexte

La CI d'un push et le hook avant push ne comptent que les validations
ajoutées dans leur plage (B-0043@39049de5) : une réponse `valider`
poussée avant le test ou le fichier protégé qu'elle autorise à changer ne
le couvre plus au push suivant, refusé, et l'humain voit sa réponse
consignée deux fois.
C'est arrivé trois fois (B-0142@e05ad571). Faire valoir une validation à
travers les pushes relâcherait `tests.attendus` et `protege.fichiers` :
une demande à l'humain. L'autre face, la gêne 6 de chess : une réponse
gardée hors du dépôt jusqu'à son changement s'affiche « en attente ».

## Décision

**Un contrôle d'avertissement, `demandes.reponse-seule`**, aux étages
agent et git, jamais en CI. Il lit la plage pas encore poussée : depuis
la tête de la branche distante où part le push (au hook avant push), ou
que suit la branche courante, sinon de même nom ; à défaut, depuis le
point de divergence avec la branche par défaut (`base_non_poussee`).
Pour chaque réponse `valider` qu'elle ajoute, il relève ce que la demande
nomme : les tests que juge `tests.attendus`, nommés en mot entier, les
fichiers de cas qu'elle cite, les fichiers protégés qu'elle cite avec une
empreinte sur la même ligne. Si elle en nomme et qu'aucun n'a changé, il
avertit : poussée seule, la réponse ne couvrira pas ce changement ; la
pousser avec lui.

Un test et un fichier de cas se mesurent sur la plage pas encore
poussée : un test ne précède jamais sa réponse (`tests.attendus` le
refuse), et un test changé plus tôt sur la branche, sous une validation
antérieure, ne doit pas faire taire l'avertissement (la revue du lot l'a
trouvé). Un fichier protégé se mesure sur la branche entière : poussé
sous une demande en attente (D-0071@9b06b40c), il précède sa réponse, qui
part ensuite seule sans dommage. Comme une valeur
attendue hors des assertions (ADR-0024@699e330b), c'est dit, pas refusé.

Les hooks avant commit et avant push, qui se taisent quand tout passe,
impriment cet avertissement sur leur sortie d'erreur.

**La réponse se consigne dès qu'elle est donnée.** L'état lit l'arbre,
fichiers non suivis compris : une réponse consignée par `socle answer
--relayed` y est répondue avant son commit. Le gabarit du skill
`socle-request` le dit, et de la commiter et la pousser avec le
changement qu'elle autorise, dans le même tour.

## Conséquences

L'agent est averti avant le push qui le gênerait ; s'il passe outre, le
refus d'après reste celui d'aujourd'hui. La copie protégée du skill
`socle-request` de ce dépôt suit son gabarit sur une demande. Se défait
en retirant le contrôle, ses lignes dans les deux hooks et la phrase du
skill.
