<!-- socle: couche=backlog zone=publique -->
# B-0309 — Le recul écrit après chaque passe de revue et à la clôture d'un lot n'a jamais arrêté un lot : quatorze reculs, tous « continuer » ; son obligation pèse sur chaque lot et chaque projet installé

> statut : ouvert · origine : J-2026-11-20-D · ref : D-0144 · lu : backlog@c64d1644

Mesuré le 20 novembre (J-2026-11-20-D) : depuis ADR-0084, quatorze
passes de revue sur neuf lots, quatorze reculs, tous « continuer » ;
celui de L-0019 a décrit la boucle du hook et conclu « continuer ». Par
construction, il pose la question à l'agent qui veut finir son lot, et
pour une passe de plus : une boucle d'un lot à l'autre lui échappe. Son
obligation coûte un paragraphe à chaque passe et à chaque clôture,
refusé par l'outil s'il manque, environ 120 lignes du moteur dans neuf
modules et un fichier de tests, et part dans chaque projet installé.
Théo a validé son retrait (D-0144) : l'historique des passes reste, qui
sert à une session neuve qui reprend un lot ; le tri des constats reste,
sans la catégorie des formes du shell (ADR-0098, D-0128).

## Satisfait quand

- [ ] une passe de revue et la clôture d'un lot relu ne demandent plus de recul, et l'historique de ses passes reste lisible dans le lot
