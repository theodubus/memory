<!-- socle: couche=backlog zone=publique -->
# B-0126 — Installer le socle sur chess : le pilote stable, un essai à blanc, puis l'installation

> statut : ouvert · origine : J-2026-11-02-K · après : D-0073 · lu : backlog@f649164c

Théo a demandé si le socle était assez mûr pour chess, son projet en
cours (J-2026-11-02-H), et validé le plan proposé (D-0073). Ce que la
mémoire établit sur chess : l'audit d'adoption y passe (F-0004), `verify`
y exécute sa CI (F-0008), l'installation s'y fait sans conflit (F-0011),
et les trois retours de son essai à blanc du 29 octobre sont corrigés.
Mais chaque retour du pilote depuis le 30 octobre a fait corriger le
socle, et l'essai à blanc date d'avant plus de dix pull requests.

Trois choix reviendront à Théo à l'installation : renommer `CLAUDE.md`,
que 35 fichiers de chess nomment ; valider l'adaptateur proposé
(`docs/fabrication/chess/adaptateur.toml`) ; écrire une raison sur le test
de déterminisme de la recherche. Les plafonds de mutation se reprennent de
`docs/fabrication/chess/mutation-caps.toml` (B-0009).

## Fait quand

- [ ] deux journées de travail réel du pilote sans retour qui corrige le socle
- [ ] un essai à blanc sur chess, avec la version publiée, sans constat bloquant
- [ ] le socle installé sur chess pour de bon, en mode adoption, l'installation fusionnée
