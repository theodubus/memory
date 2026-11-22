<!-- socle: couche=demandes zone=publique -->
# D-0156 — B-0320, B-0321 et B-0322, sans tâche faute de preuve vue en session : abandonnés sous ADR-0098, sortis de JA-0005, ou gardés ?

> date : 2026-11-22 · forme : séance

## Question posée

Posée à Théo dans la conversation le 22 novembre, après la formation des lots de JA-0005 (J-2026-11-21-Q) : trois besoins de JA-0005 restent sans tâche, leur correction touchant le hook de l'agent sans preuve vue en session (ADR-0098) ; tant qu'ils sont ouverts, JA-0005 ne se ferme pas. Pour chacun : a. l'abandonner en renvoyant à ADR-0098, un besoin se rouvrant si le défaut se voit en session ; b. le sortir de JA-0005, en attente d'une preuve, comme B-0048 ; c. le garder dans JA-0005 et lever ADR-0098 pour lui.

1. B-0320 : pousser sous un autre nom de branche la réécriture de ce qu'une branche a poussé la juge comme neuve ; un contournement exprès, que son « Satisfait quand » permet de clore par une décision qui accepte ce risque, ce que vaut a. Recommandation : a.
2. B-0321 : en session cloud, le hook de fin de tour de l'environnement ne vérifie pas le push d'un tour relancé par un hook, ni d'une branche jamais poussée. Recommandation : a.
3. B-0322 : une branche abandonnée sans fusion, repartie sous le même nom, est refusée au push sans sortie qui marche en session cloud. Recommandation : a.

Réponses : `valider` (les trois recommandations, a pour chacun), `refuser`, `contexte-insuffisant`, ou un choix par besoin.
