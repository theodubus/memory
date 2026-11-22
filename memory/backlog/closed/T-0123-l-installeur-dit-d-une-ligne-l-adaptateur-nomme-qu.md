<!-- socle: couche=backlog zone=publique -->
# T-0123 — L'installeur dit d'une ligne l'adaptateur nommé qu'il remplace par la copie déjà posée de son langage, avec la marche à suivre pour la remplacer

> statut : fait · ref : J-2026-11-22-E · origine : J-2026-11-21-L · besoin : B-0327 · lu : backlog@cc3cfb46

Un commit : `engine/socle/installer.py`, là où un adaptateur nommé
devient la copie du même langage (T-0028), imprime une ligne `!!` de la
forme de celle de la copie principale (« … non posé : … existe déjà »,
avec la marche à suivre) ; sa traduction dans `messages_en.py` ; une
note de version.

## Fait quand

- [x] `--adapter` qui nomme un fichier ou un adaptateur maintenu du langage d'une copie déjà posée dans le dossier des autres adaptateurs du projet fait imprimer une ligne `!!` qui nomme l'adaptateur écarté et la copie gardée, et un test qui échoue sur le commit parent le prouve ; un adaptateur détecté en automatique ne fait rien dire de plus
