<!-- socle: couche=backlog zone=publique -->
# L-0015 — Lot de l'historique des revues : la même passe sur un arbre sale, une ligne de bloquant mal écrite, la passe commitée et la clôture outillée, le dossier qui donne la spécification validée

> statut : en cours · origine : J-2026-11-16-AB · après : L-0018, T-0054, T-0055, T-0056, T-0062, T-0087, T-0103 · lu : backlog@050e512a

Formé le 16 novembre (J-2026-11-16-AB) pour les constats de la revue de
T-0047 (J-2026-11-16-Y), qui n'avaient pas de lot : tous touchent
l'historique des revues d'un lot et le dossier de `socle review`
(`engine/socle/review.py`, `engine/socle/memory.py`, le skill
`socle-review`) ; une seule revue les juge. Avant L-0005 : chaque lot
suivant se relit avec cet outil.

Le 17 novembre, D-0129 y ajoute B-0277 et sa tâche T-0062 (J-2026-11-17-H) : le relecteur reçoit le chemin du dossier de `socle review`, que ce lot touche aussi.

## Revues

### Passe 1 — 2026-11-19

Commits : d4d66ac..1772e68

- Bloquant : la ligne de bloquant sans puce, ni lue ni refusée
- Bloquant : le détail d'un constat privé non masqué en CI
- Ouvre : B-0298, B-0299, T-0104, T-0105

Recul : le premier bloquant a la cause de ce que T-0054 corrigeait, une
lecture des lignes de la section « Revues » par un motif plus étroit que
ce qu'un agent écrit ; le second est neuf, le détail que T-0055 ajoute aux
constats sans passer par le masquage de la zone privée. Ce que le lot
ouvre est de la nature de ce qu'il ferme : des suites de ses propres
tâches, plus petites (l'étape 2 du skill, le lot compté parmi ses
entrées closes, le guide). Les lots clos sur ces fichiers, L-0013 et
L-0018, ont déjà ouvert de telles suites, dont ce lot ; elles décroissent,
et les deux corrections tiennent en quelques lignes, chacune avec son
test : pas de passe de plus, la clôture suit. Décision : continuer.
