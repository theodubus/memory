<!-- socle: couche=backlog zone=publique -->
# B-0372 — Trois refus savent leur correction sans la donner : l'empreinte d'une consigne citée sans elle, le fichier non suivi à retirer, le texte qui cite un chemin protégé

> statut : fait · origine : J-2026-11-27-U · ref : D-0235, T-0211, J-2026-11-27-Y, J-2026-11-27-Z · lu : backlog@4d53be09

Chez chess, quatre refus (`docs/fabrication/chess/cout-et-frictions-2026-11-26.md`, §3.2, §3.5 et §3.8), confirmés
dans le code (`docs/fabrication/chess/relecture-cout-et-frictions-2026-11-27.md`) :

- une consigne citée sans son empreinte est refusée par
  `memoire.lectures`, qui renvoie à `socle show` sans donner l'empreinte
  qu'il connaît, même dans le commit qui crée la consigne ;
- le premier refus d'un fichier protégé modifié donne les formes de
  remise en état sans dire que `rm` vaut pour un fichier que git ne suit
  pas, ce que dit le second ;
- un heredoc de python qui cite `.socle/socle` dans un texte est refusé
  (`_cites`, `engine/socle/hooks.py`) : le hook reste tel quel (P4,
  ADR-0072), son message dit en plus qu'un texte qui cite un chemin
  protégé s'écrit par l'outil d'écriture.

Retenu par Théo le 27 novembre (D-0235, point 2). Le hook de l'agent
s'ouvre sur cette preuve (ADR-0098).

## Modèle de menace

Le contrôle des lectures arrête une consigne citée sans la preuve que sa
version a été lue. Il laisse passer désormais une consigne citée sans
empreinte dans la plage qui la crée : l'agent vient de l'écrire, il n'a
rien d'autre sous les yeux. Une consigne d'avant la plage reste exigée
avec son empreinte. Les deux autres refus ne changent que leur message.

## Satisfait quand

- [x] le refus d'une consigne citée sans empreinte donne l'empreinte à citer
- [x] une consigne née dans la plage jugée s'y cite sans empreinte
- [x] le refus d'un fichier protégé dit que `rm` vaut pour un fichier que git ne suit pas, et celui d'un écrivain qui cite un chemin protégé dit d'écrire ce texte par l'outil d'écriture
