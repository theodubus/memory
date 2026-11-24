<!-- socle: couche=backlog zone=publique -->
# T-0178 — Un trailer Corrige ou Fixes écrit hors du dernier paragraphe fait du commit un correctif : tests.regression vérifie son test

> statut : ouvert · origine : J-2026-11-24-AV · besoin : B-0348 · lu : backlog@56bc355f

Un commit : `est_correctif` (`engine/socle/checks_tests.py`) lit aussi
une ligne `Corrige:` ou `Fixes:` écrite hors du dernier paragraphe du
message (`trailers_hors_bloc`, de T-0059) : la première piste de B-0348,
qui fait ce que l'auteur voulait dire, plutôt qu'un avertissement qui
laisserait le commit sans vérification. Un durcissement du contrôle
`tests.regression` : une ADR le dit, avec son modèle de menace ; son
défaut injecté (un commit dont le `Corrige:` est hors du bloc final, sans
test qui échoue sur son parent) et son témoin sain dans
`engine/socle/selftest.py` ; une note de version.

## Fait quand

- [ ] un commit qui écrit `Corrige: T-NNNN` hors du dernier paragraphe, sans test qui échoue sur son parent, est refusé par `tests.regression`, et un test le montre
- [ ] le même commit, avec un tel test, passe, et un test le montre
