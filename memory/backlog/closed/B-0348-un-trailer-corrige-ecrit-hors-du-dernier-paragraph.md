<!-- socle: couche=backlog zone=publique -->
# B-0348 — Un trailer Corrige écrit hors du dernier paragraphe du message ne fait pas du commit un correctif : tests.regression le saute sans le dire

> statut : fait · origine : J-2026-11-24-AN · lu : backlog@bfe38d20 · ref : J-2026-11-24-AY, T-0178

Relevé par la revue de L-0024 (J-2026-11-24-AN). `est_correctif`
(`engine/socle/checks_tests.py`) ne lit `Corrige` et `Fixes` que dans le
dernier paragraphe du message, comme git lit les trailers : une ligne
`Corrige: T-NNNN` écrite dans un paragraphe à part, avant les lignes
d'attribution, ne fait pas du commit un correctif, et `tests.regression`
en CI, comme l'avertissement du hook `commit-msg`, le sautent sans rien
dire. Aucun refus ne l'attend : T-0059 (B-0275) n'avait rien à enrichir.
Vu dans ce dépôt : sur 1 046 commits, 27 ont leur `Corrige:` hors du
dernier paragraphe, et pour 10, dont le sujet n'est pas `fix:`, la
vérification n'a pas tourné (2d48315, 03bacc0, 624af13, b4220fa, db6b1b4,
2032b8d, 9d11256, dbc035b, entre autres).

Pistes : lire aussi une telle ligne hors du bloc final comme un
correctif (`trailers_hors_bloc`, de T-0059), ou avertir au hook
`commit-msg` qu'elle ne compte pas.

## Satisfait quand

- [x] un commit qui écrit `Corrige:` hors du dernier paragraphe de son message n'échappe plus en silence à la vérification de son test de régression
