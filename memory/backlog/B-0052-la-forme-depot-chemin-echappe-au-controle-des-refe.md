<!-- socle: couche=backlog zone=publique -->
# B-0052 — La forme depot:chemin échappe au contrôle des références

> statut : fait · origine : J-2026-10-12-Q · lu : backlog@2a6691e4 · ref : J-2026-10-13-D

Mesuré à R6, tâche 1 : pour des fichiers qu'une rustine crée, l'agent a
écrit `<rustine>.patch:<chemin>`, sur le modèle de `depot:chemin`, et le
contrôle des références les a laissés passer sans rien vérifier. Le geste
était juste (il a ajouté au projet le test qui vérifie ces chemins), mais
n'importe quelle chaîne `x:chemin` échappe ainsi au contrôle. Ne laisser
passer que les dépôts connus, ou le dire.
