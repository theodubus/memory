<!-- socle: couche=decisions zone=publique -->
# ADR-0059 — La porte de chess : les lots importants livrés, puis l'essai à blanc ; le pilote n'est plus attendu

> statut : acceptée · date : 2026-11-11 · validation : D-0096@670093a3 · source : ADR-0057@ea4706e7, B-0126@510e8202 · lu : decisions@6b98ac18

## Contexte

ADR-0057@ea4706e7 faisait attendre à chess deux journées de travail réel du
pilote sans retour bloquant. Le pilote est en pause tant que le socle se
corrige (J-2026-11-10-N@bcf0f6ad) : la condition ne peut pas se remplir. Théo
veut que l'adoption du socle sur chess se fasse cette semaine
(D-0095@f5d3f09a) et dit, le 11 novembre, de ne pas attendre le pilote :
« on faisait juste les jalons importants & corrections puis on implemente
dans chess » (D-0096@670093a3).

## Décision

1. La porte de chess devient : les lots à livrer avant chess sont
   fusionnés et publiés, puis l'essai à blanc sur chess, avec la version
   publiée, ne trouve rien de bloquant. Le pilote n'est plus attendu.
   Bloquant garde son sens : ce qui arrête l'agent ou fausse un contrôle.
2. Les lots à livrer avant chess, que l'agent choisit puisqu'il planifie :
   ce qui pèse à chaque tour d'une session cloud ou met en danger le dépôt
   d'un projet. Le budget d'une demande, déjà fait ; les réveils de
   reprise ; le hook de fin de tour qui relance en vain ; le relecteur qui
   agit dans le dépôt. Le jalon 1 (B-0154@e18495e6) en tient la liste, et se
   resserre sur eux : le reste de son allègement suit l'installation.
3. Jusqu'à l'installation, le socle ne reçoit toujours que des correctifs
   et cet allègement.
4. L'essai à blanc et l'installation (B-0126@510e8202) se font dans la
   session de chess, sur l'autre compte de Théo. Un constat bloquant de
   l'essai se corrige ici avant l'installation ; une gêne va au backlog.

## Conséquences

chess reçoit un socle qu'aucun projet n'a utilisé deux journées sans
retour : ses défauts restants se verront sur chess, le projet principal de
Théo, et s'y corrigeront au fil de l'eau. La défaire : revenir à la porte
des deux journées du pilote.
