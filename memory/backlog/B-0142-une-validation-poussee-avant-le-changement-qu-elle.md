<!-- socle: couche=backlog zone=publique -->
# B-0142 — Une validation poussée avant le changement qu'elle couvre ne le couvre plus : le push de ce changement est refusé

> statut : ouvert · origine : J-2026-11-09-D · priorité : haute · lu : backlog@e83a97a5

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

Fait quand :
- [ ] un test changé sous une validation déjà poussée se pousse sans validation nouvelle, ou l'agent est averti avant de pousser la réponse seule, et un test le montre
