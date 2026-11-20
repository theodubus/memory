<!-- socle: couche=backlog zone=publique -->
# T-0084 — La remise des copies protégées attend aussi T-0017, et chaque lot qui change un gabarit après L-0006 finit par la remise de ses copies

> statut : fait · origine : J-2026-11-18-L · ref : J-2026-11-20-J · besoin : B-0218 · lu : backlog@0595d48a

Relevé par la revue de L-0014, passe 1 (J-2026-11-18-L), constat 1 pour
le backlog. T-0072, la remise des copies protégées de ce dépôt, se dit la
dernière de L-0006, après les tâches qui changent un gabarit, mais son
`après` omet T-0017, qui change le gabarit de `socle-request`, dont la
copie protégée est dans `.claude/skills/`. Ensuite, T-0034 et T-0037
(L-0009), T-0040 (L-0010), T-0079 et T-0082 changent des gabarits de
skills sans remise de leurs copies : le second résultat de B-0218 serait
défait juste après sa clôture. Le livrable, un commit de la mémoire :
T-0072 attend T-0017, et chaque lot d'après L-0006 qui change le gabarit
d'une copie protégée finit par une tâche qui la remet.

## Fait quand

- [x] T-0072 attend T-0017, et `python3 .socle/socle roadmap --format markdown --all` le montre
- [x] chaque lot ouvert qui change le gabarit d'une copie protégée finit par une tâche qui la remet, et `python3 .socle/socle roadmap --format markdown --all` le montre
