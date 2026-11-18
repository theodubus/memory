<!-- socle: couche=backlog zone=publique -->
# B-0290 — La fin de tour qui bloque sur des contrôles en échec ne recopie pas toute leur sortie dans la conversation

> statut : ouvert · origine : D-0134 · lu : backlog@670d431f

La proposition 3 de `docs/fabrication/allegements.md`, validée par
Théo (D-0134, J-2026-11-18-U). Quand les tests échouent en fin de tour,
le hook `Stop` recopie le rapport entier des contrôles, sortie des tests
comprise : environ 10 000 jetons de traces, deux fois dans la session de
L-0016, que chaque étape suivante de la conversation relit. Le hook
bloque toujours ; il ne donnerait que le nom des contrôles en échec, la
première ligne utile de chaque test en échec et la commande qui montre
tout.

## Satisfait quand

- [ ] le refus du hook de fin de tour sur des contrôles en échec tient en quelques lignes par contrôle : son nom, la première ligne utile de chaque test en échec, et la commande qui montre tout
- [ ] la fin de tour bloque, escalade et laisse passer une relance inchangée comme avant
