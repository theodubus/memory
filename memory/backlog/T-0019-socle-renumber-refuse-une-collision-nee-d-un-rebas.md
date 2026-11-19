<!-- socle: couche=backlog zone=publique -->
# T-0019 — socle renumber reconnaît, parmi deux entrées d'un même identifiant, celle que la branche ajoute

> statut : ouvert · origine : J-2026-11-11-S · besoin : B-0176 · lu : backlog@9966bbbd

Un commit : après un rebase, `socle renumber <id>` distingue l'entrée que la branche ajoute de celle que la base a prise, et renumérote la première, ses mentions et ses empreintes.

## Fait quand

- [ ] après un rebase qui fait se heurter deux décisions du même numéro, `socle renumber` renumérote celle de la branche, ses mentions et ses empreintes, et un test le montre
- [ ] deux entrées du journal du même identifiant dans un même fichier : `socle renumber` ne renumérote que celle que la branche ajoute, et laisse l'autre et ses mentions telles quelles, et un test le montre
