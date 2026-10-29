<!-- socle: couche=backlog zone=publique -->
# B-0077 — Le moteur copié dans un projet cite la mémoire de ce dépôt

> statut : fait · origine : J-2026-10-20-Q · ref : J-2026-10-20-X · lu : backlog@1615e20b

Le moteur, copié tel quel dans le dossier `.socle` de chaque projet, porte
dans ses commentaires environ 330 renvois à la mémoire de ce dépôt-ci
(`B-0008`, `J-2026-10-10-G`, `ADR-0025`…). Dans un projet, ils ne disent
rien, et l'agent de ce projet pourrait les prendre pour des entrées de sa
propre mémoire. Relevé en séparant ce qu'un projet reçoit de ce qui
fabrique l'outil (B-0046), après les traces des échecs, retirées le
20 oct. : un commentaire du moteur dit le pourquoi en clair, et le renvoi à
la décision ou au journal reste dans la documentation de fabrication.
