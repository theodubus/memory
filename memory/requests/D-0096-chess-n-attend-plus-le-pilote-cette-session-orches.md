<!-- socle: couche=demandes zone=publique -->
# D-0096 — chess n'attend plus le pilote ; cette session orchestre, des sous-agents sur Opus implémentent, la session de chess installe le socle

> date : 2026-11-11 · forme : séance

## Question posée

Après la consigne de Théo sur les modèles (D-0095), l'agent lui a posé
deux questions dans la conversation : sur quel compte se font les
implémentations du socle, celui-ci approchant de sa limite de la semaine ;
et ce que devient la porte de chess (ADR-0057), qui attend deux journées
de travail du pilote JustCook, en pause.

Ce que l'agent retient de la réponse de Théo. chess n'attend plus le
pilote : les lots importants et les corrections du socle se livrent,
puis le socle s'installe sur chess. Cette session, sur Fable, orchestre
et planifie, et lance des sous-agents sur Opus pour les lots à livrer
avant chess. La session de chess, sur l'autre compte de Théo et sur
Fable, installe le socle sur chess et tient sa feuille de route ; cet
autre compte peut aussi renforcer les lots du socle, dans une autre
session, si celui-ci manque d'usage. L'usage de Fable de ce compte, à
62 %, est la ressource qui ne se remet pas à zéro.
