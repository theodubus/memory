<!-- socle: couche=backlog zone=publique -->
# T-0010 — Une citation de dossier dans un texte recopié d'une demande ne couvre plus les fichiers protégés qu'il contient

> statut : fait · origine : J-2026-11-14-Z · ref : J-2026-11-20-L · besoin : B-0227 · lu : backlog@9966bbbd

Un commit : `_cite_chemin` (`engine/socle/hooks.py`) ne compte pour citation d'un dossier que les fichiers approuvés des « Éléments cités », ou un chemin hors d'un texte recopié entre accents graves ; un correctif, avec son test qui échoue sur le commit parent.

## Fait quand

- [x] le hook laisse remettre en état un skill du socle qu'aucune demande n'approuve quand une demande en attente ne cite son dossier que dans une valeur recopiée entre accents graves, et un test qui échoue sur le commit parent le prouve
- [x] une demande qui approuve le fichier, ou qui cite son dossier hors d'un texte recopié, le couvre encore, et un test le montre
