<!-- socle: couche=backlog zone=publique -->
# B-0284 — La fin de tour coupée par le délai de son hook, 600 s : au-delà, la durée des étapes rapides ni ne se garde ni ne se dit

> statut : ouvert · origine : J-2026-11-18-F · lu : backlog@a966cd7a

Vu par la passe 3 de la revue de L-0012 (J-2026-11-18-F), déduit des
réglages, non reproduit. Le hook de fin de tour a un délai de 600 s,
dans `.claude/settings.json` comme dans le gabarit
`engine/socle/templates/settings.json`. Quand les étapes rapides qu'il
lance passent ce délai, la dérive même qui a fait ouvrir B-0258 (709 s,
puis 650 s), Claude Code le coupe : `verification.etapes_rapides`
n'écrit sa trace qu'au bout, l'avertissement du seuil ne se dit pas, et
les contrôles de la fin de tour ne concluent pas. `verify --fast` et le
hook avant envoi, sans délai, le disent encore à l'agent ; l'humain n'en
reçoit rien, et le modèle de menace de B-0258 ne range pas ce cas dans
ce qu'il laisse passer.

La conception n'est pas tranchée : relever le délai (un réglage
protégé, son gabarit), arrêter les étapes de la fin de tour avant lui en
le disant, ou ranger le cas au modèle de menace.

## Satisfait quand

- [ ] une fin de tour dont les étapes rapides passent le délai de son hook le dit à l'humain et à l'agent, ou le modèle de menace de B-0258 range ce cas dans ce qu'il laisse passer, par une décision
