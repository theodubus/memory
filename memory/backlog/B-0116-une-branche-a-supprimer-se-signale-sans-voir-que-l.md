<!-- socle: couche=backlog zone=publique -->
# B-0116 — Une branche à supprimer se signale sans voir que la mémoire cite un commit qu'elle seule contient

> statut : ouvert · origine : J-2026-11-01-C · lu : backlog@0121264b

L'état signale une branche distante non fusionnée et inactive, à livrer
ou à supprimer (B-0112). Il ne regarde pas si la mémoire cite, sous la
forme `commit:`, un commit que seule cette branche contient : la
supprimer fait alors échouer `memoire.references` en CI, dont le clone ne
récupère que les branches et les étiquettes, même quand GitHub garde le
commit par une pull request. C'est arrivé à ce dépôt le 1er novembre
(J-2026-11-01-C).

À faire : pour une telle branche, l'état dit de poser d'abord une
étiquette sur les commits cités, avec la commande, au lieu de proposer la
suppression seule ; et le refus de `memoire.references` sur un commit
absent du clone nomme ce remède à côté de l'historique complet.

Le 1er novembre, B-0117 retrouve le commit d'une branche supprimée dans sa
pull request : il reste le cas d'une branche qui n'en a jamais eu.
