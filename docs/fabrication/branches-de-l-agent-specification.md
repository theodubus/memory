# L'agent supprime ses branches déjà contenues : spécification

Elle répond à B-0351, sur l'intention que Théo a retenue le 25 novembre
2026 (D-0202, « 1A 2A ») : l'agent ne supprime seul que ses propres
branches de travail, celles dont le dernier commit porte sa marque, et
seulement quand leur contenu est déjà dans la branche par défaut ou dans
la branche de travail poussée ; la suppression vaut par défaut dans le
produit, et une ligne de la politique la coupe. Le mécanisme, l'agent le
décide (politique, point 3), et le voici.

## Ce qu'elle fait

Aujourd'hui, l'état calcule les branches distantes que la branche par
défaut, ou la branche de travail poussée, contient en entier, et les
donne à l'humain à supprimer, après chaque fusion et chaque passation :
la politique range la suppression d'une branche distante parmi les
actions irréversibles ou externes (point 4), et le hook de l'agent la
refuse.

Désormais, une commande du socle, `socle prune-branches`, supprime celles
de l'agent, après avoir vérifié sur l'origine, au moment même, ce qui les
rend sûres à supprimer. L'état ne donne plus à l'humain que les siennes,
et celles que l'origine a refusé de supprimer.

## Les branches de l'agent

Une branche distante est **de l'agent** quand son dernier commit porte
l'un des motifs de `[agents] markers` de la politique, ceux qui
reconnaissent déjà un commit d'agent pour la CI (`Socle-Agent:`, un
`Co-Authored-By` de Claude). Le moteur ne connaît ainsi aucun agent par
son nom. Un commit de fusion fait par GitHub, ou un commit de l'humain, en
tête de branche, la rend à l'humain.

Elle **se supprime** quand, en plus :

- l'origine l'a encore, à la tête que le dernier fetch connaît
  (`git ls-remote --heads origin`, juste avant) ;
- cette tête est contenue dans la branche par défaut de l'origine, ou dans
  la branche de travail courante telle que l'origine l'a ;
- ce n'est ni la branche par défaut, ni la branche courante, ni une
  branche que `[human] keep_branches` garde.

## La commande

`python3 .socle/socle prune-branches` :

1. `git fetch origin`, sans `--prune`, qui perdrait le commit que seule
   garde la référence d'une branche disparue (la revue de L-0043,
   ADR-0114), puis `git ls-remote --heads origin` ; une branche que
   l'origine n'a plus se passe sous silence ;
2. pour chaque branche qui se supprime, un push de suppression gardé par
   la tête vérifiée :
   `git push --force-with-lease=refs/heads/<b>:<sha> origin :refs/heads/<b>`,
   qui échoue si la branche a bougé depuis la vérification ;
3. imprime, pour chaque branche supprimée, la commande qui la recrée
   (`git push origin <sha>:refs/heads/<b>`), et pour chaque refus, sa
   raison.

`--dry-run` dit ce qu'elle supprimerait, sans rien supprimer. Un refus de
l'origine (un proxy, des droits, une règle de protection) se garde dans le
dossier local du socle (`.git/socle/`) : l'état redonne alors la branche à
l'humain, comme aujourd'hui, et la commande ne la retente qu'après un
fetch qui la montre changée.

**Le hook avant push** de git laisse passer sans rien lancer un push qui
ne fait que supprimer : rien ne part, et les étapes rapides prendraient
cinq minutes par branche.

**Le hook de l'agent** continue de refuser `git push --delete` et
`git push origin :<branche>` ; son message nomme la commande. C'est le
seul changement de son texte, sur la preuve de B-0351 (ADR-0098) : la
branche donnée à l'humain à chaque fin de lot.

## Quand l'agent la lance

- Après la fusion de sa pull request, une fois la branche locale repartie
  de la branche par défaut (skill `socle-batch`).
- Après le premier commit d'une session qui reprend une passation, poussé
  (skill `socle-handoff`) : la branche de la session précédente est alors
  contenue dans la sienne.
- Quand l'état le lui dit : une ligne pour l'agent, hors de « ce qui
  revient à l'humain », nomme les branches de l'agent à supprimer et la
  commande.

## La politique

La suppression vaut par défaut. `prune_branches = false`, dans la section
`[irreversible]` de la politique, la coupe : l'état redonne alors toutes
les branches à l'humain, et la commande refuse en le disant. Les gabarits
de la politique, en français et en anglais, portent la ligne en
commentaire, avec ce qu'elle fait. Le point 4 de la politique, dans le
gabarit d'`AGENTS.md`, nomme l'exception : « suppression distante, hors
des branches de l'agent déjà contenues ailleurs (`socle prune-branches`) ».

## Modèle de menace

Ce que la commande arrête :

- **la perte d'un commit** : une branche ne se supprime que si sa tête,
  vérifiée sur l'origine au moment même, est contenue dans une branche que
  l'origine garde ; le bail (`--force-with-lease`) refuse la suppression
  si elle a bougé entre la vérification et le push ;
- **la branche de l'humain** : sans la marque d'un agent sur son dernier
  commit, elle reste son geste ;
- **la branche par défaut, la branche courante, une branche gardée** :
  jamais ;
- **une suppression hors de la commande** : le hook de l'agent refuse
  toujours `git push --delete`.

Ce qu'elle laisse passer :

- **une pull request ouverte depuis la branche**, qui se ferme avec elle :
  son contenu reste dans la branche qui la contient, et la commande donne
  de quoi recréer la branche ; une pull request fusionnée ne craint rien ;
- **une marque d'agent posée par l'humain** sur son propre commit : la
  branche est alors traitée comme celle de l'agent ;
- **un commit que seule la branche porte et que la mémoire cite** : il ne
  peut pas exister, la branche étant contenue ailleurs ;
- **une origine qui refuse** : rien n'est supprimé, et l'humain retrouve
  la branche dans l'état.

## Ce que reçoit un projet

La commande, la ligne de l'état, le hook avant push, le message du hook
de l'agent, les gabarits de la politique et d'`AGENTS.md`, les skills
`socle-batch` et `socle-handoff`, le guide (`HELP.md`) et la note de
version, en français et en anglais. Rien à migrer : la suppression vaut à
la mise à jour, et chess la reçoit avec la sienne.
