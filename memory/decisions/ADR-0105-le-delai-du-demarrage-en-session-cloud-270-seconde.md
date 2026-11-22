<!-- socle: couche=decisions zone=publique -->
# ADR-0105 — Le délai du démarrage en session cloud : 270 secondes partagées, l'historique d'abord, au plus 120 secondes, puis 15 après un échec dans le même conteneur ; les outils ont le reste, au moins 140 secondes

> statut : acceptée · date : 2026-11-22 · source : T-0036@54a2d7b2, T-0078@06c1d5b7, B-0219@ec8ed499, J-2026-11-14-J@fa4fab91, J-2026-11-14-I@562305b1, B-0202@1fbef6c3, ADR-0035@d22aff8d, D-0111@034d5e87 · lu : decisions@7acfa1c2

## Contexte

En session cloud, le hook de démarrage installe les outils de
l'adaptateur, en 270 secondes sous les 300 du hook que pose l'installeur
(ADR-0035@d22aff8d, le gabarit `.claude/settings.json`). B-0202@1fbef6c3
y a ajouté, avant eux, l'historique d'un clone superficiel
(`git fetch --unshallow`), au plus 120 secondes, sous le même délai
(J-2026-11-14-I@562305b1). La revue l'a relevé (J-2026-11-14-J@fa4fab91,
B-0219@ec8ed499) : aucune décision ne dit ce partage, aucun test ne
montre ce que les outils reçoivent (T-0036@54a2d7b2), et un fetch qui
pend repaie ses 120 secondes à chaque démarrage du même conteneur, une
reprise ou un compactage (T-0078@06c1d5b7). Les deux fetch sans délai de
`recuperer_pull_requests` restent écartés (D-0111@034d5e87).

Mesuré (ADR-0035) : les outils de `python-pytest` s'installent en sept
secondes environ. Un fetch de l'historique qui aboutit prend quelques
secondes ; les 120 ne se paient que s'il pend.

Écartés : deux délais fixes, l'un pour l'historique, l'autre pour les
outils, ôteraient aux outils ce que l'historique n'a pas pris, quand le
clone est complet ou que le fetch aboutit vite, c'est-à-dire presque
toujours ; les outils d'abord, une installation longue (`npm ci`, une
chaîne de compilation) prendrait à l'historique tout son temps, alors
que le premier commit de l'agent en dépend (B-0202).

## Décision

1. **Un seul délai pour le travail du démarrage, 270 secondes**
   (`DELAI_DEMARRAGE`, `engine/socle/hooks.py`), compté dès l'entrée du
   hook. Le hook que pose l'installeur en a 300 : les 30 qui restent sont
   à l'état, imprimé ensuite. Un test lit la borne du gabarit et refuse
   un délai qui ne les laisse plus.
2. **L'historique d'abord, au plus 120 secondes** (`DELAI_HISTORIQUE`),
   puis 10 au plus pour s'arrêter proprement (`ARRET_HISTORIQUE`) : 130
   au pire.
3. **Les outils ont le reste du même délai**, toutes leurs commandes
   ensemble : 270 moins ce que l'historique a pris, au moins 140
   secondes, et 270 quand l'historique n'a rien à faire. Un test le
   montre, l'historique prenant son pire.
4. **Un échec de l'historique se marque pour le conteneur** : délai
   dépassé ou code non nul, une marque `historique-echoue` à côté de la
   trace des hooks, comme `outils-installes`. Au démarrage suivant du même
   conteneur, l'historique se retente sous 15 secondes seulement
   (`DELAI_HISTORIQUE_REPRISE`), arrêt en plus : les outils ont alors au
   moins 245 secondes. La ligne `!!` dit, comme au premier échec, la
   commande à relancer à la main. Un conteneur neuf, une session neuve,
   n'a pas la marque.

Un délai court plutôt que rien : un échec bref (une origine injoignable
un instant, des identifiants pas encore prêts) se rattrape souvent à la
reprise, pour une seconde ; un fetch qui pend n'y coûte plus que 15
secondes, au lieu de 120.

## Conséquences

- Le pire démarrage d'un conteneur neuf : 130 secondes d'historique, 140
  d'outils, puis l'état ; à une reprise après un échec, 25 secondes
  d'historique au pire.
- Un historique qui demande plus de 15 secondes et qui a échoué une fois
  ne se complète plus seul dans ce conteneur : l'agent lance la commande
  que la ligne `!!` lui donne, avant de commiter.
- Défaire : changer les constantes de `hooks.py`, que les tests nomment,
  avec cette décision ; retirer la marque rend à chaque démarrage les 120
  secondes.
