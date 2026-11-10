<!-- socle: couche=decisions zone=publique -->
# ADR-0057 — La porte de chess : deux journées du pilote sans retour bloquant, et d'ici là des correctifs seulement

> statut : acceptée · date : 2026-11-10 · validation : D-0093@333ad9d0 · source : D-0073@f690f8a8, B-0126@e4f0cc19 · lu : decisions@7feca569

## Contexte

Le plan de chess que Théo a validé le 2 novembre (D-0073@f690f8a8) attend,
avant l'essai à blanc et l'installation (B-0126@e4f0cc19), deux journées
de travail réel du pilote sans retour qui corrige le socle. Chaque
version nouvelle du socle en apporte : six le 10 novembre, dont un seul
grave. Tant que le socle change à ce rythme, la condition ne se remplit
pas. La passe de recul du 10 novembre l'a relevé, et Théo a validé sa
proposition 5 (D-0093@333ad9d0).

## Décision

1. La porte de chess devient : deux journées de travail réel du pilote
   sans retour bloquant. Bloquant : un retour qui arrête l'agent du pilote
   ou fausse un contrôle. Une gêne qui se contourne va au backlog, sans
   remettre le compte à zéro. Théo en juge, sur le retour du pilote.
2. Jusqu'à l'installation sur chess, le socle ne reçoit que des
   correctifs : rien de nouveau qu'il exige de l'agent ou lui refuse. Ce
   que la même demande place avant chess, l'allègement du début de
   session, des réveils de reprise et du contexte long, fait exception.
3. Le reste du plan du 2 novembre ne change pas : l'essai à blanc avec la
   version publiée, puis l'installation en mode adoption.

## Conséquences

chess reçoit un socle qui a encore de petites gênes connues. Le pilote
étant en pause tant que le socle se corrige, ses deux journées se
comptent à sa reprise. La défaire : revenir à la condition du 2 novembre.
