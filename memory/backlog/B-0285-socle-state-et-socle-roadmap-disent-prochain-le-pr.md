<!-- socle: couche=backlog zone=publique -->
# B-0285 — socle state et socle roadmap disent prochain le premier jalon par son identifiant, pas celui que sert le lot en cours, et ne signalent pas deux lots qui n'ont aucun ordre entre eux

> statut : ouvert · origine : J-2026-11-18-L · lu : backlog@95e12a28

Relevé par la revue de L-0014, passe 1 (J-2026-11-18-L), constat 4 pour
le backlog. Le prochain jalon est le premier ouvert qu'aucun autre ne
précède (D-0123, point 2) ; sans `après` entre eux, le premier par
identifiant : `socle state` et `socle roadmap` disent « JA-0002 … le
prochain », quand le lot en cours, L-0014, sert JA-0005, le jalon en cours
(D-0118). `socle roadmap` signale deux lots qui attendent un même lot sans
ordre entre eux, mais ni deux lots sans `après` du tout, rangés par
identifiant (`engine/socle/roadmap.py`, vers les lignes 129 et 147), ni
deux jalons sans ordre. À trancher avec Théo, la règle du prochain jalon
étant la sienne : le prochain jalon se déduit-il du travail en cours, ou
d'un ordre qu'il écrit ?

## Satisfait quand

- [ ] le prochain jalon que disent l'état et la suite est celui que sert le travail en cours, ou leur ordre ambigu est signalé
- [ ] deux lots ouverts sans ordre entre eux, qu'ils attendent un même lot ou rien, sont signalés
