<!-- socle: couche=backlog zone=publique -->
# T-0228 — Supprimer TestLePlafondDesProjetsInstalles (D-0242), et dire dans B-0104 que la mise à jour de JustCook pose la demande des 10 000 octets avant d'en commiter les fichiers

> statut : fait · origine : J-2026-11-28-B · ref : D-0242 · besoin : B-0385 · lu : backlog@2b83126f

Un commit, sur la validation de D-0242 par Théo le 28 novembre :
chess garde 10 000 octets pour ses skills, et JustCook, le pilote
installé le 31 octobre, posera la même demande à sa mise à jour.

## Fait quand

- [x] `tests/test_skills.py` n'a plus la classe `TestLePlafondDesProjetsInstalles`
- [x] B-0104 dit que la mise à jour de JustCook pose la demande des 10 000 octets des skills, et la voit validée, avant d'en commiter les fichiers
