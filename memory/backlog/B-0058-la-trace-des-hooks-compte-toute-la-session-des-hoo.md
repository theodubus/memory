<!-- socle: couche=backlog zone=publique -->
# B-0058 — La trace des hooks compte toute la session : des hooks de l'agent qui cessent de tirer passent pour chargés

> statut : fait · origine : J-2026-10-14-E · lu : backlog@d7395585 · ref : J-2026-10-14-K

Mesuré dans cette session : depuis sa reprise, ouverte au-dessus du dépôt,
les hooks de l'agent ne tirent plus (aucun PreToolUse ni Stop dans la trace
depuis le 12 oct. au soir), et chaque commit porte pourtant
`Socle-Hooks: SessionStart=34 PreToolUse=2186 Stop=36` : la trace compte
tous les tirs de la session, d'avant comme d'après. `hooks.trace` passe
donc, et l'avertissement de B-0050 se tait. Compter les tirs depuis le
commit précédent de la session (ou depuis l'heure de ce commit), pour
qu'un commit dont aucun hook n'a tiré le dise.
