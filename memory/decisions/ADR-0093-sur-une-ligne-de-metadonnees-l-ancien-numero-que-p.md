<!-- socle: couche=decisions zone=publique -->
# ADR-0093 — Sur une ligne de métadonnées, l'ancien numéro que portait la ligne remplacée reste : le modèle de menace d'ADR-0092 complété

> statut : acceptée · date : 2026-11-19 · source : ADR-0092@05b64671, ADR-0087@39a38e17, T-0083@56cdd069, L-0005@657fe9e5 · lu : decisions@793480b1

## Contexte

ADR-0092@05b64671 juge l'ancien numéro sur les lignes qu'une écriture
ajoute ou change, et en tire une conséquence : une ligne d'avant qui
cite un ancien numéro, retouchée pour une autre raison, se refuse, et la
retouche y nomme aussi l'identifiant actuel. La passe 1 de la revue de
L-0005@657fe9e5 a relevé ce que cette conséquence n'avait pas vu, un
bloquant : la ligne de métadonnées d'une entrée renumérotée porte son
ancien numéro dans le champ `ancien`, sans son identifiant actuel, qui
est dans le titre. Clore le lot, le passer en cours ou compléter son
`après` était refusé, pour les dix-huit lots et jalons renumérotés. Une
décision dont la `source` cite un ancien numéro ne pouvait plus changer
de statut, le seul changement qu'on lui permet : le remède du refus y
est impossible. Et le message poussait à retirer le champ `ancien`, qui
seul fait résoudre l'ancien numéro.

## Décision

Le modèle de menace d'ADR-0092, complété ; le reste vaut tel qu'écrit.

- **Ce qu'il laisse passer, en plus.** Sur une ligne de métadonnées
  d'une entrée (les lignes `>` qui suivent son titre), un ancien numéro
  que portait déjà le bloc de lignes que l'écriture remplace : le champ
  `ancien` d'une entrée qu'on clôt, la source d'une décision dont le
  statut change. Un même ancien numéro repris dans un autre champ de la
  même ligne passe aussi.
- **Ce qu'il arrête toujours.** Un ancien numéro neuf sur une ligne de
  métadonnées, qu'aucune ligne remplacée ne portait (un `après` ou un
  `ref` qui le reprend) ; une ligne de texte retouchée qui cite un ancien
  numéro sans l'identifiant actuel, comme ADR-0092 le dit.
- **Pourquoi c'est acceptable.** Une ligne de métadonnées est une suite
  de champs : changer l'un d'eux ne reprend pas l'ancien numéro qu'un
  autre garde. Le refus aide l'agent au moment où il écrit, il ne
  garantit rien (ADR-0087@39a38e17), et un ancien numéro se résout
  partout.

## Conséquences

- La conséquence d'ADR-0092 sur la ligne retouchée ne vaut plus que pour
  une ligne de texte.
- `references_refusees` (`engine/socle/hooks.py`) lit, pour chaque ligne
  changée, le texte que son bloc remplace (`lignes_remplacees`).
- Pour défaire : une ADR qui la remplace, et la ligne de métadonnées
  jugée de nouveau comme une ligne de texte.
