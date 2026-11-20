<!-- socle: couche=backlog zone=publique -->
# T-0110 — Retirer l'obligation du recul (son paragraphe, ses refus et contrôles, les marques de cause, l'arrêt par demande), garder l'historique des passes et le tri des constats sans la catégorie des formes du shell

> statut : ouvert · origine : J-2026-11-20-D · besoin : B-0309 · lu : backlog@03167aa3

Un commit, au lot L-0006 : `socle review` n'exige plus de recul avant
une passe ni à la clôture (`engine/socle/review.py`), le contrôle du
backlog ne le juge plus (`engine/socle/checks_memory.py`), les fonctions
du recul (`engine/socle/memory.py`), leurs messages, leurs défauts
injectés et leurs tests se retirent ; la section `## Revues` garde ses
passes et leurs lignes « Bloquant » et « Ouvre » ; les skills
`socle-review` et `socle-batch` et le guide ne disent plus le recul ; une
ADR remplace ADR-0084 ; une note de version. T-0104 est sans objet.

## Fait quand

- [ ] une passe de revue au-delà de la première et la clôture d'un lot relu passent sans recul, et un test le montre
- [ ] la section Revues d'un lot garde ses passes et leurs bloquants, et un test le montre
