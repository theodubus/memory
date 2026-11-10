<!-- socle: couche=decisions zone=publique -->
# ADR-0055 — Une branche jetable : la CI ne la juge pas aux envois, sa pull request la juge en entier

> statut : acceptée · date : 2026-11-10 · validation : D-0087@0aa35990 · source : B-0137@136fdbb3, ADR-0031@f8881477, J-2026-11-09-U@eecea2d0, J-2026-11-10-A@9cedfefe · lu : decisions@c402f950

## Contexte

Une branche d'essai était jugée comme la branche de travail : la CI du
socle tournait à chaque envoi, et un correctif de prototype la faisait
échouer ; un fichier d'un outil tiers copié dans la branche voyait ses
liens morts refusés dès le commit, et le déclarer tiers attendait une
validation humaine, même pour une branche jamais fusionnée (B-0137). Le
cadrage revenait à Théo (D-0087). Il a demandé si une branche ainsi
déclarée pouvait être temporairement non conforme, puis jetée ou fusionnée
sous les règles strictes ; je lui ai répondu oui, à la nuance près que les
contrôles locaux y restent (J-2026-11-09-U), et il a validé les hypothèses
(J-2026-11-10-A). Elles sont notées supposées, comme la demande le
prévoyait : une intention que l'usage confirmera ou corrigera.

## Décision

1. *Ce qu'est une branche jetable.* Une branche dont le nom commence par
   un préfixe que le projet déclare dans ses garde-fous,
   `[branches] disposable`, `proto/` à défaut. En ajouter un préfixe
   assouplit, et attend donc une demande validée ; en retirer durcit ;
   écrire le défaut tel quel ne change rien.
2. *La CI.* Le workflow de CI que pose l'installeur écarte ces branches des
   envois (`branches-ignore`) ; une pull request qui part de l'une d'elles
   lance la CI, qui la juge en entier. Le hook avant push ne juge pas comme
   la CI la plage qu'envoie une branche jetable.
3. *Les contrôles locaux.* Ceux d'avant commit et de la session de l'agent
   restent, sauf le contrôle des références sur un fichier que la branche
   ajoute, absent de la base : ses fautes y sont des avertissements, hors
   de la CI seulement.
4. *Les fichiers tiers.* Les déclarer attend toujours une validation ; sur
   une branche jetable, la règle 3 rend la déclaration inutile.
5. *La fusion.* Une branche jetable se fusionne par une pull request, dont
   la CI juge toute la plage, commit par commit ; la protection de la
   branche par défaut, qui exige la CI du socle, bloque la fusion tant
   qu'elle est rouge.

## Conséquences

Le workflow d'un projet change à la mise à jour, un fichier protégé
qu'approuve l'humain. Changer les préfixes demande de relancer
l'installeur, pour que le workflow les suive. Ce que rien ne garde : un
agent qui nommerait jetable une branche de vrai travail ; sa pull request
la rejuge en entier, et la fusion l'exige. La défaire :
`Projet.branches_jetables` dans `engine/socle/config.py`, et ses tests
dans `tests/test_branches_jetables.py`.
