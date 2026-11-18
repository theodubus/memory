<!-- socle: couche=backlog zone=publique -->
# L-0018 — Lot des allégements de D-0134 : le coût d'un lot suit sa taille

> statut : ouvert · origine : D-0134 · après : L-0017, T-0037 · lu : backlog@7b27e264

Formé le 18 novembre pour les cinq allégements que Théo a validés
(D-0134), écrits dans `docs/fabrication/allegements.md` : que le coût
d'un lot suive sa taille, mesuré sur L-0016 (75 % de la fenêtre de cinq
heures pour un correctif de format). Après L-0017, avant L-0015 : il
allège tous les lots qui suivent.

Ce qu'il portera, une tâche ou plus par proposition :
1. le circuit court des petits lots : l'orchestrateur implémente sous un
   seuil mesuré, le relecteur reçoit un dossier court (le diff et les
   critères), sauf un lot qui touche un garde-fou ou un format que
   d'autres parties lisent (les skills `socle-batch` et `socle-review`,
   `socle review`, leurs copies protégées) ;
2. la variante légère pour des valeurs attendues mécaniques, dans le
   skill `socle-request` du produit (le skill `delegate-lot` la dit
   déjà) ;
3. le hook de fin de tour qui ne recopie plus tous les échecs, mais le
   nom des contrôles, la première ligne utile de chaque test et la
   commande qui montre tout ;
4. une décision de séance qui désigne le texte qu'elle approuve, B-0286 ;
5. le coût d'un lot estimé à son annonce : T-0037, tirée de L-0009, puis
   étendue au lot.

Les tâches des points 1 à 4 s'ouvrent après l'intégration de la
passation de L-0016 (`docs/fabrication/passation-l0016/`) : avant, elles
prendraient les numéros que portent ses correctifs.
