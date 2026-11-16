<!-- socle: couche=backlog zone=publique -->
# B-0142 — Une validation poussée avant le changement qu'elle couvre ne le couvre plus : le push de ce changement est refusé

> statut : fait · origine : J-2026-11-09-D · priorité : haute · lu : backlog@e83a97a5 · ref : J-2026-11-14-C

La CI d'un push, et le hook avant push qui la reproduit, ne comptent que
les validations ajoutées dans la plage du push (B-0043) : une validation
ancienne ne couvre pas une assertion réécrite plus tard. Mais l'ordre
naturel du travail les sépare : la réponse de l'humain arrive, l'agent la
consigne et la pousse pour qu'elle ne vive pas que dans le conteneur
(B-0140), tandis que le test qu'elle couvre attend la revue adversariale
de son lot. Au push suivant, le test change sans validation dans la plage :
refusé, alors que la CI de la pull request, contre la branche par défaut,
l'accepte. C'est arrivé pour D-0083 : sa réponse poussée en 37b53f1, les
deux tests qu'elle nomme commités après la revue, le push refusé.

Pistes : le skill `socle-request` dit de ne pousser une réponse qu'avec
les changements qu'elle couvre ; ou une validation couvre, à travers les
pushes, le premier changement du test qu'elle nomme ; ou le hook avant
push le signale au push de la réponse. La deuxième touche la rigueur de
`tests.attendus` : une demande.

Le cas s'est reproduit deux jours de suite : pour des fichiers protégés le
11 novembre (D-0103), pour une valeur attendue le 12 (D-0105,
J-2026-11-12-H). Chaque fois, la réponse de l'humain a dû être consignée
une seconde fois. B-0191, ouvert ce jour-là sans voir ce sujet, en était
le doublon ; sa piste : lire les validations depuis la branche par défaut,
comme les renommages des clés de l'adoption (B-0189).

Le 13 novembre, la mise à jour de chess montre l'autre face de la règle
« commiter la réponse avec le changement qu'elle autorise » : tant que la
réponse validée dans la conversation (D-0009 de chess) n'est pas
commitée, l'état l'affiche « en attente » à l'humain, qui l'a déjà donnée
(`docs/fabrication/chess/mise-a-jour-2026-11-13.md`, gêne 6, J-2026-11-13-D).
La solution doit tenir les deux : ni push refusé, ni réponse donnée
affichée comme attendue.

## Modèle de menace

Le garde-fou est un avertissement, `demandes.reponse-seule` (ADR-0074) ;
la rigueur de `tests.attendus` et de `protege.fichiers` ne change pas.

Ce qu'il arrête : l'agent distrait qui consigne la réponse `valider`
d'une demande et la pousse seule, avant le changement qu'elle autorise.
Quand la plage pas encore poussée (depuis la tête de la branche distante,
sinon depuis la branche par défaut) ajoute cette réponse, qu'elle nomme
un test que juge `tests.attendus`, un fichier de cas ou un fichier
protégé cité avec son empreinte, et que la branche ne change encore aucun
d'eux, il le dit : dans `verify --fast`, au commit et avant que le push
parte, sur la sortie d'erreur du hook. Le push refusé du changement, plus
tard, ne vient plus par mégarde.

Ce qu'il laisse passer : c'est un avertissement, pas un refus. L'agent
qui pousse quand même la réponse seule le peut ; le push du changement
reste refusé, comme avant (B-0043), et la réponse se consigne une seconde
fois. Une réponse qui change au moins une des choses qu'elle nomme passe,
même si elle en nomme d'autres qui changeront plus tard.

Ce qu'il ne voit pas : une réponse déjà poussée, hors de la plage ; un
test nommé autrement qu'en toutes lettres, un fichier protégé cité sans
son empreinte sur la même ligne ; hors du hook avant push, un push vers
une autre branche distante que celle que suit la branche courante. Un
changement déjà sur la branche, poussé sous une demande en attente
(D-0071), n'est pas un oubli : la réponse qui le suit seule ne déclenche
rien. Le hook de fin de tour le calcule sans l'afficher quand tout passe ;
l'agent le lit dans `verify --fast`.

L'autre face, la gêne 6 de chess : l'état lit l'arbre, fichiers non
suivis compris ; une réponse consignée aussitôt par `socle answer
--relayed` y est répondue avant son commit. Le gabarit du skill
`socle-request` dit de la consigner dès qu'elle est donnée, puis de la
commiter et de la pousser avec le changement qu'elle autorise.

## Satisfait quand

- [x] un test changé sous une validation déjà poussée se pousse sans validation nouvelle, ou l'agent est averti avant de pousser la réponse seule, et un test le montre
