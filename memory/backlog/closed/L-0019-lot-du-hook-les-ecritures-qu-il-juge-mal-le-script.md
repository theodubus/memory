<!-- socle: couche=backlog zone=publique -->
# L-0019 — Lot du hook, les écritures qu'il juge mal : le script d'un heredoc, la liste qu'un find ou un grep donne à xargs, la conjonction des filtres d'un find

> statut : fait · origine : J-2026-11-19-Q · ref : J-2026-11-20-A · après : L-0005, T-0001, T-0070, T-0004, T-0003, T-0106 · lu : backlog@5be800e9

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

D-0142 posée pour elle, sans réponse avant la livraison : T-0002 sort du
lot et attend sa réponse, hors lot, comme D-0142 le dit. Les cinq
autres tâches faites et relues, la passe 1 et ses deux bloquants
corrigés, le lot est fait (J-2026-11-20-A).

## Revues

### Passe 1 — 2026-11-19

Commits : 852b0ac4..a7e93a03

- Bloquant : un argument inconnu d'un python -c qui lit ses arguments passe, et son test le range parmi les témoins sains
- Bloquant : le prompt de mise à jour de chess dit encore refusé le push de la branche courante que T-0106 fait passer
- Ouvre : B-0306, T-0108, B-0307, T-0109, B-0308

Recul : passe unique, ses deux bloquants n'ont pas de passe d'avant. Le
premier a la cause de ceux des lots du hook qui l'ont précédée : un
jugement nouveau, celui des arguments d'un `python -c`, qui laisse de
côté une forme voisine, la variable inconnue que tous les autres
écrivains refusent ; s'y ajoute ce que D-0141 vise, un trou connu écrit
parmi les témoins sains. Le second est un oubli de rédaction : un point
écrit avant T-0106 dans un document cumulatif. Ce que le lot ouvre est
de la nature de ce qu'il ferme : un filtre entre `find` et `xargs`
(B-0306) prolonge T-0004, le script qu'un heredoc écrit dans un fichier
(B-0308) prolonge T-0001, et le message d'un refus de trop (B-0307) suit
T-0001. Les lots clos sur ces fichiers en ont ouvert de telles, L-0005
(T-0106), L-0004 (B-0254) et L-0014 (T-0083), une ou deux par lot, que
D-0128 borne aux formes qu'un agent écrit ; celui-ci en ouvre trois, sur
cinq tâches. Les deux corrections tiennent en quelques lignes, la
première avec son test qui échoue sans elle : pas de passe de plus, la
clôture suit. Décision : continuer.
