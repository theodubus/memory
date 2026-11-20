<!-- socle: couche=backlog zone=publique -->
# T-0118 — socle next-id calcule l'identifiant comme socle new, branches distantes et correctifs suivis compris

> statut : ouvert · origine : J-2026-11-20-AG · besoin : B-0314 · lu : backlog@862358c7

Un commit : `cmd_next_id` passe `identifiants.pris_ailleurs(racine, type_)` à `prochain_id`, comme `socle new` ; son test, qui échoue sur le commit parent ; une note de version.

## Fait quand

- [ ] dans un dépôt dont une branche distante et un correctif suivi ont pris des identifiants, `socle next-id` les saute, et un test le montre
