<!-- socle: couche=backlog zone=publique -->
# B-0208 — Le hook de l'agent laisse supprimer un dossier qui contient le projet (rm -rf .., un ancêtre de la racine)

> statut : ouvert · origine : J-2026-11-13-H · priorité : haute · lu : backlog@f4a491f0

Le hook de l'agent juge un chemin écrit par ce qu'il est dans le projet
(`_relatif`), et ne voit pas une suppression qui l'emporte tout entier :
`rm -rf ..` lancé depuis la racine, ou `rm -rf` d'un dossier qui la
contient (le dossier des worktrees pour un sous-agent, le dossier de
l'utilisateur), passent le hook, alors qu'ils effaceraient la politique,
les hooks et toute la mémoire, ce qu'aucun contrôle ne rattrape ensuite.
`rm -rf .` et `rm -rf` de la racine elle-même, eux, sont refusés.

Vu par la revue sans contexte de B-0171 (son constat 15). La priorité
haute est la décision de Théo (D-0108@96eeead5) : la suppression d'un dossier qui
contient le projet en haute, les autres écritures que le hook ne voit pas
sans priorité (B-0206). Pour rejouer, depuis la racine du dépôt, la
commande de B-0206 avec pour arguments `'rm -rf ..'` et le chemin absolu
du dossier qui contient la racine (`None` : le hook laisse passer).

La piste : dans `hooks._juger_chemin`, refuser une suppression (`rm`,
`mv`, `git clean`, `find -delete`) d'un chemin qui contient la racine
(`hooks._atteint` le sait déjà) ; un dossier temporaire voisin du projet
reste libre.

## Fait quand

- [ ] la suppression d'un dossier qui contient le projet est refusée par le hook, et un test le montre
