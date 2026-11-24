<!-- socle: couche=backlog zone=publique -->
# B-0319 — La section du socle de l'AGENTS.md de ce dépôt ne peut plus suivre son gabarit sous son budget : la phrase de la fusion par l'agent la ferait passer de 15 989 à 16 133 octets, pour 16 000

> statut : abandonné · origine : J-2026-11-20-AP · ref : T-0020, T-0069, D-0168 · lu : backlog@a5356c77

T-0020 ajoute au gabarit d'`AGENTS.md` (`engine/socle/templates/AGENTS.md`)
une phrase de 144 octets : si la politique le permet (le guide, « La
fusion par l'agent »), l'agent fusionne lui-même sa pull request, aux
conditions du skill `socle-batch`. La section du socle de l'`AGENTS.md`
de ce dépôt, à 15 989 octets pour un budget de 16 000, ne l'a pas
reçue : recopiée de son gabarit, comme T-0069 l'a fait (J-2026-11-20-Z),
elle le dépasserait de 133 octets. Ce dépôt n'en perd rien aujourd'hui :
sa règle propre (D-0092, « Règles propres à ce dépôt ») dit déjà la
fusion par l'agent. Mais la prochaine phrase ajoutée au gabarit bute sur
le même budget, et la section reste en retard tant qu'aucune place ne
se rend.

Pistes : resserrer la partie propre à ce dépôt (sa règle de la fusion
pourrait renvoyer à la phrase du gabarit), ou relever le budget par une
demande validée, puisque le relever assouplit un garde-fou.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X4 — ne concerne que ce dépôt » : la section du socle de l'`AGENTS.md` de ce dépôt et son budget. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] la section du socle de l'`AGENTS.md` de ce dépôt est celle de son gabarit, au chemin du moteur près, et `memoire.budgets` passe
