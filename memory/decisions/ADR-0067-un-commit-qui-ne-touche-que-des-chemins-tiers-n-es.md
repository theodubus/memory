<!-- socle: couche=decisions zone=publique -->
# ADR-0067 — Un commit qui ne touche que des chemins tiers n'est pas un commit du projet

> statut : acceptée · date : 2026-11-11 · lu : decisions@d48ef38a

## Contexte

Sur chess, d'autres sessions d'agents travaillent un sous-dossier sans les
hooks ni les règles du socle ; leurs commits sont co-signés par un agent.
ADR-0031@f8881477 retire les fichiers tiers des listes de fichiers, pas
des commits : mesuré (J-2026-11-11-T@609458b5), `hooks.trace` refuse un commit
qui ne touche que ui/** déclaré tiers, et fait échouer leur pull
request au travail de CI du socle (B-0169@66f32baa).

## Décision

Amende ADR-0031. Un commit à un parent dont tous les fichiers changés
sont tiers n'est pas un commit du projet : le contexte des contrôles le
retire de la liste qu'ils jugent par commit (la trace des hooks, les
dispenses de test). Un commit qui touche aussi un fichier du projet reste
jugé en entier ; une fusion, un commit vide ou le premier aussi. Le
correctif tiers reste averti (D-0088@bf8c3a4b), et la fuite de la mémoire privée
dans un message reste jugée, le message se publiant. Un défaut injecté
(commit d'agent sans trace qui touche ui/ et la mémoire, refusé) et un
témoin (le même, sur ui/ seul, passe la CI) l'éprouvent.

## Conséquences

Les pull requests d'agents qui ne connaissent pas le socle passent son
travail de CI tant qu'elles restent sous les chemins tiers ; le guide dit
les deux limites et leur réglage, et que déclarer un chemin tiers dispense
aussi de la trace les commits qui ne touchent que lui. Conséquence assumée,
relevée par la revue : une session de l'agent du projet démarrée sans
hooks peut pousser des commits sous un chemin tiers sans que la CI le voie ;
ces commits ne touchent que des fichiers qu'aucun contrôle ne juge. Pour défaire : rendre `commits` aux deux
contrôles.
