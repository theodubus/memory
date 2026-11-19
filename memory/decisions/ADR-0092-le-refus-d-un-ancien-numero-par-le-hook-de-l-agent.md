<!-- socle: couche=decisions zone=publique -->
# ADR-0092 — Le refus d'un ancien numéro par le hook de l'agent se juge sur les lignes que l'écriture ajoute : le modèle de menace d'ADR-0087 complété

> statut : acceptée · date : 2026-11-19 · source : ADR-0087@39a38e17, T-0083@56cdd069, ADR-0082@beb85978, L-0014@cd0d35b8, D-0139@1b6b3adf · lu : decisions@cc20b34b

## Contexte

ADR-0087@39a38e17 écrit le modèle de menace du refus d'un ancien numéro
par le hook de l'agent. Ce qu'il laissait passer comprenait « une mention
que le fichier portait déjà avant l'écriture » : le hook sautait toute
mention présente n'importe où dans le fichier d'avant. La revue du lot
L-0014 l'a relevé (T-0083@56cdd069) : le journal du mois d'une migration
cite presque tous les anciens numéros, et une entrée neuve qui en
reprenait un y passait, là même où l'agent les reprend. Une ADR ne se
récrit pas ; seul son statut change ensuite : celle-ci la complète.

## Décision

Le modèle de menace d'ADR-0087, tel que T-0083 le change ; le reste
d'ADR-0087 vaut tel qu'écrit.

- **Ce qu'il arrête.** Un agent coopératif qui reprend un ancien numéro
  dans une ligne qu'une écriture ajoute ou change, par l'outil d'écriture
  ou d'édition dans un fichier `.md`, même dans un fichier qui le cite
  déjà : le refus nomme l'identifiant actuel, que l'agent cite à sa
  place.
- **Ce qu'il laisse passer.** La ligne qui nomme aussi l'identifiant
  actuel (le bilan d'une mise à jour, ou une citation de l'humain) ; une
  ligne du fichier d'avant gardée telle quelle, même quand l'écriture
  change ce qui l'entoure, les lignes se comparant une à une ; une
  écriture par le shell, que le hook ne lit pas comme l'écriture d'un
  fichier.
- **Pourquoi c'est acceptable.** Inchangé : un ancien numéro se résout
  partout et ne se réattribue jamais ; le refus aide l'agent au moment où
  il écrit, il ne garantit rien, et la CI ne le juge pas.

## Conséquences

- Une référence inventée se juge comme avant, sur tout le fichier : seul
  l'ancien numéro passe aux lignes ajoutées.
- Une ligne d'avant qui cite un ancien numéro, retouchée pour une autre
  raison, se refuse : la retouche y nomme aussi l'identifiant actuel.
- Pour défaire : une ADR qui la remplace, et `references_refusees`
  (`engine/socle/hooks.py`) qui saute de nouveau toute mention du fichier
  d'avant.
