<!-- socle: couche=decisions zone=publique -->
# ADR-0087 — Le refus d'un ancien numéro par le hook de l'agent : ce qu'il arrête, ce qu'il laisse passer, et pourquoi la CI ne le juge pas

> statut : acceptée · date : 2026-11-18 · source : T-0051@50994b00, J-2026-11-17-N@58787120, D-0123@61a56e15, ADR-0083@512e719c, ADR-0082@beb85978, B-0265@6a1180af, L-0014@cd0d35b8, T-0083@ef8b8e4f · lu : decisions@917021c8

## Contexte

Une entrée renumérotée garde son ancien numéro, qui se résout partout et
ne se réattribue jamais ; un texte neuf cite l'identifiant actuel
(D-0123@61a56e15, point 7 ; ADR-0083@512e719c). Le hook de l'agent
refusait déjà l'ancien numéro dans un texte neuf, en le disant inventé.
T-0051@50994b00 (J-2026-11-17-N@58787120) a changé ce refus : il nomme
l'identifiant actuel à citer, et une ligne qui nomme aussi l'identifiant
actuel passe. La revue du lot L-0014 a relevé que ce garde-fou changé
n'avait pas de modèle de menace écrit, ce qu'exige un garde-fou posé ou
changé (AGENTS.md, la revue).

## Décision

Le modèle de menace du refus d'un ancien numéro par le hook de l'agent :

- **Ce qu'il arrête.** Un agent coopératif qui reprend, d'un journal,
  d'une décision ou d'une demande, un ancien numéro dans un texte neuf de
  la mémoire, écrit par l'outil d'écriture ou d'édition dans un fichier
  `.md` : le refus nomme l'identifiant actuel, que l'agent cite à sa
  place.
- **Ce qu'il laisse passer.** La ligne qui nomme aussi l'identifiant
  actuel (le bilan d'une mise à jour, qui met l'ancien numéro et l'actuel
  côte à côte, ou une citation de l'humain) ; une mention que le fichier portait déjà avant
  l'écriture, comme pour toute référence, le hook ne jugeant que ce qui
  est neuf au fichier (T-0083 le resserre aux lignes ajoutées) ; une
  écriture par le shell (un heredoc, le titre que reçoit `socle new`),
  que le hook ne lit pas comme l'écriture d'un fichier.
- **Pourquoi c'est acceptable.** Un ancien numéro se résout partout
  (`socle show`, `socle url`, les contrôles des références, la lecture
  prouvée) et ne se réattribue jamais : un ancien numéro qui passe ne
  trompe ni un contrôle ni un lecteur, il lui coûte une résolution de
  plus. Le refus aide l'agent au moment où il écrit ; il ne garantit
  rien. C'est pourquoi la CI ne le juge pas : elle refuserait un texte
  juste.

## Conséquences

- Le format (`engine/socle/FORMAT.md`) dit la règle ; ce modèle dit ce
  qu'elle laisse passer, dans le cadre d'ADR-0082@beb85978 : les formes
  qu'un agent écrit, sans chercher l'écriture qui contourne.
- Il peut refuser à tort, dans un worktree d'avant une renumérotation, un
  identifiant encore vivant dans cet arbre : rare, et le refus se voit
  aussitôt.
- Pour défaire : une ADR qui la remplace ; T-0083, quand il sera fait,
  met à jour ce qu'il laisse passer.
