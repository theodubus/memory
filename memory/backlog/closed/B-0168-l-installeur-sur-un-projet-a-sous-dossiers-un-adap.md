<!-- socle: couche=backlog zone=publique -->
# B-0168 — L'installeur sur un projet à sous-dossiers : un adaptateur déduit d'un sous-dossier se lance à la racine, l'audit dit que tout passe sans lancer les capacités

> statut : fait · origine : ADR-0059 · ref : J-2026-11-11-S · lu : backlog@b809be1f

L'essai à blanc sur chess (`docs/fabrication/chess/essai-a-blanc-2026-11-11.md`, constats 1.1 et 1.2) : en automatique,
l'installeur a posé l'adaptateur JavaScript parce qu'un sous-dossier porte
un manifeste, et ses commandes, lancées à la racine, échouent ; il a
pourtant fini sur « tout passe », son audit ne lançant pas les capacités.
L'adaptateur préparé pour chess ne peut pas se donner à l'installeur, qui
ne prend qu'un nom, et les hooks de l'agent, chargés dès que les réglages
sont écrits, refusent ensuite de l'écrire. Le budget du fichier
d'instructions a été posé à 66 octets de sa taille. Le guide dit que la
session qui installe tourne sans les hooks, ce qui n'est plus vrai.

## Fait quand

- [x] en automatique, un langage dont le manifeste n'est que dans un sous-dossier ne reçoit pas d'adaptateur lancé à la racine, et l'installeur le dit
- [x] la fin de l'installation dit que les capacités de l'adaptateur n'ont pas été lancées, et « Et maintenant » fait lancer la vérification rapide avant le premier commit
- [x] l'option de l'adaptateur accepte le fichier d'un adaptateur propre au projet
- [x] le budget du fichier d'instructions posé à l'adoption laisse une marge, que l'installeur dit
- [x] le guide dit que les hooks de l'agent se chargent dans la session qui installe, et comment revenir d'un essai
