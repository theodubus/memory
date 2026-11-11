<!-- socle: couche=backlog zone=publique -->
# B-0175 — Un clone neuf échoue sur memoire.references : le journal cite commit:0e3723a, qu'aucune branche ni étiquette n'atteint

> statut : ouvert · origine : J-2026-11-11-S · lu : backlog@276b3abd

Relevé pendant B-0168. Reproduction : cloner le dépôt de travail dans un
dossier temporaire (`git clone --no-local <worktree> <dossier>`), puis
`python3 .socle/socle check` y rend 1 : `memoire.references` refuse
`memory/journal/2026-10-4.md`, ligne 1312, dont le commit cité, celui de
`refs/pull/10/head`, n'est dans le dépôt local qu'un objet qu'aucune
branche ni étiquette n'atteint (`git branch -a --contains` et `git tag
--contains` ne rendent rien). La CI le retrouve par les pull requests ;
un clone hors de GitHub, non. Le message propose déjà l'étiquette
`cite/<sha>` : la poser depuis un clone qui l'a encore, ou dire au
contrôle de lire aussi `refs/pull/*` quand ils ont été récupérés.

## Fait quand

- [ ] `python3 .socle/socle check` passe dans un clone neuf du dépôt
