<!-- socle: couche=backlog zone=publique -->
# B-0284 — La fin de tour coupée par le délai de son hook, 600 s : au-delà, la durée des étapes rapides ni ne se garde ni ne se dit

> statut : abandonné · origine : J-2026-11-18-F · lu : backlog@a966cd7a · ref : D-0168

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

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » : une fin de tour plus longue que le délai de son hook serait coupée sans le dire ; déduit des réglages, jamais vu, et `verify --fast` comme le hook avant envoi le disent encore. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] une fin de tour dont les étapes rapides passent le délai de son hook le dit à l'humain et à l'agent, ou le modèle de menace de B-0258 range ce cas dans ce qu'il laisse passer, par une décision
