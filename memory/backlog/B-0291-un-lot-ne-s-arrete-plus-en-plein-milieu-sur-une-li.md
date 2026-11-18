<!-- socle: couche=backlog zone=publique -->
# B-0291 — Un lot ne s'arrête plus en plein milieu sur une limite d'usage : son coût s'estime à son annonce, et il se découpe s'il ne tient pas dans ce qui reste

> statut : ouvert · origine : D-0134 · lu : backlog@670d431f

La proposition 5 de `docs/fabrication/allegements.md`, validée par
Théo (D-0134, J-2026-11-18-U). Les seuils du skill `socle-batch` (60 %
de la fenêtre de cinq heures, 85 % de la semaine) ne se vérifient
qu'avant chaque lancement de sous-agent : L-0016 a démarré à 1 % et
s'est arrêté à 67 %, en plein milieu, d'où une passation d'environ 8
points et le rechargement dans la session suivante. À l'annonce d'un
lot, l'agent estime son coût à partir des mesures (un sous-agent qui
implémente, un relecteur, une demande, dans
`docs/fabrication/consommation.md`) ; s'il ne tient pas dans ce qui
reste, il le découpe, commence par un lot plus petit, ou attend la
remise à zéro. T-0037 va déjà dans ce sens au niveau du sous-agent
(B-0249) ; ce besoin l'étend au lot.

## Satisfait quand

- [ ] un lot dont le coût estimé à son annonce ne tient pas dans ce qui reste de la fenêtre se découpe, se réduit ou attend sa remise à zéro, au lieu de s'arrêter en plein milieu
- [ ] l'estimation s'appuie sur des coûts mesurés, que l'agent lit à l'annonce
