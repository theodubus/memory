<!-- socle: couche=decisions zone=publique -->
# ADR-0076 — Une réponse « valider » pas encore poussée sans le changement qu'elle autorise est signalée, pas refusée : une clé des garde-fous se suit comme un test, et le contrôle qui plante avertit

> statut : acceptée · date : 2026-11-14 · source : ADR-0074@4eeb99c5, B-0215@361bbd0e, B-0216@ae4f7f09, D-0111@034d5e87, D-0040@308c950b, D-0071@9b06b40c, ADR-0024@699e330b · lu : decisions@b1d7ba83

## Contexte

La CI d'un push et le hook avant push ne comptent que les validations
ajoutées dans leur plage (B-0043@39049de5) : une réponse `valider` poussée avant
le changement qu'elle autorise ne le couvre plus au push suivant, refusé,
et l'humain voit sa réponse consignée deux fois. ADR-0074 en a fait un
avertissement, `demandes.reponse-seule`. Sa revue (J-2026-11-14-D@9e26ceef) y a
trouvé deux manques que l'usage normal rencontre, gardés par D-0111 :
une clé des garde-fous, que seule une réponse `valider` autorise aussi à
relâcher (D-0040), n'était pas suivie, alors que `cliquet.garde-fous` ne
compte lui aussi que les validations de sa plage ; et une exception du
contrôle serait devenue une erreur, qui refuse le commit, le push ou la
fin du tour. Les textes disaient aussi « dans le même tour », quand seul
« dans le même push » est juste : deux pushes dans un même tour restent
refusés (B-0216). Cette décision reprend ADR-0074 entière, et la
remplace.

## Décision

**Un contrôle d'avertissement, `demandes.reponse-seule`**, aux étages
agent et git, jamais en CI. Il lit la plage pas encore poussée : depuis
la tête de la branche distante où part le push (au hook avant push), ou
que suit la branche courante, sinon de même nom ; à défaut, depuis le
point de divergence avec la branche par défaut (`base_non_poussee`).
Pour chaque réponse `valider` qu'elle ajoute, il relève ce que la demande
nomme : les tests que juge `tests.attendus`, nommés en mot entier ; les
fichiers de cas qu'elle cite ; les clés des garde-fous qu'elle cite comme
`cliquet.garde-fous` les reconnaît, la clé citable en toutes lettres
(D-0040), parmi celles des garde-fous avant et après, celles qui ont une
valeur par défaut et celles que les règles du cliquet nomment sans
motif ; les fichiers protégés qu'elle cite avec une empreinte sur la même
ligne. Si elle en nomme et qu'aucun n'a changé, il avertit : poussée
seule, la réponse ne couvrira pas ce changement ; la pousser avec lui,
dans le même push.

Un test, un fichier de cas et une clé des garde-fous se mesurent sur la
plage pas encore poussée : aucun ne précède sa réponse (`tests.attendus`
et `cliquet.garde-fous` le refusent), et un test changé plus tôt sur la
branche, sous une validation antérieure, ne doit pas faire taire
l'avertissement. Un fichier protégé se mesure sur la branche entière :
poussé sous une demande en attente, là où la CI du socle est exigée
(D-0071), il précède sa réponse, qui part ensuite seule sans dommage.
Comme une valeur attendue hors des assertions (ADR-0024), c'est dit, pas
refusé.

**Le contrôle qui plante avertit.** Une exception levée dans le contrôle
devient un avertissement qui la nomme, jamais l'erreur qu'en ferait le
lanceur des contrôles : un avertissement ne refuse ni le commit, ni le
push, ni la fin du tour. Le moyen se tient dans le contrôle seul ; tout
autre contrôle qui plante échoue, comme avant.

Les hooks avant commit et avant push, qui se taisent quand tout passe,
impriment cet avertissement sur leur sortie d'erreur.

**La réponse se consigne dès qu'elle est donnée.** L'état lit l'arbre,
fichiers non suivis compris : une réponse consignée par `socle answer
--relayed` y est répondue avant son commit. Le gabarit du skill
`socle-request` le dit, et de la commiter et la pousser avec le
changement qu'elle autorise, dans le même push ; et qu'un fichier
protégé peut la précéder, poussé sous la demande en attente.

Restent hors du contrôle, écartés par D-0111 comme cas exotiques d'un
simple avertissement : la base non poussée de HEAD détaché, d'une branche
distante élaguée ou suivie ailleurs, d'un push d'une autre branche ; un
test nommé par sa description ; un fichier protégé cité par un lien
Markdown.

## Conséquences

L'agent est averti avant le push qui le gênerait, pour une clé des
garde-fous comme pour un test ; s'il passe outre, le refus d'après reste
celui d'aujourd'hui. Une demande qui cite une clé en passant, sans la
relâcher, fait avertir à tort tant que rien de ce qu'elle nomme ne
change : c'est un avertissement. La copie protégée du skill
`socle-request` de ce dépôt suit son gabarit sur une demande. Se défait
en retirant le contrôle, ses lignes dans les deux hooks et la phrase du
skill ; la clé des garde-fous, en retirant ses candidates de la liste de
ce que la demande nomme.
