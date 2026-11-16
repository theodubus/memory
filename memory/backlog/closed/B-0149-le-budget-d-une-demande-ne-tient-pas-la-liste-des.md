<!-- socle: couche=backlog zone=publique -->
# B-0149 — Le budget d'une demande ne tient pas la liste des fichiers protégés d'une mise à jour, et son contrat ne se découvre qu'au refus

> statut : fait · origine : J-2026-11-10-H · lu : backlog@85af71e3 · ref : J-2026-11-10-R

La demande d'approbation d'une mise à jour cite chaque fichier protégé
changé avec son empreinte : pour les 54 du pilote, avec une ligne chacun,
elle dépassait de 374 octets le budget d'une demande (12 000 octets), et
l'agent a retiré un paragraphe utile (J-2026-11-10-H). Le contrat du
contexte (trois paragraphes d'ouverture) ne s'est appris qu'au refus.

Pistes du pilote : sortir du budget la liste des fichiers protégés d'une
mise à jour ; accepter une forme courte (chemin et empreinte) ; ou une
commande du socle qui écrit cette liste dans la demande.

## Satisfait quand

- [x] une demande d'approbation d'une mise à jour tient ses fichiers protégés sans sacrifier son contexte, et l'agent sait son contrat avant de l'écrire
