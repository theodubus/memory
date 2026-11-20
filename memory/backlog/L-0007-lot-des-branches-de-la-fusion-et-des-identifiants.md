<!-- socle: couche=backlog zone=publique -->
# L-0007 — Lot des identifiants et de ce qu'une branche ajoute : la renumérotation après un rebase, le titre qui finit par un dièse, les identifiants d'un correctif, le dossier de la revue et le lien d'une demande sur une pull request

> statut : en cours · origine : J-2026-11-15-J · après : L-0006, T-0021, T-0065, T-0019, T-0085, T-0022 · lu : backlog@19378efe · ancien : B-0237

L'historique des branches et les identifiants de la mémoire : la
plage qu'un push juge quand la branche distante a disparu (B-0167), la
renumérotation d'une collision née d'un rebase (B-0176), la fusion de
sa pull request par l'agent, une option de la politique que l'humain
active (B-0200), et le lecteur des titres qui perd un dièse final
(B-0203). Deux thèmes voisins, réunis pour leur petite taille.

La revue du lot 5 y ajoute la branche qui a fusionné la branche par
défaut en cours de lot (B-0241).

Le 16 novembre, selon la règle qui réunit dans un lot les sujets qui touchent les mêmes fichiers ou le même garde-fou, appliquée à tout le backlog ouvert (J-2026-11-16-J) : les garanties hors du hook, dont la protection de la branche par défaut (B-0262), et l'état qui demande de supprimer une branche que GitHub n'a plus (B-0193), les branches comme B-0167.

Le 17 novembre, D-0129 y ajoute B-0279 et sa tâche T-0064, avec la fusion par l'agent (T-0020), et le défaut des identifiants d'une passation, B-0280 et sa tâche T-0065 (J-2026-11-17-H).

Le 20 novembre, coupé à son annonce, au-delà du seuil de neuf tâches
(ADR-0101) : la plage d'un push, la fusion par l'agent, ce qu'on
vérifie après elle, la remise des copies et les garanties hors du hook
(T-0018, T-0020, T-0064, T-0112, T-0023) forment L-0020, juste après
lui ; il garde les identifiants de la mémoire et ce qu'une branche
ajoute à la branche par défaut (J-2026-11-20-AE).

## Revues

### Passe 1 — 2026-11-20

Commits : 3e462041..db6b1b40

- Bloquant : socle renumber renomme l'entrée de la branche par défaut après sa fusion dans une branche poussée
- Bloquant : la seconde revue montre ce qu'une fusion de la branche par défaut a apporté
- Ouvre : B-0315, B-0316
