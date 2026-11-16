<!-- socle: couche=backlog zone=publique -->
# B-0182 — La fin de tour ne lance pas les étapes rapides quand seuls des fichiers de tests ont changé

> statut : fait · origine : J-2026-11-12-A · lu : backlog@8bd286ff · ref : J-2026-11-12-C

À l'installation sur chess (`docs/fabrication/chess/installation-2026-11-12.md`, point 3) : la fin de tour ne lance les
étapes rapides que si un fichier des `sources` de l'adaptateur a changé
(`engine/socle/hooks.py`, par `chemins_code`). Les fichiers de tests n'en
sont pas toujours : ni dans l'adaptateur de chess ni dans le Rust maintenu,
où les tests d'intégration vivent hors des sources. Un changement des seuls
tests n'est alors vérifié qu'au push et en CI. Ce n'est pas voulu : un test
changé se lance avant la fin du tour.

## Satisfait quand

- [x] la fin de tour lance les étapes rapides quand un fichier de tests que l'adaptateur déclare a changé, sources inchangées ; un test le montre
