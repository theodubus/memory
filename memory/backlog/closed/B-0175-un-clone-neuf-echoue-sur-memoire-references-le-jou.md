<!-- socle: couche=backlog zone=publique -->
# B-0175 — Un clone neuf échoue sur memoire.references : le journal cite commit:0e3723a, qu'aucune branche ni étiquette n'atteint

> statut : fait · origine : J-2026-11-11-S · lu : backlog@276b3abd · ref : J-2026-11-14-I

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

Mesuré le 14 novembre, sur la tête `7c20447` : un clone neuf de GitHub
passe `socle check` (rendu 0), `recuperer_pull_requests` (B-0117) y
rapportant `refs/pull/10/head` ; un clone local `--no-local` du worktree
rend 1, sur la ligne 1312 du journal et sur le titre de ce sujet. Son
origine, le worktree, n'a pas de `refs/pull/*`, seulement les copies
qu'elle en a récupérées, `refs/socle/pull/*`, que le clone ne demande
pas. Le critère couvre les deux clones : celui de GitHub est celui de la
CI et d'une session cloud ; le clone local est celui qu'un agent fait,
hors réseau, pour se juger comme un clone neuf.

## Modèle de menace

Le garde-fou est `memoire.references` sur une référence `commit:` : le
commit cité doit exister dans le dépôt, ou dans les têtes de pull
requests que le contrôle récupère de l'origine. Il les récupère
maintenant de deux sources, dans `refs/socle/pull/*` : les
`refs/pull/*/head` de l'origine (GitHub, B-0117), et les
`refs/socle/pull/*` que l'origine a elle-même récupérées, quand elle est
un clone (B-0175).

Ce qu'il arrête, comme avant : un commit inventé ou mal recopié ; un
commit que plus rien ne garde sur l'origine, sa branche supprimée sans
pull request ni étiquette (B-0116), y compris un objet qui traîne encore
dans l'origine locale sans qu'aucun ref ne l'atteigne : un clone ne le
reçoit pas, et le contrôle l'y refuse.

Ce qu'il laisse passer de plus : dans un clone d'un clone, un commit que
l'origine ne garde que par une tête de pull request récupérée, ce que la
CI accepte aussi. Un `refs/socle/pull/*` posé à la main dans l'origine
locale, vers un commit que GitHub n'a pas, passe le clone local et sera
refusé par la CI, comme déjà un commit d'une branche locale non poussée,
que le clone local reçoit avec ses branches : le clone local n'a jamais
été l'arbitre, la CI l'est. Sur GitHub, un `refs/socle/pull/*` poussé
garde le commit comme une étiquette `cite/<sha>` le garderait : rien
n'est accepté qu'aucun ref de l'origine n'atteint.

## Satisfait quand

- [x] `python3 .socle/socle check` passe dans un clone neuf du dépôt
