<!-- socle: couche=backlog zone=publique -->
# B-0283 — Un seuil que le moteur lit avec une valeur par défaut, absent des garde-fous, s'écrit plus haut sans demande : le cliquet ne connaît pas les défauts de nocopy.min_chars et staleness.active_days

> statut : abandonné · origine : J-2026-11-18-D · lu : backlog@10d2a1cf · ref : D-0168

Vu en corrigeant `nan` au cliquet des garde-fous (J-2026-11-18-D), pas
corrigé : un défaut voisin. Le moteur lit `[nocopy] min_chars` à 200 et
`[staleness] active_days` à 7 quand les garde-fous ne les écrivent pas
(`checks_docs.py`, `checks_memory.py`, `state.py`) ; le cliquet, lui, ne
connaît leur défaut que pour les trois clés de `checks_ratchet.DEFAUTS`.
Absente à la base, une telle clé « apparaît », ce qu'il juge un
durcissement libre : `assouplissements({}, {"nocopy": {"min_chars":
100000}})` et `assouplissements({}, {"staleness": {"active_days":
inf}})` rendent `[]`, mesuré sur le moteur. L'effet : `docs.copie` ou la
péremption du chantier actif désarmés sans demande, que rien ne rattrape
ensuite. Le gabarit écrit les deux clés : il faut un projet dont les
garde-fous ne les ont plus, ou pas encore.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X1 — ne compte que si l'agent cherche à contourner le socle » : un seuil absent des garde-fous s'écrit plus haut sans demande. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] écrire plus haut que la valeur par défaut du moteur une clé de seuil absente de la base exige une demande validée, pour chaque clé que le moteur lit avec un défaut, et un test le montre
