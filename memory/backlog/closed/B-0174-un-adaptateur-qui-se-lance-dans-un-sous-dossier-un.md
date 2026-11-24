<!-- socle: couche=backlog zone=publique -->
# B-0174 — Un adaptateur qui se lance dans un sous-dossier : un langage dont le manifeste n'est que plus bas, équipé sans adaptateur propre au projet

> statut : abandonné · origine : J-2026-11-11-S · priorité : basse · lu : backlog@2ee8ebee · ref : D-0168

Depuis ADR-0066, un langage dont le manifeste n'est que dans un
sous-dossier (l'interface JavaScript de chess, sous `ui/`) ne reçoit pas
d'adaptateur en automatique : ses commandes se lanceraient à la racine. Le
projet écrit alors un adaptateur propre, dont chaque commande entre dans le
sous-dossier, ou déclare le sous-dossier tiers. Un adaptateur maintenu
pourrait se lancer lui-même dans un dossier (une clé `root` de la copie, ses
commandes, sa CI et ses motifs relatifs à ce dossier), et l'installeur le
poser là. Hors du périmètre de B-0168.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X3 — peaufine la machinerie sans gêne constatée » : un adaptateur lancé dans un sous-dossier ; depuis ADR-0066, l'installeur dit au projet ses deux issues, sans gêne vue. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] une copie d'adaptateur peut déclarer le dossier où ses commandes et ses étapes de CI se lancent
- [ ] en automatique, l'installeur pose l'adaptateur d'un langage dont le manifeste n'est que dans un sous-dossier, lancé dans ce sous-dossier
