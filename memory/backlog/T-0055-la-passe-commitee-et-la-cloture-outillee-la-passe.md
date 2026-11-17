<!-- socle: couche=backlog zone=publique -->
# T-0055 — La passe commitée et la clôture outillée : la passe écrite sans commit là où socle review tourne se perd, et la clôture ne montre ni l'historique ni les trois questions

> statut : ouvert · origine : J-2026-11-16-Y · besoin : B-0263 · lu : backlog@074664f1

Relevé par la revue de T-0047, passe 2 du lot L-0013 (J-2026-11-16-Y),
constats 2 et 5 pour le backlog. `socle review` écrit la passe dans
l'entrée du lot, sans commit, là où elle tourne : le skill `socle-review`
ne dit pas de la commiter, et le skill `delegate-lot` de ce dépôt produit
le dossier dans le worktree du sous-agent, où elle se perd ; la passe
suivante récrit alors « Passe 1 », sans recul exigé. Et à la clôture,
ni le contrôle ni `socle review` ne montrent l'historique, ce que git
donne et les trois questions du recul. Le livrable, un commit : le skill
`socle-review` et son gabarit disent de commiter la passe, `delegate-lot`
produit le dossier sur la branche d'intégration, et le refus de la
clôture montre ce que montre celui d'une passe.

## Fait quand

- [ ] le gabarit du skill `socle-review` dit de commiter la passe écrite, et le skill `delegate-lot` de produire le dossier sur la branche d'intégration
- [ ] le refus de la clôture d'un lot sans recul montre l'historique, ce que git donne et les trois questions, et un test le montre
