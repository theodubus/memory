<!-- socle: couche=backlog zone=publique -->
# B-0132 — Un agent coupé par une limite d'usage ne reprend qu'au message suivant de l'humain : il doit reprendre seul à la levée de la limite

> statut : fait · origine : J-2026-11-08-H · lu : backlog@2ac91e6b · ref : J-2026-11-09-G

Quand une limite d'usage, de cinq heures ou de la semaine, coupe l'agent
au milieu d'un travail, il ne reprend qu'au message suivant de Théo ; deux
check-ins programmés, tombés pendant la limite, n'ont été lus qu'alors
(J-2026-11-08-G). Théo veut que l'agent reprenne seul, dans le socle, sans
réveiller un agent qu'aucune limite n'a coupé, en reprenant les
sous-agents coupés, la nuit comme le jour, et sans jamais réveiller une
session morte (J-2026-11-08-H). L'agent voit l'utilisation de ses deux
fenêtres et l'heure de leur remise à zéro.

## Satisfait quand

- [x] la spécification soumise à Théo et validée (D-0080, ADR-0050)
- [x] la procédure écrite et posée dans tout projet (le skill `socle-resume`, D-0081)
- [x] une coupure réelle suivie d'une reprise sans message de l'humain
