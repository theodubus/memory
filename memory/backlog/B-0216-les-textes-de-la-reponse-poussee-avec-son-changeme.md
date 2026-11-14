<!-- socle: couche=backlog zone=publique -->
# B-0216 — Les textes de la réponse poussée avec son changement disent « même tour » au lieu de « même push », et omettent le fichier protégé qui peut la précéder ; la copie protégée de socle-request en retard

> statut : ouvert · origine : J-2026-11-14-D · lu : backlog@f57ca0fd

La revue de B-0142 (J-2026-11-14-D), constat 3. Le gabarit du skill
`socle-request` (français et anglais) et ADR-0074 disent de pousser la
réponse avec son changement « dans le même tour » ; le message du
contrôle, le prompt de mise à jour de chess et le skill `delegate-lot`
disent « dans le même push », qui seul est juste : deux pushes dans un
même tour restent refusés. Le skill dit aussi de pousser la réponse
« avec » un fichier protégé, alors qu'un fichier protégé peut la précéder
sous une demande en attente (D-0071).

La copie protégée `.claude/skills/socle-request/SKILL.md` de ce dépôt est
en retard sur son gabarit depuis B-0142 : son rafraîchissement, sur une
demande, attend que ce texte soit juste.

## Fait quand

- [x] tous les textes disent « dans le même push », et le cas du fichier protégé qui précède sa réponse
- [ ] la copie protégée de ce dépôt suit son gabarit, sur une demande validée
