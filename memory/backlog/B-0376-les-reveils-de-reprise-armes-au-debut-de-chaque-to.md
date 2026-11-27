<!-- socle: couche=backlog zone=publique -->
# B-0376 — Les réveils de reprise, armés au début de chaque tour et retirés à sa fin, coûtent environ 10 % des appels d'une séance

> statut : ouvert · origine : J-2026-11-27-U · ref : D-0235 · après : B-0375 · lu : backlog@4d53be09

Chez chess (`docs/fabrication/chess/cout-et-frictions-2026-11-26.md`, §5) : 12 appels sur 118 d'une séance, pour un
filet qui n'a pas servi ; ici aussi, cinq appels de réveil ont précédé
tout travail le 27 novembre (`docs/fabrication/chess/relecture-cout-et-frictions-2026-11-27.md`). Le skill `socle-resume` fait
armer au début de chaque tour qui agit et retirer à sa fin.

Retenu par Théo le 27 novembre (D-0235, point 6) : les réveils restent
d'une réponse à l'autre et ne se déplacent que quand leur heure change ;
un réveil sans objet coûte une vérification et une ligne à l'humain, que
la vérification au réveil rend sans danger. Sans `list_events`, l'heure
se lit dans `get_session`, qui ne donne que la fenêtre nommée.

## Satisfait quand

- [ ] un tour qui trouve ses réveils à la bonne heure n'appelle aucun outil de réveil
- [ ] un réveil sans objet se vérifie et se dit en une ligne, sans reprendre le travail
