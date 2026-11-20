<!-- socle: couche=backlog zone=publique -->
# B-0314 — socle next-id ne saute ni les identifiants des branches distantes ni ceux des correctifs suivis, que socle new saute

> statut : ouvert · origine : J-2026-11-20-AG · lu : backlog@8d44189a

Vu en menant T-0065 (J-2026-11-20-AG) : `cmd_next_id`
(`engine/socle/cli.py`) appelle `prochain_id` sans `pris_ailleurs`. Il
ne saute donc ni les identifiants que prennent les branches distantes
(ADR-0026) ni ceux que crée un correctif suivi d'une passation (B-0280),
que `socle new` saute ; `FORMAT.md` les donne pourtant ensemble pour
calculer un identifiant. Un agent qui s'en sert reprend un numéro
qu'une autre branche a pris.

## Satisfait quand

- [ ] `socle next-id` rend l'identifiant que `socle new` prendrait, dans un dépôt dont une branche distante ou un correctif suivi a pris le suivant
