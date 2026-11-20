<!-- socle: couche=backlog zone=publique -->
# T-0065 — socle new compte les identifiants qu'un correctif suivi du dépôt crée, et ne les reprend pas

> statut : fait · origine : J-2026-11-17-H · ref : J-2026-11-20-AG · besoin : B-0280 · lu : backlog@1df796e8

Un commit : le calcul de l'identifiant suivant compte aussi les entrées que créent les correctifs suivis du dépôt, comme le contrôle des références compte leurs chemins ; son test ; une note de version.

## Fait quand

- [x] `socle new` ne reprend pas un identifiant qu'un correctif suivi du dépôt (`*.patch`, `*.diff`) crée, et un test le montre
