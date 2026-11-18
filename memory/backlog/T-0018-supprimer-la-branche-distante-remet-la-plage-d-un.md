<!-- socle: couche=backlog zone=publique -->
# T-0018 — La plage d'un push dont la branche distante a disparu sans fusion se juge depuis son dernier commit poussé

> statut : ouvert · origine : J-2026-11-11-G · besoin : B-0167 · lu : backlog@9966bbbd

Un commit : le hook avant push garde en local le dernier commit poussé de chaque branche et juge depuis lui la plage d'une branche distante disparue sans fusion ; à défaut, une décision dit pourquoi ce n'est pas empêché, et le refus dit que supprimer la branche n'est pas une issue.

## Fait quand

- [ ] une valeur attendue poussée, puis affaiblie et repoussée après la suppression de la branche distante, est refusée par le hook avant push, et un test le montre ; ou une décision dit pourquoi ce n'est pas empêché, et le refus le dit
