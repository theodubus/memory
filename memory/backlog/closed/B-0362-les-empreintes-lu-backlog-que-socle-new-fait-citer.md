<!-- socle: couche=backlog zone=publique -->
# B-0362 — Les empreintes « lu : backlog@… » que socle new fait citer sont refusées dès qu'une entrée du backlog change avant le commit

> statut : fait · origine : J-2026-11-26-AB · lu : backlog@dd11ac18 · ref : ADR-0083, J-2026-11-26-AO

Le point 1 du retour d'usage de chess du 26 novembre
(`docs/fabrication/chess/usage-2026-11-26.md`) : `socle new` fait citer
l'empreinte de l'index de l'arbre, les entrées du tour déjà écrites
comprises ; `memoire.lectures` n'accepte que l'index de la base, d'un
commit de la plage ou de l'arbre, à quelques entrées nouvelles près
(ADR-0083). Dès qu'une ligne de l'index change avant le commit, un
statut passé à « en-cours » ou à « fait », un titre retouché, les
empreintes des entrées écrites avant ce changement sont refusées.
Reproduit dans ce dépôt : deux tâches et un lot créés, puis une tâche
existante passée en cours, refusent la deuxième tâche et le lot ; la
première passe, son empreinte étant celle de la base. Le tri qui a ouvert
ce besoin l'a montré aussi, sans aucun changement de statut : deux
`socle new need … --task …` à la suite font refuser la première tâche, le
second besoin et sa tâche, les formes alternant. Former un lot le
déclenche à chaque fois, et le seul contournement, recopier l'empreinte
courante dans chaque entrée, vide la preuve de lecture de son sens.

## Satisfait quand

- [x] des entrées créées par `socle new` dans un même tour, suivies d'un changement de statut avant le commit, passent `memoire.lectures` sans retouche de leur empreinte
