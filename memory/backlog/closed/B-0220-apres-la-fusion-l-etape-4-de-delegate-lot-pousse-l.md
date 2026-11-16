<!-- socle: couche=backlog zone=publique -->
# B-0220 — Après la fusion, l'étape 4 de delegate-lot pousse la branche rebasée et recrée la branche distante que GitHub a supprimée

> statut : fait · origine : J-2026-11-14-S · ref : J-2026-11-14-U · lu : backlog@66065ac9

Relevé de Théo le 14 novembre (J-2026-11-14-S). L'étape 4 de
« Intégrer, pousser, fusionner » du skill `delegate-lot` dit, après la
fusion : `git fetch origin main`, `git rebase origin/main`, pousser. La
branche rebasée n'a alors rien de plus que la branche par défaut : la
pousser recrée la branche distante que GitHub a supprimée à la fusion,
au commit de fusion, et l'état la donne ensuite à Théo à supprimer
(`ccr-396af4f0-yv89xr`, à 472178a, après la pull request #47). Ce que
l'étape fait encore après (le chantier actif et le journal mis à jour)
part sur cette branche recréée et ne rejoint la branche par défaut qu'avec
la pull request suivante ; J-2026-11-14-E l'avait déjà montré.

B-0199 porte cette étape dans le produit : la corriger là.

## Satisfait quand

- [x] après la fusion, la procédure ne pousse pas une branche qui n'a rien de plus que la branche par défaut ; ce qu'elle écrit après la fusion (chantier actif, journal) part avec le travail suivant, ou se fait avant la fusion
