<!-- socle: couche=backlog zone=publique -->
# B-0283 — Un seuil que le moteur lit avec une valeur par défaut, absent des garde-fous, s'écrit plus haut sans demande : le cliquet ne connaît pas les défauts de nocopy.min_chars et staleness.active_days

> statut : ouvert · origine : J-2026-11-18-D · lu : backlog@10d2a1cf

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

## Satisfait quand

- [ ] écrire plus haut que la valeur par défaut du moteur une clé de seuil absente de la base exige une demande validée, pour chaque clé que le moteur lit avec un défaut, et un test le montre
