<!-- socle: couche=backlog zone=publique -->
# B-0298 — L'étape 2 du skill socle-review fait encore lancer socle review sans écrire sa sortie dans un fichier : un agent qui suit le bloc de code met le dossier dans la conversation

> statut : abandonné · origine : J-2026-11-19-N · lu : backlog@d7d8bee7 · ref : D-0168

Relevé par la revue de L-0015, passe 1 (J-2026-11-19-N), constat 1 pour
le backlog. T-0062 fait dire à l'étape 3 du gabarit `socle-review` que la
sortie de `socle review` s'écrit dans un fichier hors du dépôt, dont le
relecteur ne reçoit que le chemin ; mais le bloc de code de l'étape 2
reste `python3 .socle/socle review`, sans redirection. Un agent qui
exécute ce bloc tel quel met le dossier dans la conversation qui
orchestre, ce que B-0277 voulait éviter. Pistes : le dire dans l'étape 2,
ou une option `socle review --output <fichier>` (T-0062 l'envisageait).
Le gabarit est près de son plafond de 8 000 octets.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X3 — peaufine la machinerie sans gêne constatée » : l'étape 2 du skill de revue ; son étape 3 dit déjà d'écrire le dossier dans un fichier. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] un agent qui suit l'étape 2 du skill `socle-review` à la lettre n'a pas le dossier dans sa conversation
