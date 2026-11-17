<!-- socle: couche=backlog zone=publique -->
# B-0129 — Une mise à jour qui fait grossir la section du socle peut faire dépasser à AGENTS.md le budget qu'une adoption a fixé au plus juste

> statut : fait · origine : J-2026-11-05-D · ref : ADR-0045 · lu : backlog@80164bf6

Relevé par la revue adversariale du lot de D-0075 (J-2026-11-05-D). La
section du socle d'AGENTS.md se régénère à chaque mise à jour ; le lot de
D-0075 l'a fait grossir d'environ 330 octets. Une adoption fixe le budget
d'AGENTS.md au millier d'octets supérieur à sa taille d'alors, et le
cliquet ne laisse ce budget que baisser. Un projet dont AGENTS.md était à
moins de 330 octets de son budget passe donc au rouge sur
`memoire.budgets` dès la mise à jour, et relever le budget exige une
demande validée. Ce dépôt a dû couper sa partie propre pour tenir.

À faire : que la mise à jour dise, avant de régénérer la section, si elle
fera dépasser le budget, et ce que l'humain peut faire (resserrer la partie
propre du projet, ou relever le budget par une demande) ; ou que la
croissance de la section du socle elle-même compte à part du budget de la
partie propre.

## Satisfait quand

- [x] une mise à jour qui fait dépasser son budget à `AGENTS.md` le dit, avec ce que l'humain peut faire
- [x] le contrôle des budgets donne le même remède pour un fichier d'instructions
