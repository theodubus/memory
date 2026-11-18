<!-- socle: couche=backlog zone=publique -->
# B-0193 — L'état demande de supprimer une branche distante que GitHub n'a plus : il lit les références du dernier fetch, sans élagage

> statut : ouvert · origine : J-2026-11-12-O · priorité : haute · lu : backlog@6a4d0618

Le 12 novembre, l'état demandait à Théo de supprimer la branche distante
`ccr-7128ec56-nnvoun-v2`, que GitHub n'avait plus ; Théo : « Déjà
supprimée non ? Je ne la vois pas ». `branches_a_supprimer`
(`engine/socle/human.py`) lit `refs/remotes/origin`, « calculé sur le
dernier fetch » : un fetch sans élagage garde la référence d'une branche
supprimée, et l'état la donne à supprimer. Un `git fetch --prune` l'a
effacée.

Le 18 novembre, la même chose deux fois dans une session : l'état
demandait de supprimer `ccr-b742f301-i57kk1` et `ccr-d82b39da-2j0guo`,
que GitHub n'avait plus, et l'agent l'a recopié dans « Pour toi » sans
le vérifier. Théo, mot pour mot :
« Pourquoi tu continues de me demander de supprimer des branches que j'ai deja supprimé et que tu ne prends que l'info quand je te le dis alors que tu as accès à la liste des branches existantes sir github ». Un `git fetch --prune origin` les a effacées. La priorité
passe à haute, que l'agent avait mise basse ; T-0024 sort de L-0007 pour
le lot L-0017, juste après L-0016. D'ici là, l'agent vérifie sur GitHub
(`git ls-remote --heads origin`) chaque branche avant de la donner à
supprimer.

Pistes : élaguer là où le socle va déjà chercher la branche distante (le
hook de démarrage, le hook avant push), ou faire dire au message que la
liste date du dernier fetch, et comment la rafraîchir.

Théo le relève de nouveau le 14 novembre (J-2026-11-14-S) : « l'état
demande de supprimer une branche distante déjà supprimée tant que le
clone n'a pas élagué ses références (git fetch --prune) ». La branche
donnée ce jour-là à la session suivante, `ccr-396af4f0-yv89xr`, existait
bien sur GitHub, recréée après la fusion par le défaut de B-0220 : les
deux défauts se ressemblent dans ce que Théo voit, et pas dans leur
cause.

## Satisfait quand

- [ ] l'état ne demande plus à l'humain de supprimer une branche distante que GitHub n'a plus, ou dit d'où vient sa liste et comment la rafraîchir
