<!-- socle: couche=backlog zone=publique -->
# B-0258 — La durée des étapes rapides se dit, et a un seuil : verify --fast n'imprime aucune durée, et rien ne signale qu'elle a passé de 143 s à près de douze minutes

> statut : ouvert · origine : J-2026-11-16-E · lu : backlog@6e1a17c2

Un sujet du produit, d'une analyse en lecture seule du 15 novembre sur
d1d296e, que Théo a fait inscrire (J-2026-11-16-E) ; il n'en fixe ni la
priorité ni le lot. Son constat, commun avec B-0257, y est écrit avec la
nature de chaque point (mesuré, écrit, déduit, vérifié) : `verify --fast
--redo` mesuré une fois à 11 min 49 s sur un seul cœur, quand
`docs/fabrication/recul.md` écrit 143 s le 13 octobre, sur une autre
machine ; vérifié, `verify --fast` n'imprime aucune durée.

Quoi : `verify --fast` dit la durée de chaque étape et leur total. Au-delà
d'un seuil des garde-fous, un avertissement, pas un échec, nomme l'étape
la plus longue.

Pourquoi : entre les deux relevés, la durée est passée de 143 s à près de
douze minutes sans que rien ne le signale. Les tailles ont un budget, les
durées n'en ont pas.

Conception à trancher, la spécification avant le code : où s'écrit le
seuil ; sa valeur par défaut (les cinq minutes viennent du cache d'un
agent, que le moteur ne connaît pas) ; ce que le cliquet en dit.

## Fait quand

- [ ] `verify --fast` imprime la durée de chaque étape et le total, et un test le montre
- [ ] un seuil dépassé donne un avertissement qui nomme l'étape, et un test le montre
