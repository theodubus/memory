<!-- socle: couche=backlog zone=publique -->
# B-0295 — La règle de consommation de socle-batch reste ambiguë : la marge du rangement au lancement, la fenêtre de l'estimation, où se lisent les mesures, et aucune borne de ce que la session implémente sur un lot

> statut : abandonné · origine : J-2026-11-19-D · lu : backlog@00582480 · ref : D-0168

La règle de consommation du skill `socle-batch` (T-0037, T-0099) reste
ambiguë à appliquer, relevé par la revue de L-0018 (J-2026-11-19-D) :
« couvre son coût mesuré et celui du rangement » laisse lancer un
sous-agent qui fera passer sous la marge de dix points ; l'estimation à
l'annonce ne dit ni quelle fenêtre ni la marge ; la clôture doit noter
au journal le coût du rangement, qui vient après elle ; aucune forme
fixe ne dit où l'agent lit les mesures à l'annonce ; aucune borne
cumulée ne limite ce que la session qui orchestre implémente sur un lot
(six petites tâches de 140 lignes s'y feraient toutes) ; `delegate-lot`
dit encore « les seuils du skill du produit » et garde les mesures dans
`docs/fabrication/consommation.md`. Le gabarit est à son plafond de
8 000 octets : la correction doit y tenir.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X3 — peaufine la machinerie sans gêne constatée » : la règle de consommation de `socle-batch` récrite sans ambiguïté. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] un agent qui suit socle-batch sait, sans interpréter, s'il peut lancer un sous-agent, si un lot tient dans ce qui reste, et où lire les coûts mesurés
- [ ] ce que la session qui orchestre implémente sur un lot a une borne
