<!-- socle: couche=backlog zone=publique -->
# B-0193 — L'état demande de supprimer une branche distante que GitHub n'a plus : il lit les références du dernier fetch, sans élagage

> statut : ouvert · origine : J-2026-11-12-O · priorité : basse · lu : backlog@6a4d0618

Le 12 novembre, l'état demandait à Théo de supprimer la branche distante
`ccr-7128ec56-nnvoun-v2`, que GitHub n'avait plus ; Théo : « Déjà
supprimée non ? Je ne la vois pas ». `branches_a_supprimer`
(`engine/socle/human.py`) lit `refs/remotes/origin`, « calculé sur le
dernier fetch » : un fetch sans élagage garde la référence d'une branche
supprimée, et l'état la donne à supprimer. Un `git fetch --prune` l'a
effacée.

Pistes : élaguer là où le socle va déjà chercher la branche distante (le
hook de démarrage, le hook avant push), ou faire dire au message que la
liste date du dernier fetch, et comment la rafraîchir.

## Fait quand

- [ ] une branche distante supprimée n'est plus donnée à supprimer, ou le message dit d'où vient la liste ; un test qui échoue sur le commit parent le prouve
