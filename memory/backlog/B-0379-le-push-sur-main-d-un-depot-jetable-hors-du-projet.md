<!-- socle: couche=backlog zone=publique -->
# B-0379 — Le push sur `main` d'un dépôt jetable, hors du projet, est refusé comme une publication

> statut : ouvert · origine : J-2026-11-27-U · ref : D-0235 · lu : backlog@4d53be09

Chez chess (`docs/fabrication/chess/cout-et-frictions-2026-11-26.md`, §3.3), deux refus en deux semaines : un push
sur `main` d'un dépôt jetable, dans un dossier temporaire. Confirmé
(`docs/fabrication/chess/relecture-cout-et-frictions-2026-11-27.md`) : `_git_irreversible` (`engine/socle/hooks.py`) juge la
branche sans regarder le dépôt visé.

En réserve (D-0235, point 10) : une autre branche que `main` dans le dépôt
jetable suffit ; il revient s'il est revu.

## Satisfait quand

- [ ] un push vers un dépôt jetable hors du projet n'est pas refusé comme une publication du projet
