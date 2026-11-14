<!-- socle: couche=decisions zone=publique -->
# ADR-0080 — Le modèle de menace du hook de l'agent : les erreurs d'un agent coopératif, et ce que rien ne rattrape

> statut : acceptée · date : 2026-11-14 · source : D-0112@c8501606, J-2026-11-14-M@567221ed, ADR-0072@1a8b5c2d, ADR-0073@1e48220c, D-0111@034d5e87, B-0206@2ebfe7b8, B-0208@59067330 · lu : decisions@35ba5f6e

## Contexte

Pour deviner ce qu'une commande fera, le hook de l'agent relit le langage
du shell, qui a une infinité de formes : chaque revue en trouve de
nouvelles, et chaque correction en ouvre d'autres (ADR-0072@1a8b5c2d,
trente contournements en deux revues). ADR-0072 dit ce que le
hook juge, et qu'il refuse ce qu'il ne sait pas juger ; elle ne dit pas
quels trous méritent un sujet. Le backlog grossissait plus vite qu'il ne se
vidait, et les trous du hook en sont une des deux sources qui ne
s'arrêtent pas seules ; l'autre, les remarques non bloquantes des revues,
a sa règle à part (la règle 1 de D-0112@c8501606, après D-0111@034d5e87).
Théo a validé l'une et l'autre le 14 novembre (J-2026-11-14-M@567221ed).

## Décision

Cette décision complète ADR-0072, et le guide d'un projet équipé l'écrit.
Le texte de la règle 2 de D-0112, tel que Théo l'a validé :

> Le hook de l'agent arrête les erreurs d'un agent coopératif avant
> qu'elles agissent. Il juge les formes du shell qu'un agent écrit dans
> son travail, et, quelle qu'en soit la forme, ce que rien ne rattrape
> ensuite : supprimer le projet ou un dossier qui le contient, une action
> externe irréversible, une fuite de la mémoire privée (la part de la
> mémoire qui ne se publie pas) dans ce qui se publie. Une écriture d'un
> fichier protégé sous une forme qu'on n'écrit que pour contourner (un
> `eval`, `IFS`, un chemin construit au vol dans un autre langage) est
> hors de son modèle : `protege.fichiers` la refuse ensuite, et un trou de
> cette sorte n'ouvre pas de sujet.

Elle ne change aucun code : le hook refuse toujours ce qu'il sait refuser,
et ce qu'il ne sait pas juger (ADR-0072, point 6). Elle dit seulement quels
trous se corrigent. Un sujet du hook écrit son modèle de menace, dans une
section « Modèle de menace », borné à cette règle ; la revue le juge contre
lui (ADR-0073@1e48220c).

## Conséquences

- Un trou par lequel passe la suppression du projet ou d'un dossier qui le
  contient, une action externe irréversible ou une fuite de la mémoire
  privée ouvre un sujet, quelle qu'en soit la forme : rien ne rattrape son
  effet (B-0208@59067330, de priorité haute).
- Un trou par lequel passe l'écriture d'un fichier protégé ouvre un sujet
  si la forme est de celles qu'un agent écrit dans son travail ; sous une
  forme qu'on n'écrit que pour contourner, il n'en ouvre pas, et la revue
  l'écarte. Un écrivain que le hook ne sait pas lire (`python -c`) se juge
  par les chemins protégés qu'il cite en toutes lettres (B-0206@2ebfe7b8).
- Les risques acceptés qu'ADR-0072 énumère restent acceptés, et la règle
  dit lesquels gardent un sujet : ceux qui ne laissent passer qu'une
  écriture d'un fichier protégé sous une forme de contournement n'en
  méritent pas ; la revue d'un lot du hook le dit pour chacun.
- Pour défaire : c'est une décision de Théo ; une demande nouvelle, qui la
  remplace.
