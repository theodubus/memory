<!-- socle: couche=backlog zone=publique -->
# B-0079 — Une session reprise hors de la racine du projet n'est pas détectée par socle state

> statut : fait · origine : J-2026-10-20-T · ref : J-2026-10-22-C · lu : backlog@1615e20b

Une session de Claude Code reprise hors de la racine du projet (après
l'ajout d'un second dépôt, J-2026-10-20-T) n'a plus de hooks, mais
`socle state` ne le dit pas : `hooks.hooks_non_charges` cherche dans la
trace un SessionStart de la session, et une session reprise garde
l'identifiant qui en avait eu un avant. Le hook avant commit le rattrape
(`filtre_absent`), pas l'état. Juger plutôt le dernier passage des hooks
de la session : un SessionStart plus ancien que la dernière reprise, ou
aucun PreToolUse depuis, dit des hooks déchargés. À faire après le retrait
de la compatibilité (D-0033).
