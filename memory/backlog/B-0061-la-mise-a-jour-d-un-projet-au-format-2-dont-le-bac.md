<!-- socle: couche=backlog zone=publique -->
# B-0061 — La mise à jour d'un projet au format 2 dont le backlog est vide échoue

> statut : ouvert · origine : J-2026-10-14-W · lu : backlog@c716992e

Mesuré le 14 oct., en écrivant les tests de B-0059 : un projet installé au
format 2 (backlog en un fichier), dont le backlog n'a aucun sujet, refuse sa
mise à jour au format 3 : « refus : git add -- memory/backlog : fatal:
pathspec 'memory/backlog' did not match any files ». La migration
(`engine/socle/migrations.py`, découpage du backlog) supprime le fichier
unique de l'index, puis ajoute le dossier des sujets, qu'elle n'a pas créé
faute de sujet. Tout projet neuf installé au format 2 est dans ce cas.
Reproduit dans un projet jetable : installation `format_memoire=2`, commit,
puis installeur relancé. Correction probable : ne rien ajouter quand le
dossier n'existe pas (ou le créer), avec un test qui échoue sans elle.
