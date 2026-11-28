<!-- socle: couche=backlog zone=publique -->
# B-0391 — Le relevé du coût d'une séance par une commande : ses appels par nature et ses refus par contrôle, comparables d'une mesure à l'autre

> statut : ouvert · origine : J-2026-11-28-D · ref : B-0383, D-0233 · lu : backlog@68df6bf7

Le constat 9 du relevé d'après de chess
(`docs/fabrication/chess/cout-et-frictions-2026-11-28.md`). Le relevé
d'avant et celui d'après ont été faits à la main : un script de
classement écrit sur la transcription, qui s'est trompé trois fois (une
sortie qui contenait le mot « refus » comptée comme un refus, un texte
qui citait un `git revert` compté comme un commit). Chess demande une
commande qui rende les trois parties par la même méthode, pour qu'une
prochaine mesure se compare sans recompter.

JA-0003 demande déjà une commande qui relève les refus par contrôle,
depuis la trace des hooks. Les appels par nature se lisent dans la
transcription de l'agent, que le moteur ne connaît pas : la conception
dira ce qui va dans le moteur et ce qui va dans les hooks de l'agent.
Le relevé d'après montre aussi que deux mesures ne se comparent que sur
la même durée : 56 refus sur deux semaines d'un côté, 3 sur une séance
de l'autre.

## Satisfait quand

- [ ] une commande rend, pour une séance donnée, ses refus par contrôle et ses appels d'outil par nature, et un test le montre
- [ ] deux relevés de cette commande, sur deux séances, se comparent sans recompter à la main
