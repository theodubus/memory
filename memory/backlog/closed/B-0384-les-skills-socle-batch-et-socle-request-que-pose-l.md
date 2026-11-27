<!-- socle: couche=backlog zone=publique -->
# B-0384 — Les skills socle-batch et socle-request que pose l'installeur dépassent le plafond de 8 000 octets que garde un projet installé avant le 27 novembre

> statut : fait · origine : J-2026-11-27-AP · ref : B-0368, ce commit · lu : backlog@c0e72dd2

Le test de T-0223, qui rejoue la mise à jour de chess, trouve le commit
des fichiers de la mise à jour refusé par `memoire.budgets` :
`socle-batch` fait 8 035 octets et `socle-request` 8 340, pour le
plafond de 8 000 octets que chess garde de son gabarit des garde-fous.
La note `2026-11-27-a` promet pourtant que les skills que pose
l'installeur tiennent sous 8 000 octets ; T-0214 et T-0216, dans L-0055,
les ont fait grossir après elle. Constat bloquant de L-0056 : la mise à
jour suivante de chess casserait, et la CI de ce lot avec elle.

## Satisfait quand

- [x] le test qui rejoue la mise à jour de chess passe, chaque skill que pose l'installeur sous 8 000 octets
