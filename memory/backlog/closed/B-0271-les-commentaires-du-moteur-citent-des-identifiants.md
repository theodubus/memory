<!-- socle: couche=backlog zone=publique -->
# B-0271 — Les commentaires du moteur citent des identifiants de la mémoire de l'atelier (ADR-0033), et aucun test ne garde le code du produit comme le guide

> statut : abandonné · origine : J-2026-11-16-S · lu : backlog@ff00445d · ref : D-0168

Relevé par la revue du lot L-0011 (J-2026-11-16-S). ADR-0033 veut que
le produit ne renvoie jamais à l'atelier ; les commentaires du moteur
citent pourtant des identifiants de la mémoire de ce dépôt (seize dans
`engine/socle/memory.py` avant le lot, soixante-seize dans
`engine/socle/hooks.py`), qu'un projet équipé ne connaît pas, et le lot
en a ajouté deux. Le guide et les notes de version ont un test qui les en
garde (B-0268, `tests/test_notes_de_version.py`) ; le code du produit
n'en a pas.

La piste : décider si ADR-0033 s'applique aux commentaires du code (lire
son point 2) ; si oui, un test qui le garde, et le nettoyage des renvois,
remplacés par leur raison en clair.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » : des commentaires du moteur citent des identifiants de ce dépôt ; l'agent d'un projet ne lit pas ces commentaires. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] la règle d'ADR-0033 pour les commentaires du moteur est tranchée, et, si elle s'applique, un test la garde et le moteur la tient
