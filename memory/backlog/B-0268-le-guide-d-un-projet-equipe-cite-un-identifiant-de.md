<!-- socle: couche=backlog zone=publique -->
# B-0268 — Le guide d'un projet équipé cite un identifiant de l'atelier (D-0098), et aucun test ne garde HELP.md de l'atelier

> statut : ouvert · origine : J-2026-11-16-O · lu : backlog@19d900ab

Vu en menant B-0261 (J-2026-11-16-O). Le guide d'un projet équipé,
`engine/socle/HELP.md`, section 4 (« Approuver ses propres changements
protégés »), dit que l'agent remet un fichier protégé à son état du
dernier commit « quand il l'a changé par erreur (D-0098) » ;
`HELP.en.md` de même. `D-0098` est une demande de la mémoire de ce dépôt :
un projet équipé lit un identifiant qui ne renvoie à rien chez lui, contre
ADR-0033 (le produit ne renvoie jamais à l'atelier). Les notes de version
(`tests/test_notes_de_version.py`) et les skills du socle
(`tests/test_skills.py`) ont un test qui les en garde ; le guide n'en a
pas, d'où la fuite.

La piste : retirer la référence des deux guides, et un test qui refuse
dans `HELP.md` et `HELP.en.md` un identifiant de la mémoire (`ID_RE`) et
les mots de l'atelier, comme celui des notes de version.

## Fait quand

- [ ] ni `engine/socle/HELP.md` ni `engine/socle/HELP.en.md` ne citent un identifiant de la mémoire de ce dépôt ni l'atelier, et un test le garde
