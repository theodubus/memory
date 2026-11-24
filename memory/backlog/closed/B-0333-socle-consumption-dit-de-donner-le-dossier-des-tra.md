<!-- socle: couche=backlog zone=publique -->
# B-0333 — socle consumption dit de donner le dossier des transcriptions en argument quand un dossier est donné, ou quand un filtre ne laisse aucune conversation

> statut : abandonné · origine : J-2026-11-22-Q · priorité : basse · lu : backlog@3a8162c0 · ref : D-0168

La revue de L-0009 (J-2026-11-22-Q), écarté par le relecteur, que
l'orchestrateur range au backlog : il se produit dans l'usage normal.
`cmd_consumption` (`engine/socle/cli.py`) dit de donner le dossier des
transcriptions en argument quand elle ne trouve aucune conversation à
mesurer, même quand un dossier est donné, ou quand `--day`, `--until` ou
`--session` n'en laisse aucune (un jour sans session). Le code de sortie
1 se voit, mais le message envoie l'humain chercher ailleurs.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X3 — peaufine la machinerie sans gêne constatée » : un message de `socle consumption`. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] socle consumption sans conversation à mesurer dit pourquoi : aucun dossier trouvé, ou un dossier que ses filtres vident
