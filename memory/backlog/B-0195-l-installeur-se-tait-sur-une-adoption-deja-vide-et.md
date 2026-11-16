<!-- socle: couche=backlog zone=publique -->
# B-0195 — L'installeur se tait sur une adoption déjà vide, et réaffiche à chaque passage le diff des lignes de politique que l'humain a écrites

> statut : ouvert · origine : J-2026-11-13-D · priorité : basse · lu : backlog@4ed4e911

Relevé à la mise à jour du socle sur chess, le 13 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-13.md`, gênes 1 et 5).

Sur un projet dont l'adoption est déjà vide (aucun contrôle en
`warn_only`), l'installeur ne dit rien de l'adoption : l'agent de chess a
dû lancer un essai à blanc sur l'état d'avant pour vérifier qu'il n'y
avait rien à inscrire. Une ligne « aucun contrôle en adoption : rien à
inscrire » suffirait.

À chaque passage, l'installeur réaffiche aussi le diff de la politique
sur les deux lignes que Théo a écrites exprès dans celle de chess
(`[irreversible] tools`, `keep_branches`) : un écart voulu, répété comme
s'il était nouveau.

## Satisfait quand

- [ ] le « Fait quand » de T-0026 est tenu
