<!-- socle: couche=backlog zone=publique -->
# B-0151 — Aucune note de version ne dit ce qu'une version change pour un projet installé

> statut : fait · origine : J-2026-11-10-H · priorité : haute · lu : backlog@0f79b2df · ref : J-2026-11-14-T

Avec le moteur nouveau, toutes les empreintes de lecture d'un projet ont
changé (ADR-0053 : l'empreinte d'une entrée sans sa ligne de
métadonnées) ; les citations écrites avant passent toujours, mais l'agent
du pilote a dû relire avant de citer à nouveau, sans qu'aucune note ne
l'ait prévenu (J-2026-11-10-H). Rien ne dit, à la mise à jour, ce qu'une
version change pour un projet installé.

Le 13 novembre, Théo retient la priorité haute proposée (D-0108@96eeead5) :
le sujet fait partie de ceux à finir avant de revenir aux nouvelles
fonctions.

Le 14 novembre, ADR-0078 : les notes de version dans le produit
(`engine/socle/CHANGES.md` et sa version anglaise), une entrée par
changement avec ce que l'agent du projet doit faire ; l'installeur donne,
à la mise à jour qui recopie le moteur, celles que la copie du projet
n'avait pas, et le message de commit qu'il propose les nomme
(J-2026-11-14-T).

## Fait quand

- [x] une mise à jour donne à l'agent ce que la version change pour un projet installé
