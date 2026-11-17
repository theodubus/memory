<!-- socle: couche=backlog zone=publique -->
# B-0174 — Un adaptateur qui se lance dans un sous-dossier : un langage dont le manifeste n'est que plus bas, équipé sans adaptateur propre au projet

> statut : ouvert · origine : J-2026-11-11-S · priorité : basse · lu : backlog@2ee8ebee

Depuis ADR-0066, un langage dont le manifeste n'est que dans un
sous-dossier (l'interface JavaScript de chess, sous `ui/`) ne reçoit pas
d'adaptateur en automatique : ses commandes se lanceraient à la racine. Le
projet écrit alors un adaptateur propre, dont chaque commande entre dans le
sous-dossier, ou déclare le sous-dossier tiers. Un adaptateur maintenu
pourrait se lancer lui-même dans un dossier (une clé `root` de la copie, ses
commandes, sa CI et ses motifs relatifs à ce dossier), et l'installeur le
poser là. Hors du périmètre de B-0168.

## Satisfait quand

- [ ] une copie d'adaptateur peut déclarer le dossier où ses commandes et ses étapes de CI se lancent
- [ ] en automatique, l'installeur pose l'adaptateur d'un langage dont le manifeste n'est que dans un sous-dossier, lancé dans ce sous-dossier
