<!-- socle: couche=backlog zone=publique -->
# T-0118 — socle next-id calcule l'identifiant comme socle new, branches distantes et correctifs suivis compris

> statut : abandonné · origine : J-2026-11-20-AG · besoin : B-0314 · lu : backlog@862358c7 · ref : D-0168

Un commit : `cmd_next_id` passe `identifiants.pris_ailleurs(racine, type_)` à `prochain_id`, comme `socle new` ; son test, qui échoue sur le commit parent ; une note de version.

T-0118 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0314, sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] dans un dépôt dont une branche distante et un correctif suivi ont pris des identifiants, `socle next-id` les saute, et un test le montre
