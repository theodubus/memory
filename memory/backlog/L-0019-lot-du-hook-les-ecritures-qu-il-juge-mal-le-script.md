<!-- socle: couche=backlog zone=publique -->
# L-0019 — Lot du hook, les écritures qu'il juge mal : le script d'un heredoc, la liste qu'un find ou un grep donne à xargs, la conjonction des filtres d'un find

> statut : en cours · origine : J-2026-11-19-Q · après : L-0005, T-0001, T-0070, T-0002, T-0004, T-0003, T-0106 · lu : backlog@5be800e9

Coupé de L-0005 le 19 novembre sur son coût estimé (J-2026-11-19-Q) :
la moitié de L-0005 qui en portait le titre. Ce que le hook de l'agent
juge mal quand une commande écrit ou supprime : le script qu'un heredoc
ou les arguments d'un `python -c` donnent à python (T-0001, T-0070), la
liste qu'un `find`, un `grep -r` ou un `git ls-files` donne à `xargs`
(T-0002, T-0004), la conjonction des filtres d'un `find` (T-0003). Les
mêmes fonctions du jugement des écritures et des suppressions
(`engine/socle/hooks.py`) et `tests/test_garde.py`, sous ADR-0082 ;
T-0004, de priorité haute, va avec T-0002, qui juge le même `xargs`.

Le 19 novembre, la passe 1 de la revue de L-0005 y fait entrer T-0106
(J-2026-11-19-Z) : la branche courante d'un `git push` écrite par une
substitution, dans les mêmes fichiers.

Le 19 novembre au soir, T-0001, T-0070, T-0004 et T-0003 sont faites,
pas encore relues ; T-0002 et T-0106 attendent la réponse de Théo à
D-0140, qui change trois valeurs attendues qu'elles contredisent
(J-2026-11-19-AI). La série part en passation, pour une session neuve.

D-0140 validée, T-0106 est faite (J-2026-11-19-AM) ; T-0002 est arrêtée
avant son code : la raison que D-0140 lui autorise ne tient pas dans le
projet d'essai, une demande nouvelle à poser (J-2026-11-19-AL).

## Revues

### Passe 1 — 2026-11-19

Commits : 852b0ac4..a7e93a03
