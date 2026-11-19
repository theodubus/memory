<!-- socle: couche=backlog zone=publique -->
# B-0303 — Une tâche qui change ce qu'un test affirme nomme ce test dès sa création, et la demande se pose avant le lot, non en son milieu (D-0141)

> statut : ouvert · origine : J-2026-11-19-AJ · ref : D-0141, D-0140, D-0139, L-0019, L-0005 · lu : backlog@bc88ec02

Théo a retenu le 19 novembre la proposition 2 (D-0141, J-2026-11-19-AJ).
T-0002 et T-0106 ont été écrites sans chercher si un test affirmait le
contraire de leur « Fait quand » ; le conflit n'est apparu qu'aux tests
du sous-agent, au milieu de L-0019, qui s'est arrêté, a fait poser
D-0140 dans l'urgence et passer le lot à une session neuve
(J-2026-11-19-AI). L-0005 avait connu le même arrêt avec D-0139.

La règle retenue : quand l'agent écrit une tâche dont le « Fait quand »
dit qu'une commande est refusée ou qu'elle passe, ou plus généralement
ce qu'un comportement doit devenir, il cherche dans les tests ce qui
affirme le contraire ; il nomme ce test dans la tâche et pose la demande
aussitôt, avant que le lot commence. Seul l'ordre change ; c'est une
méthode de travail, que l'agent écrit dans le skill des lots et là où
une tâche s'écrit.

## Satisfait quand

- [ ] une tâche dont le critère contredit la valeur attendue d'un test existant nomme ce test dès sa création, et sa demande est posée avant le lancement du lot, comme le skill `socle-batch` le dit
