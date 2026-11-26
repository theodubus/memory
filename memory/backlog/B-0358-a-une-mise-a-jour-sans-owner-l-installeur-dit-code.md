<!-- socle: couche=backlog zone=publique -->
# B-0358 — À une mise à jour sans --owner, l'installeur dit CODEOWNERS non posé alors que le projet en a un, protégé

> statut : ouvert · origine : J-2026-11-26-AA · ref : B-0323 · lu : backlog@dd11ac18

La gêne 2 de la mise à jour de chess du 26 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-26.md`) : relancé sans
`--owner`, comme le prompt le fait à chaque mise à jour, l'installeur
dit « !! aucun propriétaire (--owner) : CODEOWNERS non posé — la
politique n'est protégée que par la CI », alors que le fichier
CODEOWNERS du projet existe, posé à l'installation. L'agent et l'humain
lisent une fausse alerte sur la protection de la politique ; et une
ligne que le gabarit ajouterait ne serait jamais posée sans `--owner`
(`installer._codeowners`).

## Satisfait quand

- [ ] une mise à jour sans `--owner` d'un projet qui a déjà son CODEOWNERS n'y signale aucun défaut, et y ajoute les lignes que le gabarit a en plus
