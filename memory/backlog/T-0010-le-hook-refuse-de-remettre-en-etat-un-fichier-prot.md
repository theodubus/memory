<!-- socle: couche=backlog zone=publique -->
# T-0010 — Le hook refuse de remettre en état un fichier protégé dont une demande ne cite que le dossier, dans une valeur recopiée

> statut : ouvert · origine : J-2026-11-14-Z · besoin : B-0227 · lu : backlog@9966bbbd

La tâche de B-0227, que la migration du backlog en quatre formes a posée dans le lot L-0006 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] une demande qui ne cite un dossier protégé que dans un texte recopié ne bloque pas la remise en état des fichiers qu'elle n'approuve pas ; un test qui échoue sur le commit parent le prouve
