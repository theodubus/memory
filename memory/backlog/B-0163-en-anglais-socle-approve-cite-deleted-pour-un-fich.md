<!-- socle: couche=backlog zone=publique -->
# B-0163 — En anglais, socle approve cite deleted pour un fichier protégé supprimé, que protege.fichiers ne lit pas

> statut : ouvert · origine : J-2026-11-10-R · lu : backlog@f697f7f8

Dans un projet dont la mémoire est en anglais, `socle approve` écrit
`deleted` comme empreinte nouvelle d'un fichier protégé supprimé
(`cmd_approve`, dans `engine/socle/cli.py`), alors que `protege.fichiers`
cherche le mot `supprimé` dans la demande validée (`proteges`, dans
`engine/socle/checks_ratchet.py`) : l'approbation d'une suppression n'y
serait pas reconnue. Lu dans le code en traitant le budget d'une demande
(J-2026-11-10-R), non reproduit ; aucun test ne couvre ce cas.

## Fait quand

- [ ] dans un projet en anglais, un fichier protégé supprimé que l'humain approuve passe la CI, et un test le montre
