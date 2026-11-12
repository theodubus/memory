<!-- socle: couche=backlog zone=publique -->
# B-0178 — L'installeur ne dit rien d'un langage en sous-dossier quand l'adaptateur est donné en fichier

> statut : fait · origine : J-2026-11-11-X · lu : backlog@cd0009c1 · ref : J-2026-11-12-C

À l'installation réelle sur chess (`docs/fabrication/chess/installation-2026-11-11.md`),
l'installeur a reçu un adaptateur propre au projet par `--adapter` : il n'a
rien dit du JavaScript qui vit sous un sous-dossier. L'avertissement de
B-0168 n'est émis qu'en détection automatique (`engine/socle/installer.py`,
sous `if detectes:`). Ce qui est posé est juste, mais l'humain qui donne un
adaptateur pour un langage n'apprend pas qu'un autre, dans un sous-dossier,
reste sans adaptateur ni déclaration de chemin tiers.

## Fait quand

- [x] avec un adaptateur donné par `--adapter`, l'installeur nomme aussi les langages dont le manifeste n'est que dans un sous-dossier et qui n'ont ni adaptateur ni chemin tiers déclaré, avec leurs deux issues
