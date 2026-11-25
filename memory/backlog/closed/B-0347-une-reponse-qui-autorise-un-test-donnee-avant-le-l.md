<!-- socle: couche=backlog zone=publique -->
# B-0347 — Une réponse qui autorise un test, donnée avant le lot qui le change, n'a pas où attendre quand ce lot se fait dans une autre session cloud

> statut : fait · origine : J-2026-11-24-AG · ref : J-2026-11-25-T, T-0134, B-0142 · lu : backlog@e1d104b0

Deux règles du produit se contredisent en session cloud, un lot par
session. T-0134 veut que la demande d'un test contraire se pose dès la
tâche ouverte, avant son lot ; B-0142, qu'une réponse `valider` se
pousse avec le changement qu'elle autorise, jamais avant, la CI ne
comptant que les validations de sa plage. Quand l'humain répond avant
le lot, et que le lot se fait dans une autre session, la réponse n'a
nulle part où attendre : le conteneur qui l'a reçue disparaît, et
poussée seule, elle ne couvre plus le test. Vu le 24 novembre, pour
T-0174 (J-2026-11-24-AG) ; le 24 aussi, la réponse de D-0174 a dû
partir en correctif dans un dossier de passation (J-2026-11-24-Z).

## Satisfait quand

- [x] une réponse donnée avant le lot de son changement couvre ce changement quand il est poussé plus tard, dans une autre session, et un test le montre
