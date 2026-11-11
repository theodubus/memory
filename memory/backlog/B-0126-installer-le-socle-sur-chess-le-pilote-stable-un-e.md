<!-- socle: couche=backlog zone=publique -->
# B-0126 — Installer le socle sur chess : le pilote stable, un essai à blanc, puis l'installation

> statut : ouvert · origine : J-2026-11-02-K · après : D-0073, B-0154, B-0168, B-0169, B-0170 · lu : backlog@f649164c

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

Le 11 novembre, Théo lève l'attente du pilote (D-0096, ADR-0059) : les
lots importants du socle se livrent, puis l'essai à blanc et
l'installation se font dans la session de chess, sur son autre compte.

L'essai à blanc du 11 novembre (`docs/fabrication/chess/essai-a-blanc-2026-11-11.md`) a rendu deux constats bloquants
et des gênes : B-0168, B-0169 et B-0170 les corrigent avant l'installation, et le
compte rendu liste ce que l'installation doit trancher avec Théo.

La feuille de route de chess se pose à l'installation, à la main et avec
Théo, depuis son carnet de bord, avec ce que le socle sait déjà faire : des
sujets ordonnés par `après`, des jalons, des priorités, des critères de fin
(D-0094). La procédure de planification (B-0101) s'écrit ensuite, sur ce
que JustCook et chess auront montré.

## Fait quand

- [ ] les lots à livrer avant chess, ceux du jalon 1 (B-0154), sont fusionnés et publiés (ADR-0059)
- [ ] un essai à blanc sur chess, avec la version publiée, sans constat bloquant
- [ ] le socle installé sur chess pour de bon, en mode adoption, l'installation fusionnée
- [ ] la feuille de route de chess posée à la main avec Théo, depuis son carnet de bord : sujets ordonnés, jalons, priorités (D-0094)
