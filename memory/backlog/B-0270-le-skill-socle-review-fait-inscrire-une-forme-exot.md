<!-- socle: couche=backlog zone=publique -->
# B-0270 — Le skill socle-review fait inscrire une forme exotique dans la liste du guide, qu'un projet équipé ne peut pas écrire (.socle/engine est protégé)

> statut : ouvert · origine : J-2026-11-16-S · lu : backlog@ff00445d

Relevé par la revue du lot B-0264 (J-2026-11-16-S). Le gabarit du skill
`socle-review` dit qu'une forme du shell qu'un agent n'écrit pas, et qui
échappe au hook, s'écarte « d'une ligne, pour la liste des formes connues
que le hook ne juge pas », que tient le guide. Dans un projet équipé, le
guide est sous le moteur installé (.socle/engine), protégé : l'agent du projet ne peut pas
l'écrire, et rien ne lui dit de signaler la forme au dépôt du socle. Le
geste se produit à chaque revue d'un lot du hook dans un projet.

La piste : le skill dit, dans un projet équipé, d'écrire la forme au
récap et de la signaler en amont (où et comment, à décider), la liste du
guide ne changeant que dans le dépôt du socle.

## Fait quand

- [ ] le skill `socle-review` et son gabarit disent ce que l'agent d'un projet équipé fait d'une forme exotique, sans geste qu'il ne peut pas faire
