<!-- socle: couche=backlog zone=publique -->
# B-0327 — Un adaptateur nommé du langage d'une copie déjà posée hors de la principale est remplacé par elle sans que l'installeur le dise

> statut : fait · ref : T-0123, J-2026-11-22-E · origine : J-2026-11-21-L · lu : backlog@b3bf0b5f

Relevé par la revue à froid de L-0008 (J-2026-11-21-L) : depuis T-0028,
un adaptateur détecté ou nommé du langage d'une copie déjà posée dans
le dossier des autres adaptateurs du projet devient cette copie (`engine/socle/installer.py`,
vers les lignes 1262-1263). Nommé (`--adapter /chemin/mon-python.toml`,
ou `--adapter python-pytest` sur une copie `python`), il n'est jamais
posé, et l'installeur ne le dit pas : son journal ne nomme que la copie.
Pour la copie principale, il le dit d'une ligne `!! … non posé : …
existe déjà`, avec la marche à suivre pour la remplacer (revue de
B-0168). Avant T-0028, l'adaptateur se posait à côté, et
`adaptateur.recouvrement` échouait : le lot a ôté l'échec, pas le
silence.

## Satisfait quand

- [x] un adaptateur nommé que l'installeur remplace par la copie déjà posée de son langage est nommé dans sa sortie, avec ce qui le remplace et comment le poser à sa place
