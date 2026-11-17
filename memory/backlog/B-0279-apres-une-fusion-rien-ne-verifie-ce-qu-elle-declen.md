<!-- socle: couche=backlog zone=publique -->
# B-0279 — Après une fusion, rien ne vérifie ce qu'elle déclenche : un déploiement ou une publication en échec passe inaperçu

> statut : ouvert · origine : J-2026-11-17-H · ref : D-0129, B-0200 · lu : backlog@1df796e8

Théo veut dans le produit (D-0129), sous une forme générale, ce que le
skill `delegate-lot` fait dans l'atelier : après la fusion, vérifier que
la distribution a tourné. Dans un projet, la fusion sur la branche par
défaut peut lancer un déploiement ou une publication ; s'il échoue,
rien ne le dit à l'humain, et l'agent est passé au lot suivant.

La vérification n'a de sens que si l'agent fusionne lui-même : c'est
l'option de B-0200 (la fusion par l'agent, que l'humain active), au même
lot. Le récap dit si les workflows lancés par la fusion ont réussi.

## Satisfait quand

- [ ] après une fusion par l'agent, l'humain apprend dans le récap si ce qu'elle a déclenché a réussi
